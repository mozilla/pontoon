from dataclasses import dataclass


@dataclass
class VCSTranslation:
    """
    A single translation of a source string into another language.
    """

    key: str
    string: str | None
    fuzzy: bool = False
