# -*- coding: utf8 -*-

from __future__ import absolute_import
import os
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

    @staticmethod
    def conflict_resolution_callback(*args, **kwargs):
        raise NotImplementedError


class PullFromGit(PullFromRepository):

    VCS = 'git'

    def pull(self, source=None, target=None):
        import git
        log.debug("Clone or update Git repository.")

        source = source or self.source
        target = target or self.target

        try:
            repo = git.Repo(target)
            repo.git.pull()
            log.debug("Git: repository at " + source + " updated.")
        except Exception, e:
            log.debug("Git: " + str(e))
            try:
                git.Git().clone(source, target)
                log.debug("Git: repository at " + source + " cloned.")
            except Exception, e:
                log.debug("Git: " + str(e))
                raise PullFromRepositoryException(unicode(e))

    @staticmethod
    def conflict_resolution_callback(*args, **kwargs):
        pass


class PullFromHg(PullFromRepository):

    VCS = 'hg'

    def pull(self, source=None, target=None):
        from mercurial import commands, hg, ui, error
        log.debug("Clone or update HG repository.")

        source = source or self.source
        target = target or self.target

        # Folders need to be manually created
        if not os.path.exists(target):
            os.makedirs(target)

        # Doesn't work with unicode type
        url = str(source)
        path = str(target)

        try:
            repo = hg.repository(ui.ui(), path)
            commands.pull(ui.ui(), repo, source=url)
            commands.update(ui.ui(), repo)
            log.debug("Mercurial: repository at " + url + " updated.")
        except error.RepoError, e:
            log.debug("Mercurial: " + str(e))
            try:
                commands.clone(ui.ui(), url, path)
                log.debug("Mercurial: repository at " + url + " cloned.")
            except Exception, e:
                log.debug("Mercurial: " + str(e))
                raise PullFromRepositoryException(unicode(e))

    @staticmethod
    def conflict_resolution_callback(*args, **kwargs):
        pass


class PullFromSvn(PullFromRepository):

    VCS = 'svn'

    def pull(self, source=None, target=None):
        import pysvn
        log.debug("Checkout or update SVN repository.")

        source = source or self.source
        target = target or self.target

        client = pysvn.Client()
        client.callback_conflict_resolver = self.conflict_resolution_callback
        client.callback_ssl_server_trust_prompt = self.ssl_server_trust_prompt

        try:
            client.checkout(source, target)
        except pysvn.ClientError, e:
            log.debug("Subversion: " + str(e))
            raise PullFromRepositoryException(unicode(e))

    @staticmethod
    def conflict_resolution_callback(conflict_description):
        import pysvn
        return pysvn.wc_conflict_choice.theirs_full, None, False

    @staticmethod
    def ssl_server_trust_prompt(trust_dict):
        return True, 2, False


class CommitToRepositoryException(Exception):
    pass


class CommitToRepository(object):

    def __init__(self, path, message, username, password):
        self.path = path
        self.message = message
        self.username = username
        self.password = password

    def commit(self, path=None, message=None, username=None, password=None):
        raise NotImplementedError


class CommitToSvn(CommitToRepository):

    VCS = 'svn'

    def commit(self, path=None, message=None, username=None, password=None):
        try:
            import pysvn
        except ImportError as e:
            raise CommitToRepositoryException("SVN module not available")
        log.debug("Commit to SVN repository.")

        path = path or self.path
        message = message or self.message
        username = username or self.username
        password = password or self.password

        client = pysvn.Client()
        client.exception_style = 1

        if len(username) > 0 and len(password) > 0:
            client.set_default_username(username)
            client.set_default_password(password)

        try:
            client.checkin([path], message)
            log.info(message)

        except pysvn.ClientError as e:
            log.debug(str(e))
            if "callback_get_login" in str(e):
                log.error('Subversion CommitError for %s: authenticate' % path)
                return {
                    'type': 'authenticate',
                    'message': 'Authentication failed.'
                }

            raise CommitToRepositoryException(str(e))


def update_from_vcs(repo_type, url, path):
    if repo_type == 'git':
        try:
            obj = PullFromGit(url, path)
            obj.pull()
        except PullFromRepositoryException as e:
            log.debug('Git PullError for %s: %s' % (url, e))

    elif repo_type == 'hg':
        try:
            obj = PullFromHg(url, path)
            obj.pull()
        except PullFromRepositoryException as e:
            log.debug('Mercurial PullError for %s: %s' % (url, e))

    elif repo_type == 'svn':
        try:
            obj = PullFromSvn(url, path)
            obj.pull()
        except PullFromRepositoryException as e:
            log.debug('Subversion PullError for %s: %s' % (url, e))


def commit_to_vcs(repo_type, path, message, username, password):
    if repo_type == 'svn':
        try:
            obj = CommitToSvn(path, message, username, password)
            return obj.commit()
        except CommitToRepositoryException as e:
            log.debug('Subversion CommitError for %s: %s' % (path, e))
            return {
                'type': 'error',
                'message': str(e)
            }
