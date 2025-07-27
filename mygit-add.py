#!/usr/bin/env python3
import sys
import mygit_util

files = sys.argv[1:]
            
def usage_check():
    if not files:
        print("usage: mygit-add <filenames>")
        exit(1)

if __name__ == "__main__":
    usage_check()
    check = mygit_util.ErrorCheck()
    check.add_check(files)
    mygit_util.GitUtil.git_add(files)