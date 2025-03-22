from os.path import dirname

from pipeline.compilers import SubProcessCompiler
from pipeline.conf import settings


class SASSCompiler(SubProcessCompiler):
    output_extension = "css"

    def match_file(self, filename):
        return filename.endswith((".scss", ".sass"))

    def compile_file(self, infile, outfile, outdated=False, force=False):
        command = (settings.SASS_BINARY, settings.SASS_ARGUMENTS, infile, outfile)
        return self.execute_command(command, cwd=dirname(infile))
