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
