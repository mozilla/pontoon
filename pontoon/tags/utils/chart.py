import math


class TagChart(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.approved_strings = kwargs.get("approved_strings")
        self.fuzzy_strings = kwargs.get("fuzzy_strings")
        self.strings_with_warnings = kwargs.get("strings_with_warnings")
        self.strings_with_errors = kwargs.get("strings_with_errors")
        self.total_strings = kwargs.get("total_strings")
        self.unreviewed_strings = kwargs.get("unreviewed_strings")

    @property
    def completion_percent(self):
        return int(
            math.floor(
                (self.approved_strings + self.strings_with_warnings)
                / float(self.total_strings)
                * 100
            )
        )

    @property
    def approved_share(self):
        return self._share(self.approved_strings)

    @property
    def fuzzy_share(self):
        return self._share(self.fuzzy_strings)

    @property
    def warnings_share(self):
        return self._share(self.strings_with_warnings)

    @property
    def errors_share(self):
        return self._share(self.strings_with_errors)

    @property
    def unreviewed_share(self):
        return self._share(self.unreviewed_strings)

    def _share(self, item):
        return round(item / float(self.total_strings) * 100) or 0
