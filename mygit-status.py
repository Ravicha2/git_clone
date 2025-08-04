#!/usr/bin/env python3
import sys
import mygit_util
import os
from glob import glob
from collections import defaultdict

def usage_check():
    if sys.argv[1:]:
        print("usage: mygit-status",file=sys.stderr)
        sys.exit (1)

def get_dir_hashes()-> dict:
    """
    unlike get_dir_hash in GitUtil, this one output dictionary in form of
    {filname:hash}
    """
    files = glob("*")
    dir_hash = defaultdict(str)
    for file in sorted(files):
        if os.path.isfile(file):
            hash = mygit_util.DiffCheck.hashContent(file)
            dir_hash[file] = hash
    return dir_hash

def get_index_hashes(path:str)->dict:
    """
    unlike get_index_hash in GitUtil, this one output dictionary in form of
    {filname:hash}
    """
    files = glob(path)
    paths = [file.split("/")[-2:] for file in files]
    hashes = defaultdict(str)
    for path in paths:
        hashes[path[0]] = path[1]

    return hashes

def get_HEAD_hashes(path:str)-> dict:
    """
    unlike get_HEAD_hash in GitUtil, this one output dictionary in form of
    {filname:hash}
    """
    hashes = defaultdict(str)
    with open(path,"r") as heads:
        heads = [head.strip() for head in heads]
        for head in heads:
            head = head.split("/")
            hashes[head[0]] = head[1]
    return hashes

def print_status(file:str, status:str)->str:
    """this should obvious enough"""
    print(f"{file} - {status}")

def build_status_message(*statuses)->str:
    """
    Quality of life function, use to join different message together
    """
    status = [status for status in statuses if status]
    return (", ").join(status)


def eval_status(dir_hashes:dict, index_hashes:dict ,head_hashes:dict)-> None:
    """
        complex status evaluation. basically get all file from 3 places, then check status of each file
        2 main things to consider on each file; version and existence.
        it use build_status_message to join each status together.
    """
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
        if existed["dir"] and not existed["index"] and not existed["head"]:         
            msg = build_status_message("untracked")    
    
        if not existed["dir"] and (existed["index"] or existed["head"]):            
            msg = build_status_message("file deleted")     
    
        if not existed['index'] and existed['head']:                                
            msg = build_status_message(msg,"deleted from index")
                
        if existed['index'] and not existed['head']:                                
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