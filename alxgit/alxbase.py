#!/usr/bin/python3
"""This module has the basic higher-level logic of alxgit .Used for object database implemented in alxdata.py to implement higher-level structures for storing directories"""

from . import alxdata
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


def is_ignored(path):
    return ".alxgit" in path.split('/')
