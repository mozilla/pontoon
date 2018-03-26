
import math


class TagChart(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.approved_strings = kwargs.get('approved_strings')
        self.fuzzy_strings = kwargs.get('fuzzy_strings')
        self.total_strings = kwargs.get('total_strings')
        self.translated_strings = kwargs.get('translated_strings')

    @property
    def approved_percent(self):
        return int(
            math.floor(
                self.approved_strings
                / float(self.total_strings) * 100))

    @property
    def approved_share(self):
        return self._share(self.approved_strings)

    @property
    def fuzzy_share(self):
        return self._share(self.fuzzy_strings)

    @property
    def translated_share(self):
        return self._share(self.translated_strings)

    def _share(self, item):
        return round(item / float(self.total_strings) * 100) or 0
