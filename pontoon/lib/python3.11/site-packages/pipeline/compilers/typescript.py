from pipeline.compilers import SubProcessCompiler
from pipeline.conf import settings


class TypeScriptCompiler(SubProcessCompiler):
    output_extension = "js"

    def match_file(self, path):
        return path.endswith(".ts")

    def compile_file(self, infile, outfile, outdated=False, force=False):
        if not outdated and not force:
            return
        command = (
            settings.TYPE_SCRIPT_BINARY,
            settings.TYPE_SCRIPT_ARGUMENTS,
            infile,
            "--outFile",
            outfile,
        )
        return self.execute_command(command)
