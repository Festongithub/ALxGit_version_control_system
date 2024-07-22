#!/usr/bin/env/python3

"""The  module setsup the alxgit command line tool"""

from setuptools import setup
# alxgit setup 

setup(name='alxgit',
      version='1.0',
      packages=['alxgit'],
      entry_points={
          'console_scripts': [
              'alxgit = alxgit.alxcli:main'
              ]
          })
