#!/usr/bin/env python3
import sys,shutil,os
from mygit_util import ErrorCheck, DiffCheck

files = sys.argv[1:]


def addfile(files):
        for file in files:
            if DiffCheck.isExisted(file):
                continue
            if not os.path.isdir(f".mygit/index/{file}"):
                os.mkdir(f".mygit/index/{file}")
            else:
                shutil.rmtree(f".mygit/index/{file}")
                os.mkdir(f".mygit/index/{file}")

            hashedName = DiffCheck.hashContent(file)
            shutil.copy(file, f".mygit/index/{file}/{hashedName}")


def usage_check():
    if not files:
        print("usage: mygit-add <filenames>")
        exit(1)

if __name__ == "__main__":
    usage_check()
    check = ErrorCheck()
    check.add_check(files)
    addfile(files)        