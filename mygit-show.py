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

def dissect(arg1)->tuple:
    """
    dissect argument 1 which separte by ':' into 2 arguments
    """
    index = arg1.index(":")    
    commit_num = arg1[:index]
    filename = arg1[index+1:]
    return commit_num, filename

def show_file(commit_num,filename)->None:
    """
        use cat_file from GitUtil to show file content,
        however, cat_file can only show commited file, to show file from index, need to handle separately 
    """
    if commit_num:
        hash_val = mygit_util.GitUtil.find_file(filename,commit_num)

        if not hash_val:
            print(f"mygit-show: error: '{filename}' not found in commit {commit_num}")
            exit(1)
        if mygit_util.GitUtil.cat_file(filename,commit_num):
            print(mygit_util.GitUtil.cat_file(filename,commit_num))
        
    else:
        index_file = glob(f".mygit/index/{filename}/*")

        if index_file:
            with open(index_file[0],"r") as id_file:
                content = id_file.read().strip()
            if content:
                print(content)
            return
        else:
            print(f"mygit-show: error: '{filename}' not found in index")
            exit(1)
            
            
if __name__ == "__main__":
    usage_check()
    commit_num, filename = dissect(arg1)
    check = mygit_util.ErrorCheck()
    check.show_check(commit_num,filename)
    show_file(commit_num,filename)