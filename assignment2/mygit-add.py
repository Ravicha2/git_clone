#!/usr/bin/env python3
import sys,shutil,os
from glob import glob
from mygit_util import ErrorCheck, DiffCheck

files = sys.argv[1:]


def addfile(files):
    if not os.path.isdir(".mygit/index"):
            os.mkdir(".mygit/index")
    for file in files:
        if not os.path.isdir(f".mygit/index/{file}"):
             os.mkdir(f".mygit/index/{file}")

        hashedName = DiffCheck.hashContent(file)
        index = f".mygit/index/{file}/{hashedName}"

        with open(".mygit/HEAD",'r') as cached:
            heads = cached.readlines()
            heads = [head.strip() for head in heads]
        if file+"/"+hashedName in heads:
             continue
        current_index = glob(f".mygit/index/{file}/*")
        if current_index:
            os.remove(current_index[0])
        shutil.copy(file,index)
            

def usage_check():
    if not files:
        print("usage: mygit-add <filenames>")
        exit(1)

if __name__ == "__main__":
    usage_check()
    check = ErrorCheck()
    check.add_check(files)
    addfile(files)        