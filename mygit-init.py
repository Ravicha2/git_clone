#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import mygit_util

def usage_check():
    if sys.argv[1:]:
        print("usage: mygit-init",file=sys.stderr)
        exit(1)

def git_init():
    print("Initialized empty mygit repository in .mygit")
    os.mkdir(".mygit")
    os.mkdir(".mygit/objects")
    os.mkdir(".mygit/index")
    os.mkdir(".mygit/commits")
    Path(".mygit/HEAD").touch()
    os.mkdir(".mygit/refs")
    os.mkdir(".mygit/refs/heads/")
    os.mkdir(".mygit/refs/branch/")
    Path(".mygit/refs/branch/trunk").touch()
    os.mkdir(".mygit/refs/heads/trunk")
    Path(".mygit/refs/heads/trunk/HEAD").touch()

if __name__ == "__main__":
    usage_check()
    check = mygit_util.ErrorCheck()
    check.init_check()
    git_init()