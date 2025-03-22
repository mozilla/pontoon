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
Translate HTML files using Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/html2po.html
for examples and usage instructions.
"""

import os
import sys

from translate.convert import convert
from translate.misc.optrecurse import ProgressBar
from translate.storage import html, po


class po2html:
    """Read inputfile (po) and templatefile (html), write to outputfile (html)."""

    def lookup(self, string):
        unit = self.inputstore.sourceindex.get(string, None)
        if unit is None:
            return string
        unit = unit[0]
        if unit.istranslated():
            return unit.target
        if self.includefuzzy and unit.isfuzzy():
            return unit.target
        return unit.source

    def mergestore(self, inputstore, templatetext, includefuzzy):
        """Convert a file to html format."""
        self.inputstore = inputstore
        self.inputstore.require_index()
        self.includefuzzy = includefuzzy
        output_store = html.htmlfile(inputfile=templatetext, callback=self.lookup)
        return output_store.filesrc


def converthtml(
    inputfile, outputfile, templatefile, includefuzzy=False, outputthreshold=None
):
    """Read inputfile (po) and templatefile (html), write to outputfile (html)."""
    inputstore = po.pofile(inputfile)

    if not convert.should_output_store(inputstore, outputthreshold):
        return False

    convertor = po2html()
    if templatefile is None:
        raise ValueError("must have template file for HTML files")
    outputstring = convertor.mergestore(inputstore, templatefile, includefuzzy)
    outputfile.write(outputstring.encode("utf-8"))
    return 1


class PO2HtmlOptionParser(convert.ConvertOptionParser):
    def __init__(self):
        formats = {
            ("po", "htm"): ("htm", converthtml),
            ("po", "html"): ("html", converthtml),
            ("po", "xhtml"): ("xhtml", converthtml),
            ("po"): ("html", converthtml),
        }
        super().__init__(formats, usetemplates=True, description=__doc__)
        self.add_threshold_option()
        self.add_fuzzy_option()

    def recursiveprocess(self, options):
        if (
            self.isrecursive(options.template, "template")
            and not self.isrecursive(options.input, "input")
            and self.can_be_recursive(options.output, "output")
        ):
            self.recursiveprocess_by_templates(options)
        else:
            super().recursiveprocess(options)

    @staticmethod
    def can_be_recursive(fileoption, filepurpose):
        return fileoption is not None and not os.path.isfile(fileoption)

    def recursiveprocess_by_templates(self, options):
        """Recurse through directories and process files, by templates (html) not input files (po)."""
        inputfile = self.openinputfile(options, options.input)
        self.inputstore = po.pofile(inputfile)
        templatefiles = self.recurse_template_files(options)
        self.ensurerecursiveoutputdirexists(options)
        progress_bar = ProgressBar(options.progress, templatefiles)
        for templatepath in templatefiles:
            fulltemplatepath = os.path.join(options.template, templatepath)
            outputpath = templatepath
            fulloutputpath = os.path.join(options.output, outputpath)
            self.checkoutputsubdir(options, os.path.dirname(outputpath))
            try:
                success = self.processfile(
                    self.processfile_with_fixed_inputstore,
                    options,
                    None,
                    fulloutputpath,
                    fulltemplatepath,
                )
            except Exception:
                self.warning(
                    f"Error processing: input {options.input}, output {fulloutputpath}, template {fulltemplatepath}",
                    options,
                    sys.exc_info(),
                )
                success = False
            progress_bar.report_progress(templatepath, success)

    def processfile_with_fixed_inputstore(
        self,
        inputfile,
        outputfile,
        templatefile,
        includefuzzy=False,
        outputthreshold=None,
    ):
        if not convert.should_output_store(self.inputstore, outputthreshold):
            return False

        convertor = po2html()
        outputstring = convertor.mergestore(self.inputstore, templatefile, includefuzzy)
        outputfile.write(outputstring.encode("utf-8"))
        return 1

    def recurse_template_files(self, options):
        """Recurse through directories and return files to be processed."""
        dirstack = [""]
        join = os.path.join
        templatefiles = []
        while dirstack:
            top = dirstack.pop(-1)
            names = os.listdir(join(options.template, top))
            dirs = []
            for name in names:
                filepath = join(top, name)
                fullfilepath = join(options.template, filepath)
                # handle directories...
                if os.path.isdir(fullfilepath):
                    dirs.append(filepath)
                elif os.path.isfile(fullfilepath):
                    if not self.isvalidtemplatename(name):
                        # only handle names that match recognized output
                        # file extensions
                        continue
                    templatefiles.append(filepath)
            # make sure the directories are processed next time round.
            dirs.reverse()
            dirstack.extend(dirs)
        return templatefiles

    def isvalidtemplatename(self, filename):
        """Checks if this is a valid template/output filename."""
        _, ext = self.splitext(filename)
        return any(ext == templateformat for _, templateformat in self.outputoptions)


def main(argv=None):
    parser = PO2HtmlOptionParser()
    parser.run(argv)


if __name__ == "__main__":
    main()
