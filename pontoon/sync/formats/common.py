from dataclasses import dataclass

from moz.l10n.model import Message


@dataclass
class RepoTranslation:
    """
    A single translation of a source string into another language.
    """

    key: tuple[str, ...]
    string: str
    value: Message
    properties: dict[str, Message] | None = None
    fuzzy: bool = False
