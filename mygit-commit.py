#!/usr/bin/env python3
import sys
import os
import mygit_util
from glob import glob
import shutil

args = sys.argv[1:]

def usage_check():
    try:
        if len(args) != 2:
            raise NameError
        if args[0] not in ["-m","-a"]:
            raise NameError
    except NameError:
        print("usage: mygit-commit [-a] -m commit-message")

def commit_log():
    commit_num = len(glob(".mygit/commits/*"))
    print(f"Committed as commit {commit_num}")
    os.mkdir(f".mygit/commits/{commit_num}")

    commit_msg = args[1]
    files = [("/").join(file.split("/")[2:]) for file in glob(".mygit/index/*/*")]

    with open(f".mygit/commits/{commit_num}/COMMIT_MSG","w") as msg:
        msg.writelines(commit_msg)
    with open(f".mygit/commits/{commit_num}/snapshot.txt","w") as snapshot:
        for file in files:
            snapshot.writelines(file+"\n")

def commit():
    instage = glob(".mygit/index/*")
    if not instage:
        print("nothing to commit")
        return
    
    commit_log()

    for file in instage:
        path = glob(file+"/*")[0]
        path = path.split("/")
        hash_val = path[-1]
        filename = path[-2]
        if not os.path.isdir(f".mygit/objects/{filename}"):
            os.mkdir(f".mygit/objects/{filename}")
        shutil.move(f".mygit/index/{filename}/{hash_val}",f".mygit/objects/{filename}/")
    
    for file in instage:
        shutil.rmtree(file)
        


if __name__ == "__main__":
    usage_check()
    commit()