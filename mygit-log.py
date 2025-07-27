#!/usr/bin/env python3
import sys
from glob import glob
from mygit_util import ErrorCheck


def usage_check():
    try:
        if len(sys.argv) > 1:
            raise NameError
    except NameError:
        print("usage: mygit-log")

def log():
    object_file = glob(f".mygit/commits/*")
    committed_num = max([int(committed.split("/")[-1]) for committed in object_file])
    for commit_num in range(committed_num,-1,-1):
        with open(".mygit/commits/"+str(commit_num)+"/COMMIT_MSG",'r') as commit_msg:
            msg = commit_msg.read()
            print(f"{commit_num} {msg}")


if __name__ == "__main__":
    usage_check()
    check = ErrorCheck()
    check.log_check()
    log()
