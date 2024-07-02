#!/usr/bin/env python3
import argparse
import os
import sys
from . import alxbase
from . import alxdata

def main():
    """Test for the alxgit command"""
    args = parse_args()
    args.func(args)

def parse_args():
    """Parse the args"""
    parser = argparse.ArgumentParser ()

    commands = parser.add_subparsers(dest='command')
    commands.required = True

    init_parser = commands.add_parser('init')
    init_parser.set_defaults (func=init)

    hash_object_parser = commands.add_parser('hash-object')
    hash_object_parser.set_defaults (func=hash_object)
    hash_object_parser.add_argument('file')

    cat_file_parser = commands.add_parser('cat-file')
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument('object')

    write_tree_parser = commands.add_parser('write-tree')
    write_tree_parser.set_defaults(func=write_tree)

    
    return parser.parse_args ()

def init(args):
    """initialize repository"""
    alxdata.init()
    print(f'Initialized empty alxgit repository in {os.getcwd()}/{alxdata.GIT_DIR}')


def hash_object(args):
    """Hash and encode the file"""
    with open(args.file, 'rb') as f:
        print(alxdata.hash_object(f.read()))


def cat_file(args):
    """check file contents"""
    sys.stdout.flush()
    sys.stdout.buffer.write(alxdata.get_object(args.object, expected=None))


def write_tree(args):
    """Create the working directory"""
    base.write_tree()
    print(base.write_tree())

