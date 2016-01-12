# -*- coding: utf8 -*-
from __future__ import absolute_import
import logging
import os
import subprocess

from django.conf import settings


log = logging.getLogger('pontoon')


class PullFromRepositoryException(Exception):
    pass


class PullFromRepository(object):

    def __init__(self, source, target):
        self.source = source
        self.target = target

    def pull(self, source=None, target=None):
        raise NotImplementedError


class PullFromGit(PullFromRepository):

    def pull(self, source=None, target=None):
        log.debug("Git: Update repository.")

        source = source or self.source
        target = target or self.target

        command = ["git", "fetch", "--all"]
        execute(command, target)

        # Undo local changes
        command = ["git", "reset", "--hard", "origin/master"]
        code, output, error = execute(command, target)

        if code == 0:
            log.debug("Git: Repository at " + source + " updated.")

        else:
            log.debug("Git: " + unicode(error))
            log.debug("Git: Clone instead.")
            command = ["git", "clone", "--depth", "1", source, target]
            code, output, error = execute(command)

            if code == 0:
                log.debug("Git: Repository at " + source + " cloned.")

            else:
                raise PullFromRepositoryException(unicode(error))


class PullFromHg(PullFromRepository):

    def pull(self, source=None, target=None):
        log.debug("Mercurial: Update repository.")

        source = source or self.source
        target = target or self.target

        # Undo local changes
        command = ["hg", "revert", "--all", "--no-backup"]
        execute(command, target)

        command = ["hg", "pull", "-u"]
        code, output, error = execute(command, target)

        if code == 0:
            log.debug("Mercurial: Repository at " + source + " updated.")

        else:
            log.debug("Mercurial: " + unicode(error))
            log.debug("Mercurial: Clone instead.")
            command = ["hg", "clone", source, target]
            code, output, error = execute(command)

            if code == 0:
                log.debug("Mercurial: Repository at " + source + " cloned.")

            else:
                raise PullFromRepositoryException(unicode(error))


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
            command = ["svn", "checkout", "--trust-server-cert",
                       "--non-interactive", source, target]

        code, output, error = execute(command, env=get_svn_env())

        if code != 0:
            raise PullFromRepositoryException(unicode(error))

        log.debug("Subversion: Repository at " + source + " %s." % status)


class CommitToRepositoryException(Exception):
    pass


class CommitToRepository(object):

    def __init__(self, path, message, user, url):
        self.path = path
        self.message = message
        self.user = user
        self.url = url

    def commit(self, path=None, message=None, user=None):
        raise NotImplementedError

    def nothing_to_commit(self):
        return log.warning('Nothing to commit')


class CommitToGit(CommitToRepository):

    def commit(self, path=None, message=None, user=None):
        log.debug("Git: Commit to repository.")

        path = path or self.path
        message = message or self.message
        user = user or self.user
        author = user.display_name_and_email

        # Embed git identity info into commands
        git_cmd = ['git', '-c', 'user.name=Mozilla Pontoon', '-c',
                   'user.email=pontoon@mozilla.com']

        # Add new and remove missing paths
        execute(git_cmd + ['add', '-A', '--', path], path)

        # Commit
        commit = git_cmd + ['commit', '-m', message, '--author', author]
        code, output, error = execute(commit, path)
        if code != 0 and len(error):
            raise CommitToRepositoryException(unicode(error))

        # Push
        push = ["git", "push", self.url, 'master']
        code, output, error = execute(push, path)
        if code != 0:
            raise CommitToRepositoryException(unicode(error))

        if 'Everything up-to-date' in error:
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
            raise CommitToRepositoryException(unicode(error))

        # Push
        push = ["hg", "push"]
        code, output, error = execute(push, path)
        if code == 1 and 'no changes found' in output:
            return self.nothing_to_commit()

        if code != 0 and len(error):
            raise CommitToRepositoryException(unicode(error))

        log.info(message)


class CommitToSvn(CommitToRepository):

    def commit(self, path=None, message=None, user=None):
        log.debug("Subversion: Commit to repository.")

        path = path or self.path
        message = message or self.message
        user = user or self.user
        author = user.display_name_and_email

        # Commit
        command = ["svn", "commit", "-m", message, "--with-revprop",
                   "author=%s" % author, path]
        code, output, error = execute(command, env=get_svn_env())
        if code != 0:
            raise CommitToRepositoryException(unicode(error))

        if not output and not error:
            return self.nothing_to_commit()

        log.info(message)


def execute(command, cwd=None, env=None):
    try:
        st = subprocess.PIPE
        proc = subprocess.Popen(
            args=command, stdout=st, stderr=st, stdin=st, cwd=cwd, env=env)

        (output, error) = proc.communicate()
        code = proc.returncode
        return code, output, error

    except OSError as error:
        return -1, "", error


def update_from_vcs(repo_type, url, path):
    try:
        obj = globals()['PullFrom%s' % repo_type.capitalize()](url, path)
        obj.pull()

    except PullFromRepositoryException as e:
        error = '%s Pull Error for %s: %s' % (repo_type.upper(), url, e)
        log.debug(error)
        raise Exception(error)


def commit_to_vcs(repo_type, path, message, user, url):
    try:
        obj = globals()['CommitTo%s' % repo_type.capitalize()](
            path, message, user, url)
        return obj.commit()

    except CommitToRepositoryException as e:
        log.debug('%s Commit Error for %s: %s' % (repo_type.upper(), path, e))
        raise e


def get_svn_env():
    """Return an environment dict for running SVN in."""
    if settings.SVN_LD_LIBRARY_PATH:
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = (settings.SVN_LD_LIBRARY_PATH + ':' +
                                  env['LD_LIBRARY_PATH'])
        return env
    else:
        return None


class VCSRepository(object):
    @classmethod
    def for_type(cls, repo_type, path):
        SubClass = cls.REPO_TYPES.get(repo_type)
        if SubClass is None:
            raise ValueError('No subclass found for repo type {0}.'.format(repo_type))

        return SubClass(path)

    def __init__(self, path):
        self.path = path

    def execute(self, cmd, cwd=None, env=None, log_errors=False):
        code, output, error = execute(cmd, cwd=cwd, env=env)
        if log_errors and code != 0:
            log.error('Error while executing command `{cmd}` in `{cwd}`: {stderr}'.format(
                cmd=unicode(cmd), cwd=cwd, stderr=error
            ))
        return code, output, error


class SvnRepository(VCSRepository):
    def execute(self, cmd, cwd=None, env=None, log_errors=False):
        return execute(cmd, cwd=cwd, env=get_svn_env())

    @property
    def revision(self):
        code, output, error = self.execute(['svnversion', self.path], log_errors=True)
        return output.strip() if code == 0 else None


class GitRepository(VCSRepository):
    @property
    def revision(self):
        code, output, error = self.execute(
            ['git', 'rev-parse', 'master'],
            cwd=self.path,
            log_errors=True
        )
        return output.strip() if code == 0 else None


class HgRepository(VCSRepository):
    @property
    def revision(self):
        code, output, error = self.execute(
            ['hg', 'identify', '--id'],
            cwd=self.path,
            log_errors=True
        )
        return output.strip() if code == 0 else None


# TODO: Tie these to the same constants that the Repository model uses.
VCSRepository.REPO_TYPES = {
    'hg': HgRepository,
    'svn': SvnRepository,
    'git': GitRepository,
}


def get_revision(repo_type, path):
    repo = VCSRepository.for_type(repo_type, path)
    return repo.revision
