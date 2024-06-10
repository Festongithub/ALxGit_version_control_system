#!/usr/bin/python3

class AlxRepository(object):
    """An Alx Repository"""

    worktree = None
    gitdir = None
    conf = None

    def __init__(self, path, force= False):
        """
        Initializes the repository
        path: defines the file paths
        Force: disabales all the checks
        """
        self.worktree = path
        self.gitdir = os.path.join(path, ".alx")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception("Not an Alx repository %s" % path)


        self.conf = configparser.Configparser()
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
        """Manipulation of the path and computation path under repo's getdir"""
        return os.path.join(repo.getdir, *path)

