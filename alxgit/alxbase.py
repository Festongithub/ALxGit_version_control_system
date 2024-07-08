#!/usr/bin/python3

"""The mdoule has the higher logic of alxgit"""

from collections import deque, namedtuple
import itertools
import operator
import os
import string

from . import alxdata

def init():
    """initialize different aspects of repository"""
    alxdata.init()
    alxdata.update_ref('HEAD', alxdata.RefValue(symbolic=True, value='refs/heads/master'))


def write_tree(directory='.'):
    """Takes the current working directory and store it to the object database"""
    entries = []
    with os.scandir(directory) as alx:
        for entry in alx:
            full = f'{directory}/{entry.name}'
            if is_ignored(full):
                continue

            if entry.is_file(follow_symlinks=False):
                type_ = 'alxblob'
                with open(full, 'rb') as f:
                    #print(alxdata.hash_object(f.read()), full)
                    oid = alxdata.hash_object(f.read())
            elif entry.is_dir(follw_symlinks=False):
                #write_tree(full)
                type_ = 'tree'
                oid = write_tree(full)
            entries.append((entry.name, oid, type_))
        tree = ''.join(f'{type_} {oid} {name}\n'
                       for name, oid, type_
                       in sorted(entries))
        return alxdata.hash_object(tree.encode(), 'tree')


def iter_tree_entries(oid):
    """Takes an OID of a tree, tokenize it line-by-line and yield raw string values
    """
    if not oid:
        return
    tree = alxdata.get_object(oid, 'tree')
    for entry in tree.decode().splitlines():
        type_, oid, name = entry.split(' ', 2)
        yield type_, oid,  name

def get_tree(oid, alxbase_path=''):
    result = {}
    for type_, oid, name in iter_tree_entries(oid):
        assert '/' not in name
        assert name not in('..', '.')
        path = alxbase_path + name
        if type_ == 'alxblob':
            result[path] = oid
        elif type_ == 'tree':
            result.update(get_tree(oid, f'{path}/'))
        else:
            assert False, f'Unknown tree entry {type_}'
    return result

def get_working_tree():
    """compare working tree to a commit"""
    res = {}
    for root, _, filenames in os.walk('.'):
        for filename in filenames:
            path = os.path.relpath(f'{root}/{filename}')
            if is_ignored(path) or not os.path.isfile(path):
                continue
            with open(path, 'rb') as f:
                result[path] = alxdata.hash_object(f.read())
        return result


def empty_current_directory():
    """Delete all existing stuff before reading"""
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
            except(FileNotFoundError, OSError):
                pass

def read_tree(tree_oid):
    empty_current_directory()
    for path, oid in get_tree(tree_oid, alxbase_path='./').items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(alxdata.get_object(oid))

def commit(message):
    """write commit"""
    commit = f'tree {write_tree()}\n'

    HEAD = alxdata.get_ref('HEAD').value
    if HEAD:
        commit += f'parent {HEAD}\n'

    commit += '\n'
    commit += f'{message}\n'

    oid = alxdata.hash_object(commit.encode(), 'commit')
    
    alxdata.update_ref('HEAD', alxdata.RefValue(symbolic=False, value=oid))

    return oid

def checkout(name):
    """implement alxgit checkout"""
    oid = get_oid(name)
    commit = get_commit(oid)
    read_tree(commit.tree)

    if is_branch(name):
        HEAD = alxdata.RefValue(symbolic=True, value=f'refs/heads/{name}')
    else:
        HEAD = alxdata.RefValue(symbolic=False, value=oid)

    alxdata.update_ref('HEAD', HEAD, deref=False)

def merge(other):
    pass


def create_tag(name, oid):
    """creates tag"""
    alxdata.update_ref(f'refs/tags/{name}', alxdata.RefValue(symbolic=False, value=oid))

def iter_branch_names():
    """show all branches"""
    for refname, _ in alxdata.iter_ref('refs/heads/'):
        yield os.path.relpath(refname, 'refs/heads/')


def is_branch(branch):
    """check if it is branch"""
    return alxdata.get_ref(f'refs/heads/{branch}').value is not None

def reset(oid):
    """move HEAD to an OID of choice to undo the commit"""
    alxdata.update_ref('HEAD', alxdata.RefValue(symbolic=False, value=oid))


def create_branch(name, oid):
    """Create new branch"""
    alxdata.update_ref(f'refs/heads/{name}', alxdata.RefValue(symbolic=False, value=oid))

def get_branch_name():
    """Print current branch name"""
    HEAD = alxdata.get_ref('HEAD', deref=False)
    if not HEAD.symbolic:
        return None
    HEAD = HEAD.value
    assert HEAD.startswith('refs/heads/')
    return os.path.relpath(HEAD, 'refs/heads')

Commit = namedtuple('commit', ['tree', 'parent', 'message'])

def get_commit(oid):
    """gets the commit message"""
    parent = None

    commit = alxdata.get_object(oid, 'commit').decode()
    lines = iter(commit.splitlines())
    for line in itertools.takewhile(operator.truth, lines):
        key, value = line.split(' ', 1)
        if key == 'tree':
            tree = value
        elif key == 'parent':
            parent = value
        else:
            assert False, f'Unknown field {key}'

    message ='\n'.join(lines)
    return Commit(tree=tree, parent=parent, message=message)

def iter_commits_and_parents(oids):
    """Iterate commands"""
    oids = deque(oids)
    visited = set()

    while oids:
        oid = oids.popleft()
        if not oid or oid in visited:
            continue
        visited.add(oid)
        yield oid

        commit = get_commit(oid)
        oids.appendleft(commit.parent)

def get_oid(name):
    """resolves a name to an OID"""
    if name == '@': name == 'HEAD'
    #return alxdata.get_ref(name) or name
    refs_to_test = [
            f'{name}',
            f'refs/{name}',
            f'refs/tags/{name}',
            f'refs/heads/{name}',
            ]

    for ref in refs_to_test:
        if alxdata.get_ref(ref, deref=False).value:
            return alxdata.get_ref(ref).value
    #name is SHA1
    is_hex = all(c in string.hexdigits for c in name)
    if len(name) == 40 and is_hex:
        return name

    assert False,  f'Unknown name {name}'

def is_ignored(path):
    """ingnores .alxgit file"""
    return '.alxgit' in path.split('/')
