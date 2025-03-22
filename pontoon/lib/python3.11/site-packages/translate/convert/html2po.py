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
#

"""
Convert HTML files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/html2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import html, po


class html2po:
    def convertfile(
        self,
        inputfile,
        filename,
        duplicatestyle="msgctxt",
        keepcomments=False,
    ):
        """Convert an html file to .po format."""
        thetargetfile = po.pofile()
        self.convertfile_inner(inputfile, thetargetfile, keepcomments)
        thetargetfile.removeduplicates(duplicatestyle)
        return thetargetfile

    @staticmethod
    def convertfile_inner(inputfile, outputstore, keepcomments):
        """Extract translation units from an html file and add to a pofile object."""
        htmlparser = html.htmlfile(inputfile=inputfile)
        for htmlunit in htmlparser.units:
            thepo = outputstore.addsourceunit(htmlunit.source)
            thepo.addlocations(htmlunit.getlocations())
            if keepcomments:
                thepo.addnote(htmlunit.getnotes(), "developer")


def converthtml(
    inputfile,
    outputfile,
    templates,
    pot=False,
    duplicatestyle="msgctxt",
    keepcomments=False,
):
    """
    reads in stdin using fromfileclass, converts using convertorclass,
    writes to stdout.
    """
    convertor = html2po()
    outputstore = convertor.convertfile(
        inputfile,
        getattr(inputfile, "name", "unknown"),
        duplicatestyle=duplicatestyle,
        keepcomments=keepcomments,
    )
    outputstore.serialize(outputfile)
    return 1


class Html2POOptionParser(convert.ConvertOptionParser):
    def __init__(self):
        formats = {
            "html": ("po", self.convert),
            "htm": ("po", self.convert),
            "xhtml": ("po", self.convert),
            None: ("po", self.convert),
        }
        super().__init__(formats, usetemplates=False, usepots=True, description=__doc__)
        self.add_option(
            "--keepcomments",
            dest="keepcomments",
            default=False,
            action="store_true",
            help="preserve html comments as translation notes in the output",
        )
        self.passthrough.append("keepcomments")
        self.add_duplicates_option()
        self.add_multifile_option()
        self.passthrough.append("pot")

    def convert(
        self,
        inputfile,
        outputfile,
        templates,
        pot=False,
        duplicatestyle="msgctxt",
        multifilestyle="single",
        keepcomments=False,
    ):
        """Extract translation units from one html file."""
        convertor = html2po()
        if hasattr(self, "outputstore"):
            convertor.convertfile_inner(inputfile, self.outputstore, keepcomments)
        else:
            outputstore = convertor.convertfile(
                inputfile,
                getattr(inputfile, "name", "unknown"),
                duplicatestyle=duplicatestyle,
                keepcomments=keepcomments,
            )
            outputstore.serialize(outputfile)
        return 1

    def recursiveprocess(self, options):
        """Recurse through directories and process files. (override)."""
        if options.multifilestyle == "onefile":
            self.outputstore = po.pofile()
            super().recursiveprocess(options)
            if not self.outputstore.isempty():
                self.outputstore.removeduplicates(options.duplicatestyle)
                outputfile = super().openoutputfile(options, options.output)
                self.outputstore.serialize(outputfile)
                if options.output:
                    outputfile.close()
        else:
            super().recursiveprocess(options)

    def isrecursive(self, fileoption, filepurpose="input"):
        """Check if fileoption is a recursive file. (override)."""
        if hasattr(self, "outputstore") and filepurpose == "output":
            return True
        return super().isrecursive(fileoption, filepurpose=filepurpose)

    def checkoutputsubdir(self, options, subdir):
        """
        Check if subdir under options.output needs to be created,
        creates if neccessary. Do nothing if in single-output-file mode. (override).
        """
        if hasattr(self, "outputstore"):
            return
        super().checkoutputsubdir(options, subdir)

    def openoutputfile(self, options, fulloutputpath):
        """Open the output file, or do nothing if in single-output-file mode. (override)."""
        if hasattr(self, "outputstore"):
            return None
        return super().openoutputfile(options, fulloutputpath)


def main(argv=None):
    parser = Html2POOptionParser()
    parser.run(argv)


if __name__ == "__main__":
    main()
