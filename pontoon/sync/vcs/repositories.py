# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
import logging
import os
import scandir
import subprocess

from django.conf import settings

from pontoon.base.models import Repository

log = logging.getLogger(__name__)


class PullFromRepositoryException(Exception):
    pass


class PullFromRepository(object):
    def __init__(self, source, target, branch):
        self.source = source
        self.target = target
        self.branch = branch

    def pull(self, source=None, target=None):
        raise NotImplementedError


class PullFromGit(PullFromRepository):
    def pull(self, source=None, target=None, branch=None):
        log.debug("Git: Update repository.")

        source = source or self.source
        target = target or self.target
        branch = branch or self.branch

        command = ["git", "fetch", "--all"]
        execute(command, target)

        # Undo local changes
        remote = "origin"
        if branch:
            remote += "/" + branch

        command = ["git", "reset", "--hard", remote]
        code, output, error = execute(command, target)

        if code != 0:
            log.info("Git: " + str(error))
            log.debug("Git: Clone instead.")
            command = ["git", "clone", source, target]
            code, output, error = execute(command)

            if code != 0:
                raise PullFromRepositoryException(str(error))

            log.debug("Git: Repository at " + source + " cloned.")
        else:
            log.debug("Git: Repository at " + source + " updated.")

        if branch:
            command = ["git", "checkout", branch]
            code, output, error = execute(command, target)

            if code != 0:
                raise PullFromRepositoryException(str(error))

            log.debug("Git: Branch " + branch + " checked out.")


class PullFromHg(PullFromRepository):
    def pull(self, source=None, target=None):
        log.debug("Mercurial: Update repository.")

        source = source or self.source
        target = target or self.target

        # Undo local changes: Mercurial doesn't offer anything more elegant
        command = ["rm", "-rf", target]
        code, output, error = execute(command)

        command = ["hg", "clone", source, target]
        code, output, error = execute(command)

        if code == 0:
            log.debug("Mercurial: Repository at " + source + " cloned.")

        else:
            raise PullFromRepositoryException(str(error))


class PullFromSvn(PullFromRepository):
    def pull(self, source=None, target=None):
        log.debug("Subversion: Checkout or update repository.")

        source = source or self.source
        target = target or self.target

        if os.path.exists(target):
            status = "updated"
            command = ["svn", "update", "--accept", "theirs-full", target]

        else:
            status = "checked out"
            command = [
                "svn",
                "checkout",
                "--trust-server-cert",
                "--non-interactive",
                source,
                target,
            ]

        code, output, error = execute(command, env=get_svn_env())

        if code != 0:
            raise PullFromRepositoryException(str(error))

        log.debug("Subversion: Repository at " + source + " %s." % status)


class CommitToRepositoryException(Exception):
    pass


class CommitToRepository(object):
    def __init__(self, path, message, user, branch, url):
        self.path = path
        self.message = message
        self.user = user
        self.url = url
        self.branch = branch

    def commit(self, path=None, message=None, user=None):
        raise NotImplementedError

    def nothing_to_commit(self):
        return log.warning("Nothing to commit")


class CommitToGit(CommitToRepository):
    def commit(self, path=None, message=None, user=None, branch=None):
        log.debug("Git: Commit to repository.")

        path = path or self.path
        message = message or self.message
        user = user or self.user
        branch = branch or self.branch
        author = user.display_name_and_email

        # Embed git identity info into commands
        git_cmd = [
            "git",
            "-c",
            f"user.name={settings.VCS_SYNC_NAME}",
            "-c",
            f"user.email={settings.VCS_SYNC_EMAIL}",
        ]

        # Add new and remove missing paths
        execute(git_cmd + ["add", "-A", "--", path], path)

        # Commit
        commit = git_cmd + ["commit", "-m", message, "--author", author]
        code, output, error = execute(commit, path)
        if code != 0 and len(error):
            raise CommitToRepositoryException(str(error))

        # Push
        push_target = "HEAD"
        if branch:
            push_target = branch

        push = ["git", "push", self.url, push_target]
        code, output, error = execute(push, path)
        if code != 0:
            raise CommitToRepositoryException(str(error))

        if "Everything up-to-date" in error:
            return self.nothing_to_commit()

        log.info(message)


class CommitToHg(CommitToRepository):
    def commit(self, path=None, message=None, user=None):
        log.debug("Mercurial: Commit to repository.")

        path = path or self.path
        message = message or self.message
        user = user or self.user
        author = user.display_name_and_email

        # Add new and remove missing paths
        add = ["hg", "addremove"]
        execute(add, path)

        # Commit
        commit = ["hg", "commit", "-m", message, "-u", author]
        code, output, error = execute(commit, path)
        if code != 0 and len(error):
            raise CommitToRepositoryException(str(error))

        # Push
        push = ["hg", "push"]
        code, output, error = execute(push, path)

        if code == 1 and "no changes found" in output:
            return self.nothing_to_commit()

        if code != 0 and len(error):
            raise CommitToRepositoryException(str(error))

        log.info(message)


class CommitToSvn(CommitToRepository):
    def commit(self, path=None, message=None, user=None):
        log.debug("Subversion: Commit to repository.")

        path = path or self.path
        message = message or self.message
        user = user or self.user
        author = user.display_name_and_email

        # Commit
        command = [
            "svn",
            "commit",
            "-m",
            message,
            "--with-revprop",
            "author=%s" % author,
            path,
        ]

        code, output, error = execute(command, env=get_svn_env())
        if code != 0:
            raise CommitToRepositoryException(error)

        if not output and not error:
            return self.nothing_to_commit()

        log.info(message)


def execute(command, cwd=None, env=None):
    try:
        st = subprocess.PIPE
        proc = subprocess.Popen(
            args=command, stdout=st, stderr=st, stdin=st, cwd=cwd, env=env
        )

        (output, error) = proc.communicate()

        # Make sure that we manipulate strings instead of bytes, to avoid
        # compatibility errors in Python 3.
        if type(output) is bytes:
            output = output.decode("utf-8")
        if type(error) is bytes:
            error = error.decode("utf-8")

        code = proc.returncode
        return code, output, error

    except OSError as error:
        if type(error) is bytes:
            error = error.decode("utf-8")
        return -1, "", error


def update_from_vcs(repo_type, url, path, branch):
    obj = globals()["PullFrom%s" % repo_type.capitalize()](url, path, branch)
    obj.pull()


def commit_to_vcs(repo_type, path, message, user, branch, url):
    try:
        obj = globals()["CommitTo%s" % repo_type.capitalize()](
            path, message, user, branch, url
        )
        return obj.commit()

    except CommitToRepositoryException as e:
        log.debug("%s Commit Error for %s: %s" % (repo_type.upper(), path, e))
        raise e


def get_svn_env():
    """Return an environment dict for running SVN in."""
    if settings.SVN_LD_LIBRARY_PATH:
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = (
            settings.SVN_LD_LIBRARY_PATH + ":" + env["LD_LIBRARY_PATH"]
        )
        return env
    else:
        return None


class VCSRepository(ABC):
    @classmethod
    def for_type(cls, repo_type, path):
        SubClass = cls.REPO_TYPES.get(repo_type)
        if SubClass is None:
            raise ValueError("No subclass found for repo type {0}.".format(repo_type))

        return SubClass(path)

    def __init__(self, path):
        self.path = path

    def execute(self, cmd, cwd=None, env=None, log_errors=True):
        cwd = cwd or self.path
        code, output, error = execute(cmd, cwd=cwd, env=env)
        if log_errors and code != 0:
            log.error(
                "Error while executing command `{cmd}` in `{cwd}`: {stderr}".format(
                    cmd=str(cmd), cwd=cwd, stderr=error
                )
            )
        return code, output, error

    @abstractmethod
    def get_changed_files(self, path, from_revision, statuses=None):
        """Get a list of changed files in the repository."""
        pass

    @abstractmethod
    def get_removed_files(self, path, from_revision):
        """Get a list of removed files in the repository."""
        pass

    @property
    @abstractmethod
    def revision(self):
        pass


class SvnRepository(VCSRepository):
    def execute(self, cmd, cwd=None, env=None, log_errors=False):
        return execute(cmd, cwd=cwd, env=get_svn_env())

    @property
    def revision(self):
        code, output, error = self.execute(["svnversion", self.path], log_errors=True)
        return output.strip() if code == 0 else None

    def get_changed_files(self, path, from_revision, statuses=None):
        statuses = statuses or ("A", "M")

        def normalize_revision(rev):
            """Remove all non digit characters from the revision number. """
            return "".join(filter(lambda c: c.isdigit(), rev))

        from_revision = normalize_revision(from_revision)
        code, output, error = self.execute(
            ["svn", "diff", "-r", "{}:{}".format(from_revision, "HEAD"), "--summarize"],
            cwd=path,
        )
        if code == 0:
            # Mark added/modfied files as the changed ones
            return [
                line.split()[1]
                for line in output.split("\n")
                if line and line[0] in statuses
            ]
        return []

    def get_removed_files(self, path, from_revision):
        return self.get_changed_files(path, from_revision, ("D",))


class GitRepository(VCSRepository):
    @property
    def revision(self):
        code, output, error = self.execute(["git", "rev-parse", "HEAD"],)
        return output.strip() if code == 0 else None

    def get_changed_files(self, path, from_revision, statuses=None):
        statuses = statuses or ("A", "M")
        code, output, error = self.execute(
            [
                "git",
                "diff",
                "--name-status",
                "{}..HEAD".format(from_revision),
                "--",
                path,
            ],
        )
        if code == 0:
            return [
                line.split()[1]
                for line in output.split("\n")
                if line and line[0] in statuses
            ]
        return []

    def get_removed_files(self, path, from_revision):
        return self.get_changed_files(path, from_revision, ("D",))


class HgRepository(VCSRepository):
    @property
    def revision(self):
        code, output, error = self.execute(
            ["hg", "identify", "--id", "--rev=default"], cwd=self.path, log_errors=True
        )
        return output.strip() if code == 0 else None

    def _strip(self, rev):
        "Ignore trailing + in revision number. It marks local changes."
        return rev.rstrip("+")

    def get_changed_files(self, path, from_revision, statuses=None):
        statuses = statuses or ("A", "M")
        code, output, error = self.execute(
            [
                "hg",
                "status",
                "-a",
                "-m",
                "-r",
                "--rev={}".format(self._strip(from_revision)),
                "--rev=default",
            ],
            cwd=path,
        )
        if code == 0:
            # Mark added / modified files as the changed ones
            return [
                line.split()[1]
                for line in output.split("\n")
                if line and line[0] in statuses
            ]
        return []

    def get_removed_files(self, path, from_revision):
        return self.get_changed_files(path, self._strip(from_revision), ("R",))


VCSRepository.REPO_TYPES = {
    Repository.Type.HG: HgRepository,
    Repository.Type.SVN: SvnRepository,
    Repository.Type.GIT: GitRepository,
}


def get_revision(repo_type, path):
    repo = VCSRepository.for_type(repo_type, path)
    return repo.revision


def get_changed_files(repo_type, path, revision):
    """Return a list of changed files for the repository."""
    repo = VCSRepository.for_type(repo_type, path)
    log.info("Retrieving changed files for: {}:{}".format(path, revision))
    # If there's no latest revision we should return all the files in the latest
    # version of repository
    if revision is None:
        paths = []
        for root, _, files in scandir.walk(path):
            for f in files:
                if root[0] == "." or "/." in root:
                    continue
                paths.append(os.path.join(root, f).replace(path + "/", ""))
        return paths, []

    return (
        repo.get_changed_files(path, revision),
        repo.get_removed_files(path, revision),
    )
