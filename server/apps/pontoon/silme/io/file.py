from ..format import Manager
from .clients import IOClient, FileFormatClient
from ..core import Package, Structure, EntityList, Blob
from silme.core.list import is_entitylist

import os
import sys
import codecs

def register(Manager):
    Manager.register(FileClient)

def resolve_package(id, *args):
    return FileClient.get_package(*args)

def resolve_entitylist(id, p2, source, parser):
    return FileClient.get_entitylist(p2, source, parser)

def resolve_structure(id, p2, source, parser):
    return FileClient.get_structure(p2, source, parser)

def resolve_blob(id, p2, source):
    return FileClient.get_blob(p2, source)

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
                        uri=None,
                        object_type='list',
                        source=None,
                        ordered=False,
                        lazy=False,
                        ignore=['CVS','.svn','.DS_Store', '.hg']):
        pack = FileFormatClient.get_package(path, object_type, source, ignore)
        try:
            leafs = os.listdir(path)
        except OSError as e:
            raise OSError('Not a directory: ' + path + ': ' + str(e))
        except Exception as e:
            raise Exception('Could not load directory: ' + path + ': ' + str(e))
        if lazy:
            cls._get_package_lazy(path, pack, leafs, object_type, source, ignore)
        else:
            cls._get_package_full(path, pack, leafs, object_type, source, ignore)
        return pack

    @classmethod
    def _get_package_full(cls, path,
                          pack,
                          leafs,
                          object_type,
                          source,
                          ignore):
        (b_source, oe_source) = cls._get_source_policy(source)
        for elem in leafs:
            p2 = os.path.join(path, elem)
            if cls._should_ignore(ignore, path=p2, elem=[elem]):
                continue

            if os.path.isdir(p2):
                pack._packages[elem] = cls.get_package(p2, None, object_type, source, False, False, ignore)
            else:
                try:
                    parser = Manager.get(path=elem)
                except KeyError:
                    pack._structures[elem] = cls.get_blob(p2, b_source)
                else:
                    if object_type=='list':
                        pack._structures[elem] = cls.get_entitylist(p2, oe_source, parser)
                    elif object_type=='blob':
                        pack._structures[elem] = cls.get_blob(p2, b_source)
                    else:
                        pack._structures[elem] = cls.get_structure(p2, oe_source, parser)

    @classmethod
    def _get_package_lazy(cls, path,
                          pack,
                          leafs,
                          object_type,
                          source,
                          ignore):
        (b_source, oe_source) = cls._get_source_policy(source)
        for elem in leafs:
            p2 = os.path.join(path, elem)
            if cls._should_ignore(ignore, path=p2, elem=[elem]):
                continue

            if os.path.isdir(p2):
                pack._packages.set_stub(elem, resolve_package, p2, None, object_type, source, False, True, ignore) 
            else:
                try:
                    parser = Manager.get(path=elem)
                except KeyError:
                    pack._structures.set_stub(elem, resolve_blob, p2, source=b_source)
                else:
                    if object_type=='list':
                        pack._structures.set_stub(elem, resolve_entitylist, p2, source=oe_source, parser=parser)
                    elif object_type=='blob':
                        pack._structures.set_stub(elem, resolve_blob, p2, source=b_source)
                    else:
                        pack._structures.set_stub(elem, resolve_structure, p2, source=oe_source, parser=parser)

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
        elif is_entitylist(object):
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
        with codecs.open(path, 'r', encoding=encoding) as file:
            text = file.read()
        return text

    @classmethod
    def _read_without_encoding(cls, path):
        with open(path, 'rb') as file:
            return file.read()
