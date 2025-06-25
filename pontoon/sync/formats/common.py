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
        group_comment: str = "",
        resource_comment: str = "",
        fuzzy: bool = False,
        source=None,
    ):
        self.key = key
        self.context = context
        self.order = order
        self.string = string
        self.source_string = source_string
        self.comments = comments or []
        self.group_comment = group_comment
        self.resource_comment = resource_comment
        self.fuzzy = fuzzy
        self.source = source or []

    def __repr__(self):
        return f"<VCSTranslation {self.key}>"
