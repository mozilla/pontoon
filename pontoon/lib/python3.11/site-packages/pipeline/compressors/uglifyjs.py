from pipeline.compressors import SubProcessCompressor
from pipeline.conf import settings


class UglifyJSCompressor(SubProcessCompressor):
    def compress_js(self, js):
        command = (settings.UGLIFYJS_BINARY, settings.UGLIFYJS_ARGUMENTS)
        if self.verbose:
            command += " --verbose"
        return self.execute_command(command, js)
