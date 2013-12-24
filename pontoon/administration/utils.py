# -*- coding: utf8 -*-

from __future__ import absolute_import
import pysvn
import mercurial
import os
import commonware


log = commonware.log.getLogger('playdoh')


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
        url = str(url)
        path = str(path)

        try:
            repo = mercurial.hg.repository(ui.ui(), path)
            mercurial.commands.pull(mercurial.ui.ui(), repo, source=source)
            mercurial.commands.update(mercurial.ui.ui(), repo)
            #log.debug("Mercurial: Repository for " + l.name + " updated.")
        except mercurial.error.RepoError, e:
            log.debug("Mercurial: " + str(e))
            try:
                mercurial.commands.clone(mercurial.ui.ui(), source, target)
                #log.debug("Mercurial: Repository for " + l.name + " cloned.")
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
        try:
            client.checkout(source, target)
        except pysvn.ClientError, e:
            log.debug("Subversion: " + str(e))
            raise PullFromRepositoryException(unicode(e))

    @staticmethod
    def conflict_resolution_callback(conflict_description):
        return pysvn.wc_conflict_choice.theirs_full, None, False


def update_from_vcs(repo_type, url, path):
    if repo_type == 'hg':
        obj = PullFromHg(url, path)
        obj.pull()
    elif repo_type == 'svn':
        obj = PullFromSvn(url, path)
        obj.pull()
