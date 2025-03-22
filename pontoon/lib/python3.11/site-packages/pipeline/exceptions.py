class PipelineException(Exception):
    pass


class PackageNotFound(PipelineException):
    pass


class CompilerError(PipelineException):
    def __init__(self, msg, command=None, error_output=None):
        super().__init__(msg)

        self.command = command
        self.error_output = error_output.strip()


class CompressorError(PipelineException):
    pass
