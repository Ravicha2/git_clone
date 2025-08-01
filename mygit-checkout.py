#!/usr/bin/env python3
import sys
from glob import glob
import mygit_util
import os
from pathlib import Path


args = sys.argv[1:]

def usage_check(args):
    if len(args) != 1:
        print("usage: mygit-checkout <branch>")
        exit(1)

def error_check(branch_name):
    if not glob(f".mygit/refs/heads/{branch_name}"):
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
    current_head = glob(".mygit/refs/branch/*")[0]
    os.remove(current_head)
    Path(f".mygit/refs/branch/{target_branch}").touch()
    target_head_path = glob(f".mygit/refs/heads/{target_branch}/HEAD")[0]
    with open(target_head_path, "r") as target_head_file:
        target_files = {}
        for line in target_head_file:
            filename, hash_val = line.strip().split("/")
            target_files[filename] = hash_val

    with open(".mygit/HEAD","r") as head:
        curr_head_files = {file.strip().split("/")[0] for file in head}
    
    to_delete = curr_head_files - set(target_files.keys())

    for file in to_delete:
        if os.path.exists(file):
            os.remove(file)

    for name,hash_val in target_files.items():
        with open(f".mygit/objects/{hash_val}","r") as object:
            with open(name,"w") as dir_file:
                dir_file.writelines(object.readlines())

    with open(".mygit/HEAD", "w") as head_file:
        for filename, hash_val in target_files.items():
            head_file.write(f"{filename}/{hash_val}\n")

if __name__ == "__main__":
    usage_check(args)
    check = mygit_util.ErrorCheck()
    check.checkout_check()
    branch_name = args[0]
    error_check(branch_name)
    detect_conflict(branch_name)
    mygit_util.GitUtil.save_HEAD()
    switch_to(branch_name)