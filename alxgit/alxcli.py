#!/usr/bin/python3

"""Implements the alxcli command"""

import argparse
import os
import subprocess
import sys
import textwrap

from . import alxbase
from model_data import alxdata
from diff import alxdiff
from . import remote_model


def main():
    """Run arguments on command line"""
    with alxdata.change_alxgit_dir('.'):
        args = parse_args()
        args.func(args)


def parse_args():
    """Parse the arguments"""
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(dest='command')
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

    write_tree_parser = commands.add_parser('write-tree')
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser('read-tree')
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument('tree', type=oid)

    commit_parser = commands.add_parser('commit')
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument('-m', '--message', required=True)

    log_parser = commands.add_parser('log')
    log_parser.set_defaults(func=log)
    log_parser.add_argument('oid', default='@', type=oid, nargs='?')
    show_parser = commands.add_parser('show')
    show_parser.set_defaults(func=show)
    show_parser.add_argument('oid', default='@', type=oid, nargs='?')

    diff_parser = commands.add_parser('diff')
    diff_parser.set_defaults(func=diff)
    diff_parser.add_argument('--cached', action='store_true')
    diff_parser.add_argument('commit', nargs='?')

    checkout_parser = commands.add_parser('checkout')
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument('commit')

    tag_parser = commands.add_parser('tag')
    tag_parser.set_defaults(func=tag)
    tag_parser.add_argument('name')
    tag_parser.add_argument('oid', default='@',
                            type=oid, nargs='?')

    branch_parser = commands.add_parser('branch')
    branch_parser.set_defaults(func=branch)
    branch_parser.add_argument('name', nargs='?')
    branch_parser.add_argument('start_point', default='@',
                               type=oid, nargs='?')

    k_parser = commands.add_parser('k')
    k_parser.set_defaults(func=k)

    status_parser = commands.add_parser('status')
    status_parser.set_defaults(func=status)

    reset_parser = commands.add_parser('reset')
    reset_parser.set_defaults(func=reset)
    reset_parser.add_argument('commit', type=oid)

    merge_parser = commands.add_parser('merge')
    merge_parser.set_defaults(func=merge)
    merge_parser.add_argument('commit', type=oid)

    merge_base_parser = commands.add_parser('merge-base')
    merge_base_parser.set_defaults(func=merge_base)
    merge_base_parser.add_argument('commit1', type=oid)
    merge_base_parser.add_argument('commit2', type=oid)

    fetch_parser = commands.add_parser('fetch')
    fetch_parser.set_defaults(func=fetch)
    fetch_parser.add_argument('remote')

    push_parser = commands.add_parser('push')
    push_parser.set_defaults(func=push)
    push_parser.add_argument('push')

    add_parser = commands.add_parser('add')
    checkout_parser.set_defaults(func=add)
    checkout_parser.add_argument('file', nargs='+')
    return parser.parse_args()


def init(args):
    alxbase.init()
    print(f'Initialized empty alxgit repository in
          {os.getcwd()}/{alxdata.GIT_DIR}')


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


def print_commit(oid, commit, refs=None):
    """print commit message"""
    refs_str = f'({", ".join(refs)})' if refs else ''
    print(f'commit {oid}{refs_str}\n')
    print(textwrap.indent(commit.message, '   '))
    print(' ')


def log(args):
    """walks the list of commit and print them"""
    refs = {}
    for refname, ref in alxdata.iter_refs():
        refs.setdefault(ref.value, []).append(refname)

    for oid in alxbase.iter_commits_and_parents({args.oid}):
        commit = alxbase.get_commit(oid)
        print_commit(oid, commit, refs.get(oid))

        # refs_str = f '({", ".join(refs[oid])})' if oid in refs else ''
        # print(f'commit {oid}{refs_str}\n')
        # print(textwrap.indent(commit.message, '   '))
        # print('')


def show(args):
    """show commit messages"""
    if not args.oid:
        return
    commit = alxbase.get_commit(args.oid)
    parent_tree = None
    if commit.parents:
        parent_tree = alxbase.get_commit(commit.parents[0]).tree

    print_commit(args.oid, commit)
    result = alxdiff.diff_trees(
            alxbase.get_tree(parent_tree), alxbase.get_tree(commit.tree))
    # print(result)
    sys.stdout.flush()
    sys.stdout.buffer.write(result)


def diff(args):
    """comapare working tree to a commit"""
    oid = args.commit and alxbase.get_commit(args.commit)

    if args.commit:
        tree_from = alxbase.get_tree(oid and alxbase.get_commit(oid).tree)
    if args.cached:
        tree_to = alxbase.getindex_tree()
        if not args.commit:
            oid = alxbase.get_oid('@')
            tree_from = alxbase.get_tree(oid and alxbase.get_commit(oid).tree)
        else:
            tree_to = alxbase.ge_working_tree()
            if not args.commit:
                tree_from = alxbase.get_index_tree()

    result = alxdiff.diff_tree(tree_from, tree_to)
    sys.stdout.flush()
    sys.stdout.buffer.write(result)


def checkout(args):
    """implement alxgit chekout"""
    alxbase.checkout(args.commit)


def tag(args):
    """implement create tag function"""
    oid = args.oid or alxdata.get_ref('HEAD')
    alxbase.create_tag(args.name, args.oid)


def branch(args):
    """Alxgit branch"""
    # alxbase.create_branch(args.name, args.start_point)
    if not args.name:
        current = alxbase.get_branch_name()
        for branch in alxbase.iter_branch_names():
            prefix = '*' if branch == current else ' '
            print(f'{prefix} {branch}')
        else:
            alxbase.create_branch(args.name, args.start_point)
            print(f'Branch {args.name} created at {args.start_point[:10]}')


def k(args):
    """Visualisation tool for the commit"""
    dot = 'digraph commits {\n'

    oids = set()
    for refname, ref in alxdata.iter_refs(deref=False):
        dot += f'"{refname}" [shape=note]\n'
        dot += f' "{refname}" -> "{ref.value}"\n'
        if not ref.symbolic:
            oids.add(ref.value)

    for oid in alxbase.iter_commits_and_parents(oids):
        commit = alxbase.get_commit(oid)
        dot += f' "{oid}" [shape=box style=filled label="{oid[:10]}"]\n'
        for parent in commit.parents:
            dot += f' "{oid}" -> "{parent}"\n'

    dot += '}'
    print(dot)

    with subprocess.Popen(
            ['dot', '-Tgtk', '/dev/stdin'],
            stdin=subprocess.PIPE) as proc:
        proc.communicate(dot.encode())


def status(args):
    """alxgit status"""
    HEAD = alxbase.get_oid('@')
    branch = alxbase.get_branch_name()
    if branch:
        print(f'On branch {branch}')
    else:
        print(f'HEAD detached at {HEAD[:10]}')
    MERGE_HEAD = alxdata.get-ref('MERGE_HEAD').value
    if MERGE_HEAD:
        print(f'Merging with {MERGE_HEAD[:10]}')

    print('\nChanges to be committed:\n')
    HEAD_tree = HEAD and alxbase.get_commit(HEAD).tree
    for path, action in alxdiff.iter_changed_files(
            alxbase.get_tree(HEAD_tree), alxbase.get_working_tree()):
        print(f'{action:>12}: {path}')

    print('\nChanges not staged for commit:\n')
    for path, action in alxdiff.iter_changed_files(alxbase.get_index_tree(),
                                                   alxbase.get_working_tree()):
        print(f'{action:>12}: {path}')


def reset(args):
    """Move HEAD"""
    alxbase.reset(args.commit)


def merge(args):
    """alxgit merge function"""
    alxbase.merge(args.commit)


def merge_base(args):
    """receives two commits OIDs and find their common ancestor"""
    print(alxbase.get_merge_base(args.commit1, args.commit2))


def fetch(args):
    """print remote refs"""
    remote_model.fetch(args.remote_model)


def push(args):
    """push commit"""
    remote_model.push(args.remote, f'refs/heads/{args.branch}')


def add(args):
    """add files to the repository"""
    alxbase.add(args.files)
