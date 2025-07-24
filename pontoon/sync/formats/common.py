from dataclasses import dataclass


@dataclass
class VCSTranslation:
    """
    A single translation of a source string into another language.
    """

    key: tuple[str, ...]
    string: str
    fuzzy: bool = False
