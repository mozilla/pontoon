#
# Copyright 2008 Mozilla Corporation, Zuza Software Foundation
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
Convert Gettext PO files to TikiWiki's language.php files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/tiki2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import po, tiki


class po2tiki:
    """Convert a PO file and a template TikiWiki file to a TikiWiki file."""

    SourceStoreClass = po.pofile
    TargetStoreClass = tiki.TikiStore
    TargetUnitClass = tiki.TikiUnit

    def __init__(self, input_file, output_file, template_file=None):
        """Initialize the converter."""
        self.source_store = self.SourceStoreClass(input_file)
        self.output_file = output_file
        self.target_store = self.TargetStoreClass()

    def convert_unit(self, unit):
        """Convert a source format unit to a target format unit."""
        target_unit = self.TargetUnitClass(unit.source)
        target_unit.target = unit.target
        locations = unit.getlocations()
        if locations:
            target_unit.addlocations(locations)
        # If a word is "untranslated" but the target isn't empty and isn't the
        # same as the source it's been translated and we switch it. This is an
        # assumption but should remain true as long as these scripts are used.
        if target_unit.getlocations() == ["untranslated"] and unit.source not in {
            unit.target,
            "",
        }:
            target_unit.location = []
            target_unit.addlocation("translated")
        return target_unit

    def convert_store(self):
        """Convert a single source format file to a target format file."""
        for source_unit in self.source_store.units:
            if source_unit.isblank() or source_unit.isheader():
                continue
            self.target_store.addunit(self.convert_unit(source_unit))

    def run(self):
        """Run the converter."""
        if self.source_store.isempty():
            return 0

        self.convert_store()
        self.target_store.serialize(self.output_file)
        return 1


def run_converter(inputfile, outputfile, template=None):
    """Wrapper around converter."""
    return po2tiki(inputfile, outputfile, template).run()


formats = {
    "po": ("tiki", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    parser.run(argv)


if __name__ == "__main__":
    main()
