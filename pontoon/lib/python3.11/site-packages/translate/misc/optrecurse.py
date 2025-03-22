#
# Copyright 2002-2006 Zuza Software Foundation
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

import fnmatch
import logging
import optparse
import os.path
import re
import sys
import traceback
from io import BytesIO

from translate import __version__
from translate.misc import progressbar


class ProgressBar:
    progress_types = {
        "dots": progressbar.DotsProgressBar,
        "none": progressbar.NoProgressBar,
        "bar": progressbar.HashProgressBar,
        "names": progressbar.MessageProgressBar,
        "verbose": progressbar.VerboseProgressBar,
    }

    def __init__(self, progress_type, allfiles):
        """Set up a progress bar appropriate to the progress_type and files."""
        if progress_type in {"bar", "verbose"}:
            file_count = len(allfiles)
            self._progressbar = self.progress_types[progress_type](0, file_count)
            logger = logging.getLogger(os.path.basename(sys.argv[0])).getChild(
                "progress"
            )
            logger.setLevel(logging.INFO)
            logger.propagate = False
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter())
            logger.addHandler(handler)
            logger.info("processing %d files...", file_count)
        else:
            self._progressbar = self.progress_types[progress_type]()

    def report_progress(self, filename, success):
        """Show that we are progressing..."""
        self._progressbar.amount += 1
        self._progressbar.show(filename)


class ManPageOption(optparse.Option):
    ACTIONS = (*optparse.Option.ACTIONS, "manpage")

    def take_action(self, action, dest, opt, value, values, parser):
        """take_action that can handle manpage as well as standard actions."""
        if action == "manpage":
            parser.print_manpage()
            sys.exit(0)
        return super().take_action(action, dest, opt, value, values, parser)


class ManHelpFormatter(optparse.HelpFormatter):
    def __init__(
        self, indent_increment=0, max_help_position=0, width=80, short_first=1
    ):
        super().__init__(indent_increment, max_help_position, width, short_first)

    def format_option_strings(self, option):
        """Return a comma-separated list of option strings & metavariables."""
        if option.takes_value():
            metavar = option.metavar or option.dest.upper()
            metavar = f"\\fI{metavar}\\fP"
            short_opts = [sopt + metavar for sopt in option._short_opts]
            long_opts = [lopt + "\\fR=\\fP" + metavar for lopt in option._long_opts]
        else:
            short_opts = option._short_opts
            long_opts = option._long_opts

        opts = short_opts + long_opts if self.short_first else long_opts + short_opts

        return "\\fB{}\\fP".format("\\fR, \\fP".join(opts))


class StdoutWrapper:
    def __init__(self):
        self.out = sys.stdout

    def __getattr__(self, name):
        return getattr(self.out, name)

    def write(self, content):
        if isinstance(content, bytes):
            try:
                self.out.write(content.decode("utf-8"))
            except UnicodeDecodeError:
                self.out.write("Unable to write binary content to the terminal")
        else:
            self.out.write(content)


class RecursiveOptionParser(optparse.OptionParser):
    """A specialized Option Parser for recursing through directories."""

    def __init__(
        self, formats, usetemplates=False, allowmissingtemplate=False, description=None
    ):
        """
        Construct the specialized Option Parser.

        :type formats: Dictionary
        :param formats: See :meth:`~.RecursiveOptionParser.setformats`
        for an explanation of the formats parameter.
        """
        super().__init__(version="%prog " + __version__.sver, description=description)
        self.setmanpageoption()
        self.setprogressoptions()
        self.seterrorleveloptions()
        self.setformats(formats, usetemplates)
        self.passthrough = []
        self.allowmissingtemplate = allowmissingtemplate
        logging.basicConfig(format="%(name)s: %(levelname)s: %(message)s")

    def get_prog_name(self):
        return os.path.basename(sys.argv[0])

    def setmanpageoption(self):
        """
        creates a manpage option that allows the optionparser to generate a
        manpage.
        """
        manpageoption = ManPageOption(
            None,
            "--manpage",
            dest="manpage",
            default=False,
            action="manpage",
            help="output a manpage based on the help",
        )
        self.define_option(manpageoption)

    def format_manpage(self):
        """Returns a formatted manpage."""
        result = []
        prog = self.get_prog_name()

        def formatprog(x):
            return x.replace("%prog", prog)

        def formatToolkit(x):
            return x.replace("%prog", "Translate Toolkit")

        result.extend(
            (
                '.\\" Autogenerated manpage\n',
                f'.TH {prog} 1 "{formatToolkit(self.version)}" "" "{formatToolkit(self.version)}"\n',
                ".SH NAME\n",
                "{} \\- {}\n".format(
                    self.get_prog_name(), self.description.split("\n\n")[0]
                ),
                ".SH SYNOPSIS\n",
                ".PP\n",
            )
        )
        usage = "\\fB%prog "
        usage += " ".join(self.getusageman(option) for option in self.option_list)
        usage += "\\fP"
        result.append(f"{formatprog(usage)}\n")
        description_lines = self.description.split("\n\n")[1:]
        if description_lines:
            result.extend(
                (
                    ".SH DESCRIPTION\n",
                    "\n\n".join(
                        re.sub("\\.\\. note::", "Note:", l) for l in description_lines
                    ),
                )
            )
        result.append(".SH OPTIONS\n")
        ManHelpFormatter().store_option_strings(self)
        result.append(".PP\n")
        for option in self.option_list:
            result.extend(
                (
                    ".TP\n",
                    "{}\n".format(str(option).replace("-", "\\-")),
                    "{}\n".format(option.help.replace("-", "\\-")),
                )
            )
        return "".join(result)

    def print_manpage(self, file=None):
        """Outputs a manpage for the program using the help information."""
        if file is None:
            file = sys.stdout
        file.write(self.format_manpage())

    def set_usage(self, usage=None):
        """
        sets the usage string - if usage not given, uses getusagestring for
        each option.
        """
        if usage is None:
            self.usage = "%prog " + " ".join(
                self.getusagestring(option) for option in self.option_list
            )
        else:
            super().set_usage(usage)

    def warning(self, msg, options=None, exc_info=None):
        """Print a warning message incorporating 'msg' to stderr."""
        if options:
            if options.errorlevel == "traceback":
                errorinfo = "\n".join(
                    traceback.format_exception(exc_info[0], exc_info[1], exc_info[2])
                )
            elif options.errorlevel == "exception":
                errorinfo = "\n".join(
                    traceback.format_exception_only(exc_info[0], exc_info[1])
                )
            elif options.errorlevel == "message":
                errorinfo = str(exc_info[1])
            else:
                errorinfo = ""
            if errorinfo:
                msg += ": " + errorinfo
        logging.getLogger(self.get_prog_name()).warning(msg)

    @staticmethod
    def getusagestring(option):
        """Returns the usage string for the given option."""
        optionstring = "|".join(option._short_opts + option._long_opts)
        if getattr(option, "optionalswitch", False):
            optionstring = f"[{optionstring}]"
        if option.metavar:
            optionstring += " " + option.metavar
        if getattr(option, "required", False):
            return optionstring
        return f"[{optionstring}]"

    @staticmethod
    def getusageman(option):
        """Returns the usage string for the given option."""
        optionstring = "\\fR|\\fP".join(option._short_opts + option._long_opts)
        if getattr(option, "optionalswitch", False):
            optionstring = f"\\fR[\\fP{optionstring}\\fR]\\fP"
        if option.metavar:
            optionstring += f" \\fI{option.metavar}\\fP"
        if getattr(option, "required", False):
            return optionstring
        return f"\\fR[\\fP{optionstring}\\fR]\\fP"

    def define_option(self, option):
        """
        Defines the given option, replacing an existing one of the same
        short name if neccessary...
        """
        for short_opt in option._short_opts:
            if self.has_option(short_opt):
                self.remove_option(short_opt)
        for long_opt in option._long_opts:
            if self.has_option(long_opt):
                self.remove_option(long_opt)
        self.add_option(option)

    def setformats(self, formats, usetemplates):
        """
        Sets the format options using the given format dictionary.

        :type formats: Dictionary or iterable
        :param formats: The dictionary *keys* should be:

                        - Single strings (or 1-tuples) containing an
                          input format (if not *usetemplates*)
                        - Tuples containing an input format and
                          template format (if *usetemplates*)
                        - Formats can be *None* to indicate what to do
                          with standard input

                        The dictionary *values* should be tuples of
                        outputformat (string) and processor method.
        """
        self.inputformats = []
        outputformats = []
        templateformats = []
        self.outputoptions = {}
        self.usetemplates = usetemplates
        if isinstance(formats, dict):
            formats = formats.items()
        for formatgroup, outputoptions in formats:
            if isinstance(formatgroup, str) or formatgroup is None:
                formatgroup = (formatgroup,)
            if not isinstance(formatgroup, tuple):
                raise TypeError("formatgroups must be tuples or None/str/unicode")
            if len(formatgroup) < 1 or len(formatgroup) > 2:
                raise ValueError("formatgroups must be tuples of length 1 or 2")
            if len(formatgroup) == 1:
                formatgroup += (None,)
            inputformat, templateformat = formatgroup
            if not isinstance(outputoptions, tuple) or len(outputoptions) != 2:
                raise ValueError("output options must be tuples of length 2")
            outputformat, processor = outputoptions
            if inputformat not in self.inputformats:
                self.inputformats.append(inputformat)
            if outputformat not in outputformats:
                outputformats.append(outputformat)
            if templateformat not in templateformats:
                templateformats.append(templateformat)
            self.outputoptions[inputformat, templateformat] = (
                outputformat,
                processor,
            )
        inputformathelp = self.getformathelp(self.inputformats)
        inputoption = optparse.Option(
            "-i",
            "--input",
            dest="input",
            default=None,
            metavar="INPUT",
            help=f"read from INPUT in {inputformathelp}",
        )
        inputoption.optionalswitch = True
        inputoption.required = True
        self.define_option(inputoption)
        excludeoption = optparse.Option(
            "-x",
            "--exclude",
            dest="exclude",
            action="append",
            type="string",
            metavar="EXCLUDE",
            default=["CVS", ".svn", "_darcs", ".git", ".hg", ".bzr"],
            help="exclude names matching EXCLUDE from input paths",
        )
        self.define_option(excludeoption)
        outputformathelp = self.getformathelp(outputformats)
        outputoption = optparse.Option(
            "-o",
            "--output",
            dest="output",
            default=None,
            metavar="OUTPUT",
            help=f"write to OUTPUT in {outputformathelp}",
        )
        outputoption.optionalswitch = True
        outputoption.required = True
        self.define_option(outputoption)
        if self.usetemplates:
            self.templateformats = templateformats
            templateformathelp = self.getformathelp(self.templateformats)
            templateoption = optparse.Option(
                "-t",
                "--template",
                dest="template",
                default=None,
                metavar="TEMPLATE",
                help=f"read from TEMPLATE in {templateformathelp}",
            )
            self.define_option(templateoption)

    def setprogressoptions(self):
        """Sets the progress options."""
        progressoption = optparse.Option(
            None,
            "--progress",
            dest="progress",
            default="bar",
            choices=list(ProgressBar.progress_types.keys()),
            metavar="PROGRESS",
            help="show progress as: {}".format(", ".join(ProgressBar.progress_types)),
        )
        self.define_option(progressoption)

    def seterrorleveloptions(self):
        """Sets the errorlevel options."""
        self.errorleveltypes = ["none", "message", "exception", "traceback"]
        errorleveloption = optparse.Option(
            None,
            "--errorlevel",
            dest="errorlevel",
            default="message",
            choices=self.errorleveltypes,
            metavar="ERRORLEVEL",
            help="show errorlevel as: {}".format(", ".join(self.errorleveltypes)),
        )
        self.define_option(errorleveloption)

    @staticmethod
    def getformathelp(formats):
        """Make a nice help string for describing formats..."""
        formats = sorted(f for f in formats if f is not None)
        if len(formats) == 0:
            return ""
        if len(formats) == 1:
            return "{} format".format(", ".join(formats))
        return "{} formats".format(", ".join(formats))

    @staticmethod
    def isrecursive(fileoption, filepurpose="input"):
        """Checks if fileoption is a recursive file."""
        if fileoption is None:
            return False
        if isinstance(fileoption, list):
            return True
        return os.path.isdir(fileoption)

    def parse_args(self, args=None, values=None):
        """
        Parses the command line options, handling implicit input/output
        args.
        """
        (options, args) = super().parse_args(args, values)
        # some intelligent as to what reasonable people might give on the
        # command line
        if args and not options.input:
            if len(args) > 1:
                options.input = args[:-1]
                args = args[-1:]
            else:
                options.input = args[0]
                args = []
        if args and not options.output:
            options.output = args[-1]
            args = args[:-1]
        if args:
            self.error(
                "You have used an invalid combination of --input, --output and freestanding args"
            )
        if isinstance(options.input, list) and len(options.input) == 1:
            options.input = options.input[0]
        if options.input is None:
            self.error(
                "You need to give an inputfile or use - for stdin ; use --help for full usage instructions"
            )
        elif options.input == "-":
            options.input = None
        return (options, args)

    def getpassthroughoptions(self, options):
        """Get the options required to pass to the filtermethod..."""
        passthroughoptions = {}
        for optionname in dir(options):
            if optionname in self.passthrough:
                passthroughoptions[optionname] = getattr(options, optionname)
        return passthroughoptions

    def getoutputoptions(self, options, inputpath, templatepath):
        """Works out which output format and processor method to use..."""
        if inputpath:
            inputbase, inputext = self.splitinputext(inputpath)
        else:
            inputext = None
        if templatepath:
            templatebase, templateext = self.splittemplateext(templatepath)
        else:
            templateext = None
        if (inputext, templateext) in self.outputoptions:
            return self.outputoptions[inputext, templateext]
        if (inputext, "*") in self.outputoptions:
            outputformat, fileprocessor = self.outputoptions[inputext, "*"]
        elif ("*", templateext) in self.outputoptions:
            outputformat, fileprocessor = self.outputoptions["*", templateext]
        elif ("*", "*") in self.outputoptions:
            outputformat, fileprocessor = self.outputoptions["*", "*"]
        elif (inputext, None) in self.outputoptions:
            return self.outputoptions[inputext, None]
        elif (None, templateext) in self.outputoptions:
            return self.outputoptions[None, templateext]
        elif ("*", None) in self.outputoptions:
            outputformat, fileprocessor = self.outputoptions["*", None]
        elif (None, "*") in self.outputoptions:
            outputformat, fileprocessor = self.outputoptions[None, "*"]
        else:
            if self.usetemplates:
                if inputext is None:
                    raise ValueError(
                        "don't know what to do with input format (no file extension), no template file"
                    )
                if templateext is None:
                    raise ValueError(
                        "don't know what to do with input format %s, no template file"
                        % (os.extsep + inputext)
                    )
                raise ValueError(
                    f"don't know what to do with input format {os.extsep + inputext}, template format {os.extsep + templateext}"
                )
            raise ValueError(
                "don't know what to do with input format %s" % (os.extsep + inputext)
            )
        if outputformat == "*":
            if inputext:
                outputformat = inputext
            elif templateext:
                outputformat = templateext
            elif ("*", "*") in self.outputoptions:
                outputformat = None
            else:
                if self.usetemplates:
                    raise ValueError(
                        "don't know what to do with input format (no file extension), no template file"
                    )
                raise ValueError(
                    "don't know what to do with input format (no file extension)"
                )
        return outputformat, fileprocessor

    @staticmethod
    def getfullinputpath(options, inputpath):
        """Gets the full path to an input file."""
        if options.input:
            return os.path.join(options.input, inputpath)
        return inputpath

    @staticmethod
    def getfulloutputpath(options, outputpath):
        """Gets the full path to an output file."""
        if options.recursiveoutput and options.output:
            return os.path.join(options.output, outputpath)
        return outputpath

    def getfulltemplatepath(self, options, templatepath):
        """Gets the full path to a template file."""
        if not options.recursivetemplate:
            return templatepath
        if templatepath is not None and self.usetemplates and options.template:
            return os.path.join(options.template, templatepath)
        return None

    def run(self):
        """
        Parses the arguments, and runs recursiveprocess with the resulting
        options...
        """
        (options, args) = self.parse_args()
        self.recursiveprocess(options)

    def recursiveprocess(self, options):
        """Recurse through directories and process files."""
        if self.isrecursive(options.input, "input") and getattr(
            options, "allowrecursiveinput", True
        ):
            self.ensurerecursiveoutputdirexists(options)
            if isinstance(options.input, list):
                inputfiles = self.recurseinputfilelist(options)
            else:
                inputfiles = self.recurseinputfiles(options)
        elif options.input:
            inputfiles = [os.path.basename(options.input)]
            options.input = os.path.dirname(options.input)
        else:
            inputfiles = [options.input]
        options.recursiveoutput = self.isrecursive(
            options.output, "output"
        ) and getattr(options, "allowrecursiveoutput", True)
        options.recursivetemplate = (
            self.usetemplates
            and self.isrecursive(options.template, "template")
            and getattr(options, "allowrecursivetemplate", True)
        )
        # sort the input files to preserve the order between runs as much as possible.
        # this makes for more merge-friendly content in single-output-file mode.
        inputfiles.sort()
        progress_bar = ProgressBar(options.progress, inputfiles)
        for inputpath in inputfiles:
            try:
                templatepath = self.gettemplatename(options, inputpath)
                # If we have a recursive template, but the template doesn't
                # have this input file, let's drop it.
                if (
                    options.recursivetemplate
                    and templatepath is None
                    and not self.allowmissingtemplate
                ):
                    self.warning(
                        f"No template at {templatepath}. Skipping {inputpath}."
                    )
                    continue
                outputformat, fileprocessor = self.getoutputoptions(
                    options, inputpath, templatepath
                )
                fullinputpath = self.getfullinputpath(options, inputpath)
                fulltemplatepath = self.getfulltemplatepath(options, templatepath)
                outputpath = self.getoutputname(options, inputpath, outputformat)
                fulloutputpath = self.getfulloutputpath(options, outputpath)
                if options.recursiveoutput and outputpath:
                    self.checkoutputsubdir(options, os.path.dirname(outputpath))
            except Exception:
                self.warning(
                    f"Couldn't handle input file {inputpath}", options, sys.exc_info()
                )
                continue
            try:
                success = self.processfile(
                    fileprocessor,
                    options,
                    fullinputpath,
                    fulloutputpath,
                    fulltemplatepath,
                )
            except Exception:
                self.warning(
                    f"Error processing: input {fullinputpath}, output {fulloutputpath}, template {fulltemplatepath}",
                    options,
                    sys.exc_info(),
                )
                success = False
            progress_bar.report_progress(inputpath, success)

    def ensurerecursiveoutputdirexists(self, options):
        if not self.isrecursive(options.output, "output"):
            if not options.output:
                self.error(optparse.OptionValueError("No output directory given"))
            try:
                self.warning("Output directory does not exist. Attempting to create")
                os.mkdir(options.output)
            except OSError:
                self.error(
                    optparse.OptionValueError(
                        "Output directory does not exist, attempt to create failed"
                    )
                )

    @staticmethod
    def openinputfile(options, fullinputpath):
        """Opens the input file."""
        if fullinputpath is None:
            return sys.stdin
        return open(fullinputpath, "rb")

    @staticmethod
    def openoutputfile(options, fulloutputpath):
        """Opens the output file."""
        if fulloutputpath is None:
            return StdoutWrapper()
        return open(fulloutputpath, "wb")

    @staticmethod
    def opentempoutputfile(options, fulloutputpath):
        """Opens a temporary output file."""
        return BytesIO()

    def finalizetempoutputfile(self, options, outputfile, fulloutputpath):
        """Write the temp outputfile to its final destination."""
        outputfile.seek(0, 0)
        outputstring = outputfile.read()
        outputfile = self.openoutputfile(options, fulloutputpath)
        outputfile.write(outputstring)
        outputfile.close()

    def opentemplatefile(self, options, fulltemplatepath):
        """Opens the template file (if required)."""
        if fulltemplatepath is not None:
            if os.path.isfile(fulltemplatepath):
                return open(fulltemplatepath, "rb")
            self.warning(f"missing template file {fulltemplatepath}")
        return None

    def processfile(
        self, fileprocessor, options, fullinputpath, fulloutputpath, fulltemplatepath
    ):
        """Process an individual file."""
        inputfile = self.openinputfile(options, fullinputpath)
        if fulloutputpath and fulloutputpath in {fullinputpath, fulltemplatepath}:
            outputfile = self.opentempoutputfile(options, fulloutputpath)
            tempoutput = True
        else:
            outputfile = self.openoutputfile(options, fulloutputpath)
            tempoutput = False
        templatefile = self.opentemplatefile(options, fulltemplatepath)
        passthroughoptions = self.getpassthroughoptions(options)
        result = fileprocessor(
            inputfile, outputfile, templatefile, **passthroughoptions
        )
        if fullinputpath is not None:
            inputfile.close()
        if result:
            if tempoutput:
                self.warning("writing to temporary output...")
                self.finalizetempoutputfile(options, outputfile, fulloutputpath)
            if fulloutputpath and os.path.isfile(fulloutputpath):
                outputfile.close()
            return True
        # remove the file if it is a file (could be stdout etc)
        if fulloutputpath and os.path.isfile(fulloutputpath):
            outputfile.close()
            os.unlink(fulloutputpath)
        return False

    @staticmethod
    def mkdir(parent, subdir):
        """Makes a subdirectory (recursively if neccessary)."""
        if not os.path.isdir(parent):
            raise ValueError(
                f"cannot make child directory {subdir!r} if parent {parent!r} does not exist"
            )
        currentpath = parent
        subparts = subdir.split(os.sep)
        for part in subparts:
            currentpath = os.path.join(currentpath, part)
            if not os.path.isdir(currentpath):
                os.mkdir(currentpath)

    def checkoutputsubdir(self, options, subdir):
        """
        Checks to see if subdir under options.output needs to be created,
        creates if neccessary.
        """
        fullpath = os.path.join(options.output, subdir)
        if not os.path.isdir(fullpath):
            self.mkdir(options.output, subdir)

    @staticmethod
    def isexcluded(options, inputpath):
        """Checks if this path has been excluded."""
        basename = os.path.basename(inputpath)
        for excludename in options.exclude:
            if fnmatch.fnmatch(basename, excludename):
                return True
        return False

    def recurseinputfilelist(self, options):
        """Use a list of files, and find a common base directory for them."""
        # find a common base directory for the files to do everything
        # relative to
        commondir = os.path.dirname(os.path.commonprefix(options.input))
        inputfiles = []
        for inputfile in options.input:
            if self.isexcluded(options, inputfile):
                continue
            if inputfile.startswith(commondir + os.sep):
                inputfiles.append(inputfile.replace(commondir + os.sep, "", 1))
            else:
                inputfiles.append(inputfile.replace(commondir, "", 1))
        options.input = commondir
        return inputfiles

    def recurseinputfiles(self, options):
        """Recurse through directories and return files to be processed."""
        dirstack = [""]
        join = os.path.join
        inputfiles = []
        while dirstack:
            top = dirstack.pop(-1)
            names = os.listdir(join(options.input, top))
            dirs = []
            for name in names:
                inputpath = join(top, name)
                if self.isexcluded(options, inputpath):
                    continue
                fullinputpath = self.getfullinputpath(options, inputpath)
                # handle directories...
                if os.path.isdir(fullinputpath):
                    dirs.append(inputpath)
                elif os.path.isfile(fullinputpath):
                    if not self.isvalidinputname(name):
                        # only handle names that match recognized input
                        # file extensions
                        continue
                    inputfiles.append(inputpath)
            # make sure the directories are processed next time round.
            dirs.reverse()
            dirstack.extend(dirs)
        return inputfiles

    @staticmethod
    def splitext(pathname):
        """
        Splits *pathname* into name and ext, and removes the extsep.

        :param pathname: A file path
        :type pathname: string
        :return: root, ext
        :rtype: tuple
        """
        root, ext = os.path.splitext(pathname)
        ext = ext.replace(os.extsep, "", 1)
        return (root, ext)

    def splitinputext(self, inputpath):
        """Splits an *inputpath* into name and extension."""
        return self.splitext(inputpath)

    def splittemplateext(self, templatepath):
        """Splits a *templatepath* into name and extension."""
        return self.splitext(templatepath)

    def templateexists(self, options, templatepath):
        """Returns whether the given template exists..."""
        fulltemplatepath = self.getfulltemplatepath(options, templatepath)
        return os.path.isfile(fulltemplatepath)

    def gettemplatename(self, options, inputname):
        """Gets an output filename based on the input filename."""
        if not self.usetemplates:
            return None
        if not inputname or not options.recursivetemplate:
            return options.template
        inputbase, inputext = self.splitinputext(inputname)
        if options.template:
            for inputext1, templateext1 in self.outputoptions:
                if inputext == inputext1:
                    if templateext1:
                        templatepath = inputbase + os.extsep + templateext1
                        if self.templateexists(options, templatepath):
                            return templatepath
            if "*" in self.inputformats:
                for inputext1, templateext1 in self.outputoptions:
                    if inputext1 in {inputext, "*"}:
                        if templateext1 == "*":
                            templatepath = inputname
                            if self.templateexists(options, templatepath):
                                return templatepath
                        elif templateext1:
                            templatepath = inputbase + os.extsep + templateext1
                            if self.templateexists(options, templatepath):
                                return templatepath
        return None

    def getoutputname(self, options, inputname, outputformat):
        """Gets an output filename based on the input filename."""
        if not inputname or not options.recursiveoutput:
            return options.output
        inputbase, inputext = self.splitinputext(inputname)
        outputname = inputbase
        if outputformat:
            outputname += os.extsep + outputformat
        return outputname

    def isvalidinputname(self, inputname):
        """Checks if this is a valid input filename."""
        inputbase, inputext = self.splitinputext(inputname)
        return (inputext in self.inputformats) or ("*" in self.inputformats)
