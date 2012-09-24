import silme.io
from silme.core import Blob
from silme.io.clients import IOClient, RCSClient
import silme.format
from silme.core import L10nPackage
from file import FileClient

import pysvn
import os
import shutil
import codecs
import re

def register(Manager):
    Manager.register(SVNClient)

class SVNClient (RCSClient):
    name = 'svn'
    desc = "SVN Client"
    type = IOClient.__name__
    client = None

    def __init__ (self):
        self.user = {'login':None, 'password':None}

    @classmethod
    def get_blob(cls, path, source=True):
        (p, rev) = cls._explode_path(path)
        
        blob = Blob()
        blob.id = os.path.basename(path)
        if source:
            blob.source = cls.get_source_without_encoding(p)
        blob.uri = p
        return blob

    @classmethod
    def get_entitylist(cls, path, source=False, code='default', parser=None):
        (p, rev) = cls._explode_path(path)

        if not parser:
            parser = silme.format.Manager.get(path=p)
        src = cls.get_source(p, encoding = parser.encoding,
                            fallback = parser.fallback)
        entitylist = parser.get_entitylist(src[0], code=code)
        entitylist.id = os.path.basename(p)
        entitylist.uri = p
        if source:
            entitylist.source = src[0]
        entitylist.encoding = src[1]
        return entitylist

    @classmethod
    def get_l10nobject(cls, path, source=False, code='default', parser=None):
        (p, rev) = cls._explode_path(path)

        if not parser:
            parser = silme.format.Manager.get(path=p)
        src = cls.get_source(p, encoding = parser.encoding,
                            fallback = parser.fallback)
        l10nobject = parser.get_l10nobject(src[0], code=code)
        l10nobject.id = os.path.basename(p)
        l10nobject.uri = p
        if source:
            l10nobject.source = src[0]
        l10nobject.encoding = src[1]
        return l10nobject

    @classmethod
    def get_l10npackage(cls, path,
                        code='default',
                        object_type='l10nobject',
                        source=None,
                        ignore=['CVS','.svn','.DS_Store', '.hg']):
        (p, rev) = cls._explode_path(path)

        l10npackage = L10nPackage()
        l10npackage.id = os.path.basename(p)
        l10npackage.uri = p
        
        # if source is None, load it for blob
        if source is None:
            b_source = True # blob source
            oe_source = False # l10nobject & entitylist source
        elif source is False: # don't load it for anyone
            b_source = False
            oe_source = False
        else: # load it for everyone
            b_source = True
            oe_source = True

        cls.client = pysvn.Client()
        entry_list = cls.client.list(path, recurse=True)
        for i in entry_list:
            elem = os.path.basename(i[0].path)
            if ignore.__class__.__name__=='function': # is function
                if ignore(i[0].path):
                    continue
                else:
                    if os.path.basename(i[0].path) in ignore:
                        continue
            if i[0].kind == pysvn.node_kind.file:
                dirname = os.path.dirname(i[0].path)
                filename =    os.path.basename(i[0].path)
                # @var relpath: relative-path to the given path'
                relpath = re.sub(os.path.dirname(p), '', dirname, 1)
                if relpath.startswith('/'):
                    relpath = os.path.split(relpath)[1]
                try:
                    parser = silme.format.Manager.get(path=elem)
                except Exception:
                    l10npackage.add_object(cls.get_blob(i[0].path, source=b_source), relpath)
                else:
                    if object_type=='object':
                        l10npackage.add_object(cls.get_blob(i[0].path, source=b_source), relpath)
                    elif object_type=='entitylist':
                        l10npackage.add_objects(cls.get_entitylist(i[0].path, source=oe_source, code=code, parser=parser), relpath)
                    else:
                        l10npackage.add_objects(cls.get_l10nobject(i[0].path, source=oe_source, code=code, parser=parser), relpath)
        return l10npackage

#========================

    @classmethod
    def _explode_path(cls, path):
        return (path, 0)

    @classmethod
    def _read_with_encoding(cls, path, encoding):
        client = pysvn.Client()
        text = client.cat(path, revision=pysvn.Revision( pysvn.opt_revision_kind.head ))
        return text

    @classmethod
    def _read_without_encoding(cls, path):
        client = pysvn.Client()
        text = client.cat(path, revision=pysvn.Revision( pysvn.opt_revision_kind.head ))
        return text

#=========
"""
    @classmethod
    def get_source (cls, path, revision=None):
        string    = u''
        client = pysvn.Client()
        if revision == None:
            string = client.cat(path, revision=pysvn.Revision( pysvn.opt_revision_kind.head ))
        else:    
            string = client.cat(path, revision=pysvn.Revision( pysvn.opt_revision_kind.number, revision ))
        return string

    @classmethod
    def get_l10nobject (cls, path):
        format_parser = silme.format.Manager.get(path)
        source = cls.get_source(path)
        l10nobject = format_parser.parse(source)
        l10nobject.id = os.path.basename(path)
        return l10nobject

    @classmethod
    def get_l10npackage (cls, path, load_objects = True):
        l10npackage = L10nPackage()
        l10npackage.id = os.path.basename(path)
        client = pysvn.Client()
        entry_list = client.list(path, recurse=False)
        for i in entry_list:
            if i[0].kind == pysvn.node_kind.dir and i[0].path != path:
                l10npackage.add_package(cls.get_l10npackage(i[0].path))
            if i[0].kind == pysvn.node_kind.file:
                l10npackage.add_object(cls.get_l10nobject(path=i[0].path))
        return l10npackage

    @classmethod
    def writeObject (cls, object, path):
        tmppath = '/tmp/testtmp'
        format_parser = silme.format.Manager.get(object.id)
        if not format_parser:
            if isinstance(object, Object):
                string = object.source
            else:
                return
        else:
            string = formatParser.dump_l10nobject(object)
        cls.write_to_file(path, string)


    @classmethod
    def write_to_file (cls, url, content):
        (path, file) = os.path.split(url)
        tmppath = '/tmp/testtmp'
        client = pysvn.Client()
        #client.callback_get_login = self.login
        client.checkout(path, tmppath)
        ioClient = IOManager.get('file')
        ioClient.write_to_file(content, os.path.join(tmppath, file))
        client.checkin(tmppath, log_message="test checkin from library")
        shutil.rmtree(tmppath)

    @classmethod
    def write_l10npackage (cls, l10npackage, url, message=None):
        tmppath = '/tmp/testtmp'
        client = pysvn.Client()
        #client.callback_get_login = self.login
        client.checkout(url, tmppath, recurse=True)
        ioClient = silme.io.Manager.get('file')
        ioClient.write_l10npackage(l10npackage, tmppath)
        client.checkin(tmppath, log_message="test checkin from library")
        shutil.rmtree(tmppath)

    def set_login_data (self, user, password):
        self.user['login'] = user
        self.user['password'] = password

    def login (self, realm, username, may_save):
        retcode=True
        username = self.user['login']
        password = self.user['password']
        save = True
        return retcode, username, password, save
"""