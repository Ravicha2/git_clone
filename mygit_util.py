#!/usr/bin/env python3
import os
import re
import hashlib
import sys
import shutil
from glob import glob
from pathlib import Path

class ErrorCheck():

    @staticmethod
    def mygit_check(operation):
        if not os.path.isdir(".mygit"):
            print(f"{operation}: error: mygit repository directory .mygit not found",file=sys.stderr)
            return False
        return True
    
    @staticmethod
    def valid_name(file, operation):
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", file):
            if operation == "mygit-branch":
                print(f"{operation}: error: invalid branch name '{file}'", file=sys.stderr)
            else:
                print(f"{operation}: error: invalid filename '{file}'", file=sys.stderr)
            return False
        return True
    
    @staticmethod
    def valid_path(file,operation):
        if not os.path.isfile(file):
            print(f"{operation}: error: can not open '{file}'",file=sys.stderr)
            return False
        return True
    
    @staticmethod
    def valid_commit(commit,operation):
        if not os.path.isdir(f".mygit/commits/{commit}"):
            print(f"{operation}: error: unknown commit '{commit}'",file=sys.stderr)
            return False
        return True

    def init_check(self):
            if not os.path.isdir(".mygit"):
                 os.path.isdir(".mygit")
            else:
                print("mygit-init: error: .mygit already exists",file=sys.stderr)
                exit(1)

    def add_check(self,files):
        if not ErrorCheck.mygit_check("mygit-add"):
            exit(1)
            
        with open(".mygit/HEAD",'r') as heads:
            head_lines = heads.readlines()
        head_lines = [head.strip().split("/")[-2] for head in head_lines]
                
        for file in files:
            if not ErrorCheck.valid_name(file,"mygit-add"):
                exit(1)
            if not os.path.isfile(file):
                if file not in head_lines:
                    print(f"mygit-add: error: can not open '{file}'",file=sys.stderr)
                    exit(1)

    def commit_check(self):
        if not ErrorCheck.mygit_check("mygit-commit"):
            exit(1)

    def log_check(self):
        if not ErrorCheck.mygit_check("mygit-log"):
            exit(1)

    def show_check(self,commit_num,filename):
        if not ErrorCheck.mygit_check("mygit-show"):
            exit(1)
        if not ErrorCheck.valid_commit(commit_num,"mygit-show"):
            exit(1)
        if not ErrorCheck.valid_name(filename,"mygit-show"):
            exit(1)

    def rm_check(self,filename):
        if not ErrorCheck.mygit_check("mygit-rm"):
            exit(1)
        if not ErrorCheck.valid_name(filename,"mygit-rm"):
            exit(1)
        
    
    def status_check(self):
        if not ErrorCheck.mygit_check("mygit-rm"):
            exit(1)

    def branch_check(self,branch_name):
        if not ErrorCheck.mygit_check("mygit-branch"):
            exit(1)
        if not branch_name:
            return
        if branch_name.isdigit():
            print(f"mygit-branch: error: invalid branch name '{branch_name}'", file=sys.stderr)
            exit(1)
        if not ErrorCheck.valid_name(branch_name,"mygit-branch"):
            exit(1)
    
    def checkout_check(self):
        if not ErrorCheck.mygit_check("mygit-checkout"):
            exit(1)
        

class DiffCheck:
    @staticmethod
    def hashContent(file):
        try:
            with open(file,"r") as f:
                content = f.read()
            return hashlib.sha1(content.encode()).hexdigest()
        except:
            return None
    
    @staticmethod
    def get_dir_hash(filename:str) -> str:
        if os.path.isfile(filename):
            hash = DiffCheck.hashContent(filename)
            return hash
        return None
    
    @staticmethod
    def get_index_hash(filename:str) -> str:
        try:
            path = glob(f".mygit/index/{filename}/*")[0]
        except:
            return None
        if path:
            hash = path.split("/")[-1]
            return hash
        return None
    
    @staticmethod
    def get_HEAD_hash(filename:str,head=".mygit/HEAD") -> str:
        with open(head,"r") as heads:
            lines = heads.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith(f"{filename}/"):
                return line.split("/")[-1]
        
        return None
    
    @staticmethod
    def state_check(filename):
        dir_hash = DiffCheck.get_dir_hash(filename)
        index_hash = DiffCheck.get_index_hash(filename)
        head_hash = DiffCheck.get_HEAD_hash(filename)
        state = {"d=i": dir_hash == index_hash,
                 "d=h": dir_hash == head_hash,
                 "i=h": index_hash == head_hash,
                 }
        return state
    
class GitUtil:
    @staticmethod
    def git_add(files):
        if not os.path.isdir(".mygit/index"):
            os.mkdir(".mygit/index")

        for file in files:
            if not os.path.isdir(f".mygit/index/{file}"):
                os.mkdir(f".mygit/index/{file}")

            hashedName = DiffCheck.hashContent(file)
            

            if hashedName:
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
            else:
                try:
                    shutil.rmtree(f".mygit/index/{file}")
                except:
                    print(f"mygit-add: error: can not open '{file}'",file=sys.stderr)

    @staticmethod
    def save_HEAD():
        with open(".mygit/HEAD","r") as head:
            current_file = head.read()
        current_head = Path(glob(".mygit/refs/branch/*")[0]).name

        with open(f".mygit/refs/heads/{current_head}/HEAD","w") as write_target:
            write_target.write(current_file)

    @staticmethod
    def current_node():
        current_branch = Path(glob(".mygit/refs/branch/*")[0]).name
        with open(f".mygit/refs/heads/{current_branch}/latest_commit","r") as current_head:
            node = current_head.read()
        return node


    @staticmethod
    def ancestors(commit:int,ancestor_list:set)-> set:
        try:
            with open(f".mygit/commits/{commit}/parent") as commit:
                parent_commit = commit.read()
        except:
            print(f"mygit-merge: error: unknown commit '{commit}'")
            exit(1)
        ancestor_list.add(parent_commit)

        if int(parent_commit) >= 0:
            ancestor_list = GitUtil.ancestors(parent_commit,ancestor_list)
            return ancestor_list
        else:
            return ancestor_list
    
    @staticmethod
    def common_ancestor(target, current)-> int:
        target_ancestor_lists = set(target)
        current_ancestor_lists = set(current)

        target_ancestor_lists = GitUtil.ancestors(target, target_ancestor_lists)
        current_ancestor_lists = GitUtil.ancestors(current, current_ancestor_lists)
        #print(target_ancestor_lists,current_ancestor_lists)
        return max(current_ancestor_lists.intersection(target_ancestor_lists))
    
    @staticmethod
    def find_file(filename,commit_num):
        found = False
        snapshot = glob(f".mygit/commits/{commit_num}/snapshot.txt")
        if snapshot:
            with open(snapshot[0],'r') as file_pointers:
                pointers = file_pointers.readlines()
                for pointer in pointers:
                    pointed_file,hash_val = pointer.split("/")
                    #print(pointed_file,filename)
                    if f"{pointed_file}" == f"{filename}":
                        found = True
                        break

        if found:
            return hash_val.strip()

        return None
    
    @staticmethod
    def cat_file(file,commit):
        hash_val = GitUtil.find_file(file,commit)
        if hash_val:
            with open(f".mygit/objects/{hash_val}") as file:
                content = file.read()
                return content.strip()