from pipeline.compilers import SubProcessCompiler
from pipeline.conf import settings


class ES6Compiler(SubProcessCompiler):
    output_extension = "js"

    def match_file(self, path):
        return path.endswith(".es6")

    def compile_file(self, infile, outfile, outdated=False, force=False):
        if not outdated and not force:
            return  # File doesn't need to be recompiled
        command = (
            settings.BABEL_BINARY,
            settings.BABEL_ARGUMENTS,
            infile,
            "-o",
            outfile,
        )
        return self.execute_command(command)
