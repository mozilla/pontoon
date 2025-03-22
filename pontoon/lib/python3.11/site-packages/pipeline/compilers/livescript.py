from pipeline.compilers import SubProcessCompiler
from pipeline.conf import settings


class LiveScriptCompiler(SubProcessCompiler):
    output_extension = "js"

    def match_file(self, path):
        return path.endswith(".ls")

    def compile_file(self, infile, outfile, outdated=False, force=False):
        if not outdated and not force:
            return  # File doesn't need to be recompiled
        command = (
            settings.LIVE_SCRIPT_BINARY,
            "-cp",
            settings.LIVE_SCRIPT_ARGUMENTS,
            infile,
        )
        return self.execute_command(command, stdout_captured=outfile)
