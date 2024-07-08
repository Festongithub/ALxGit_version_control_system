#!/usr/bin/python3

"""This module manages data in alxgit"""
import hashlib
import os
from collections import namedtuple

GIT_DIR = '.alxgit'

def init():
    os.makedirs(GIT_DIR)
    os.makedirs(f'{GIT_DIR}/objects')

RefValue = namedtuple('RefValue', ['symbolic', 'value'])

def update_ref(ref, value, deref=True):
    """sets the HEAD"""
    #assert not value.symbolic
    ref = get_ref_internale(ref, deref)[0]

    assert value.value
    if value.symbolic:
        value = f'ref: {value.value}'
    else:
        value = value.value

    ref_path = f'{GIT_DIR}/{ref}'
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, 'w') as f:
        f.write(value)

def get_ref(ref, deref=True):
    """gets head of commit message"""
    return get_ref_internal(ref, deref)[1]

def get_ref_internal(ref, deref):
    """dereference refs for reading and writing"""
    ref_path = f'{GIT_DIR}/{ref}'
    value = None
    if os.path.isfile(ref_path):
        with open(ref_path) as f:
            value = f.read().strip()
    symbolic = bool(value) and value.startswith('ref:')
    if symbolic:
        value = value.split(':', 1)[1].strip()
        if deref:
            return get_ref_internal(value, deref=True)
    return ref, RefValue(symbolic=symbolic, value=value)

def iter_refs(prefix='', deref=True):
    """visualisation for mess"""
    refs = ['HEAD']
    for root, _, filenames in os.walk(f'{GIT_DIR}/refs/'):
        root = os.path.relpath(root, GIT_DIR)
        refs.extend(f'{root}/{name}' for name in filenames)

    for refname in refs:
        if not refname.startswith(prefix):
            continue
        yield refname, get_ref(refname, deref=deref)


def hash_object(data, type_='alxblob'):
    """hashing file"""
    obj = type_.encode() + b'\x00' + data
    oid = hashlib.sha1(obj).hexdigest()
    with open(f'{GIT_DIR}/objects/{oid}', 'wb') as out:
        out.write(obj)
    return oid


def get_object(oid, expected='alxblob'):
    """returns oid of hashed objects"""
    with open(f'{GIT_DIR}/objects/{oid}', 'rb') as f:
        obj =  f.read()

    type_, _, content = obj.partition(b'\x00')
    type_ = type_.decode()

    if expected is not None:
        assert type_ == expected, f'Expected {expected}, got{type_}'
    return content
