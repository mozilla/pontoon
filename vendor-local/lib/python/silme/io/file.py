from ..format import Manager
from .clients import IOClient, FileFormatClient
from ..core import Package, Structure, EntityList, Blob

import os
import sys
import codecs

def register(Manager):
    Manager.register(FileClient)

class FileClient (FileFormatClient):
    name = 'file'
    desc = "File Client"
    type = IOClient.__name__

    @classmethod
    def matches_path(cls, path):
        """
        tests if the ioclient should be used for this type of path
        Matches any:
        1) "/foo"
        2) "./foo"
        3) "file://foo"
        """
        return path.startswith('/') or \
                path.startswith('./') or \
                path.startswith('../') or \
                path.startswith('file://')

    @classmethod
    def get_package(cls, path,
                        code='default',
                        object_type='l10nobject',
                        source=None,
                        ignore=['CVS','.svn','.DS_Store', '.hg']):
        l10npackage = FileFormatClient.get_package(path, code, object_type, source, ignore)
        (b_source, oe_source) = cls._get_source_policy(source)

        try:
            l = os.listdir(path)
        except OSError, e:
            raise OSError('Not a directory: ' + path + ': ' + str(e))
        except Exception, e:
            raise Exception('Could not load directory: ' + path + ': ' + str(e))
        for elem in l:
            p2 = os.path.join(path, elem)
            if cls._should_ignore(ignore, path=p2, elem=[elem]):
                continue

            if os.path.isdir(p2):
                l10npackage._packages[elem] = cls.get_package(p2, code=code, object_type=object_type, source=source, ignore=ignore)
            else:
                try:
                    parser = Manager.get(path=elem)
                except KeyError:
                    l10npackage._structures[elem] = cls.get_blob(p2, source=b_source)
                else:
                    if object_type=='object':
                        l10npackage._structures[elem] = cls.get_blob(p2, source=b_source)
                    elif object_type=='entitylist':
                        l10npackage._structures[elem] = cls.get_entitylist(p2, source=oe_source, code=code, parser=parser)
                    else:
                        l10npackage._structures[elem] = cls.get_structure(p2, source=oe_source, code=code, parser=parser)

        return l10npackage

    @classmethod
    def write_blob(cls, blob, path):
        path = os.path.join(path, blob.id) if os.path.isdir(path) else path
        cls.write_source(blob.source,
                        path,
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
        path = os.path.join(path, elist.id) if os.path.isdir(path) else path
        cls.write_source(string,
                        path,
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
        path = os.path.join(path, object.id) if os.path.isdir(path) else path
        cls.write_source(string,
                        path,
                        format_parser.encoding)
        return True

    @classmethod
    def write_object(cls, object, path, encoding=None):
        if isinstance(object, Structure):
            cls.write_structure(object, path, encoding=encoding)
        elif isinstance(object, EntityList):
            cls.write_entitylist(object, path, encoding=encoding)
        elif isinstance(object, Blob):
            cls.write_blob(object, path)
        else:
            raise TypeError('Cannot write object of such type (%s)' % object.__class__.__name__)

    @classmethod
    def write_package(cls, l10npack, path):
        if not os.path.isdir(path):
            os.makedirs(path)
        for i in l10npack.packages():
            if not os.path.isdir(os.path.join(path, i.id)):
                os.mkdir(os.path.join(path, i.id))
            cls.write_package(l10npack.package(i.id), os.path.join(path, i.id))
        for i in l10npack.structures():
            cls.write_object(l10npack.structure(i.id), path)
        return True

    @classmethod
    def write_source(cls, content, path, encoding=None):
        if encoding is None:
            f = open(path, mode='wb')
            f.write(content)
            f.close()
        else:
            cls._write_source_with_encoding(content, path, encoding=encoding)
        return True

    @classmethod
    def path_type(cls, path):
        """
        returns 'package', 'object' depending on the path type
        """
        if os.path.isdir(path):
            return 'package'
        else:
            return 'object'

#========================================================================

    @classmethod
    def _write_source_with_encoding(cls, content, path, encoding='utf-8'):
        f = codecs.open(path, encoding=encoding, mode='w+')
        try:
            # write BOM if the encoding requires it
            if encoding in cls.bomdict.keys():
                f.write(cls.bomdict[encoding])
            f.write(content)
        except UnicodeEncodeError:
            # fallback to utf_8
            f = codecs.open(path, encoding='utf_8', mode='w+')
            try:
                f.write(content)
            except:
                raise Exception('could not write file: '+path)
        f.close()
        return True
    
    @classmethod
    def _read_with_encoding(cls, path, encoding):
        file = codecs.open(path, 'r', encoding=encoding)
        text = file.read()
        file.close()
        return text

    @classmethod
    def _read_without_encoding(cls, path):
        file = open(path, 'rb')
        text = file.read()
        file.close()
        return text

