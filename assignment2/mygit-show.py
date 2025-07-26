#!/usr/bin/env python3
import sys
import mygit_util
import os
from glob import glob

arg1 = sys.argv[1]

def usage_check():
    if len(sys.argv) != 2:
        print("usage: mygit-show <commit>:<filename>")
        exit(1)

def dissect(arg1):
    index = arg1.index(":")    
    commit_num = arg1[:index]
    filename = arg1[index+1:]
    return commit_num, filename

def find_file(filename,commit_num):

    found = False
    for commit in range(int(commit_num),-1,-1):
        snapshot = glob(f".mygit/commits/{commit}/snapshot.txt")[0]

        with open(snapshot,'r') as file_pointers:
            pointers = file_pointers.readlines()
            for pointer in pointers:
                pointed_file,hash_val = pointer.split("/")
                if pointed_file == filename:
                    found = True
                    hash_val = hash_val
                    break

        if found:
            return hash_val.strip()

    return


def show_file(commit_num,filename):
    if commit_num:
        hash_val = find_file(filename,commit_num)

        if not hash_val:
            print(f"mygit-show: error: '{filename}' not found in commit {commit_num}")
            exit(1)

    else:
        index_file = glob(f".mygit/index/{filename}/*")

        if index_file:
            with open(index_file[0],"r") as id_file:
                content = id_file.read()
            print(content.strip())
            return
        else:
            object_file = glob(f".mygit/commits/*")
            committed_num = max([int(committed.split("/")[-1]) for committed in object_file])
            hash_val = find_file(filename,committed_num)
        if not hash_val:
            print(f"mygit-show: error: '{filename}' not found in index")
            exit(1)
            

    with open(f".mygit/objects/{filename}/{hash_val}") as file:
        content = file.read()
        print(content.strip())
            
if __name__ == "__main__":
    usage_check()
    commit_num, filename = dissect(arg1)
    check = mygit_util.ErrorCheck()
    check.show_check(commit_num,filename)
    show_file(commit_num,filename)