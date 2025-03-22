from pipeline.compressors import SubProcessCompressor
from pipeline.conf import settings


class TerserCompressor(SubProcessCompressor):
    def compress_js(self, js):
        command = (settings.TERSER_BINARY, settings.TERSER_ARGUMENTS)
        if self.verbose:
            command += " --verbose"
        return self.execute_command(command, js)
