from pontoon.sync.vcs.translation import VCSTranslation


class ParsedResource:
    """
    Parent class for parsed resources as returned by parse.

    Each supported format parser should return an instance of a class
    that inherits from this class.
    """

    entities: dict[str, VCSTranslation]

    @property
    def translations(self) -> list[VCSTranslation]:
        """
        Return a list of VCSTranslation instances or subclasses that
        represent the translations in the resource.
        """
        raise NotImplementedError()
