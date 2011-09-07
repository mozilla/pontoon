import codecs
import os
import sys

from ..core import Blob, Package
from ..format import Manager as FManager

try:
    import chardet
    char_detector=True
except ImportError:
    char_detector=False

try:
    unichr
except:
    unichr = chr

class IOClient(object):
    bomdict = { 'utf_8_sig' : codecs.BOM_UTF8,
                'utf_16_be' : codecs.BOM_UTF16_BE,
                'utf_16_le' : codecs.BOM_UTF16_LE,
                'utf_16' : codecs.BOM_UTF16 }

    @classmethod
    def matches_path(cls, path):
        """
        tests if the ioclient should be used for this type of path
        """
        raise NotImplementedError()

    @classmethod
    def get_blob(cls, path, uri=None, source=True):
        raise NotImplementedError()

    @classmethod
    def get_entitylist(cls, path,
                       uri=None,
                       source=False,
                       ordered=True,
                       lazy=True,
                       parser=None):
        raise NotImplementedError()

    @classmethod
    def get_structure(cls, path, uri=None, source=False, parser=None):
        raise NotImplementedError()

    @classmethod
    def get_idlist(cls, path):
        raise NotImplementedError()

    @classmethod
    def get_package(cls, path,
                        uri=None,
                        object_type='structure',
                        source=None,
                        ordered=False,
                        lazy=False,
                        ignore=['CVS','.svn','.DS_Store', '.hg']):
        raise NotImplementedError()

    @classmethod
    def get_source(cls, path, encoding=None, fallback=None):
        """
        reads source from the path
        """
        raise NotImplementedError()

    @classmethod
    def get_source_with_encoding(cls, path, encoding):
        """
        reads source with encoding fallback
        """
        raise NotImplementedError()

    @classmethod
    def get_source_without_encoding(cls, path):
        """
        reads source ignoring encoding (in binary compatible mode)
        """
        raise NotImplementedError()

    @classmethod
    def write_blob(cls, blob, path):
        raise NotImplementedError()

    @classmethod
    def write_entitylist(cls, elist, path):
        raise NotImplementedError()

    @classmethod
    def write_structure(cls, l10nobject, path):
        raise NotImplementedError()

    @classmethod
    def write_object(cls, object, path):
        raise NotImplementedError()

    @classmethod
    def write_package(cls, l10npackage, path):
        raise NotImplementedError()

    @classmethod
    def write_source(cls, source, path, encoding):
        """
        writes source to destination path
        """
        raise NotImplementedError()

    @classmethod
    def path_type(cls, path):
        """
        returns 'package', 'object' depending on the path type
        """
        raise NotImplementedError()


class FileFormatClient(IOClient):

    @classmethod
    def get_blob(cls, path, uri=None, source=True):
        blob = Blob(os.path.basename(path))
        if source:
            blob.source = cls.get_source_without_encoding(path)
        blob.uri = uri or path
        return blob

    @classmethod
    def get_entitylist(cls, path,
                       uri=None,
                       source=False,
                       ordered=True,
                       lazy=True,
                       parser=None):
        if not parser:
            parser = FManager.get(path=path)
        src = cls.get_source(path, encoding = parser.encoding,
                            fallback = parser.fallback)
        entitylist = parser.get_entitylist(src[0])
        entitylist.id = os.path.basename(path)
        entitylist.uri = uri or path
        if source:
            entitylist.source = src[0]
        entitylist.encoding = src[1]
        return entitylist

    @classmethod
    def get_idlist(cls, path,
                   uri=None,
                   source=False,
                   ordered=True,
                   parser=None):
        if not parser:
            parser = FManager.get(path=path)
        src = cls.get_source(path, encoding = parser.encoding,
                            fallback = parser.fallback)
        ids = parser.get_idlist(src[0])
        return ids

    @classmethod
    def get_structure(cls, path, uri=None, source=False,  parser=None):
        if not parser:
            parser = FManager.get(path=path)
        src = cls.get_source(path, encoding = parser.encoding,
                            fallback = parser.fallback)
        l10nobject = parser.get_structure(src[0])
        l10nobject.id = os.path.basename(path)
        l10nobject.uri = uri or path
        if source:
            l10nobject.source = src[0]
        l10nobject.encoding = src[1]
        return l10nobject

    @classmethod
    def get_package(cls, path,
                        uri=None,
                        object_type='list',
                        source=None,
                        ordered=False,
                        lazy=False,
                        ignore=['CVS','.svn','.DS_Store', '.hg']):
        l10npackage = Package(id=os.path.basename(path))
        l10npackage.uri = path
        return l10npackage

    @classmethod
    def get_source(cls, path, encoding=None, fallback=None):
        """
        reads source with all autoguessing, encoding guessing.
        This methods is offered for reading sources that are semantically
        meaningfull for later use.
        """
        # if the encoding parameter is specified, force it to being used
        # There is no fallback if opening with this encoding fails!
        if encoding is not None:
            output = cls.get_source_with_encoding(path, encoding)
            if output[1] != encoding and (fallback is None or 
                                        output[1] not in fallback):
                raise Exception('The encoding for path ' + path + ' is not ' + \
                                encoding + ' like expected, but ' + output[1] + \
                                '. ' + output[1] + ' is not in the fallback list' + \
                                ', break.')
            return output
        else:
            # if no encoding specified, try the fallback list
            fallback = fallback or ('utf_8',)
            for coding in fallback:
                try:
                    return cls.get_source_with_encoding(path, coding)
                except UnicodeDecodeError as e:
                    continue
            # UniversalDetector: only used if available
            # When used, a slow down of 10 to 20 times can be expected!
            # Be warned: sometimes it detects the encoding wrongly!
            if char_detector:
                try:
                    coding=\
                    chardet.detect(cls._read_without_encoding(path))['encoding'].lower()
                except Exception as e:
                    pass # TODO: logging
                else:
                    try:
                        return cls.get_source_with_encoding(path, coding)
                    except UnicodeDecodeError as e:
                        pass # TODO: logging
            # last chance: try to open using the system default encoding
            try:
                return cls.get_source_with_encoding(path, sys.getdefaultencoding())
            except:
                pass
            try:
                return unicode(cls._read_without_encoding(path))
            except Exception as e:
                raise Exception('Failed to find proper encoding')

    @classmethod
    def get_source_with_encoding(cls, path, encoding):
        try:
            text = cls._read_with_encoding(path, encoding)
        except IOError as e:
            raise IOError(path + ': ' + str(e))
        text, encoding = cls._test_bom(text, encoding)
        if isinstance(text, str):
            return cls._to_unicode(text, encoding)
        else:
            return (text, encoding)

    @classmethod
    def get_source_without_encoding(cls, path):
        try:
            return cls._read_without_encoding(path)
        except IOError as e:
            raise IOError(path + ': ' + str(e))
        except Exception as e:
            raise

    @classmethod
    def _test_bom(cls, text, encoding):
        # unichr(65279) == \ufeff == Unicode BOM as text
        bc = unichr(65279)
        if encoding == 'utf_8' and text.startswith(bc):
            text = text[len(bc):]
            encoding = 'utf_8_sig'
        elif encoding in cls.bomdict.keys() and text.startswith(bc):
            text = text[len(bc):]
        elif encoding == 'utf_8_sig' and not text.startswith(bc):
            encoding = 'utf_8'
        return (text, encoding)

    @classmethod
    def _to_unicode(cls, text, encoding):
        # we want to work only on unicode strings!
        #decode_to_unicode = codecs.getdecoder(encoding)
        #text = decode_to_unicode(text)[0]
        return (text, encoding)

    @staticmethod
    def _get_source_policy(source):
        # returns two variables that define whether the source of a file
        # should be attached to a given object
        #
        # if source is True - l10nobject,entitylist and blob get source
        # if source is False - none of them gets source
        # if source is None - l10nobject and entity list get it, blob does not
        if source is None:
            b_source = True # blob source
            oe_source = False # l10nobject & entitylist source
        elif source is False: # don't load it for anyone
            b_source = False
            oe_source = False
        else: # load it for everyone
            b_source = True
            oe_source = True
        return (b_source, oe_source)
    
    @staticmethod
    def _should_ignore(ignore, path, elem):
        # allows objects and packages to be ignored inside get_l10npackage.
        #
        # ignore argument of IOClient.get_l10npackage can be:
        # list - list of files and directories to ignore
        # function - in which case the function will be launched against each
        #            object or package load
        if ignore.__class__.__name__=='function': # is function
            return ignore(path, elem)
        else:
            return any([i in ignore for i in elem])

    @classmethod
    def _write_source_with_encoding(cls, content, path, encoding=None):
        raise NotImplementedError()
    
    @classmethod
    def _read_with_encoding(cls, path, encoding):
        raise NotImplementedError()

    @classmethod
    def _read_without_encoding(cls, path):
        raise NotImplementedError()

class DBClient (IOClient):
    get_blob = None
    get_structure = None
    write_blob = None
    write_structure = None
    write_source = None

    def get_entitylist (cls, path):
        raise NotImplementedError()

    @classmethod
    def write_object(cls, object, path, encoding=None):
        if isinstance(object, EntityList):
            cls.write_entitylist(object, path, encoding=encoding)
        else:
            raise TypeError()

class RCSClient (FileFormatClient):
    pass
