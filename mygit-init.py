#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import mygit_util


def usage_check():
    if sys.argv[1:]:
        print("usage: mygit-init",file=sys.stderr)
        exit(1)

def git_init()->None:
    """
    .mygit
    ├── HEAD                        (current HEAD)
    ├── commits                     (commits will record here)
    ├── index                       (index)
    ├── objects                     (file content will record here)
    └── refs                        (reference point, useful when working with branches)
        ├── branch
        │   └── trunk               (current branch)
        └── heads
            └── trunk
                ├── HEAD            (latest version of everything on this branch)
                └── latest_commit   (latest commit, start with -1)

    """
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
    Path(".mygit/refs/heads/trunk/latest_commit").touch()
    with open(".mygit/refs/heads/trunk/latest_commit",'w') as init:
        init.write("-1")

if __name__ == "__main__":
    usage_check()
    check = mygit_util.ErrorCheck()
    check.init_check()
    git_init()