#!/usr/bin/python3

import semantic_version as semver
import subprocess


def checkWorkingDirectory():
    dirStatus = subprocess.check_output(['git', 'status', '--porcelain'])
    return dirStatus.decode('utf-8')


def getVersion():
    ver = ''
    try:
        ver = subprocess.check_output(['git', 'describe', '--tags', '--exact-match', 'HEAD'])
        ver = ver.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print("Failed to get version:", str(e))

    return ver


v = getVersion()
print(v)
print(checkWorkingDirectory())
