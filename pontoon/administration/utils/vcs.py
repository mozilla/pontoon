# -*- coding: utf8 -*-

from __future__ import absolute_import
import base64
import os
import subprocess
import commonware.log


log = commonware.log.getLogger('pontoon')


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
        log.debug("Clone or update Git repository.")

        source = source or self.source
        target = target or self.target

        command = ["git", "fetch", "--all"]
        execute(command, target)

        # Undo local changes
        command = ["git", "reset", "--hard", "origin/master"]
        code, output, error = execute(command, target)

        if code == 0:
            log.debug("Git: repository at " + source + " updated.")

        else:
            log.debug("Git: " + unicode(error))
            command = ["git", "clone", source, target]
            code, output, error = execute(command)

            if code == 0:
                log.debug("Git: repository at " + source + " cloned.")

            else:
                raise PullFromRepositoryException(unicode(error))


class PullFromHg(PullFromRepository):

    def pull(self, source=None, target=None):
        log.debug("Clone or update HG repository.")

        source = source or self.source
        target = target or self.target

        # Undo local changes
        command = ["hg", "revert", "--all", "--no-backup"]
        execute(command, target)

        command = ["hg", "pull", "-u"]
        code, output, error = execute(command, target)

        if code == 0:
            log.debug("Mercurial: repository at " + source + " updated.")

        else:
            log.debug("Mercurial: " + unicode(error))
            command = ["hg", "clone", source, target]
            code, output, error = execute(command)

            if code == 0:
                log.debug("Mercurial: repository at " + source + " cloned.")

            else:
                raise PullFromRepositoryException(unicode(error))


class PullFromSvn(PullFromRepository):

    def pull(self, source=None, target=None):
        log.debug("Checkout or update SVN repository.")

        source = source or self.source
        target = target or self.target

        if os.path.exists(target):
            status = "updated"
            command = ["svn", "update", "--accept", "theirs-full", target]

        else:
            status = "checked out"
            command = ["svn", "checkout", "--trust-server-cert",
                       "--non-interactive", source, target]

        code, output, error = execute(command)

        if code != 0:
            raise PullFromRepositoryException(unicode(error))

        log.debug("Subversion: repository at " + source + " %s." % status)


class CommitToRepositoryException(Exception):
    pass


class CommitToRepository(object):

    def __init__(self, path, message, user, data):
        self.path = path
        self.message = message
        self.user = user
        self.data = data

    def commit(self, path=None, message=None, user=None, data=None):
        raise NotImplementedError


class CommitToGit(CommitToRepository):

    def commit(self, path=None, message=None, user=None):
        log.debug("Commit to Git repository.")

        path = path or self.path
        message = message or self.message
        user = user or self.user

        # Set commit author
        name = user.first_name
        if not name:
            name = user.email.split('@')[0]
        author = ' '.join([name, '<%s>' % user.email])

        # Add
        add = ["git", "add", "-A"]
        execute(add, path)

        # Commit
        commit = ["git", "commit", "-m", message, "--author", author]
        code, output, error = execute(commit, path)
        if code != 0 and len(error):
            raise CommitToRepositoryException(unicode(error))

        # Push
        push = ["git", "push"]
        code, output, error = execute(push, path)
        if code != 0:
            raise CommitToRepositoryException(unicode(error))

        log.info(message)


class CommitToHg(CommitToRepository):

    def commit(self, path=None, message=None, user=None):
        log.debug("Commit to Mercurial repository.")

        path = path or self.path
        message = message or self.message
        user = user or self.user

        # Set commit author
        name = user.first_name
        if not name:
            name = user.email.split('@')[0]
        author = ' '.join([name, '<%s>' % user.email])

        # Commit
        commit = ["hg", "commit", "-m", message, "-u", author]
        code, output, error = execute(commit, path)
        if code != 0 and len(error):
            raise CommitToRepositoryException(unicode(error))

        # Push
        push = ["hg", "push"]
        code, output, error = execute(push, path)
        if code != 0:
            raise CommitToRepositoryException(unicode(error))

        log.info(message)


class CommitToSvn(CommitToRepository):

    def commit(self, path=None, message=None, user=None, data=None):
        log.debug("Commit to SVN repository.")

        path = path or self.path
        message = message or self.message
        user = user or self.user
        data = data or self.data

        # Check if user authenticated
        from pontoon.base.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        username = data.get('auth', {}).get('username', profile.svn_username)
        password = data.get('auth', {}).get(
            'password', base64.decodestring(profile.svn_password))

        command = ["svn", "commit", "-m", message, path]
        if len(username) > 0 and len(password) > 0:
            command += ['--username', username, '--password', password]

        code, output, error = execute(command)

        if code == 0:
            log.info(message)

            # Save username and password
            if data.get('auth', {}).get('remember', {}) == 1:
                if profile.svn_username != username:
                    profile.svn_username = username
                if base64.decodestring(profile.svn_password) != password:
                    profile.svn_password = base64.encodestring(password)
                profile.save()
                log.info("Username and password saved.")

        elif "E215004" in error:
            log.debug(error)
            log.debug('Subversion authentication failed for %s' % path)
            return {
                'type': 'authenticate',
                'message': 'Authentication failed.'
            }

        else:
            if "E155011" in error:
                error = \
                    'Content out of date. Try updating from repository first.'

            raise CommitToRepositoryException(unicode(error))


def execute(command, cwd=None):
    try:
        st = subprocess.PIPE
        proc = subprocess.Popen(
            args=command, stdout=st, stderr=st, stdin=st, cwd=cwd)

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


def commit_to_vcs(repo_type, path, message, user, data):
    try:
        obj = globals()['CommitTo%s' % repo_type.capitalize()](
            path, message, user, data)
        return obj.commit()

    except CommitToRepositoryException as e:
        log.debug('%s Commit Error for %s: %s' % (repo_type.upper(), path, e))
        return {
            'type': 'error',
            'message': unicode(e)
        }
