#!/usr/bin/env python3
import sys
import argparse
import os
import mygit_util
from glob import glob
import shutil
from pathlib import Path

args = sys.argv[1:]

class MyArgumentParser(argparse.ArgumentParser):
    def error(self, _):
        print("usage: mygit-branch [-d] <branch>")
        sys.exit(1)
        
def error_check(delete,branch_name):
    """
        check if branch can be add or delete
    """
    branches = [Path(branch).name for branch in glob(".mygit/refs/heads/*")]
    if not delete:
        if branch_name in branches:
            print(f"mygit-branch: error: branch '{branch_name}' already exists")
            exit(1)
    else:
        if not branch_name:
            print("mygit-branch: error: branch name required")
            exit(1)
        if branch_name not in branches:
            print(f"mygit-branch: error: branch '{branch_name}' doesn't exist")
            exit(1)

def parse_args():
    parser = MyArgumentParser()
    
    parser.add_argument('-d', action='store_true', help='remove branch')
    parser.add_argument('branch_name', nargs='?', help='new/removed branch name')

    args = parser.parse_args()
    delete = args.d
    branch_name = args.branch_name  

    if not branch_name and delete:
        parser.error("branch name required")

    return delete, branch_name

def create_branch(branch_name):
    """
    1. save head just in case
    2. add new branch records
    3. write current commit  to branch record
    """
    mygit_util.GitUtil.save_HEAD()
    os.mkdir(f".mygit/refs/heads/{branch_name}")
    Path(f".mygit/refs/heads/{branch_name}/HEAD").touch()
    Path(f".mygit/refs/heads/{branch_name}/latest_commit").touch()
    
    current = mygit_util.GitUtil.current_node()
    with open(f".mygit/refs/heads/{branch_name}/latest_commit","w") as latest_commit:
        latest_commit.write(current)

    with open(".mygit/HEAD","r") as head:
        head_file = head.readlines()
    with open(f".mygit/refs/heads/{branch_name}/HEAD","w") as new_branch:
        new_branch.writelines(head_file)

def delete_branch(branch_name):
    """
    1. check if it can be deleted (trunk, current branch or unmerge)
    2. delete branch
    """
    current_branch = Path(glob(".mygit/refs/branch/*")[0]).name
    
    if branch_name == "trunk":
        print("mygit-branch: error: can not delete branch 'trunk': default branch")
        exit(1)

    if branch_name == current_branch:
        print(f"mygit-branch: error: can not delete branch '{branch_name}': current branch")
        exit(1)


    with open(f".mygit/refs/heads/{branch_name}/latest_commit") as target_head:
        target = target_head.read()
    current_node = mygit_util.GitUtil.current_node()

    ancestors = mygit_util.GitUtil.ancestors(current_node,set(current_node))
    if target not in ancestors:
        print(f"mygit-branch: error: branch '{branch_name}' has unmerged changes")
        exit(1)


    shutil.rmtree(f".mygit/refs/heads/{branch_name}")
    print(f"Deleted branch '{branch_name}'")

if __name__ == "__main__":
    if not glob(".mygit/commits/*"):
        print("mygit-branch: error: this command can not be run until after the first commit")
        exit(1)
    delete, branch_name = parse_args()
    check = mygit_util.ErrorCheck()
    check.branch_check(branch_name)
    error_check(delete,branch_name)
    if not delete:
        if branch_name:
            create_branch(branch_name)
        else:
            for branch in sorted(glob(".mygit/refs/heads/*")):
                print(branch.split("/")[-1])
    if delete:
        delete_branch(branch_name) 
    