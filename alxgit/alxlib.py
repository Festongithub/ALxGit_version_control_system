#!/usr/bin/env python3
import argparse
from . import alxbase
from . import alxdata
import os
import sys
import textwrap


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

    read_tree_parser = commands.add_parser('read-tree')
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument('tree')

    commit_parser = commands.add_parser('commit')
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument('-m', '--message', required=True)

    log_parser = commands.add_parser('log')
    log_parser.set_defaults(func=log)
    log_parser.add_argument('oid', nargs='?')

    checkout_parser = commands.add_parser('checkout')
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument('oid')

    tag_parser = commands.add_parser('tag')
    tag_parser.set_defaults(func=tag)
    tag_parser.add_argument('name')
    tag_parser.add_argument('oid', nargs='?')
    

    
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
    alxbase.write_tree()
    print(base.write_tree())

def read_tree(args):
    alxbase.read_tree(args.tree)

def commit(args):
    """Create commit message"""
    print(alxbase.commit(args.message))


def log(args):
    """list the log in alxgit"""
    #oid = alxdata.get_HEAD()
    oid = args.oid or alxdata.get_ref('HEAD')
    while oid:
        commit = alxbase.get_commit(oid)

        print(f'commit {oid}\n')
        print(textwrap.indent(commit.message, '  '))
        print('')

        oid = commit.parent

def checkout(args):
    """Check commit messages"""
    alxbase.checkout(args.oid)

def tag(args):
    oid = args.oid or alxdata.get_ref('HEAD')
    alxbase.create_tag(args.name, oid)
