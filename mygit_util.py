#!/usr/bin/env python3
import os
import re
import hashlib
import sys
import shutil
from glob import glob

class ErrorCheck():

    @staticmethod
    def mygit_check(operation):
        if not os.path.isdir(".mygit"):
            print(f"{operation}: error: mygit repository directory .mygit not found",file=sys.stderr)
            return False
        return True
    
    @staticmethod
    def valid_name(file,operation):
        if not re.search(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*",file):
            print(f"{operation}: error: invalid filename '{file}'",file=sys.stderr)
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
    def get_HEAD_hash(filename:str) -> str:
        with open(".mygit/HEAD","r") as heads:
            lines = heads.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith(filename):
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