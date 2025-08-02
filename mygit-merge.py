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

def get_all_files(*commits):
    all_files = set()
    for commit in commits:
        with open(f".mygit/commits/{commit}/snapshot.txt") as files:
            for file in files:
                file = file.strip().split("/")[0]
                all_files.add(file)
    return all_files

def compare_commit(file,current,target):
    branching_point = mygit_util.GitUtil.common_ancestor(current,target)
    #print(file,current,target)
    original_file = mygit_util.GitUtil.cat_file(file,branching_point)
    current_file = mygit_util.GitUtil.cat_file(file,current)
    target_file = mygit_util.GitUtil.cat_file(file,target)
    if original_file or current_file or target_file:
        print(f"original {file}",original_file,sep="\n")
        print(f"current branch {file}",current_file,sep="\n")
        print(f"target {file}",target_file,sep="\n")

def merge_cases(current,target):
    branching_point = int(mygit_util.GitUtil.common_ancestor(current,target))
    if branching_point == current and target > current:
        print("Fast Forward")
    if branching_point == target and current > target:
        print("Already Merged")
    


if __name__ == "__main__":
    target, msg = parse_args()
    current = mygit_util.GitUtil.current_node()
    if not target.isdigit():
        with open(f".mygit/refs/heads/{target}/latest_commit") as target_head:
            target = target_head.read()
    all_files = get_all_files(current,target)
    for file in all_files:
        compare_commit(file,current,target)
    
    
    