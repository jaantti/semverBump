#!/usr/bin/python3
import argparse
from enum import Enum
import semantic_version as semver
import subprocess
import sys


class Version(Enum):
    LAST = 1
    HEAD = 2


def raiseError(message):
    print('Error:', message)
    sys.exit(0)


def checkWorkingDirectory():
    dirStatus = subprocess.check_output(['git', 'status', '--porcelain'])
    return dirStatus.decode('utf-8')


def getVersion(versionType):
    ver = ''
    try:
        if versionType == Version.HEAD:
            ver = subprocess.check_output(['git', 'describe', '--tags', '--exact-match', 'HEAD'])
        elif versionType == Version.LAST:
            ver = subprocess.check_output(['git', 'describe', '--tags'])
        else:
            raiseError('Wron versionType:', versionType)
        ver = ver.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        #print('Failed to get version:', str(e))
        pass

    return ver


def updateLocal():
    try:
        subprocess.run(['git', 'fetch'], check=True)
        subprocess.run(['git', 'pull'], check=True)
    except subprocess.CalledProcessError as e:
        raiseError('Failed to update from remote: ' + str(e))


parser = argparse.ArgumentParser(description='Check and bump software version')
parser.add_argument('-b', '--bump', help='bump major|minor|patch. Bumps major, minor or patch part of software version', nargs='?')
# parser.add_argument('-c', '--conf', help='Configuration file name (from dir conf/)', nargs='?')

args = parser.parse_args()

if args.bump:
    if args.bump in ('major', 'minor', 'patch'):
        updateLocal()
                
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

        print('Updating version:', str(oldVersion), '->', str(nextVersion))
        userInput = input('Is this correct (y/n)?: ')
        if userInput in ('y', 'n'):
            if userInput == 'n':
                print('Exiting...')
                sys.exit(0)
        else:
            raiseError('Invalid input')

    else:
        parser.print_help()
        raiseError('Invalid parameter')
