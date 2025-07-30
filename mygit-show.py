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
    snapshot = glob(f".mygit/commits/{commit_num}/snapshot.txt")
    if snapshot:
        with open(snapshot[0],'r') as file_pointers:
            pointers = file_pointers.readlines()
            for pointer in pointers:
                pointed_file,hash_val = pointer.split("/")
                if pointed_file == filename:
                    found = True
                    break
    else:
        return

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
            print(f"mygit-show: error: '{filename}' not found in index")
            exit(1)
            
    with open(f".mygit/objects/{hash_val}") as file:
        content = file.read()
        print(content.strip())
            
if __name__ == "__main__":
    usage_check()
    commit_num, filename = dissect(arg1)
    check = mygit_util.ErrorCheck()
    check.show_check(commit_num,filename)
    show_file(commit_num,filename)