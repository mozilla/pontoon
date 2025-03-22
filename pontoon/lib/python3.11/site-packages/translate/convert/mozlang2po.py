#
# Copyright 2008, 2011 Zuza Software Foundation
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

"""Convert Mozilla .lang files to Gettext PO localization files."""

from translate.convert import convert
from translate.storage import mozilla_lang as lang
from translate.storage import po


class lang2po:
    """Convert one Mozilla .lang file to a single PO file."""

    SourceStoreClass = lang.LangStore
    TargetStoreClass = po.pofile
    TargetUnitClass = po.pounit

    def __init__(
        self,
        input_file,
        output_file,
        template_file=None,
        blank_msgstr=False,
        duplicate_style="msgctxt",
        encoding="utf-8",
    ):
        """Initialize the converter."""
        self.blank_msgstr = blank_msgstr
        self.duplicate_style = duplicate_style

        self.extraction_msg = None
        self.output_file = output_file
        self.source_store = self.SourceStoreClass(input_file, encoding=encoding)
        self.target_store = self.TargetStoreClass()
        self.template_store = None

        if template_file is not None:
            self.template_store = self.SourceStoreClass(template_file)

    def convert_unit(self, unit):
        """Convert a source format unit to a target format unit."""
        target_unit = self.TargetUnitClass()
        target_unit.addlocations(unit.getlocations())
        target_unit.addnote(unit.getnotes(), "developer")
        target_unit.source = unit.source
        target_unit.target = unit.target
        return target_unit

    def convert_store(self):
        """Convert a single source format file to a target format file."""
        self.extraction_msg = f"extracted from {self.source_store.filename}"

        for source_unit in self.source_store.units:
            self.target_store.addunit(self.convert_unit(source_unit))

    def merge_stores(self):
        """Convert two source format files to a target format file."""
        raise NotImplementedError

    def run(self):
        """Run the converter."""
        if self.template_store is None:
            self.convert_store()
        else:
            self.merge_stores()

        if self.extraction_msg:
            self.target_store.header().addnote(self.extraction_msg, "developer")

        self.target_store.removeduplicates(self.duplicate_style)

        if self.target_store.isempty():
            return 0

        self.target_store.serialize(self.output_file)
        return 1


def run_converter(
    input_file,
    output_file,
    template_file=None,
    pot=False,
    duplicatestyle="msgctxt",
    encoding="utf-8",
):
    """Wrapper around converter."""
    return lang2po(
        input_file,
        output_file,
        template_file,
        blank_msgstr=pot,
        duplicate_style=duplicatestyle,
        encoding=encoding,
    ).run()


formats = {"lang": ("po", run_converter)}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats, usepots=True, description=__doc__)
    parser.add_option(
        "",
        "--encoding",
        dest="encoding",
        default="utf-8",
        help="The encoding of the input file (default: UTF-8)",
    )
    parser.passthrough.append("encoding")
    parser.add_duplicates_option()
    parser.run(argv)


if __name__ == "__main__":
    main()
