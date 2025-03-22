from os.path import dirname

from pipeline.compilers import SubProcessCompiler
from pipeline.conf import settings


class StylusCompiler(SubProcessCompiler):
    output_extension = "css"

    def match_file(self, filename):
        return filename.endswith(".styl")

    def compile_file(self, infile, outfile, outdated=False, force=False):
        command = (settings.STYLUS_BINARY, settings.STYLUS_ARGUMENTS, infile)
        return self.execute_command(command, cwd=dirname(infile))
