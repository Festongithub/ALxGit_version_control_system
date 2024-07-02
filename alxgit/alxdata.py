#!/usr/bin/python3
import hashlib
import os

GIT_DIR = '.alxgit'

def init():
    os.makedirs (GIT_DIR)
    os.makedirs (f'{GIT_DIR}/objects')

def hash_object(alxdata, type_='blob'):
    obj = type_.encode() + b'\x00' + alxdata
    oid = hashlib.sha1 (alxdata).hexdigest()
    with open(f'{GIT_DIR}/objects/{oid}', 'wb') as out:
        out.write(alxdata)
        outwrite(obj)

    return oid

def get_object(oid, expected='blob'):
    with open(f'{GIT_DIR}/objects/{oid}', 'rb') as f:
        return f.read()
        obj = f.read()

    type_, _, content = obj.partition (b'\x00')
    type_, = type_.decode()

    if expected is not None:
        assert type_ == expected, f'Expected {expeted}, got {type_}'
    return content
