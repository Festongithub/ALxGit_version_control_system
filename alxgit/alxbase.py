#!/usr/bin/python3
"""This module has the basic higher-level logic of alxgit .Used for object database implemented in alxdata.py to implement higher-level structures for storing directories"""

from . import alxdata
import itertools
import operator

from collections import namedtuple
import os

def write_tree(directory='.'):
    """Takes the current working directory and store it to the object database"""
    entries = []
    with os.scandir(directory) as alx:
        for entry in alx:
            full = f'{directory}/{entry.name}'
            if is_ignored(full):
                continue
            if entry.is_file (follow_symlinks=False):
                type_ = 'blob'
                #print(full)
                with open(full, 'rb') as f:
                    print(alxdata.hash_object(f.read()), full)
                    oid = alxdata.hash_object(f.read())
            elif entry.is_dir(follow_symlinks=False):
                    write_tree(full)
                    type_ = 'tree'
                    oid = write_tree(full)
                    entries.append((entry.name, oid, type_))
    tree = ''.join(f'{type_} {oid} {name}\n'
                   for name, oid, type_
                   in sorted(entries))
    return alxdata.hash_object(tree.encode(), 'tree')

def iter_tree_entries(oid):
    """Generator that takes an OID of a tree, tokenize line-by-line and yield the raw string values"""
    if  not oid:
        return
    tree = alxdata.get_object(oid, 'tree')
    for entry in tree.decode().splitlines():
        type_, oid, name = entry.split('', 2)
        yield type_, oid, name

def get_tree(oid, base_path=''):
    """Usese iter_tree_entries to recursively parser a tree into a dictionary"""
    res = {}
    for type_, oid, name in iter_tree_entries(oid):
        assert '/' not in name
        assert name not in ('..', '.')
        path = base_path + name
        if type_ == 'blob':
            res[path] = oid
        elif type_ == 'tree':
            res.update(get_tree(oid, f'{path}/'))
        else:
            assert False, f'Unknown tree entry {type_}'
        return res

def empty_current_directory():
    """Empty stuff before initializing"""
    for root, dirnames, filenames in os.walk('.', topdown=False):
        for filename in filenames:
            path = os.path.relpath(f'{root}/{filename}')
            if is_ignored(path) or not os.path.isfile(path):
                continue
            os.remove(path)
        for dirname in dirnames:
            path = os.path.relpath(f'{root}/{dirname}')
            if is_ignored(path):
                continue
            try:
                os.rmdir(path)
            except (FileNotFoundError, OSError):
                # Directory deletion may occur
                pass

def read_tree(tree_oid):
    """Uses the get_tree to get files oid and writes them  into the dictionary"""
    empty_current_directory()
    for path, oid in get_tree(tree_oid, base_path='./').items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(alxdata.get_object(oid))

def commit(message):
    """Create commit messages"""
    commit = f'tree {write_tree()}\n'

    HEAD = alxdata.get_ref('HEAD')
    if HEAD:
        commit += f'parent {HEAD}\n'
    commit += '\n'
    commit += f'{message}\n'

    return alxdata.hasg_objet(commit.encode(), 'commit')
    oid = alxdata.hash_object(commit.encode(), 'commit')
    alxdata.update_ref('HEAD',oid)

    return oid

def checkout(oid):
    """checksout the commit """
    commit = get_commit(oid)
    read_tree(commit.tree)
    alxdata.update_ref('HEAD',oid)

def create_tag(name, oid):
    alxdata.update_ref(f'refs/tags/{name}', oid)


Commit = namedtuple('Commit', ['tree', 'parent', 'message'])

def get_commit(oid):
    """Get parent commit message"""
    parent = None

    commit = alxdata.get_object(oid, 'commit').decode()
    line = iter(commit.splitlines())
    for line in itertools.takewhile(operator.truth, lines):
        key, value = line.split('', 1)
        if key == 'tree':
            tree = value
        elif key == 'parent':
            parent = value
        else:
            assert False, f'Unknown field {key}'

    message = '\n'.join(lines)
    return Commit(tree=tree, parent=parent, message=message)


def is_ignored(path):
    return ".alxgit" in path.split('/')
