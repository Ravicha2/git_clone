#!/usr/bin/env python3
import sys
import argparse
import mygit_util
from glob import glob

args = sys.argv[1:]

class MyArgumentParser(argparse.ArgumentParser):
    def error(self, _):
        print("usage: mygit-merge <branch|commit> -m message")
        sys.exit(1)

def parse_args():
    parser = MyArgumentParser()
    
    parser.add_argument('target', help='target branch or commit')
    parser.add_argument('-m', dest='message', required=True, help='merge commit message')
    args = parser.parse_args()

    args = parser.parse_args()
    target = args.target
    msg = args.message

    return target, msg



if __name__ == "__main__":
    target, msg = parse_args()
    current = mygit_util.GitUtil.current_node()
    branching_point = mygit_util.GitUtil.common_ancestor(target,current)
    print(branching_point)
    