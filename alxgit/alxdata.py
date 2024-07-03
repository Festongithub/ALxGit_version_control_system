#!/usr/bin/python3
import hashlib
import os

GIT_DIR = '.alxgit'

def init():
    os.makedirs (GIT_DIR)
    os.makedirs (f'{GIT_DIR}/objects')

#def set_HEAD(oid):
    #"""sets the head"""
    #with open(f'{GIT_DIR}/HEAD', 'w') as f:
        #f.write(oid)

def update_ref(ref, oid):
    ref_path = f'{GIT_DIR}/{ref}'
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, 'w') as f:
        f.write(oid)

def get_ref(ref):
    """Gets the head of commit"""
    ref_path = f'{GIT_DIR}/{ref}'
    if os.path.isfile(ref_path):
        with open(ref_path) as f:
            return f.read().strip()


def hash_object(alxdata, type_='blob'):
    obj = type_.encode() + b'\x00' + alxdata
    oid = hashlib.sha1 (alxdata).hexdigest()
    with open(f'{GIT_DIR}/objects/{oid}', 'wb') as out:
        out.write(alxdata)
        out.write(obj)

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
