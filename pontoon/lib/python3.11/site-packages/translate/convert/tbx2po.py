#
# Copyright 2006-2007 Zuza Software Foundation
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
Convert TermBase eXchange (.tbx) glossary file into a Gettext PO file.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/tbx2po.html
for examples and usage instructions
"""

from translate.storage import po, tbx


class tbx2po:
    """
    A class that takes translations from a .tbx file and puts them in a .po
    file.
    """

    def convertfile(self, tbxfile):
        """
        Converts a tbxfile to a tbxfile, and returns it. uses templatepo if
        given at construction.
        """
        self.pofile = po.pofile()
        for tbxunit in tbxfile.units:
            term = po.pounit()
            term.source = tbxunit.source
            term.target = tbxunit.target
            term.setcontext(tbxunit.getnotes("definition"))
            term.addnote(
                "Part of speech: {}".format(tbxunit.getnotes("pos")), "developer"
            )
            self.pofile.addunit(term)
        self.pofile.removeduplicates()
        return self.pofile


def converttbx(inputfile, outputfile, templatefile, charset=None, columnorder=None):
    """
    Reads in inputfile using tbx, converts using tbx2po, writes to
    outputfile.
    """
    inputstore = tbx.tbxfile(inputfile)
    convertor = tbx2po()
    outputstore = convertor.convertfile(inputstore)
    if len(outputstore.units) == 0:
        return 0
    outputstore.serialize(outputfile)
    return 1


def main():
    from translate.convert import convert

    formats = {
        ("tbx", None): ("po", converttbx),
    }
    parser = convert.ConvertOptionParser(
        formats, usetemplates=False, description=__doc__
    )
    parser.run()


if __name__ == "__main__":
    main()
