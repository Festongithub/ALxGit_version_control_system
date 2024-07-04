#!/usr/bin/python3

"""Implements the alxcli command"""

import argparse
import os
import sys
import textwrap


from . import alxbase
from . import alxdata

def main():
    args = parse_args()
    args.func(args)

def parse_args():
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(dest = 'command')
    commands.required = True

    oid = alxbase.get_oid

    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func=init)

    hash_object_parser = commands.add_parser('hash-object')
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument('file')

    cat_file_parser = commands.add_parser('cat-file')
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument('object', type=oid)
    
    write_tree_parser = commands.add_parser('write-file')
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser('read-tree')
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument('tree', type=oid)

    commit_parser = commands.add_parser('commit')
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument('-m', '--message', required=True)

    log_parser = commands.add_parser('log')
    log_parser.set_defaults(func=log)
    log_parser.add_argument('oid', type=oid,  nargs='?')

    checkout_parser = commands.add_parser('checkout')
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument('oid', type=oid)

    tag_parser = commands.add_parser('tag')
    tag_parser.set_defaults(func=tag)
    tag_parser.add_argument('name')
    tag_parser.add_argument('oid', type=oid,  nargs='?')
    


    return parser.parse_args()

def init(args):
    #print('Hello world!')
    alxdata.init()
    print(f'Initialized empty alxgit repository in {os.getcwd()}/{alxdata.GIT_DIR}')

def hash_object(args):
    with open(args.file, 'rb') as f:
        print(alxdata.hash_object(f.read()))

def cat_file(args):
    """Print hashed objects"""
    sys.stdout.flush()
    sys.stdout.buffer.write(alxdata.get_object(args.object, expected=None))


def write_tree(args):
    """Stores the current working directory"""
    print(alxbase.write_tree())

def read_tree(args):
    """list and read tree"""
    alxbase.read_tree(args.tree)

def commit(args):
    """write commit"""
    print(alxbase.commit(args.message))

def log(args):
    """walks the list of commit and print them"""
    oid = args.oid or alxdata.get_ref('HEAD')
    while oid:
        commit = alxbase.get_commit(oid)

        print(f'commit{oid}\n')
        print(textwrap.indent(commit.message, ' '))
        print('')

        oid = commit.parent
def checkout(args):
    """implement alxgit chekout"""
    alxbase.checkout(args.oid)


def tag(args):
    """implement create tag function"""
    oid = args.oid or alxdata.get_ref('HEAD')
    alxbase.create_tag(args.name, oid)
