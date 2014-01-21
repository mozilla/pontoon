# -*- coding: utf8 -*-

from __future__ import absolute_import
import pysvn
from mercurial import commands, hg, ui, error
import os
import commonware


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


class PullFromHg(PullFromRepository):

    VCS = 'hg'

    def pull(self, source=None, target=None):
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
        return pysvn.wc_conflict_choice.theirs_full, None, False

    @staticmethod
    def ssl_server_trust_prompt(trust_dict):
        return True, 2, False


def update_from_vcs(repo_type, url, path):
    if repo_type == 'hg':
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
            log.debug('SVN PullError for %s: %s' % (url, e))
