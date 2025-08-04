#!/usr/bin/env python3
import os
import re
import hashlib
import sys
import shutil
from glob import glob
from pathlib import Path

class ErrorCheck():
    """
    ErrorCheck is a class contains serveral function related to error handling. mostly used to filter out bad input. 
    the main function is mygit_check, valid_name, valid_path and valid_commit.
    the rest is the combination of meantioned functions with some modification to correctly handle input.
    """

    @staticmethod
    def mygit_check(operation:str) -> bool:
        """check if .mygit directory already existed. """
        if not os.path.isdir(".mygit"):
            print(f"{operation}: error: mygit repository directory .mygit not found",file=sys.stderr)
            return False

        return True
    
    @staticmethod
    def valid_name(file:str, operation:str) -> bool:
        """check if the name is valid according to the spec. """
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", file):
            if operation == "mygit-branch":
                print(f"{operation}: error: invalid branch name '{file}'", file=sys.stderr)
            else:
                print(f"{operation}: error: invalid filename '{file}'", file=sys.stderr)
            return False

        return True
    
    @staticmethod
    def valid_path(file:str,operation:str)-> bool:
        """check if path is existed. """
        if not os.path.isfile(file):
            print(f"{operation}: error: can not open '{file}'",file=sys.stderr)
            return False

        return True
    
    @staticmethod
    def valid_commit(commit:str,operation:str)-> bool:
        """check if the commit existed. """
        if not os.path.isdir(f".mygit/commits/{commit}"):
            print(f"{operation}: error: unknown commit '{commit}'",file=sys.stderr)
            return False

        return True

    def init_check(self)-> None:
        """inverse of mygit check"""
        if not os.path.isdir(".mygit"):
                os.path.isdir(".mygit")
        else:
            print("mygit-init: error: .mygit already exists",file=sys.stderr)
            exit(1)

    def add_check(self,files:str) -> None:
        """
        before proceed 'add' operation, check if filename is valid and existed either deleted but tracked or present in directory
        """

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

    def commit_check(self) -> None:
        """
        not much to check here, since if nothing index or no new update, it response with nothing to commit, not an error
        """
        if not ErrorCheck.mygit_check("mygit-commit"):
            exit(1)

    def log_check(self) -> None:
        """
        same as commit_check, print nothing if nothing to log
        """
        if not ErrorCheck.mygit_check("mygit-log"):
            exit(1)

    def show_check(self,commit_num:str,filename:str) -> None:
        """
        check if name is ok and commit existed
        """
        if not ErrorCheck.mygit_check("mygit-show"):
            exit(1)
        if not ErrorCheck.valid_commit(commit_num,"mygit-show"):
            exit(1)
        if not ErrorCheck.valid_name(filename,"mygit-show"):
            exit(1)

    def rm_check(self,filename:str) -> None:
        """
        check if filename is ok, remove non-existed will be handle later
        """
        if not ErrorCheck.mygit_check("mygit-rm"):
            exit(1)
        if not ErrorCheck.valid_name(filename,"mygit-rm"):
            exit(1)
        
    
    def status_check(self) -> None:
        if not ErrorCheck.mygit_check("mygit-rm"):
            exit(1)

    def branch_check(self,branch_name:str) -> None:
        """
            check if branch existed. if not given, just blindly passed
        """
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
    """
        class Diffcheck will contain function relate to version comparison
    """
    @staticmethod
    def hashContent(file:str) -> str:
        """
            input: path to file
            output: hash generate from file content, None if not found
        """
        try:
            with open(file,"r") as f:
                content = f.read()
            return hashlib.sha1(content.encode()).hexdigest()
        except:
            return None
    
    @staticmethod
    def get_dir_hash(filename:str) -> str:
        """
            input: file name
            output: hashed content of the file inside the current directory, none if not found
        """
        if os.path.isfile(filename):
            hash = DiffCheck.hashContent(filename)
            return hash

        return None
    
    @staticmethod
    def get_index_hash(filename:str) -> str:
        """
            input: file name
            output: hashed content of the file inside index, none if not found
        """
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
        """
            input: file name, specific head
            output: hashed content of the file inside that head, none if not found
        """
        with open(head,"r") as heads:
            lines = heads.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith(f"{filename}/"):
                return line.split("/")[-1]
        
        return None
    
    @staticmethod
    def state_check(filename:str)->dict:
        """
            input: file name
            output: summary of the versions of a file comparing to index and current head

            d for directoty
            i for index
            h for head

        """
        dir_hash = DiffCheck.get_dir_hash(filename)
        index_hash = DiffCheck.get_index_hash(filename)
        head_hash = DiffCheck.get_HEAD_hash(filename)

        state = {"d=i": dir_hash == index_hash,
                 "d=h": dir_hash == head_hash,
                 "i=h": index_hash == head_hash,
                 }
        return state
    
class GitUtil:
    """
        GitUtil contain function more complex function relate to git operation
    """
    @staticmethod
    def git_add(files:str) -> None:
        """
            - actual git add operation
            - add file to index
        """

        if not os.path.isdir(".mygit/index"):
            os.mkdir(".mygit/index")

        for file in files:

            hashedName = DiffCheck.hashContent(file)

            if hashedName:
                if not os.path.isdir(f".mygit/index/{file}"):
                    os.mkdir(f".mygit/index/{file}")
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
                    #print(glob(".mygit/index/*"))
                    shutil.rmtree(f".mygit/index/{file}")
                except:
                    print(f"mygit-add: error: can not open '{file}'",file=sys.stderr)

    @staticmethod
    def save_HEAD() -> None:
        """
            when running checkout, it is needed to save the current state of HEAD to refs/ before move to other branches
        """
        with open(".mygit/HEAD","r") as head:
            current_file = head.read()
        current_head = Path(glob(".mygit/refs/branch/*")[0]).name

        with open(f".mygit/refs/heads/{current_head}/HEAD","w") as write_target:
            write_target.write(current_file)

    @staticmethod
    def current_node() -> str:
        """
            Quality of life function: just output current commit
            As I see git as a tree graph and commit as a node, therefore commit = node
        """

        current_branch = Path(glob(".mygit/refs/branch/*")[0]).name

        with open(f".mygit/refs/heads/{current_branch}/latest_commit","r") as current_head:
            node = current_head.read()

        return node


    @staticmethod
    def ancestors(commit:int,ancestor_list:set)-> set:
        """
            recursively record the predecessor of the commit with -1 being initial uncommited state before commit 0
            output a set of ancestors
        """
        try:
            with open(f".mygit/commits/{commit}/parent") as commit:
                parent_commits = commit.readlines()
        except:
            print(f"mygit-merge: error: unknown commit '{commit}'")
            exit(1)
        
        for parent in parent_commits:
            parent = parent.strip()
            ancestor_list.add(parent)

            if int(parent) >= 0:
                ancestor_list = GitUtil.ancestors(parent,ancestor_list)
            else:
                return ancestor_list
            
        return ancestor_list
    
    @staticmethod
    def common_ancestor(target:str, current:str)-> int:
        """
        output commit
        get list of ancestor of current commit and target commit, then find intersection
        the highest intersected commit is where branch is created
        """

        target_ancestor_lists = set(target)
        current_ancestor_lists = set(current)

        target_ancestor_lists = GitUtil.ancestors(target, target_ancestor_lists)
        current_ancestor_lists = GitUtil.ancestors(current, current_ancestor_lists)

        return max(current_ancestor_lists.intersection(target_ancestor_lists))
    
    @staticmethod
    def find_file(filename:str,commit_num:str)-> str:
        """
            find the hash of a file in specified commit
            return nothing if not existed
        """

        found = False

        snapshot = glob(f".mygit/commits/{commit_num}/snapshot.txt")
        if snapshot:
            with open(snapshot[0],'r') as file_pointers:
                pointers = file_pointers.readlines()

                for pointer in pointers:
                    pointed_file,hash_val = pointer.split("/")

                    if f"{pointed_file}" == f"{filename}":
                        found = True
                        break

        if found:
            return hash_val.strip()

        return 
    
    @staticmethod
    def cat_file(file:str,commit:str)-> str:
        """
        work like 'cat' command, show content of a file of a specified commit
        """

        hash_val = GitUtil.find_file(file,commit)

        if hash_val:
            with open(f".mygit/objects/{hash_val}") as file:
                content = file.read()
                return content.strip()
    
    @staticmethod
    def extract_files(readline:list)-> dict:
        """
        nothing fancy, not even sure if it is used more than once but it get element got from readlines()
        and extract them into dictionary with 
        {filename : hash}
        """

        files = dict()
        for r in readline:
            name, hashval = r.strip().split("/")
            files[name] = hashval

        return files
    
    @staticmethod
    def copy_to(hash_val:str,target_path:str)->None:
        """
        basically write file content(specified by hash) to target path
        """

        with open(f".mygit/objects/{hash_val}","r") as obj_file:
            with open(target_path,"w") as location:
                location.write(obj_file.read())

    @staticmethod
    def commit_log(commit_msg:str)-> None:
        """
        All things recorded inside commits directory generate from this one
        it create {commit_num} directory with commit message, snapshot, parent commit
        inside snapshot.txt are recorded version of files in form of

        file_name/hash_value
        """

        commit_num = len(glob(".mygit/commits/*"))
        print(f"Committed as commit {commit_num}")
        os.mkdir(f".mygit/commits/{commit_num}")

        files = [("/").join(file.split("/")[2:]) for file in glob(".mygit/index/*/*")]

        with open(f".mygit/commits/{commit_num}/COMMIT_MSG","w") as msg:
            msg.writelines(commit_msg)

        with open(f".mygit/commits/{commit_num}/snapshot.txt","w") as snapshot:
            for file in files:     
                snapshot.writelines(file+"\n")
        
        current_branch = Path(glob(".mygit/refs/branch/*")[0]).name
        with open(f".mygit/refs/heads/{current_branch}/latest_commit",'r') as previous_commit:
            parent_commit = previous_commit.read()
            
        with open(f".mygit/commits/{commit_num}/parent","w") as parent:
            parent.writelines(parent_commit)

        with open(f".mygit/refs/heads/{current_branch}/latest_commit","w") as latest_commit:
            latest_commit.write(f"{commit_num}")