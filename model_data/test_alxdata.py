#!/usr/bin/python3

"""For testing purpposes"""

import unittest
import tempfile
import os
import shutil
import hashlib
import json
import alxdata

from alxdata import change_alxgit_dir, init, update_ref, get_ref,delete_ref, hash_object,get_object,object_exists, RefValue


class TestAlxgit(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        with change_alxgit_dir(self.test_dir):
            init()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_init(self):
        with change_alxgit_dir(self.test_dir):
            init()
            self.assertTrue(os.path.isdir(f'{self.test_dir}/.alxgit'))
            self.assertTrue(os.path.isdir(f'{self.test_dir}/.alxgit/objects'))

    def test_update_and_get_ref(self):
        ref = 'HEAD'
        value = RefValue(symbolic=False, value='1234567890abcdef')
        with change_alxgit_dir(self.test_dir):
            update_ref(ref, value)
            self.assertEqual(get_ref(ref), value)

    def test_delete_ref(self):
        ref = 'HEAD'
        value = RefValue(symbolic=False, value='1234567890abcdef')
        with change_alxgit_dir(self.test_dir):
            update_ref(ref, value)
            delete_ref(ref)
            self.assertIsNone(get_ref(ref).value)

    def test_hash_object(self):
        alxdata = b'test content'
        with change_alxgit_dir(self.test_dir):
            oid = hash_object(alxdata)
            expected_oid = hashlib.sha1(b'blob\x00' + alxdata).hexdigest()
            self.assertEqual(oid, expected_oid)
            self.assertTrue(object_exists(oid))

    def test_get_object(self):
        alxdata = b'test content'
        with change_alxgit_dir(self.test_dir):
            oid = hash_object(alxdata)
            content = get_object(oid)
            self.assertEqual(content,alxdata)

    def test_object_exists(self):
        alxdata = b'test content'
        with change_alxgit_dir(self.test_dir):
            oid = hash_object(alxdata)
            self.assertTrue(object_exists(oid))
            self.assertFalse(object_exists('nonexistent'))

if __name__ == '__main__':
    unittest.main()

