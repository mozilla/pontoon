from django.core.files import temp as tempfile

from pipeline.compressors import SubProcessCompressor
from pipeline.conf import settings


class CSSTidyCompressor(SubProcessCompressor):
    def compress_css(self, css):
        output_file = tempfile.NamedTemporaryFile(suffix=".pipeline")

        command = (
            settings.CSSTIDY_BINARY,
            "-",
            settings.CSSTIDY_ARGUMENTS,
            output_file.name,
        )
        self.execute_command(command, css)

        filtered_css = output_file.read()
        output_file.close()
        return filtered_css
