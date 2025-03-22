class MemcachedException(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code


class AuthenticationNotSupported(MemcachedException):
    pass


class InvalidCredentials(MemcachedException):
    pass
