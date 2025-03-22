#
# Copyright 2006-2010 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""factory methods to build real storage objects that conform to base.py."""

import os
from functools import lru_cache
from importlib import import_module

from translate.storage.base import TranslationStore
from translate.storage.directory import Directory

# TODO: Monolingual formats (with template?)

decompressclass = {
    "gz": ("gzip", "GzipFile"),
    "bz2": ("bz2", "BZ2File"),
}


_classes_str = {
    "csv": ("csvl10n", "csvfile"),
    "tab": ("omegat", "OmegaTFileTab"),
    "utf8": ("omegat", "OmegaTFile"),
    "po": ("po", "pofile"),
    "pot": ("po", "pofile"),
    "mo": ("mo", "mofile"),
    "gmo": ("mo", "mofile"),
    "qm": ("qm", "qmfile"),
    "lang": ("mozilla_lang", "LangStore"),
    "utx": ("utx", "UtxFile"),
    "_wftm": ("wordfast", "WordfastTMFile"),
    "_trados_txt_tm": ("trados", "TradosTxtTmFile"),
    "catkeys": ("catkeys", "CatkeysFile"),
    "qph": ("qph", "QphFile"),
    "tbx": ("tbx", "tbxfile"),
    "tmx": ("tmx", "tmxfile"),
    "ts": ("ts2", "tsfile"),
    "xliff": ("xliff", "xlifffile"),
    "xlf": ("xliff", "xlifffile"),
    "sdlxliff": ("xliff", "xlifffile"),
    "ftl": ("fluent", "FluentFile"),
}
###  XXX:  if you add anything here, you must also add it to translate.storage.

"""Dictionary of file extensions and the names of their associated class.

Used for dynamic lazy loading of modules.
_ext is a pseudo extension, that is their is no real extension by that name.
"""


def _examine_txt(storefile):
    """Determine the true filetype for a .txt file."""
    if isinstance(storefile, str) and os.path.exists(storefile):
        storefile = open(storefile, "rb")
    try:
        start = storefile.read(600).strip()
    except AttributeError:
        raise ValueError("Need to read object to determine type")
    # Some encoding magic for Wordfast
    from translate.storage import wordfast

    encoding = "utf-16" if wordfast.TAB_UTF16 in start.split(b"\n")[0] else "iso-8859-1"
    start = start.decode(encoding)
    if "%Wordfast TM" in start:
        pseudo_extension = "_wftm"
    elif "<RTF Preamble>" in start:
        pseudo_extension = "_trados_txt_tm"
    else:
        raise ValueError("Failed to guess file type.")
    storefile.seek(0)
    return pseudo_extension


_hiddenclasses = {"txt": _examine_txt}


def _guessextention(storefile):
    """
    Guesses the type of a file object by looking at the first few
    characters.  The return value is a file extention.
    """
    start = storefile.read(300).strip()
    if b"<xliff " in start:
        extention = "xlf"
    elif b'msgid "' in start:
        extention = "po"
    elif b"%Wordfast TM" in start:
        extention = "txt"
    elif b"<!DOCTYPE TS>" in start:
        extention = "ts"
    elif b"<tmx " in start:
        extention = "tmx"
    elif b"#UTX" in start:
        extention = "utx"
    else:
        raise ValueError("Failed to guess file type.")
    storefile.seek(0)
    return extention


def _getdummyname(storefile):
    """
    Provides a dummy name for a file object without a name attribute, by
    guessing the file type.
    """
    return "dummy." + _guessextention(storefile)


def _getname(storefile):
    """Returns the filename."""
    if storefile is None:
        raise ValueError(
            "This method cannot magically produce a filename when given None as input."
        )
    if not isinstance(storefile, str):
        if not hasattr(storefile, "name"):
            storefilename = _getdummyname(storefile)
        else:
            storefilename = storefile.name
    else:
        storefilename = storefile
    return storefilename


@lru_cache(maxsize=128)
def import_class(module_name, class_name, prefix=None):
    if prefix:
        module_name = f"{prefix}.{module_name}"
    module = import_module(module_name)
    return getattr(module, class_name)


def getclass(
    storefile,
    localfiletype=None,
    ignore=None,
    classes=None,
    classes_str=None,
    hiddenclasses=None,
):
    """
    Factory that returns the applicable class for the type of file
    presented.  Specify ignore to ignore some part at the back of the name
    (like .gz).
    """
    storefilename = _getname(storefile)
    if classes_str is None:
        classes_str = _classes_str
    if hiddenclasses is None:
        hiddenclasses = _hiddenclasses
    if ignore and storefilename.endswith(ignore):
        storefilename = storefilename[: -len(ignore)]
    ext = localfiletype
    if ext is None:
        root, ext = os.path.splitext(storefilename)
        ext = ext[len(os.path.extsep) :].lower()
        decomp = None
        if ext in decompressclass:
            decomp = ext
            root, ext = os.path.splitext(root)
            ext = ext[len(os.path.extsep) :].lower()
        if ext in hiddenclasses:
            guesserfn = hiddenclasses[ext]
            if decomp:
                _file = import_class(*decompressclass[decomp])
                ext = guesserfn(_file(storefile))
            else:
                ext = guesserfn(storefile)
    try:
        # we prefer classes (if given) since that is the older API that Pootle uses
        if classes:
            storeclass = classes[ext]
        else:
            storeclass = import_class(*classes_str[ext], "translate.storage")
    except KeyError:
        raise ValueError(f"Unknown filetype ({storefilename})")
    return storeclass


def getobject(
    storefile,
    localfiletype=None,
    ignore=None,
    classes=None,
    classes_str=None,
    hiddenclasses=None,
):
    """
    Factory that returns a usable object for the type of file presented.

    :type storefile: file or str or TranslationStore
    :param storefile: File object or file name.

    Specify ignore to ignore some part at the back of the name (like .gz).
    """
    if isinstance(storefile, TranslationStore):
        return storefile
    if classes_str is None:
        classes_str = _classes_str
    if hiddenclasses is None:
        hiddenclasses = _hiddenclasses
    if isinstance(storefile, str):
        if os.path.isdir(storefile) or storefile.endswith(os.path.sep):
            return Directory(storefile)
    storefilename = _getname(storefile)
    storeclass = getclass(
        storefile,
        localfiletype,
        ignore,
        classes=classes,
        classes_str=classes_str,
        hiddenclasses=hiddenclasses,
    )
    if os.path.exists(storefilename) or not getattr(storefile, "closed", True):
        name, ext = os.path.splitext(storefilename)
        ext = ext[len(os.path.extsep) :].lower()
        if ext in decompressclass:
            _file = import_class(*decompressclass[ext])
            storefile = _file(storefilename)
        store = storeclass.parsefile(storefile)
    else:
        store = storeclass()
        store.filename = storefilename
    return store


supported = [
    (
        "Gettext PO file",
        ["po", "pot"],
        [
            "text/x-gettext-catalog",
            "text/x-gettext-translation",
            "text/x-po",
            "text/x-pot",
        ],
    ),
    (
        "XLIFF Translation File",
        ["xlf", "xliff", "sdlxliff"],
        ["application/x-xliff", "application/x-xliff+xml"],
    ),
    (
        "Gettext MO file",
        ["mo", "gmo"],
        ["application/x-gettext-catalog", "application/x-mo"],
    ),
    ("Qt .qm file", ["qm"], ["application/x-qm"]),
    ("TBX Glossary", ["tbx"], ["application/x-tbx"]),
    ("TMX Translation Memory", ["tmx"], ["application/x-tmx"]),
    ("Qt Linguist Translation File", ["ts"], ["application/x-linguist"]),
    ("Qt Phrase Book", ["qph"], ["application/x-qph"]),
    ("OmegaT Glossary", ["utf8", "tab"], ["application/x-omegat-glossary"]),
    ("UTX Dictionary", ["utx"], ["text/x-utx"]),
    ("Haiku catkeys file", ["catkeys"], ["application/x-catkeys"]),
    ("Fluent file", ["ftl"], []),
]


def supported_files():
    """
    Returns data about all supported files.

    :return: list of type that include (name, extensions, mimetypes)
    :rtype: list
    """
    return supported[:]
