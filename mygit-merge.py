#!/usr/bin/env python3
import sys
import argparse
import mygit_util
from glob import glob
from pathlib import Path
import os
import shutil

args = sys.argv[1:]

class MyArgumentParser(argparse.ArgumentParser):
    def error(self, _):
        print("usage: mygit-merge <branch|commit> -m message")
        sys.exit(1)

def parse_args():
    parser = MyArgumentParser()
    
    parser.add_argument('target', help='target branch or commit')
    parser.add_argument('-m', dest='message', help='merge commit message')
    args = parser.parse_args()

    args = parser.parse_args()
    target = args.target
    msg = args.message
    if not msg:
        print("mygit-merge: error: empty commit message")
        exit(1)
    return target, msg

def get_all_files(*commits):
    """
    get files (ignore version) from commits,
    """
    all_files = set()
    for commit in commits:
        try:
            with open(f".mygit/commits/{commit}/snapshot.txt") as files:
                for file in files:
                    file = file.strip().split("/")[0]
                    all_files.add(file)
        except:
            print(f"mygit-merge: error: unknown commit '{commit}'")
            exit(1)
    return all_files

def compare_commit(files,current,target):
    """
    check if there are any merge conflicts. Merge conflicts identify by:
    if current version of file is not the same as target branch version
        if one of them is identical to branching point version (no change since branch created)
        then there's no conflict, else raise error
    """
    branching_point = mygit_util.GitUtil.common_ancestor(current,target)
    conflicted_file = []
    for file in files:
        original_hash = mygit_util.GitUtil.find_file(file,branching_point)
        current_hash = mygit_util.GitUtil.find_file(file,current)
        target_hash = mygit_util.GitUtil.find_file(file,target)
        conflict = False
        if current_hash != target_hash:
            if not current_hash or not target_hash:
                continue
            if (original_hash != current_hash) and (original_hash != target_hash):
                conflict = True
                conflicted_file.append(file)
    if conflict:
        print("mygit-merge: error: These files can not be merged:")
        print(("\n").join(conflicted_file))
        exit(1)
    

def merge_cases(branching_point,current_commit,target_commit):
    """
    determine if the merge operation is Fast-forward merge or true merge

    Fast forward merge identfy by
        0───1       (trunk)
            └────2  (b1)
    if merge b1 into trunk, it is fast forward merge, since it is the same as commit on trunk
        0───1───2
    and no new commit created

    for true merge
        0───1────3  (trunk)
            └────2  (b1)
    now we need to compare commit 2 and 3 to see if it create any conflict, if no conflict, create new commit
        0───1────3────4  
            └────2────└
    commit 4 is create from merge, this commit will have 2 parents(2,3)
    """
    branching_point = int(branching_point)
    current_commit = int(current_commit)
    target_commit = int(target_commit)

    if branching_point == current_commit:
        if target_commit > current_commit:
            print("Fast-forward: no commit created")
            FF_merge(branching_point, current_commit, target_commit)
            current_branch = Path(glob(".mygit/refs/branch/*")[0]).name
            with open(f".mygit/refs/heads/{current_branch}/latest_commit","w") as latest_commit:
                latest_commit.write(f"{target_commit}")

    elif branching_point == target_commit:
        if current_commit > target_commit:
            print("Already up to date")
            exit(0)
    else:
        #print("Branches Diverged — True Merge Required")
        true_merge(branching_point, current_commit, target_commit)

def merge_record(branching_point, current_commit, target_commit):
    """
    choose the version to apply when merge. To select the version
    compare the version on each branch with branching point version, select the version that is different from branching point
    """
    all_files = get_all_files(current_commit,target_commit)
    merging_file = dict()
    for file in all_files:
        original_hash = mygit_util.GitUtil.find_file(file,branching_point)
        current_hash = mygit_util.GitUtil.find_file(file,current_commit)
        target_hash = mygit_util.GitUtil.find_file(file,target_commit)
        if current_hash == target_hash:
            merging_file[file] = current_hash
        else:
            if original_hash == current_hash:
                merging_file[file] = target_hash

            elif original_hash == target_hash:
                merging_file[file] = current_hash

    return merging_file

def state_check(branching_point, current_commit, target_commit):
    """
        checking if there are any unstaged change or uncomitted file left since merge will overwrite index and current directory
    """
    merging_file = merge_record(branching_point, current_commit, target_commit)
    branching_point = int(branching_point)
    current_commit = int(current_commit)
    target_commit = int(target_commit)

    for file in glob("*"):
        if os.path.isdir(file):
            continue

        file_hash = mygit_util.DiffCheck.get_dir_hash(file)
        file = Path(file).name
        head = mygit_util.DiffCheck.get_HEAD_hash(file)
        state = mygit_util.DiffCheck.state_check(file)
        merge_version = merging_file.get(file)
        bp_hash = mygit_util.GitUtil.find_file(branching_point,file)
    
        if not state["i=h"] and head:
            print("mygit-merge: error: can not merge: local changes to files")
            exit(1)

        if not head and merge_version and file_hash != merge_version:
            print("mygit-merge: error: can not merge: local changes to files")
            exit(1)

        if file_hash != merge_version:
            if not merging_file.get(file):
                continue

            if branching_point == current_commit:
                if target_commit > current_commit:
                    continue # FF merge case

            if bp_hash == file_hash or bp_hash == merge_version:
                continue

            if not bp_hash:
                continue

            print("mygit-merge: error: can not merge")
            exit(1)


def update_index(new_files):
    """
    update index to reflect merge, include merge version of file and new file created on each branch
    """
    for file,hash_val in new_files.items():
        if (index_hash := mygit_util.DiffCheck.get_index_hash(file)) != hash_val:
            if index_hash:
                shutil.rmtree(f".mygit/index/{file}")
            os.mkdir(f".mygit/index/{file}")
            try:
                with open(f".mygit/objects/{hash_val}","r") as merge_file:
                    with open(f".mygit/index/{file}/{hash_val}","w") as new_index:
                        new_index.write(merge_file.read())
            except:
                continue
        
def update_head():
    """
    work like mygit-commit, just take data from index to head, but no new file created so no need to touch objects
    """
    new_head = []
    for file in glob(".mygit/index/*/*"):
        file = ("/").join(file.split("/")[-2:])
        new_head.append(f"{file}\n")
    with open(".mygit/HEAD","w") as head:
        head.writelines(new_head)

def update_dir():
    """
    apply merged version of each file to directory
    """
    for file in glob(".mygit/index/*/*"):
        file, hash_val = file.split("/")[-2:]
        with open(f".mygit/objects/{hash_val}","r") as stored_content:
            with open(file,"w") as dir_file:
                dir_file.write(stored_content.read())


def FF_merge(branching_point, current_commit, target_commit):
    """
    as mentioned to concept of Fast-forward merge, now the implementation as followed
    1. update index
    2. update head
    3. update directory
    update snapshot in commit to include new file (since no new commit created)
    """
    new_head = merge_record(branching_point,current_commit,target_commit)
    update_index(new_head)
    update_head()
    update_dir()
    # update snapshot commit
    with open(f".mygit/commits/{current_commit}/snapshot.txt","w") as snapshot:
        for file, hash_val in new_head.items():
            snapshot.writelines(f"{file}/{hash_val}")


def true_merge(branching_point, current_commit, target_commit):
    """
    1. update index
    2. update head
    3. update directory
    4. create new commit log
    5. update latest commit(pointer to parent)
    """
    new_head = merge_record(branching_point,current_commit,target_commit)
    update_index(new_head)
    update_head()
    update_dir()

    parent = [f"{current_commit}\n",f"{target_commit}\n"]
    previous_commit = len(glob(".mygit/commits/*"))
    mygit_util.GitUtil.commit_log(msg)

    with open(f".mygit/commits/{previous_commit}/parent","w") as parent_file:
        parent_file.writelines(parent)

    latest_commit = len(glob(".mygit/commits/*")) - 1
    current_branch = Path(glob(".mygit/refs/branch/*")[0]).name
    with open(f".mygit/refs/heads/{current_branch}/latest_commit","w") as new_commit:
        new_commit.write(f"{latest_commit}")

if __name__ == "__main__":
    target, msg = parse_args()
    current = mygit_util.GitUtil.current_node()
    if not target.isdigit():
        try:
            with open(f".mygit/refs/heads/{target}/latest_commit") as target_head:
                target = target_head.read()
        except:
            print(f"mygit-merge: error: unknown branch '{target}'")
            exit(1)
    all_files = get_all_files(current,target)
    branching_point = mygit_util.GitUtil.common_ancestor(current,target)
    compare_commit(all_files,current,target)
    state_check(branching_point,current,target)
    merge_cases(branching_point,current,target)
