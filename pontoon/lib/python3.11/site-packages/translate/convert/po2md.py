#
# Copyright 2023 Zuza Software Foundation & Anders Kaplan
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
Translate Markdown files using Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/md2po.html
for examples and usage instructions.
"""

import os
import sys

from translate.convert import convert
from translate.misc.optrecurse import ProgressBar
from translate.storage import markdown, po

DEFAULT_MAX_LINE_LENGTH = 80


class MarkdownTranslator:
    def __init__(self, inputstore, includefuzzy, outputthreshold, maxlength):
        self.inputstore = inputstore
        self.inputstore.require_index()
        self.includefuzzy = includefuzzy
        self.outputthreshold = outputthreshold
        self.maxlength = maxlength

    def translate(self, templatefile, outputfile):
        if not convert.should_output_store(self.inputstore, self.outputthreshold):
            return False

        outputstore = markdown.MarkdownFile(
            inputfile=templatefile,
            callback=self._lookup,
            max_line_length=self.maxlength if self.maxlength > 0 else None,
        )
        outputfile.write(outputstore.filesrc.encode("utf-8"))
        return 1

    def _lookup(self, string):
        unit = self.inputstore.sourceindex.get(string, None)
        if unit is None:
            return string
        unit = unit[0]
        if unit.istranslated():
            return unit.target
        if self.includefuzzy and unit.isfuzzy():
            return unit.target
        return unit.source


class PO2MDOptionParser(convert.ConvertOptionParser):
    def __init__(self):
        formats = {
            ("po", "md"): ("md", self._translate_md_file),
            ("po", "markdown"): ("markdown", self._translate_md_file),
            ("po", "txt"): ("txt", self._translate_md_file),
            ("po", "text"): ("text", self._translate_md_file),
        }
        super().__init__(formats, usetemplates=True, description=__doc__)
        self.add_option(
            "-m",
            "--maxlinelength",
            type="int",
            dest="maxlength",
            default=DEFAULT_MAX_LINE_LENGTH,
            help="reflow (word wrap) the output to the given maximum line length. set to 0 to disable",
        )
        self.passthrough.append("maxlength")
        self.add_threshold_option()
        self.add_fuzzy_option()

    @staticmethod
    def _translate_md_file(
        inputfile,
        outputfile,
        templatefile,
        includefuzzy,
        outputthreshold,
        maxlength,
    ):
        inputstore = po.pofile(inputfile)
        translator = MarkdownTranslator(
            inputstore, includefuzzy, outputthreshold, maxlength
        )
        return translator.translate(templatefile, outputfile)

    def recursiveprocess(self, options):
        if (
            self.isrecursive(options.template, "template")
            and not self.isrecursive(options.input, "input")
            and self.can_be_recursive(options.output, "output")
        ):
            self.recursiveprocess_by_templates(options)
        else:
            super().recursiveprocess(options)

    def can_be_recursive(self, fileoption, filepurpose):
        return fileoption is not None and not os.path.isfile(fileoption)

    def recursiveprocess_by_templates(self, options):
        """Recurse through directories and process files, by templates (markdown) not input files (po)."""
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
                    self.process_file_with_fixed_inputstore,
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
        del progress_bar

    def process_file_with_fixed_inputstore(
        self,
        inputfile,
        outputfile,
        templatefile,
        includefuzzy,
        outputthreshold,
        maxlength,
    ):
        translator = MarkdownTranslator(
            self.inputstore, includefuzzy, outputthreshold, maxlength
        )
        return translator.translate(templatefile, outputfile)

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
    parser = PO2MDOptionParser()
    parser.run(argv)


if __name__ == "__main__":
    main()
