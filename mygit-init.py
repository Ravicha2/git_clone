#!/usr/bin/env python3
import os
import sys
from mygit_util import ErrorCheck

def usage_check():
    if sys.argv[1:]:
        print("usage: mygit-init")
        exit(1)

def git_init():
    print("Initialized empty mygit repository in .mygit")
    os.mkdir(".mygit")
    os.mkdir(".mygit/objects")
    os.mkdir(".mygit/index")
    os.mkdir(".mygit/commits")
    os.mkdir(".mygit/HEAD")
    os.mkdir(".mygit/refs")
    os.mkdir(".mygit/refs/heads")

if __name__ == "__main__":
    usage_check()
    check = ErrorCheck()
    check.init_check()
    git_init()