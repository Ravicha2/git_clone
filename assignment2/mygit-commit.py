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

def add_to_HEAD(filename, hash):
    head_path = ".mygit/HEAD"
    new_version = True

    if os.path.exists(head_path):
        with open(head_path, 'r') as head:
            cached = head.readlines()
            for line in cached:
                if line.strip() == f"{filename}/{hash}":
                    new_version = False

    if new_version:
        with open(head_path, 'r') as head:
            lines = head.readlines()

        with open(head_path, 'w') as head:
            for line in lines:
                if not line.startswith(f"{filename}/"):
                    head.write(line)
            head.write(f"{filename}/{hash}\n")

    return new_version



def commit():
    instage = glob(".mygit/index/*")
    if not instage:
        print("nothing to commit")
        return
    change = False

    for file in instage:
        index = glob(file+"/*")[0]
        pointer = index.split("/")
        hash_val = pointer[-1]
        filename = pointer[-2]
        new_version = add_to_HEAD(filename,hash_val)
        if new_version:
            change = True
            shutil.copy(index,f".mygit/objects/{hash_val}")
    if change:
        commit_log()
    else:
        print("nothing to commit")
        return


if __name__ == "__main__":
    usage_check()
    check = mygit_util.ErrorCheck()
    check.commit_check()
    commit()