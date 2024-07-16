#!/usr/bin/python3

"""Performs the alxgit fetch """
import os
from model_data  import alxdata
from . import alxbase

REMOTE_REFS_BASE = 'refs/heads/'
LOCAL_REFS_BASE  = 'refs/remote/'

def fetch(remote_path):
    """print remote refs"""
    refs = get_remote_refs(remote_path, REMOTE_REFS_BASE)

    for oid in alxbase.iter_objects_in_commits(refs.values()):
        alxdata.fetch_object_if_missing(oid, remote_path)

    for remote_name, value in refs.items():
        refname = os.path.relpath(remote_name, REMOTE_REFS_BASE)
        alxdata.update_ref(f'{LOCAL_REFS_BASE}/{refname}',
                           alxdata.RefValue(symbolic=False, value=value))

def push(remote_path, refname):
    """Get refs data"""
    remote_refs = get_remote_refs(remote_path)
    remote_ref = remote_refs.get(refname)
    loc_ref = alxdata.get_ref(refname).value
    assert loc_ref

    assert not remote_ref or alxbase.is_ancestor_of(loc_ref, remote_ref)

    known_rem_refs = filter(alxdata.object_exists, remote_refs.values())
    remote_obj = set(alxbase.iter_objects_in_commits(known_rem_refs))
    loc_obj = set(alxbase.iter_objeccts_in_commits({local_ref}))


    obj_to_push = loc_obj - remote_obj
    # push missing objects
    for oid in obj_to_push:
        alxdata.push_object(oid, remote_path)

    with alxdata.change_git_dir(remote_path):
        alxdata.update_ref(refname,
                           alxdata.RefValue(symbolic=False, value=loc_ref))

def get_remote_refs(remote_path, prefix=''):
    with alxdata.change_alxgit_dir(remote_path):
        return {refname: ref.value for refname, ref in alxdata.iter_refs(prefix)}
