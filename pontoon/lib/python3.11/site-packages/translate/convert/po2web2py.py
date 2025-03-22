#
# Copyright 2009-2010 Zuza Software Foundation
#
# This file is part of translate.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#

"""
Convert GNU/gettext PO files to web2py translation dictionaries (.py).

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/web2py2po.html
for examples and usage instructions.
"""

from io import StringIO

from translate.convert import convert
from translate.storage import factory


class po2pydict:
    def __init__(self):
        return

    @staticmethod
    def convertstore(inputstore, includefuzzy):
        str_obj = StringIO()

        mydict = {}
        for unit in inputstore.units:
            if unit.isheader():
                continue
            if unit.istranslated() or (includefuzzy and unit.isfuzzy()):
                mydict[unit.source] = unit.target
            else:
                mydict[unit.source] = unit.source.replace("@markmin\x01", "")

        str_obj.write("# -*- coding: utf-8 -*-\n")
        str_obj.write("{\n")
        for source_str, trans_str in sorted(mydict.items()):
            str_obj.write(f"{source_str!r}: {trans_str!r},\n")
        str_obj.write("}\n")
        str_obj.seek(0)
        return str_obj


def convertpy(
    inputfile, outputfile, templatefile=None, includefuzzy=False, outputthreshold=None
):
    inputstore = factory.getobject(inputfile)

    if not convert.should_output_store(inputstore, outputthreshold):
        return 0

    convertor = po2pydict()
    outputstring = convertor.convertstore(inputstore, includefuzzy)

    outputfile.write(bytes(outputstring.read(), "utf-8"))
    return 1


def main(argv=None):
    formats = {("po", "py"): ("py", convertpy), ("po", None): ("py", convertpy)}
    parser = convert.ConvertOptionParser(
        formats, usetemplates=False, description=__doc__
    )
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == "__main__":
    main()
