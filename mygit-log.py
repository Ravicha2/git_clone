#!/usr/bin/env python3
import sys
from glob import glob
import mygit_util


def usage_check():
    try:
        if len(sys.argv) > 1:
            raise NameError
    except NameError:
        print("usage: mygit-log")

def log():
    current_node = mygit_util.GitUtil.current_node()
    ancestor_list = list(mygit_util.GitUtil.ancestors(current_node,set(current_node)))
    for commit_num in sorted(ancestor_list,reverse=True):
        if int(commit_num) >= 0:
            with open(".mygit/commits/"+str(commit_num)+"/COMMIT_MSG",'r') as commit_msg:
                msg = commit_msg.read()
                print(f"{commit_num} {msg}")


if __name__ == "__main__":
    usage_check()
    check = mygit_util.ErrorCheck()
    check.log_check()
    log()
