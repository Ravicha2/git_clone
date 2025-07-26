#!/usr/bin/env python3
import os
import re
import hashlib
from glob import glob

class ErrorCheck():
    #def __init__(self):
    #    mygit = pathlib.Path(".mygit")
    
    def init_check(self):
            if not os.path.isdir(".mygit"):
                 os.path.isdir(".mygit")
            else:
                print("mygit-init: error: .mygit already exists")
                exit(1)

    def add_check(self,files):
        for file in files:

            if not re.search(r"^[a-zA-Z0-9][a-zA-Z0-9._-]",file):
                print(f"mygit-add: error: invalid filename '{file}'")
                exit(1)
            
            if not os.path.isfile(file):
                 print(f"mygit-add: error: can not open '{file}'")
                 exit(1)
    
    def commit_check(self,files):
        pass 



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
        
    
    
     
     
                 