class ParseError(RuntimeError):
    """Exception to raise when parsing fails."""


class VCSTranslation:
    """
    A single translation of a source string into another language.

    Since a string can have different translations based on plural
    forms, all of the different forms are stored under self.strings, a
    dict where the keys equal possible values for
    pontoon.base.models.Translation.plural_form and the values equal the
    translation for that plural form.
    """

    def __init__(
        self,
        *,
        key: str,
        context: str,
        order: int,
        strings: dict[str | None, str],
        source_string: str = "",
        source_string_plural: str = "",
        comments: list[str] | None = None,
        group_comments: list[str] | None = None,
        resource_comments: list[str] | None = None,
        fuzzy: bool = False,
        source=None,
    ):
        self.key = key
        self.context = context
        self.order = order
        self.strings = strings
        self.source_string = source_string
        self.source_string_plural = source_string_plural
        self.comments = comments or []
        self.group_comments = group_comments
        self.resource_comments = resource_comments
        self.fuzzy = fuzzy
        self.source = source or []

    def __repr__(self):
        return f"<VCSTranslation {self.key}>"
