#!/usr/bin/python3
import alxlib
import argparse

class ALXRepository(object):
    """An ALX repository"""

    worktree = None
    gitdir = None
    conf = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path(path, ".alx")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception("Not an ALX repository %s" % path)


        self.conf = configparser.ConfigParser()
        cf = repo_self(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            version = int(self.conf.get("core", "repositoryformatversion"))
            if version != 0:
                raise Exception("Unsupported repositoryformatversion %s" % version)

    
    def repo_path(repo, *path):
        """Compute path under repo's gitdir"""
        return os.path.join(repo.gitdir, *path)

    def repo_file(repo, *path, mkdir=False):
        if repo_dir(repo, *path[:-1], mkdir=mkdir):
            return repo_path(repo, *path)

    def repo_dir(repo, *path, mkdir=False):
        path = repo_path(repo, *path)

        if os.path.exists(path):
            if(os.path.isdir(path)):
                return path
            else:
                raise Exception("Not a directory %s " % path)

        if mkdir:
            os.makedirs(path)
            return path
        else:
            return None
    
    def repo_create(path):
        """Create a new repository at path"""
        repo = ALXRepository(path, True)

        if os.path.exists(repo.worktree):
            if not os.path.isdir(repo.worktree):
                raise Exception("%s is not directory!" % path)
            if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
                raise Exception("%s is not empty")
            else:
                os.makedirs(repo.worktree)

            assert repo_dir(repo, "branches", mkdir=True)
            assert repo_dir(repo, "objects", mkdir=True)
            assert repo_dir(repo, "refs", mkdir=True)
            assert repo_dir(repo, "refs", "head", mkdir=True)

            with open(repo_file(repo, "description"), "w") as f:
                f.write("Unnamed respository; edit this file 'description'to name the repository.\n")

            #.alx/HEAD
            with open(repo_file(repo, "HEAD"), "w") as f:
                f.write("ref: ref/heads/master\n")

            with open(repo_file(repo, "config"), "w") as f:
                config = repo_default_config()
                config.write(f)
            return repo

        def repo_default_config():
            ret =  configparser.ConfigParser()

            ret.add_section("core")
            ret.set("core", "repositoryformatversion", "0")
            ret.set("core", "filemode", "false")
            ret.set("core", "bare", "false")

            return ret 
        def cmd_init(args):
                    repo_create(args.path) 

argsp = argsubparsers.add_parser("init", help="Initialize a new repository")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to create the repository.")       