class ParsedResource:
    """
    Parent class for parsed resources as returned by parse.

    Each supported format parser should return an instance of a class
    that inherits from this class.
    """

    @property
    def translations(self):
        """
        Return a list of VCSTranslation instances or subclasses that
        represent the translations in the resource.
        """
        raise NotImplementedError()

    def save(self, locale):
        """
        Save any changes made to the VCSTranslation objects from
        self.translations back to the originally parsed resource file.

        :param Locale locale:
            Locale of the file being saved.
        """
        raise NotImplementedError()
