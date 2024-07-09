#!/usr/bin/python3
import subprocess

from collections import defaultdict
from tempfile import NamedTemporaryFile as Temp

from . import alxdata


"""List changed files in commit"""
from collections import defaultdict

def compare_trees(*tree):
    """compute differences between objects"""
    entries = defaultdict(lambda: [None] * len (trees))
    for i, tree in enumerate(trees):
        for path, oid in tree.items():
            entries[path][i] = oid
    for path, oids in entries.items():
        yield(path, *oids)


def iter_changed_files(t_from, t_to):
    for path, o_from, o_to in compare_trees(t_from, t_to):
        if o_from != o_to:
            action = ('new file' if not o_from else
                      'deleted' if not o_to else
                      'modified')
            yield path, action


def diff_trees(t_from, t_to):
    """file path"""
    output = b''
    for path, origin, destination in compare_trees(t_from, t_to):
        if origin != destination:
            output += diff_blobs(origin, destination)
        return output

def diff_blobs(origin, destination, path='alxblob'):
    """print diff of commit"""
    with Temp() as f_from, Temp() as f_to:
        for oid, f in ((origin, f_from), (destination, f_to)):
            if oid:
                f.write(alxdata.get_object(oid))
                f.flush()
        with subprocess.Popen(
                ['alxdiff', '--unified', '--show-c-function',
                 '--label', f'a/{path}', f_from.name,
                 '--label', f'b/{path}', f_to.name],
                stdout=subprocess.PIPE) as proc:
            output, _ = proc.communicate()

        return output

def merge_trees(t_base, t_HEAD, t_other):
    tree = {}
    for path, o_base,o_HEAD, o_other in compare_trees(t_base, t_HEAD, t_other):
        tree[path] = alxdata.hash_object(merge_blobs, (o_base,o_HEAD, o_other))
    return tree


def merge_blobs(o_HEAD, o_other):
    with Temp() as f_base, Temp() as f_HEAD,  Temp() as f_other:
        for oid, f in ((o_base, f_base), (o_HEAD, f_HEAD), (o_other, f_other)):
            if oid:
                f.write (alxdata.get_object(oid))
                f.flush()

        with subprocess.Popen(
                ['alxdiff3', '-m',
                 '-L','HEAD', f_HEAD.name,
                 '-L', 'BASE', f_base.name,
                 '-L', 'MERGE_HEAD',f_other.name
                 ], stdout=subprocess.PIPE) as proc:
                    output, _ = proc.communicate()
                    assert proc.returncode in (0,1)
                    return output
