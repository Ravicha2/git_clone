#!/usr/bin/env python3
import sys
import mygit_util
import os
from glob import glob
from collections import defaultdict, OrderedDict

def usage_check():
    if sys.argv[1:]:
        print("usage: mygit-status")
        exit (1)

def get_dir_hash():
    files = glob("*")
    dir_hash = defaultdict(str)
    for file in sorted(files):
        if os.path.isfile(file):
            hash = mygit_util.DiffCheck.hashContent(file)
            dir_hash[file] = hash
    return dir_hash

def get_index_hash(path):
    files = glob(path)
    paths = [file.split("/")[-2:] for file in files]
    hashes = defaultdict(str)
    for path in paths:
        hashes[path[0]] = path[1]

    return hashes

def get_HEAD_hash(path):
    hashes = defaultdict(str)
    with open(path,"r") as heads:
        heads = [head.strip() for head in heads]
        for head in heads:
            head = head.split("/")
            hashes[head[0]] = head[1]
    return hashes

def print_status(file,status):
    print(f"{file} - {status}")

def build_status_message(*status):
    return (", ").join(status)

def hash_changed(hash1,hash2):
    return hash1 != hash2


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
        dir_hash = dir_hashes[file]
        index_hash = index_hashes[file]
        head_hash = head_hashes[file]

        if existed["dir"] and not existed["index"] and not existed["head"]:         # only in dir (100,200)
            msg = build_status_message("untracked")     
        
        if not existed["dir"] and (existed["index"] or existed["head"]):            # not in dir and in index or head (001,010,011)
            msg = build_status_message("file deleted")      
        
        if not existed['index'] and existed['head']:                                # not in index and in head (001,101,201)
            msg = build_status_message("deleted from index",msg)        
                    
        if existed['index'] and not existed['head']:                                # in index and not in head (010,110,210)
            msg = build_status_message("add to index",msg)      
        
        if existed['dir'] and existed['head'] and not existed['index']:             # in dir and in head and not in index (101,201,)
            if hash_changed(dir_hash, head_hash):       
                msg = build_status_message(msg,"file change")       
        
        if not existed["dir"] and existed['index'] and existed['head']:             # not in dir and in index and head
            if hash_changed(index_hash, head_hash):
                msg = build_status_message(msg,"changes staged for commit")
            else:
                msg = build_status_message(msg, "changes not staged for commit")

        if existed['dir'] and existed['index'] and existed['head']:
            if not hash_changed(dir_hash, index_hash) and \
                not hash_changed(dir_hash, head_hash):
                msg = build_status_message("same as repo")
        
            elif hash_changed(dir_hash, head_hash):
                msg = build_status_message("file changed")
        
                if not hash_changed(dir_hash,index_hash):
                    msg = build_status_message(msg, "changes staged for commit")
        
                elif not hash_changed(index_hash, head_hash):
                    msg = build_status_message(msg,"changes not staged for commit")
        
                else:
                    msg = build_status_message(msg,"different changes staged for commit")
        print_status(file,msg)

if __name__ == "__main__":
    usage_check()
    dir_hashes = get_dir_hash()
    index_hashes = get_index_hash(".mygit/index/*/*")
    head_hashes = get_HEAD_hash(".mygit/HEAD")
    eval_status(dir_hashes,index_hashes,head_hashes)