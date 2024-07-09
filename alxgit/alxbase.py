#!/usr/bin/python3

"""The mdoule has the higher logic of alxgit"""

from collections import deque, namedtuple
import itertools
import operator
import os
import string

from . import alxdata
from . import alxdiff


def init():
    """initialize different aspects of repository"""
    alxdata.init()
    alxdata.update_ref('HEAD', alxdata.RefValue(symbolic=True, value='refs/heads/master'))


def write_tree(directory='.'):
    """Takes the current working directory and store it to the object database"""
    tree_as_index = {}
    with alxdata.get_index() as index:
        for path, oid in index.items():
            path = path.split('/')
            dirpath, filename = path[:-1], path[-1]

            current = tree_as_index
            for dirname in dirpath:
                current = current.setdefault(dirname, {})
            current[filename] = oid
        def write_tree_recursive(tree_dict):
            entries = []
            for name, value in tree_dict:
                type_ = 'tree'
                oid = write_tree_recursive(value)
            else:
                type_ = 'alxblob'
                oid = value
            entries.append((name, oid, tyep))
        
        tree = ''.join(f'{type_} {oid} {name}\n'
                       for name, oid, type_ in sorted(entries))
        return alxdata.hash_object(tree.encode(), 'tree')
    return write_tree_recursive(tree_as_index)

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
    """get tree name"""
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

def get_index_tree():
    with alxdata.ge_index() as index:
        return index


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

def read_tree(tree_oid, update_working=False):
    with alxdata.get_index() as index:
        index.clear()
        index.update(get_tree(tree_oid))

        if update_working:
            checkout_index(index)

def read_tree_merged(t_base, t_HEAD, t_other, update_working=False):
    """Merge in working directory"""
    with alxdata.get_index() as index:
        index.clear()
        index.update(diff.merge_trees(
            get_tree(t_base),
            get_tree(t_HEAD),
            get_tree(t_other)
            ))
        if update_working:
            checkout_index(index)

def checkout_index(index):
    empty_current_directory()
    for path, oid in index.items():
        os.makedirs(os.path.dirname(f'./{path}'), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(alxdata.get_object(oid, 'alxblob'))

def commit(message):
    """write commit"""
    commit = f'tree {write_tree()}\n'

    HEAD = alxdata.get_ref('HEAD').value
    if HEAD:
        commit += f'parent {HEAD}\n'

    MERGE_HEAD = alxdata.get_ref('MERGE_HEAD').value
    if MERGE_HEAD:
        commit += f'parent {MERGE_HEAD}\n'
        alxdata.delete_ref('MERGE_HEAD', deref=False)

    commit += '\n'
    commit += f'{message}\n'

    oid = alxdata.hash_object(commit.encode(), 'commit')
    
    alxdata.update_ref('HEAD', alxdata.RefValue(symbolic=False, value=oid))

    return oid

def checkout(name):
    """implement alxgit checkout"""
    oid = get_oid(name)
    commit = get_commit(oid)
    read_tree(commit.tree, update_working=True)

    if is_branch(name):
        HEAD = alxdata.RefValue(symbolic=True, value=f'refs/heads/{name}')
    else:
        HEAD = alxdata.RefValue(symbolic=False, value=oid)

    alxdata.update_ref('HEAD', HEAD, deref=False)

def merge(other):
    """merge head into other"""
    HEAD = alxdata.get_ref('HEAD').value
    assert HEAD
    merge_base = get_merge_base(other, HEAD)
    #c_base = get_commit(merge_base)
    #c_HEAD = get_commit(HEAD)
    c_other = get_commit(other)

    if merge_base == HEAD:
        read_tree(c_other.tree, update_working=True)
        alxdata.update_ref('HEAD', alxdata.RefValue(symbolic=False, value=other))
        print('Fast-forward merge, no need to commit')
        return

    alxdata.update_ref('MERGE_HEAD', alxdata.RefValue(symbolic=False, value=other))

    c_base = get_commit(merge_base)
    c_HEAD = get_commit(HEAD)
    read_tree_merged(c_base.tree, c_HEAD.tree, c_other.tree, update_working=True)
    print('Merged in working tree\nPlease commit')

def get_merge_base(oid1, oid2):
    """Compute common ancestor of a commit"""
    parents1 = set(iter_commits_and_parents ({oid1}))

    for oid in iter_commits_and_parents({oid2}):
        if oid in parents1:
            return oid
def is_ancestor(commit, maybe_ancestor):
    """check ancestry of push"""
    return maybe_ancestor in iter_commits_and_parents({commit})

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

Commit = namedtuple('Commit', ['tree', 'parents', 'message'])

def get_commit(oid):
    """gets the commit message"""
    parents = []

    commit = alxdata.get_object(oid, 'commit').decode()
    lines = iter(commit.splitlines())
    for line in itertools.takewhile(operator.truth, lines):
        key, value = line.split(' ', 1)
        if key == 'tree':
            tree = value
        elif key == 'parent':
            parents.append(value)
        else:
            assert False, f'Unknown field {key}'

    message ='\n'.join(lines)
    return Commit(tree=tree, parents=parents, message=message)

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
        oids.extendleft(commit.parents)
        oid.extend(commit.parents[1:])

def iter_objects_in_commits(oids):
    """Takes a list of commit OIDs"""
    visited = set()
    def iter_objects_in_tree(oid):
        visited.add(oid)
        yield oid
        for type_, oid, _ in iter_tree_entries(oid):
            if oid not in visited:
                if type_ == 'tree':
                    yield from iter_objects_in_tree(oid)
                else:
                    visited.add(oid)
                    yield oid
    for oid in iter_commits_and_parents(oids):
        yield oid
        commit = get_commit(oid)
        if commit.tree not in visited:
            yield from iter_objects_in_tree(commit.tree)

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
def add(filenames):
    def add_file(filename):
        filename = os.path.relpath(filename)
        with open(filename, 'rb') as f:
            oid = alxdata.hash_object(f.read())
        index[filename] = oid
    def add_directory(dirname):
        for root, _, filenames in os.walk(dirname):
            path = os.path.relpath(f'{root}/{filename}')
            if is_ignored(path) or not os.path.isfile(path):
                continue
            add_file(path)
    with alxdata.get_index() as index:
        for name in filenames:
            if os.path.isfile(name):
                add_file(name)
            elif os.path.isdir(name):
                add_directory(name)

def is_ignored(path):
    """ingnores .alxgit file"""
    return '.alxgit' in path.split('/')
