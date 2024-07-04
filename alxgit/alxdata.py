#!/usr/bin/python3

"""This module manages data in alxgit"""
import hashlib
import os

GIT_DIR = '.alxgit'

def init():
    os.makedirs(GIT_DIR)
    os.makedirs(f'{GIT_DIR}/objects')

def hash_object(data, type_='alxblob'):
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
