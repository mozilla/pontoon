#
# Copyright 2004-2006 Zuza Software Foundation
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
Convert plain text (.txt) files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/txt2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import po, txt


class txt2po:
    """Convert one plain text (.txt) file to a single PO file."""

    SourceStoreClass = txt.TxtFile
    TargetStoreClass = po.pofile
    TargetUnitClass = po.pounit

    def __init__(
        self,
        input_file,
        output_file,
        template_file=None,
        duplicate_style="msgctxt",
        encoding="utf-8",
        flavour=None,
        no_segmentation=False,
    ):
        """Initialize the converter."""
        self.duplicate_style = duplicate_style

        self.extraction_msg = None
        self.output_file = output_file
        self.source_store = self.SourceStoreClass(
            input_file,
            encoding=encoding,
            flavour=flavour,
            no_segmentation=no_segmentation,
        )
        self.target_store = self.TargetStoreClass()
        self.template_store = None

        if template_file is not None:
            self.template_store = self.SourceStoreClass(
                template_file,
                encoding=encoding,
                flavour=flavour,
                no_segmentation=no_segmentation,
            )

    def convert_store(self):
        """Convert a single source format file to a target format file."""
        self.extraction_msg = f"extracted from {self.source_store.filename}"

        for source_unit in self.source_store.units:
            target_unit = self.target_store.addsourceunit(source_unit.source)
            target_unit.addlocations(source_unit.getlocations())

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
    duplicatestyle="msgctxt",
    encoding="utf-8",
    flavour=None,
    no_segmentation=False,
):
    """Wrapper around converter."""
    return txt2po(
        input_file,
        output_file,
        template_file,
        duplicate_style=duplicatestyle,
        encoding=encoding,
        flavour=flavour,
        no_segmentation=no_segmentation,
    ).run()


formats = {
    "txt": ("po", run_converter),
    "*": ("po", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats, usepots=True, description=__doc__)
    parser.add_option(
        "",
        "--encoding",
        dest="encoding",
        default="utf-8",
        type="string",
        help="The encoding of the input file (default: UTF-8)",
    )
    parser.passthrough.append("encoding")
    parser.add_option(
        "",
        "--flavour",
        dest="flavour",
        default="plain",
        type="choice",
        choices=["plain", "dokuwiki", "mediawiki"],
        help=("The flavour of text file: plain (default), dokuwiki, mediawiki"),
        metavar="FLAVOUR",
    )
    parser.passthrough.append("flavour")
    parser.add_option(
        "",
        "--no-segmentation",
        dest="no_segmentation",
        default=False,
        action="store_true",
        help="Don't segment the file, treat it like a single message",
    )
    parser.passthrough.append("no_segmentation")
    parser.add_duplicates_option()
    parser.run(argv)


if __name__ == "__main__":
    main()
