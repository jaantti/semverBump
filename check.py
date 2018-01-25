#!/usr/bin/python3
import argparse
from enum import Enum
import semantic_version as semver
import subprocess
import sys

CONF_FILE = 'conf.hpp'
CONF_VARIABLE = 'version'
CONF_LENGTH = 4


class Version(Enum):
    LAST = 1
    HEAD = 2


def raiseError(message):
    print('Error:', message)
    sys.exit(0)


def checkWorkingDirectory():
    dirStatus = subprocess.check_output(['git', 'status', '--porcelain'])
    return dirStatus.decode('utf-8')


def isRemoteUpToDate():
    dirStatus = subprocess.check_output(['git', 'cherry'])
    if len(dirStatus.decode('utf-8')) == 0:
        return True
    else:
        return False


def getVersion(versionType):
    ver = ''
    try:
        if versionType == Version.HEAD:
            ver = subprocess.check_output(['git', 'describe', '--tags', '--exact-match', 'HEAD'])
        elif versionType == Version.LAST:
            ver = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0'])
        else:
            raiseError('Wrong versionType:', versionType)
        ver = ver.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        pass

    return ver


def updateLocal():
    try:
        subprocess.run(['git', 'fetch'], check=True)
        subprocess.run(['git', 'pull'], check=True)
    except subprocess.CalledProcessError as e:
        raiseError('Failed to update from remote: ' + str(e))


def tagAndPush(tagName):
    try:
        subprocess.run(['git', 'tag', tagName])
        subprocess.run(['git', 'push', '--tags'])
    except subprocess.CalledProcessError as e:
        raiseError('Failed to tag commit: ' + str(e))


def checkVersionInSource(filename, variable, version):
    versionCorrect = False
    try:
        with open(filename, 'r') as f:
            for line in f:
                if variable in line:
                    try:
                        newLine = line[line.index('{') + 1:line.index('}')]
                        ver = [i.strip() for i in newLine.split(',')]
                        if len(ver) == CONF_LENGTH and ver[3] == '0':
                            versionString = '.'.join(ver[:-1])
                            if semver.validate(versionString) and version == semver.Version(versionString):
                                versionCorrect = True
                                break
                    except ValueError:
                        continue
    except FileNotFoundError:
        raiseError('File not found: ' + filename)
    return versionCorrect


parser = argparse.ArgumentParser(description='Check and bump software version')
parser.add_argument('-b', '--bump', help='bump major|minor|patch. Bumps major, minor or patch part of software version', nargs='?')

args = parser.parse_args()

if args.bump:
    if args.bump in ('major', 'minor', 'patch'):
        updateLocal()

        remoteUpToDate = isRemoteUpToDate()
        if not remoteUpToDate:
            raiseError('Local changes are not pushed to remote')

        clean = checkWorkingDirectory()
        if len(clean) != 0:
            raiseError('Working directory not clean')

        versionLast = getVersion(Version.LAST)
        versionHead = getVersion(Version.HEAD)
        if len(versionLast) == 0:
            raiseError('Failed to get software version')

        if versionLast == versionHead:
            raiseError('Commit is already tagged: ' + versionHead)

        verCorrect = semver.validate(versionLast)
        if not verCorrect:
            raiseError('Previous version not in correct format: ' + versionLast)

        oldVersion = semver.Version(versionLast)

        nextVersion = semver.Version(versionLast)
        if args.bump == 'major':
            nextVersion = oldVersion.next_major()
        elif args.bump == 'minor':
            nextVersion = oldVersion.next_minor()
        elif args.bump == 'patch':
            nextVersion = oldVersion.next_patch()

        if (not checkVersionInSource(CONF_FILE, CONF_VARIABLE, nextVersion)):
            raiseError("Version in '" + CONF_FILE + "' needs to be updated to " + str(nextVersion))

        print('Updating version:', str(oldVersion), '->', str(nextVersion))
        userInput = input('Is this correct (y/n)?: ')
        if userInput in ('y', 'n'):
            if userInput == 'n':
                print('Exiting...')
                sys.exit(0)
        else:
            raiseError('Invalid input')

        tagAndPush(str(nextVersion))
        print('Success')

    else:
        parser.print_help()
        raiseError('Invalid parameter')
