#!/usr/bin/env python3
import os
import re
import hashlib
import shutil
from glob import glob

class ErrorCheck():

    @staticmethod
    def mygit_check(operation):
        if not os.path.isdir(".mygit"):
            print(f"{operation}: error: mygit repository directory .mygit not found")
            return False
        return True
    
    @staticmethod
    def valid_name(file,operation):
        if not re.search(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*",file):
            print(f"{operation}: error: invalid filename '{file}'")
            return False
        return True
    
    @staticmethod
    def valid_path(file,operation):
        if not os.path.isfile(file):
            print(f"{operation}: error: can not open '{file}'")
            return False
        return True
    
    @staticmethod
    def valid_commit(commit,operation):
        if not os.path.isdir(f".mygit/commits/{commit}"):
            print(f"{operation}: error: unknown commit '{commit}'")
            return False
        return True

    def init_check(self):
            if not os.path.isdir(".mygit"):
                 os.path.isdir(".mygit")
            else:
                print("mygit-init: error: .mygit already exists")
                exit(1)

    def add_check(self,files):
        if not ErrorCheck.mygit_check("mygit-add"):
            exit(1)
        
        for file in files:
            if not ErrorCheck.valid_name(file,"mygit-add"):
                exit(1)
            
            if not ErrorCheck.valid_path(file,"mygit-add"):
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




class DiffCheck:
    @staticmethod
    def hashContent(file):
        with open(file,"r") as f:
            content = f.read()
        return hashlib.sha1(content.encode()).hexdigest()
    

    @staticmethod
    def isExisted(file):
        hash_val = DiffCheck.hashContent(file)
        dir = f".mygit/objects/{file}"

        if not os.path.isdir(dir):
            return False
        
        for existing in os.listdir(dir):
            if existing == hash_val:
                return True
        
        return False
        
    
class GitUtil:
    @staticmethod
    def git_add(files):
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
     
                 