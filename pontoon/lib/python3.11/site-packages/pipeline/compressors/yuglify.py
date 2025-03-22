from pipeline.compressors import SubProcessCompressor
from pipeline.conf import settings


class YuglifyCompressor(SubProcessCompressor):
    def compress_common(self, content, compress_type, arguments):
        command = (settings.YUGLIFY_BINARY, f"--type={compress_type}", arguments)
        return self.execute_command(command, content)

    def compress_js(self, js):
        return self.compress_common(js, "js", settings.YUGLIFY_JS_ARGUMENTS)

    def compress_css(self, css):
        return self.compress_common(css, "css", settings.YUGLIFY_CSS_ARGUMENTS)
