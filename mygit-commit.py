#!/usr/bin/env python3
import sys
import os
import mygit_util
from glob import glob
import shutil
from pathlib import Path

args = sys.argv[1:]

def raise_error():
    print("usage: mygit-commit [-a] -m commit-message")
    exit(1)

def usage_check():
    len_arg = len(args)

    if len_arg == 2:
        if args[0] not in {"-m", "-am"}:
            raise_error()
    elif len_arg == 3:
        if args[0] != "-a" or args[1] != "-m":
            raise_error()
    else:
        raise_error()
    
def autoadd():
    staged = glob(".mygit/index/*")
    files = [file.split("/")[-1] for file in staged]
    mygit_util.GitUtil.git_add(files)
                            
def add_to_HEAD(filename, hash):
    head_path = ".mygit/HEAD"
    new_version = True
    

    if os.path.exists(head_path):
        with open(".mygit/HEAD", 'r') as head:
            cached = head.readlines()
        for line in cached:
            if line.strip() == f"{filename}/{hash}":
                new_version = False
                break

    if new_version:
        with open(head_path, 'r') as head:
            lines = head.readlines()

        with open(head_path, 'w') as head:
            for line in lines:
                if not line.startswith(f"{filename}/"):
                    head.write(line)
            head.write(f"{filename}/{hash}\n")

    return new_version
    
def clean_head():
    indices = glob(".mygit/index/*/*")
    index_file = set()

    for i in indices:
        filename = i.strip().split("/")[-2]
        index_file.add(filename)

    new_version = False
    with open(".mygit/HEAD", 'r') as head:
        lines = head.readlines()
        cleaned_line = []

    for line in lines:
        line = line.strip()
        filename = line.split("/")[0]

        if filename in index_file:
            cleaned_line.append(line+"\n")
        else:
            new_version = True
    with open(".mygit/HEAD","w") as cleaned_head:
        cleaned_head.writelines(cleaned_line)
        
    return new_version


def commit():
    instage = glob(".mygit/index/*")
    if not instage:
        with open(".mygit/HEAD", 'r') as head:
            if not head.read().strip():
                print("nothing to commit")
                return
            
    change = clean_head()

    for file in instage:
        index = glob(file+"/*")[0]
        pointer = index.split("/")
        hash_val = pointer[-1]
        filename = pointer[-2]
        new_version = add_to_HEAD(filename,hash_val)
        if new_version:
            change = True
            shutil.copy(index,f".mygit/objects/{hash_val}")

    #change = clean_head()
    if change:
        mygit_util.GitUtil.commit_log(args[1])
    else:
        print("nothing to commit")
        return


if __name__ == "__main__":
    usage_check()
    check = mygit_util.ErrorCheck()
    check.commit_check()
    if args[0] in {"-a","-am"}:
        autoadd()
    commit()