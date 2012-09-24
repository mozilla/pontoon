from ..format import Manager
from .clients import IOClient, FileFormatClient
from ..core import Package, Structure, Blob

import os
import zipfile
import re
import shutil
import tempfile

def register(Manager):
    Manager.register(JarClient)

class JarClient(FileFormatClient):
    name = 'jar'
    desc = "Jar Client"
    type = IOClient.__name__
    zfile = None

    @classmethod
    def matches_path(cls, path):
        """
        tests if the ioclient should be used for this type of path
        example: jar:browser.jar!/content/branding/
        """
        return path.startswith('jar:') or path.endswith('.jar')

    @classmethod
    def get_blob(cls, path, source=True):
        (p, j, i) = cls._explode_path(path)
        return super(JarClient, cls).get_blob(path, uri=i, source=source)

    @classmethod
    def get_entitylist(cls, path, source=False, code='default', parser=None):
        (p, j, i) = cls._explode_path(path)
        return super(JarClient, cls).get_entitylist(path, uri=i, source=source, code=code, parser=parser)

    @classmethod
    def get_structure(cls, path, source=False, code='default', parser=None):
        (p, j, i) = cls._explode_path(path)
        return super(JarClient, cls).get_structure(path, uri=i, source=source, code=code, parser=parser)

    @classmethod
    def get_package(cls, path,
                        code='default',
                        object_type='l10nobject',
                        source=None,
                        ignore=['CVS','.svn','.DS_Store', '.hg']):
        (protocol, jarpath, ipath) = cls._explode_path(path)
        l10npackage = FileFormatClient.get_package(path, code, object_type, source, ignore)
        (b_source, oe_source) = cls._get_source_policy(source)

        if ipath:
            ipath = os.path.dirname(ipath)
        if not cls.zfile:
            try:
                cls._open_jar(jarpath)
            except Exception,e:
                raise Exception('Could not load a jar file: ' + jarpath + ': ' + str(e))
            # @var jar_open_stat: We need to know if the JAR-file was already open
            jar_open_stat = False
        else:
            jar_open_stat = True
        for name in cls.zfile.namelist():
            dirname = os.path.dirname(name)
            filename =    os.path.basename(name)
            # filter out dir entries or entries for dirs not in ipath
            if not filename or (ipath and not dirname.startswith(ipath)):
                continue

            relpath = dirname[len(ipath):] if ipath else dirname
            relpath = relpath[1:] if relpath.startswith('/') else relpath

            if cls._should_ignore(ignore, path=relpath, elem=[filename]):
                continue

            try:
                parser = Manager.get(path=filename)
            except KeyError, e:
                l10npackage.add_structure(cls.get_blob(name, source=True), relpath)
            else:
                if object_type=='blob':
                    l10npackage.add_structure(cls.get_blob(name, source=True), relpath)
                elif object_type=='entitylist':
                    l10npackage.add_structure(cls.get_entitylist(name, source=source,
                                            parser=parser), relpath)
                else:
                    l10npackage.add_structure(cls.get_structure(name, source=source,
                                            parser=parser), relpath)
        # close the JAR-file only, if it was opened in this method
        if not jar_open_stat:
            cls._close_jar()
        return l10npackage

    @classmethod
    def write_blob(cls, blob, path):
        cls.write_source(blob.source,
                        path,
                        blob.id,
                        encoding=None)

    @classmethod
    def write_entitylist(cls, elist, path, encoding=None):
        if encoding is None and hasattr(elist, 'encoding'):
            encoding = elist.encoding
        try:
            format_parser = Manager.get(path=elist.id)
        except KeyError:
            raise Exception('No parser for given object type')
        string = format_parser.dump_entitylist(elist)
        cls.write_source(string,
                        path,
                        elist.id,
                        encoding)
        return True

    @classmethod
    def write_structure(cls, object, path, encoding=None):
        if encoding is None and hasattr(object, 'encoding'):
            encoding = object.encoding
        try:
            format_parser = Manager.get(path=object.id)
        except KeyError:
            raise Exception('No parser for given object type ('+object.id+')')
        string = format_parser.dump_structure(object)
        cls.write_source(string,
                        path,
                        object.id,
                        format_parser.encoding)
        return True

    @classmethod
    def write_structure(cls, object, path, encoding=None):
        if isinstance(object, Structure):
            cls.write_structure(object, path, encoding=encoding)
        elif isinstance(object, EntityList):
            cls.write_entitylist(object, path, encoding=encoding)
        elif isinstance(object, Blob):
            cls.write_blob(object, path)

    @classmethod
    def write_package(cls, l10npack, path, ipath=''):
        if not cls.zfile:
            cls._open_jar(os.path.join(path, l10npack.id+'.jar'), mode='w')

        for object in l10npack.get_structures():
            cls.write_structure(object, os.path.join(ipath, object.id))
        for pack in l10npack.get_packages():
            cls.write_l10npackage(pack, path, os.path.join(ipath, pack.id))

        if cls.zfile:
            cls._close_jar()

    @classmethod
    def write_source(cls, content, path, name, encoding=None):
        if not cls.zfile:
            (p, j, i) = cls._explode_path(path)
            cls._open_jar(j, mode='a')
            cls.zfile.writestr(os.path.join(i, name), content)
            cls._close_jar()
        else:
            cls.zfile.writestr(path, content)
        return True

#========================================================================

    @classmethod
    def _explode_path(cls, path):
        if path.startswith('jar:'):
            try:
                delim = path.index('!')
            except:
                delim = None
            protocol = path[0:4]
            jarpath = path[4:delim]
            internalpath = delim and path[delim+1:] or ''
        elif path.endswith('.jar'):
            protocol = None
            jarpath = path
            internalpath = None
        else:
            protocol = None
            jarpath = None
            internalpath = path
        return (protocol, jarpath, internalpath)

    @classmethod
    def _open_jar(cls, path, mode='r'):
        '''
        Opens the given jar-file and returns a zipfile instance
        @param path: path to a jar-file
        '''
        if cls.zfile is not None:
            if cls.zfile.mode == mode:
                return True
            else:
                cls._close_jar()
        if mode is not 'w' and not zipfile.is_zipfile(path):
            raise Exception('Not a valid JAR-file: ' + path + ' !')
        cls.zfile = zipfile.ZipFile(path, mode)

    @classmethod
    def _close_jar(cls):
        '''
        Close an open jar-file instance
        '''
        if cls.zfile is None:
            raise KeyError('It looks like there is nothing to be closed!')
        cls.zfile.close()
        cls.zfile = None

    @classmethod
    def _read_with_encoding(cls, path, encoding):
        if cls.zfile is None:
            (protocol, jpath, ipath) = cls._explode_path(path)
            cls._open_jar(jpath)
            text = cls.zfile.read(ipath).decode(encoding)
            cls._close_jar()
            return text
        else:
            return cls.zfile.read(path).decode(encoding)

    @classmethod
    def _read_without_encoding(cls, path):
        if cls.zfile is None:
            (protocol, jpath, ipath) = cls._explode_path(path)
            cls._open_jar(jpath)
            text = cls.zfile.read(ipath)
            cls._close_jar()
            return text
        else:
            return cls.zfile.read(path)

def zipfile_delete(self, file):
    # create temporary file
    f = tempfile.mkstemp()
    os.remove(f[1])
    zfile = zipfile.ZipFile(f[1], mode='w')
    for item in self.infolist():
        buf = self.read(item.filename)
        if not item.filename==file:
            zfile.writestr(item, buf)
    zfile.close()
    shutil.move(zfile.filename, self.filename)

zipfile.ZipFile.delete = zipfile_delete
