#!/usr/bin/python3

""" This module create the repo for the alx"""
import argparse
from argparse import ArgumentParser

class ALXRepository(object):
    """class repository"""

    worktree = None
    gitdir = None
    conf = None

    def __init__(self, path, force=False):
        """Initializes the gitdir"""
        self.worktree = path
        self.gitdir = os.path.join(path, ".alx")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception("Not an Alx repository %s" % path)

        # check configuration file in .alx/config
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")


        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            version = int(self.conf.get("core", "repositoryformatversion"))
            if version != 0:
                raise Exception("Unsupported repositoryformatversion %s" % version)


    def repo_path(repo, *path):
        """Path under repos gitdir"""
        return os.path.join(repo.gitdir, *path)


    def repo_file(repo, *path, mkdir=False):
        """create dirname(*path) if absent"""

        if repo_dir(repo, *path[:-1], mkdir=mkdir):
            return repo_path(path, *path)

    def repo_dir(repo, *path, mkdir=False):
        """create dir *path if absent if mkdir"""
        path = repo_path(repo, *path)

        if os.path.exists(path):
            if (os.path.isdir(path)):
                return path
            else:
                raise Exception("Not a directory %s" % path)

            if mkdir:
                os.mkdirs(path)
                return path
            else:
                return None

    def repo_create(path):
        """Create a new repository at path."""

        repo = ALXRepository(path, True)

        # First, we make sure the path either doesn't exist or is an
        # empty dir.

        if os.path.exists(repo.worktree):
            if not os.path.isdir(repo.worktree):
                raise Exception ("%s is not a directory!" % path)
            if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
                raise Exception("%s is not empty!" % path)
        else:
            os.makedirs(repo.worktree)
            
            assert repo_dir(repo, "branches", mkdir=True)
            assert repo_dir(repo, "objects", mkdir=True)
            assert repo_dir(repo, "refs", "tags", mkdir=True)
            assert repo_dir(repo, "refs", "heads", mkdir=True)

            # .alx/description
            with open(repo_file(repo, "description"), "w") as f:
                f.write("Unnamed repository; edit this file 'description' to name the repository.\n")
            with open(repo_file(repo, "HEAD"), "w") as f:
                f.write("ref: refs/heads/master\n")
                    
            with open(repo_file(repo, "config"), "w") as f:
                config = repo_default_config()
                config.write(f)

            return repo

    def repo_default_config():
        """Repository configuration"""

        ret = configparser.ConfigParser()

        ret.add_section("core")
        ret.set("core", "repositoryformatversion", "0")
        ret.set("core", "filemode", "false")
        ret.set("core", "bare", "false")

        return ret


argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository")

def cmd_init(args):
    repo_create(args.path)


