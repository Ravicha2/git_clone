#!/usr/bin/env python3
import sys
import mygit_util
import os
from glob import glob

def usage_check():
    if sys.argv[1:]:
        print("usage: mygit-status",file=sys.stderr)
        sys.exit (1)

def get_dir_hashes():
    files = glob("*")
    dir_hash = dict()
    for file in sorted(files):
        if os.path.isfile(file):
            hash = mygit_util.DiffCheck.hashContent(file)
            dir_hash[file] = hash
    return dir_hash

def get_index_hashes(path):
    files = glob(path)
    paths = [file.split("/")[-2:] for file in files]
    hashes = dict()
    for path in paths:
        hashes[path[0]] = path[1]

    return hashes

def get_HEAD_hashes(path):
    hashes = dict()
    with open(path,"r") as heads:
        heads = [head.strip() for head in heads]
        for head in heads:
            head = head.split("/")
            hashes[head[0]] = head[1]
    return hashes

def print_status(file,status):
    print(f"{file} - {status}")

def build_status_message(*statuses):
    status = [status for status in statuses if status]
    return (", ").join(status)


def eval_status(dir_hashes,index_hashes,head_hashes):
    dir_files, index_files, head_files = list(dir_hashes.keys()),list(index_hashes.keys()),list(head_hashes.keys())
    all_files = sorted(list(set(dir_files+index_files+head_files)))
    for file in all_files:
        msg = ""
        existed = {
            "dir": file in dir_files,
            "index": file in index_files,
            "head": file in head_files
        }
        state = mygit_util.DiffCheck.state_check(file)
        if existed["dir"] and not existed["index"] and not existed["head"]:         # only in dir (100,200)
            msg = build_status_message("untracked")     
        
        if not existed["dir"] and (existed["index"] or existed["head"]):            # not in dir and in index or head (001,010,011)
            msg = build_status_message("file deleted")      
        
        if not existed['index'] and existed['head']:                                # not in index and in head (001,101,201)
            msg = build_status_message(msg,"deleted from index")  
            continue      
                    
        if existed['index'] and not existed['head']:                                # in index and not in head (010,110,210)
            msg = build_status_message("added to index",msg)      
        
        if state["d=i"] and state["d=h"] and existed["dir"]:
            msg = build_status_message("same as repo")

        if existed["dir"] and existed["index"] and ((not state["d=i"]) or (not state["d=h"] and existed["head"])):
            msg = build_status_message(msg,"file changed")
            if state["i=h"] and existed["index"]:
                msg = build_status_message(msg, "changes not staged for commit")
            elif state["d=i"]:
                msg = build_status_message(msg, "changes staged for commit")
            else:
                if existed["head"] and existed["index"]:
                    msg = build_status_message(msg, "different changes staged for commit")
    
        print_status(file,msg)

if __name__ == "__main__":
    usage_check()
    check = mygit_util.ErrorCheck()
    check.status_check()
    dir_hashes = get_dir_hashes()
    index_hashes = get_index_hashes(".mygit/index/*/*")
    head_hashes = get_HEAD_hashes(".mygit/HEAD")
    eval_status(dir_hashes,index_hashes,head_hashes)