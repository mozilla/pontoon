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
Convert TikiWiki's language.php files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/tiki2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import po, tiki


class tiki2po:
    """Convert one or two TikiWiki's language.php files to a single PO file."""

    SourceStoreClass = tiki.TikiStore
    TargetStoreClass = po.pofile
    TargetUnitClass = po.pounit

    def __init__(
        self, input_file, output_file, template_file=None, include_unused=False
    ):
        """Initialize the converter."""
        self.include_unused = include_unused

        self.output_file = output_file
        self.source_store = self.SourceStoreClass(input_file)
        self.target_store = self.TargetStoreClass()

    def convert_unit(self, unit):
        """Convert a source format unit to a target format unit."""
        target_unit = self.TargetUnitClass()
        locations = unit.getlocations()
        if locations:
            target_unit.addlocations(locations)
        target_unit.source = unit.source
        target_unit.target = unit.target
        return target_unit

    def convert_store(self):
        """Convert a single source format file to a target format file."""
        for source_unit in self.source_store.units:
            if not self.include_unused and "unused" in source_unit.getlocations():
                continue
            self.target_store.addunit(self.convert_unit(source_unit))

    def run(self):
        """Run the converter."""
        self.convert_store()
        if self.target_store.isempty():
            return 0

        self.target_store.serialize(self.output_file)
        return 1


def run_converter(input_file, output_file, template_file=None, includeunused=False):
    """Wrapper around converter."""
    return tiki2po(input_file, output_file, template_file, includeunused).run()


formats = {
    "php": ("po", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    parser.add_option(
        "",
        "--include-unused",
        dest="includeunused",
        action="store_true",
        default=False,
        help="Include strings in the unused section",
    )
    parser.passthrough.append("includeunused")
    parser.run(argv)


if __name__ == "__main__":
    main()
