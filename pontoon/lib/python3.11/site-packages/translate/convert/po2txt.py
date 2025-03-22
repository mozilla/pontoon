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
Convert Gettext PO localization files to plain text (.txt) files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/txt2po.html
for examples and usage instructions.
"""

import textwrap

from translate.convert import convert
from translate.storage import factory


class po2txt:
    """
    po2txt can take a po file and generate txt.

    best to give it a template file otherwise will just concat msgstrs
    """

    def __init__(
        self,
        input_file,
        output_file,
        template_file=None,
        include_fuzzy=False,
        output_threshold=None,
        encoding="utf-8",
        wrap=None,
    ):
        """Initialize the converter."""
        self.source_store = factory.getobject(input_file)

        self.should_output_store = convert.should_output_store(
            self.source_store, output_threshold
        )
        if self.should_output_store:
            self.include_fuzzy = include_fuzzy
            self.encoding = encoding
            self.wrap = wrap

            self.output_file = output_file
            self.template_file = template_file

    def wrapmessage(self, message):
        """Rewraps text as required."""
        if self.wrap is None:
            return message
        return "\n".join(
            textwrap.fill(line, self.wrap, replace_whitespace=False)
            for line in message.split("\n")
        )

    def convert_store(self):
        """Convert a source file to a target file."""
        txtresult = ""
        for unit in self.source_store.units:
            if not unit.istranslatable():
                continue
            if unit.istranslated() or (self.include_fuzzy and unit.isfuzzy()):
                txtresult += self.wrapmessage(unit.target) + "\n\n"
            else:
                txtresult += self.wrapmessage(unit.source) + "\n\n"
        return txtresult.rstrip()

    def merge_stores(self):
        """
        Convert a source file to a target file using a template file.

        Source file is in source format, while target and template files use
        target format.
        """
        txtresult = self.template_file.read().decode(self.encoding)
        # TODO: make a list of blocks of text and translate them individually
        # rather than using replace
        for unit in self.source_store.units:
            if not unit.istranslatable():
                continue
            if not unit.isfuzzy() or self.include_fuzzy:
                txtsource = unit.source
                txttarget = self.wrapmessage(unit.target)
                if unit.istranslated():
                    txtresult = txtresult.replace(txtsource, txttarget)
        return txtresult

    def run(self):
        """Run the converter."""
        if not self.should_output_store:
            return False

        if self.template_file is None:
            outputstring = self.convert_store()
        else:
            outputstring = self.merge_stores()

        self.output_file.write(outputstring.encode("utf-8"))
        return True


def run_converter(
    inputfile,
    outputfile,
    templatefile=None,
    wrap=None,
    includefuzzy=False,
    encoding="utf-8",
    outputthreshold=None,
):
    """Wrapper around converter."""
    return po2txt(
        inputfile,
        outputfile,
        templatefile,
        include_fuzzy=includefuzzy,
        output_threshold=outputthreshold,
        encoding=encoding,
        wrap=wrap,
    ).run()


formats = {
    ("po", "txt"): ("txt", run_converter),
    ("po"): ("txt", run_converter),
    ("xlf", "txt"): ("txt", run_converter),
    ("xlf"): ("txt", run_converter),
    ("xliff", "txt"): ("txt", run_converter),
    ("xliff"): ("txt", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.add_option(
        "",
        "--encoding",
        dest="encoding",
        default="utf-8",
        type="string",
        help="The encoding of the template file (default: UTF-8)",
    )
    parser.passthrough.append("encoding")
    parser.add_option(
        "-w",
        "--wrap",
        dest="wrap",
        default=None,
        type="int",
        help="set number of columns to wrap text at",
        metavar="WRAP",
    )
    parser.passthrough.append("wrap")
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == "__main__":
    main()
