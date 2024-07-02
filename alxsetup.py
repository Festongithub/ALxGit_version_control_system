#!/usr/bin/env python3

from setuptools import setup

setup (name='alxgit',
       version='1.0',
       packages=['alxgit'],
       entry_points = {
           'console_scripts': [
               'alxgit = alxgit.alxlib:main']
           })
