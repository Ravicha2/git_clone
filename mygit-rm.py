#!/usr/bin/env python3
import sys
import argparse
import mygit_util
import os
import shutil

args = sys.argv[1:]

class MyArgumentParser(argparse.ArgumentParser):
    def error(self, _):
        print("usage: mygit-rm [--force] [--cached] <filenames>")
        sys.exit(1)

def parse_args():
    parser = MyArgumentParser()

    parser.add_argument('--force', action='store_true', help='Force removal')
    parser.add_argument('--cached', action='store_true', help='Remove only from index (cached)')
    parser.add_argument('filenames', nargs='+', help='Files to remove')

    args = parser.parse_args()
    option = []
    if args.cached:
        option.append('cached')
    if args.force:
        option.append('force')
    if not args.cached and not args.force:
        option = ['default']

    return option, args.filenames

def error_check(filename,option):
    state = mygit_util.DiffCheck.state_check(filename)
    dir_hash = mygit_util.DiffCheck.get_dir_hash(filename)
    index_hash = mygit_util.DiffCheck.get_index_hash(filename)
    #head_hash = mygit_util.DiffCheck.get_HEAD_hash(filename)
    if not index_hash:
        print(f"mygit-rm: error: '{filename}' is not in the mygit repository",file=sys.stderr)
        exit(1)
    if "force" not in option:
        if not state["i=h"] and index_hash:
            if "cached" not in option and state["d=i"]:
                print(f"mygit-rm: error: '{filename}' has staged changes in the index",file=sys.stderr)
                exit(1)
        if not state["d=i"] and state["i=h"] and dir_hash and index_hash and "cached" not in option:
            print(f"mygit-rm: error: '{filename}' in the repository is different to the working file",file=sys.stderr)
            exit(1)
        if not state["d=i"] and not state["i=h"] and dir_hash and index_hash:
            print(f"mygit-rm: error: '{filename}' in index is different to both the working file and the repository")
            exit(1)

def remove_from_index(filename):
    try:
        shutil.rmtree(f".mygit/index/{filename}")
    except:
        print(f"mygit-rm: error: '{filename}' is not in the mygit repository",file=sys.stderr)
        exit(1)


def remove_from_dir(filename):
    current = mygit_util.DiffCheck.get_dir_hash(filename)

    if current:
        os.remove(filename)


if __name__ == "__main__":
    option, files = parse_args()
    check = mygit_util.ErrorCheck()
    for file in files:
        check.rm_check(file)
    for file in files:
        error_check(file,option)
    for file in files:
        if "cached" not in option:
            remove_from_dir(file)
            remove_from_index(file)
        else:
            remove_from_index(file)