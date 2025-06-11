class ParseError(RuntimeError):
    """Exception to raise when parsing fails."""


class VCSTranslation:
    """
    A single translation of a source string into another language.
    """

    def __init__(
        self,
        *,
        key: str,
        context: str,
        order: int,
        string: str | None,
        source_string: str = "",
        comments: list[str] | None = None,
        group_comments: list[str] | None = None,
        resource_comments: list[str] | None = None,
        fuzzy: bool = False,
        source=None,
    ):
        self.key = key
        self.context = context
        self.order = order
        self.string = string
        self.source_string = source_string
        self.comments = comments or []
        self.group_comments = group_comments
        self.resource_comments = resource_comments
        self.fuzzy = fuzzy
        self.source = source or []

    def __repr__(self):
        return f"<VCSTranslation {self.key}>"
