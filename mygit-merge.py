#!/usr/bin/env python3
import sys
import argparse
import mygit_util
from glob import glob

args = sys.argv[1:]

class MyArgumentParser(argparse.ArgumentParser):
    def error(self, _):
        print("usage: mygit-merge <branch|commit> -m message")
        sys.exit(1)

def parse_args():
    parser = MyArgumentParser()
    
    parser.add_argument('target', help='target branch or commit')
    parser.add_argument('-m', dest='message', required=True, help='merge commit message')
    args = parser.parse_args()

    args = parser.parse_args()
    target = args.target
    msg = args.message
    return target, msg

def compare_commit(file,current,target):
    branching_point = mygit_util.GitUtil.common_ancestor(current,target)
    #print(file,current,target)
    original_file = mygit_util.GitUtil.cat_file(file,branching_point)
    current_file = mygit_util.GitUtil.cat_file(file,current)
    target_file = mygit_util.GitUtil.cat_file(file,target)
    print("original file",original_file,sep="\n")
    print("current branch file",current_file,sep="\n")
    print("target file",target_file,sep="\n")


if __name__ == "__main__":
    target, msg = parse_args()
    current = mygit_util.GitUtil.current_node()
    if not target.isdigit():
        with open(f".mygit/refs/heads/{target}/latest_commit") as target_head:
            target = target_head.read()
    compare_commit(1,current,target)
    
    
    