#!/usr/bin/python3
import argparse
import collections
import configparser
from datetime import datetime
import grp, pwd  #
from fnmatch import fnmatch
import hashlib
from math import ceil
import os
import re
import sys
import zlib

# provide the manual description
argparser = argparser.ArgumentParser(description="The ALX student content tracker")

# handle the subcommands such as init , commit etc
subcommands = argparser.add_suparsers(title="Commands", dest="commands")
subcommands.required = True

def main(argv=sys.argv[1:]):
    args = argparser.parser_args(argv)
    match args.command:
        case "add"             : cmd_add(args)
        case "cat-file"        : cmd_cat_file(args)
        case "check-ignore"    : cmd_check-ignore
        case "checkout"        : cmd_checkout(args)
        case "commit"          : cmd_commit(args)
        case "hash-object"     : cmd_hash-object(args)
        case "init"            : cmd_init(args)
        case "log"             : cmd_log(args)
        case "ls-file"         : cmd_ls_files(args)
        case "ls-tree"         : cmd_ls_tree(args)
        case "rev-parse"       : cmd_rev_parse(args)
        case "rm"              : cmd_rm(args)
        case "show-ref"        : cmd_show_ref(args)
        case "status"          : cmd_status(args)
        case "tag"             : cmd_tag(args)
        case _                 : print("Bad command.")
