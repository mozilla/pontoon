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
Handles converting of files between formats (used by
:mod:`translate.convert` tools).
"""

import os.path
from io import BytesIO

from translate.misc import optrecurse

# Don't import optparse ourselves, get the version from optrecurse.
optparse = optrecurse.optparse


class ConvertOptionParser(optrecurse.RecursiveOptionParser):
    """A specialized Option Parser for convertor tools..."""

    def __init__(
        self,
        formats,
        usetemplates=False,
        usepots=False,
        allowmissingtemplate=False,
        description=None,
    ):
        """Construct the specialized Option Parser."""
        super().__init__(
            formats,
            usetemplates,
            allowmissingtemplate=allowmissingtemplate,
            description=description,
        )
        self.usepots = usepots
        self.settimestampoption()
        self.setpotoption()
        self.set_usage()

    def add_fuzzy_option(self, default=False):
        """Adds an option to include / exclude fuzzy translations."""
        fuzzyhelp = "use translations marked fuzzy"
        nofuzzyhelp = "don't use translations marked fuzzy"
        if default:
            fuzzyhelp += " (default)"
        else:
            nofuzzyhelp += " (default)"
        self.add_option(
            "",
            "--fuzzy",
            dest="includefuzzy",
            action="store_true",
            default=default,
            help=fuzzyhelp,
        )
        self.add_option(
            "",
            "--nofuzzy",
            dest="includefuzzy",
            action="store_false",
            default=default,
            help=nofuzzyhelp,
        )
        self.passthrough.append("includefuzzy")

    def add_remove_untranslated_option(self, default=False):
        """
        Adds an option to remove key value from output if it is
        untranslated.
        """
        self.add_option(
            "",
            "--removeuntranslated",
            dest="remove_untranslated",
            default=False,
            action="store_true",
            help="remove untranslated strings from output",
        )
        self.passthrough.append("remove_untranslated")

    def add_threshold_option(self, default=None):
        """
        Adds an option to output only stores where translation percentage
        exceeds the threshold.
        """
        self.add_option(
            "",
            "--threshold",
            dest="outputthreshold",
            default=default,
            metavar="PERCENT",
            type="int",
            help="only convert files where the translation completion is above PERCENT",
        )
        self.passthrough.append("outputthreshold")

    def add_duplicates_option(self, default="msgctxt"):
        """Adds an option to say what to do with duplicate strings."""
        self.add_option(
            "",
            "--duplicates",
            dest="duplicatestyle",
            default=default,
            type="choice",
            choices=["msgctxt", "merge"],
            help=f"what to do with duplicate strings (identical source text): merge, msgctxt (default: '{default}')",
            metavar="DUPLICATESTYLE",
        )
        self.passthrough.append("duplicatestyle")

    def add_multifile_option(self, default="single"):
        """Adds an option to say how to split the po/pot files."""
        self.add_option(
            "",
            "--multifile",
            dest="multifilestyle",
            default=default,
            type="choice",
            choices=["single", "toplevel", "onefile"],
            help="how to split po/pot files (single, toplevel or onefile)",
            metavar="MULTIFILESTYLE",
        )
        self.passthrough.append("multifilestyle")

    @staticmethod
    def potifyformat(fileformat):
        """Converts a .po to a .pot where required."""
        if fileformat is None:
            return fileformat
        if fileformat == "po":
            return "pot"
        if fileformat.endswith(os.extsep + "po"):
            return fileformat + "t"
        return fileformat

    def getformathelp(self, formats):
        """Make a nice help string for describing formats..."""
        # include implicit pot options...
        helpformats = []
        for fileformat in formats:
            helpformats.append(fileformat)
            potformat = self.potifyformat(fileformat)
            if potformat != fileformat:
                helpformats.append(potformat)
        return super().getformathelp(helpformats)

    def filterinputformats(self, options):
        """Filters input formats, processing relevant switches in options."""
        if self.usepots and options.pot:
            return [self.potifyformat(inputformat) for inputformat in self.inputformats]
        return self.inputformats

    def filteroutputoptions(self, options):
        """Filters output options, processing relevant switches in options."""
        if self.usepots and options.pot:
            outputoptions = {}
            for (inputformat, templateformat), (
                outputformat,
                convertor,
            ) in self.outputoptions.items():
                inputformat = self.potifyformat(inputformat)
                templateformat = self.potifyformat(templateformat)
                outputformat = self.potifyformat(outputformat)
                outputoptions[inputformat, templateformat] = (outputformat, convertor)
            return outputoptions
        return self.outputoptions

    def setpotoption(self):
        """
        Sets the ``-P``/``--pot`` option depending on input/output formats
        etc.
        """
        if self.usepots:
            potoption = optparse.Option(
                "-P",
                "--pot",
                action="store_true",
                dest="pot",
                default=False,
                help="output PO Templates (.pot) rather than PO files (.po)",
            )
            self.define_option(potoption)

    def settimestampoption(self):
        """Sets ``-S``/``--timestamp`` option."""
        timestampopt = optparse.Option(
            "-S",
            "--timestamp",
            action="store_true",
            dest="timestamp",
            default=False,
            help="skip conversion if the output file has newer timestamp",
        )
        self.define_option(timestampopt)

    def verifyoptions(self, options):
        """
        Verifies that the options are valid (required options are present,
        etc).
        """

    def run(self, argv=None):
        """Parses the command line options and runs the conversion."""
        (options, args) = self.parse_args(argv)
        self.inputformats = self.filterinputformats(options)
        self.outputoptions = self.filteroutputoptions(options)
        try:
            self.verifyoptions(options)
        except Exception as e:
            self.error(str(e))
        self.recursiveprocess(options)

    def processfile(
        self, fileprocessor, options, fullinputpath, fulloutputpath, fulltemplatepath
    ):
        if options.timestamp and _output_is_newer(fullinputpath, fulloutputpath):
            return False

        return super().processfile(
            fileprocessor, options, fullinputpath, fulloutputpath, fulltemplatepath
        )


def copyinput(inputfile, outputfile, templatefile, **kwargs):
    """Copies the input file to the output file."""
    outputfile.write(inputfile.read())
    return True


def copytemplate(inputfile, outputfile, templatefile, **kwargs):
    """Copies the template file to the output file."""
    outputfile.write(templatefile.read())
    return True


class Replacer:
    """An object that knows how to replace strings in files."""

    def __init__(self, searchstring, replacestring):
        self.searchstring = searchstring
        self.replacestring = replacestring

    def doreplace(self, text):
        """Actually replace the text."""
        if self.searchstring is not None and self.replacestring is not None:
            return text.replace(self.searchstring, self.replacestring)
        return text

    def searchreplaceinput(self, inputfile, outputfile, templatefile, **kwargs):
        """Copies the input file to the output file, searching and replacing."""
        outputfile.write(self.doreplace(inputfile.read()))
        return True

    def searchreplacetemplate(self, inputfile, outputfile, templatefile, **kwargs):
        """
        Copies the template file to the output file, searching and
        replacing.
        """
        outputfile.write(self.doreplace(templatefile.read()))
        return True


# archive files need to know how to:
# - openarchive: creates an archive object for the archivefilename
#   * requires a constructor that takes the filename
# - iterarchivefile: iterate through the names in the archivefile
#   * requires the default iterator to do this
# - archivefileexists: check if a given pathname exists inside the archivefile
#   * uses the in operator - requires __contains__ (or will use __iter__
#     by default)
# - openarchiveinputfile: returns an open input file from the archive, given
#   the path
#   * requires an archivefile.openinputfile method that takes the pathname
# - openarchiveoutputfile: returns an open output file from the archive, given
#   the path
#   * requires an archivefile.openoutputfile method that takes the pathname


class ArchiveConvertOptionParser(ConvertOptionParser):
    """
    ConvertOptionParser that can handle recursing into single archive files.

    ``archiveformats`` maps extension to class. If the extension doesn't
    matter, it can be None.

    If the extension is only valid for input/output/template, it can be given
    as ``(extension, filepurpose)``.
    """

    def __init__(
        self,
        formats,
        usetemplates=False,
        usepots=False,
        description=None,
        archiveformats=None,
    ):
        if archiveformats is None:
            self.archiveformats = {}
        else:
            self.archiveformats = archiveformats
        self.archiveoptions = {}
        super().__init__(formats, usetemplates, usepots, description=description)

    def isrecursive(self, fileoption, filepurpose="input"):
        """Checks if **fileoption** is a recursive file."""
        if self.isarchive(fileoption, filepurpose):
            return True
        return super().isrecursive(fileoption, filepurpose)

    def isarchive(self, fileoption, filepurpose="input"):
        """Returns whether the file option is an archive file."""
        if not isinstance(fileoption, str):
            return False
        mustexist = filepurpose != "output"
        if mustexist and not os.path.isfile(fileoption):
            return False
        fileext = self.splitext(fileoption)[1]
        # if None is in the archive formats, then treat all non-directory
        # inputs as archives
        return (
            self.getarchiveclass(fileext, filepurpose, os.path.isdir(fileoption))
            is not None
        )

    def getarchiveclass(self, fileext, filepurpose, isdir=False):
        """Returns the archiveclass for the given fileext and filepurpose."""
        archiveclass = self.archiveformats.get(fileext, None)
        if archiveclass is not None:
            return archiveclass
        archiveclass = self.archiveformats.get((fileext, filepurpose), None)
        if archiveclass is not None:
            return archiveclass
        if not isdir:
            archiveclass = self.archiveformats.get(None, None)
            if archiveclass is not None:
                return archiveclass
            archiveclass = self.archiveformats.get((None, filepurpose), None)
            if archiveclass is not None:
                return archiveclass
        return None

    def openarchive(self, archivefilename, filepurpose, **kwargs):
        """Creates an archive object for the given file."""
        archiveext = self.splitext(archivefilename)[1]
        archiveclass = self.getarchiveclass(
            archiveext, filepurpose, os.path.isdir(archivefilename)
        )
        archiveoptions = self.archiveoptions.copy()
        archiveoptions.update(kwargs)
        return archiveclass(archivefilename, **archiveoptions)

    def recurseinputfiles(self, options):
        """
        Recurse through archive file / directories and return files to be
        converted.
        """
        if self.isarchive(options.input, "input"):
            options.inputarchive = self.openarchive(options.input, "input")
            return self.recursearchivefiles(options)
        return super().recurseinputfiles(options)

    def recursearchivefiles(self, options):
        """Recurse through archive files and convert files."""
        inputfiles = []
        for inputpath in options.inputarchive:
            if self.isexcluded(options, inputpath):
                continue
            top, name = os.path.split(inputpath)
            if not self.isvalidinputname(name):
                continue
            inputfiles.append(inputpath)
        return inputfiles

    def openinputfile(self, options, fullinputpath):
        """Opens the input file."""
        if self.isarchive(options.input, "input"):
            return options.inputarchive.openinputfile(fullinputpath)
        return super().openinputfile(options, fullinputpath)

    def getfullinputpath(self, options, inputpath):
        """Gets the absolute path to an input file."""
        if self.isarchive(options.input, "input"):
            return inputpath
        return os.path.join(options.input, inputpath)

    def opentemplatefile(self, options, fulltemplatepath):
        """Opens the template file (if required)."""
        if fulltemplatepath is not None:
            if options.recursivetemplate and self.isarchive(
                options.template, "template"
            ):
                # TODO: deal with different names in input/template archives
                if fulltemplatepath in self.templatearchive:
                    return self.templatearchive.openinputfile(fulltemplatepath)
                self.warning(f"missing template file {fulltemplatepath}")
        return super().opentemplatefile(options, fulltemplatepath)

    def getfulltemplatepath(self, options, templatepath):
        """Gets the absolute path to a template file."""
        if templatepath is not None and self.usetemplates and options.template:
            if self.isarchive(options.template, "template"):
                return templatepath
            if not options.recursivetemplate:
                return templatepath
            return os.path.join(options.template, templatepath)
        return None

    def templateexists(self, options, templatepath):
        """Returns whether the given template exists..."""
        if templatepath is not None and self.isarchive(options.template, "template"):
            # TODO: deal with different names in input/template archives
            return templatepath in self.templatearchive
        return super().templateexists(options, templatepath)

    def getfulloutputpath(self, options, outputpath):
        """Gets the absolute path to an output file."""
        if self.isarchive(options.output, "output"):
            return outputpath
        if options.recursiveoutput and options.output:
            return os.path.join(options.output, outputpath)
        return outputpath

    def checkoutputsubdir(self, options, subdir):
        """
        Checks to see if subdir under ``options.output`` needs to be
        created, creates if neccessary.
        """
        if not self.isarchive(options.output, "output"):
            super().checkoutputsubdir(options, subdir)

    def openoutputfile(self, options, fulloutputpath):
        """Opens the output file."""
        if self.isarchive(options.output, "output"):
            outputstream = self.outputarchive.openoutputfile(fulloutputpath)
            if outputstream is None:
                self.warning(
                    f"Could not find where to put {fulloutputpath} in output "
                    "archive; writing to tmp"
                )
                return BytesIO()
            return outputstream
        return super().openoutputfile(options, fulloutputpath)

    def recursiveprocess(self, options):
        """Recurse through directories and convert files."""
        if hasattr(options, "multifilestyle"):
            self.archiveoptions = {"multifilestyle": options.multifilestyle}
            for filetype in ("input", "output", "template"):
                allowoption = f"allowrecursive{filetype}"
                if options.multifilestyle == "onefile" and getattr(
                    options, allowoption, True
                ):
                    setattr(options, allowoption, False)

        if (
            self.usetemplates
            and options.template
            and self.isarchive(options.template, "template")
        ):
            self.templatearchive = self.openarchive(options.template, "template")

        if options.output and self.isarchive(options.output, "output"):
            self.outputarchive = self.openarchive(options.output, "output", mode="w")
        return super().recursiveprocess(options)

    def processfile(
        self, fileprocessor, options, fullinputpath, fulloutputpath, fulltemplatepath
    ):
        """Run an individual conversion."""
        if options.timestamp and _output_is_newer(fullinputpath, fulloutputpath):
            return False

        if self.isarchive(options.output, "output"):
            inputfile = self.openinputfile(options, fullinputpath)
            # TODO: handle writing back to same archive as input/template
            templatefile = self.opentemplatefile(options, fulltemplatepath)
            outputfile = self.openoutputfile(options, fulloutputpath)
            passthroughoptions = self.getpassthroughoptions(options)
            if fileprocessor(inputfile, outputfile, templatefile, **passthroughoptions):
                if not outputfile.isatty():
                    outputfile.close()
                return True
            if fulloutputpath and os.path.isfile(fulloutputpath):
                outputfile.close()
                os.unlink(fulloutputpath)
            return False
        return super().processfile(
            fileprocessor, options, fullinputpath, fulloutputpath, fulltemplatepath
        )


def _output_is_newer(input_path, output_path):
    """
    Check if input_path was not modified since output_path was generated,
    used to avoid needless regeneration of output.
    """
    if not input_path or not output_path:
        return False

    if not os.path.exists(input_path) or not os.path.exists(output_path):
        return False

    input_mtime = os.path.getmtime(input_path)
    output_mtime = os.path.getmtime(output_path)

    return output_mtime > input_mtime


def should_output_store(store, threshold):
    """
    Check if the percent of translated source words more than or equal to
    the given threshold.
    """
    if not threshold:
        return True

    from translate.tools import pocount

    units = [unit for unit in store.units if unit.istranslatable()]
    translated = [unit for unit in units if unit.istranslated()]
    wordcounts = {unit.getid(): pocount.wordsinunit(unit) for unit in units}

    def sourcewords(elementlist):
        return sum(wordcounts[unit.getid()][0] for unit in elementlist)

    translated_count = sourcewords(translated)
    total_count = sourcewords(units)
    percent = translated_count * 100 / total_count

    return percent >= threshold


def main(argv=None):
    parser = ArchiveConvertOptionParser({}, description=__doc__)
    parser.run(argv)
