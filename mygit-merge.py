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
    original_file = mygit_util.GitUtil.find_file(file,branching_point)
    current_file = mygit_util.GitUtil.find_file(file,current)
    target_file = mygit_util.GitUtil.find_file(file,target)
    if current_file == target_file:
        print("Merge Compatible: Select one")
    else:
        if original_file == current_file:
            print("Merge Compatible: target file changed")
        elif original_file == target_file:
            print("Merge Compatible: Current file changed")
        else:
            print("Merge incompatible: both file changed")
            exit(1)
    

def merge_cases(current_commit,target_commit):
    branching_point = int(mygit_util.GitUtil.common_ancestor(current_commit,target_commit))
    current_commit = int(current_commit)
    target_commit = int(target_commit)

    if branching_point == current_commit:
        if target_commit > current_commit:
            print("Fast Forward Merge Required")
    elif branching_point == target_commit:
        if current_commit > target_commit:
            print("Already Merged")
            exit(0)
    else:
        print("Branches Diverged — True Merge Required")

def FF_merge():
    pass

def true_merge():
    pass

if __name__ == "__main__":
    target, msg = parse_args()
    current = mygit_util.GitUtil.current_node()
    if not target.isdigit():
        with open(f".mygit/refs/heads/{target}/latest_commit") as target_head:
            target = target_head.read()
    all_files = get_all_files(current,target)
    merge_cases(current,target)
    for file in all_files:
        compare_commit(file,current,target)
    
    
    