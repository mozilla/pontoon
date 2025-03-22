from pipeline.compressors import SubProcessCompressor
from pipeline.conf import settings


class CSSMinCompressor(SubProcessCompressor):
    def compress_css(self, css):
        command = (settings.CSSMIN_BINARY, settings.CSSMIN_ARGUMENTS)
        return self.execute_command(command, css)
