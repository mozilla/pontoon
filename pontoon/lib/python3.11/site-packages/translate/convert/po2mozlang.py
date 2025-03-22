#
# Copyright 2008,2011 Zuza Software Foundation
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

# Original Author: Dan Schafer <dschafer@mozilla.com>
# Date: 10 Jun 2008

"""Convert Gettext PO localization files to Mozilla .lang files."""

from translate.convert import convert
from translate.storage import mozilla_lang, po


class po2lang:
    """Convert a PO file to a Mozilla .lang file."""

    SourceStoreClass = po.pofile
    TargetStoreClass = mozilla_lang.LangStore
    TargetUnitClass = mozilla_lang.LangUnit

    def __init__(
        self,
        input_file,
        output_file,
        template_file=None,
        include_fuzzy=False,
        output_threshold=None,
        mark_active=True,
    ):
        """Initialize the converter."""
        self.source_store = self.SourceStoreClass(input_file)

        self.should_output_store = convert.should_output_store(
            self.source_store, output_threshold
        )
        if self.should_output_store:
            self.include_fuzzy = include_fuzzy

            self.output_file = output_file
            self.target_store = self.TargetStoreClass(mark_active=mark_active)

    def convert_unit(self, unit):
        """Convert a source format unit to a target format unit."""
        target_unit = self.TargetUnitClass(unit.source)
        if self.include_fuzzy or not unit.isfuzzy():
            target_unit.target = unit.target
        else:
            target_unit.target = ""
        if unit.getnotes("developer"):
            target_unit.addnote(unit.getnotes("developer"), "developer")
        return target_unit

    def convert_store(self):
        """Convert a single source format file to a target format file."""
        for source_unit in self.source_store.units:
            if source_unit.isheader() or not source_unit.istranslatable():
                continue
            self.target_store.addunit(self.convert_unit(source_unit))

    def run(self):
        """Run the converter."""
        if not self.should_output_store:
            return 0

        if self.source_store.isempty():
            return 0

        self.convert_store()
        self.target_store.serialize(self.output_file)
        return 1


def run_converter(
    inputfile,
    outputfile,
    templatefile=None,
    includefuzzy=False,
    mark_active=True,
    outputthreshold=None,
):
    """Wrapper around converter."""
    return po2lang(
        inputfile, outputfile, templatefile, includefuzzy, outputthreshold, mark_active
    ).run()


formats = {
    "po": ("lang", run_converter),
    ("po", "lang"): ("lang", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.add_option(
        "",
        "--mark-active",
        dest="mark_active",
        default=False,
        action="store_true",
        help="mark the file as active",
    )
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.passthrough.append("mark_active")
    parser.run(argv)


if __name__ == "__main__":
    main()
