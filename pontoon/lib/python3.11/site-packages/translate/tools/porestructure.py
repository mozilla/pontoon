#
# Copyright 2005, 2006 Zuza Software Foundation
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
Restructure Gettxt PO files produced by
:doc:`poconflicts </commands/poconflicts>` into the original directory tree
for merging using :doc:`pomerge </commands/pomerge>`.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pomerge.html
for examples and usage instructions.
"""

import os
import sys

from translate.misc import optrecurse
from translate.storage import po


class SplitOptionParser(optrecurse.RecursiveOptionParser):
    """a specialized Option Parser for posplit."""

    def parse_args(self, args=None, values=None):
        """Parses the command line options, handling implicit input/output args."""
        (options, args) = super().parse_args(args, values)
        if not options.output:
            self.error("Output file is rquired")
        return (options, args)

    def set_usage(self, usage=None):
        """Sets the usage string - if usage not given, uses getusagestring for each option."""
        if usage is None:
            self.usage = (
                "%prog "
                + " ".join(self.getusagestring(option) for option in self.option_list)
                + "\n  "
                + "input directory is searched for PO files with (poconflicts) comments, all entries are written to files in a directory structure for pomerge"
            )
        else:
            super().set_usage(usage)

    def recursiveprocess(self, options):
        """Recurse through directories and process files."""
        if not self.isrecursive(options.output, "output"):
            self.warning("Output directory does not exist. Attempting to create")
            try:
                # TODO: maybe we should only allow it to be created, otherwise
                # we mess up an existing tree.
                os.mkdir(options.output)
            except Exception:
                self.error(
                    optrecurse.optparse.OptionValueError(
                        "Output directory does not exist, attempt to create failed"
                    )
                )
        if self.isrecursive(options.input, "input") and getattr(
            options, "allowrecursiveinput", True
        ):
            if isinstance(options.input, list):
                inputfiles = self.recurseinputfilelist(options)
            else:
                inputfiles = self.recurseinputfiles(options)
        elif options.input:
            inputfiles = [os.path.basename(options.input)]
            options.input = os.path.dirname(options.input)
        else:
            inputfiles = [options.input]
        self.textmap = {}
        progress_bar = optrecurse.ProgressBar(options.progress, inputfiles)
        for inputpath in inputfiles:
            fullinputpath = self.getfullinputpath(options, inputpath)
            try:
                success = self.processfile(options, fullinputpath)
            except Exception:
                self.warning(
                    f"Error processing: input {fullinputpath}",
                    options,
                    sys.exc_info(),
                )
                success = False
            progress_bar.report_progress(inputpath, success)

    def processfile(self, options, fullinputpath):
        """Process an individual file."""
        inputfile = self.openinputfile(options, fullinputpath)
        inputpofile = po.pofile(inputfile)
        for pounit in inputpofile.units:
            if not (pounit.isheader() or pounit.hasplural()):  # XXX
                if pounit.hasmarkedcomment("poconflicts"):
                    for comment in pounit.othercomments:
                        if comment.find("# (poconflicts)") == 0:
                            pounit.othercomments.remove(comment)
                            break
                    # TODO: refactor writing out
                    outputpath = comment[comment.find(")") + 2 :].strip()
                    self.checkoutputsubdir(options, os.path.dirname(outputpath))
                    fulloutputpath = os.path.join(options.output, outputpath)
                    if os.path.isfile(fulloutputpath):
                        outputfile = open(fulloutputpath, "rb")
                        outputpofile = po.pofile(outputfile)
                    else:
                        outputpofile = po.pofile()
                    outputpofile.units.append(
                        pounit
                    )  # TODO:perhaps check to see if it's already there...
                    with open(fulloutputpath, "wb") as fh:
                        outputpofile.serialize(fh)


def main():
    # outputfile extentions will actually be determined by the comments in the
    # po files
    pooutput = ("po", None)
    formats = {(None, None): pooutput, ("po", "po"): pooutput, "po": pooutput}
    parser = SplitOptionParser(formats, description=__doc__)
    parser.set_usage()
    parser.run()


if __name__ == "__main__":
    main()
