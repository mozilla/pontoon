#
# Copyright 2002-2010 Zuza Software Foundation
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

"""
Merges XLIFF and Gettext PO localization files.

Snippet file produced by e.g. :doc:`pogrep </commands/pogrep>` and updated by a
translator can be merged back into the original files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pomerge.html
for examples and usage instructions.
"""

import logging

from translate.storage import factory
from translate.storage.poheader import poheader


def mergestores(store1, store2, mergeblanks, mergefuzzy, mergecomments):
    """Take any new translations in store2 and write them into store1."""
    for unit2 in store2.units:
        if unit2.isheader():
            if isinstance(store1, poheader):
                store1.mergeheaders(store2)
            continue
        unit1 = store1.findid(unit2.getid())
        if unit1 is None:
            unit1 = store1.findunit(unit2.source)
        if unit1 is None:
            logging.error(
                "The template does not contain the following unit:\n%s", str(unit2)
            )
        else:
            if not mergeblanks and len(unit2.target.strip()) == 0:
                continue
            if not mergefuzzy and unit2.isfuzzy():
                continue
            unit1.merge(unit2, overwrite=True, comments=mergecomments)
    return store1


def str2bool(option):
    """
    Convert a string value to boolean.

    :param option: yes, true, 1, no, false, 0
    :type option: String
    :rtype: Boolean

    """
    option = option.lower()
    if option in {"yes", "true", "1"}:
        return True
    if option in {"no", "false", "0"}:
        return False
    raise ValueError(f"invalid boolean value: {option!r}")


def mergestore(
    inputfile,
    outputfile,
    templatefile,
    mergeblanks="no",
    mergefuzzy="no",
    mergecomments="yes",
):
    try:
        mergecomments = str2bool(mergecomments)
    except ValueError:
        raise ValueError(f"invalid mergecomments value: {mergecomments!r}")
    try:
        mergeblanks = str2bool(mergeblanks)
    except ValueError:
        raise ValueError(f"invalid mergeblanks value: {mergeblanks!r}")
    try:
        mergefuzzy = str2bool(mergefuzzy)
    except ValueError:
        raise ValueError(f"invalid mergefuzzy value: {mergefuzzy!r}")
    inputstore = factory.getobject(inputfile)
    if templatefile is None:
        # just merge nothing
        templatestore = type(inputstore)()
    else:
        templatestore = factory.getobject(templatefile)
    outputstore = mergestores(
        templatestore, inputstore, mergeblanks, mergefuzzy, mergecomments
    )
    if outputstore.isempty():
        return 0
    outputstore.serialize(outputfile)
    return 1


def main():
    from translate.convert import convert

    formats = {
        ("po", "po"): ("po", mergestore),
        ("po", "pot"): ("po", mergestore),
        ("pot", "po"): ("po", mergestore),
        ("pot", "pot"): ("pot", mergestore),
        "po": ("po", mergestore),
        "pot": ("po", mergestore),
        ("xlf", "po"): ("po", mergestore),
        ("xlf", "pot"): ("po", mergestore),
        ("xlf", "xlf"): ("xlf", mergestore),
        ("po", "xlf"): ("xlf", mergestore),
        ("xliff", "po"): ("po", mergestore),
        ("xliff", "pot"): ("po", mergestore),
        ("xliff", "xliff"): ("xliff", mergestore),
        ("po", "xliff"): ("xliff", mergestore),
    }
    mergeblanksoption = convert.optparse.Option(
        "",
        "--mergeblanks",
        dest="mergeblanks",
        action="store",
        default="yes",
        help="whether to overwrite existing translations with blank translations (yes/no). Default is yes.",
    )
    mergefuzzyoption = convert.optparse.Option(
        "",
        "--mergefuzzy",
        dest="mergefuzzy",
        action="store",
        default="yes",
        help="whether to consider fuzzy translations from input (yes/no). Default is yes.",
    )
    mergecommentsoption = convert.optparse.Option(
        "",
        "--mergecomments",
        dest="mergecomments",
        action="store",
        default="yes",
        help="whether to merge comments as well as translations (yes/no). Default is yes.",
    )
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.add_option(mergeblanksoption)
    parser.passthrough.append("mergeblanks")
    parser.add_option(mergefuzzyoption)
    parser.passthrough.append("mergefuzzy")
    parser.add_option(mergecommentsoption)
    parser.passthrough.append("mergecomments")
    parser.run()


if __name__ == "__main__":
    main()
