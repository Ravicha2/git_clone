#!/usr/bin/env python3

from glob import glob
import mygit_util

node = mygit_util.GitUtil.current_node()
branch = glob(".mygit/refs/branch/*")[0].split("/")[-1]

print(f"you are on branch '{branch}' commit {node}")