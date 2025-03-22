#
# Copyright 2002-2008 Zuza Software Foundation
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
Convert Gettext PO localization files to PHP localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/php2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import php, po

eol = "\n"


class rephp:
    def __init__(self, templatefile, inputstore):
        self.outputstore = php.phpfile(templatefile)
        self.inputstore = inputstore
        self.inmultilinemsgid = False
        self.inecho = False
        self.inarray = False
        self.equaldel = "="
        self.enddel = ";"
        self.prename = ""
        self.quotechar = ""

    def convertstore(self, includefuzzy=False):
        self.includefuzzy = includefuzzy
        self.inputstore.makeindex()

        for unit in self.outputstore.units:
            inputunit = self.inputstore.locationindex.get(unit.getid())

            if inputunit is not None:
                if inputunit.isfuzzy():
                    if self.includefuzzy:
                        # inputunit.istranslated() is always False now,
                        # because inputunit.isfuzzy() is True.
                        # So we need to check if inputunit.target is truthy.
                        if inputunit.target:
                            unit.target = inputunit.target
                        else:
                            unit.target = unit.source
                    else:
                        unit.target = unit.source
                elif inputunit.istranslated():
                    unit.target = inputunit.target
                else:
                    unit.target = unit.source
            else:
                unit.target = unit.source
        return bytes(self.outputstore)


def convertphp(
    inputfile, outputfile, templatefile, includefuzzy=False, outputthreshold=None
):
    inputstore = po.pofile(inputfile)

    if not convert.should_output_store(inputstore, outputthreshold):
        return False

    if templatefile is None:
        raise ValueError("must have template file for php files")

    convertor = rephp(templatefile, inputstore)
    output = convertor.convertstore(includefuzzy)
    outputfile.write(output)
    return 1


def main(argv=None):
    # handle command line options
    formats = {
        ("po", "php"): ("php", convertphp),
        ("po", "html"): ("html", convertphp),
    }
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == "__main__":
    main()
