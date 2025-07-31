#!/usr/bin/env python3
import sys
from glob import glob
import mygit_util
import os

args = sys.argv[1:]

def usage_check(args):
    if len(args) != 1:
        print("usage: mygit-checkout <branch>")
        exit(1)

def error_check(branch_name):
    if not glob(f".mygit/refs/heads/{branch_name}"):
        print(glob(f".mygit/refs/branch/{branch_name}"))
        print(f"mygit-checkout: error: unknown branch '{branch_name}'")
        exit(1)
    
    

def detect_conflict(target_branch): # only check tracked file
    conflict = False
    conflicted_file = []
    curr_branch_file = set(glob("*"))
    target_branch_files = glob(f".mygit/refs/heads/{target_branch}/HEAD")[0]
    
    with open(target_branch_files,"r") as files:
        target_file = files.readlines()
    target_branch_files = {file.strip().split("/")[0] for file in target_file}

    all_files = curr_branch_file.union(target_branch_files)

    for file in all_files:
        if not os.path.isfile(file):
            continue  
        
        dir_hash = mygit_util.DiffCheck.get_dir_hash(file)
        index_hash = mygit_util.DiffCheck.get_index_hash(file)
        head_hash = mygit_util.DiffCheck.get_HEAD_hash(file)
        target_hash = mygit_util.DiffCheck.get_HEAD_hash(file,f".mygit/refs/heads/{target_branch}/HEAD")

        if not index_hash and not head_hash and not target_hash:
            continue

        elif head_hash != target_hash:
            if dir_hash != index_hash:
                conflicted_file.append(file)
                conflict =True
    if conflict:
        conflicted_file = sorted(conflicted_file)
        print("mygit-checkout: error: Your changes to the following files would be overwritten by checkout:")
        print(("\n").join(conflicted_file))
        exit(1)
        
def switch_to(target_branch):
    print(f"Switched to branch '{target_branch}'")
    target_branch_files = glob(f".mygit/refs/heads/{target_branch}/HEAD")[0]

    with open(target_branch_files,"r") as target_files:
        targets = {target.strip().split("/")[0]:target.strip().split("/")[1] for target in target_files.readlines()}        # if comback to this later, please make it readable
    
    for name,hash in targets.items():
        with open(f".mygit/objects/{hash}","r") as object:
            with open(name,"w") as dir_file:
                dir_file.writelines(object.readlines())

    # not done, need to remove file that in one branch, but not in the other

if __name__ == "__main__":
    usage_check(args)
    check = mygit_util.ErrorCheck()
    check.checkout_check()
    branch_name = args[0]
    error_check(branch_name)
    detect_conflict(branch_name)
    mygit_util.GitUtil.save_HEAD()
    switch_to(branch_name)