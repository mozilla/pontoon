from ...core import Structure
from ...core.entity import _extract_value, CustomEntity

# codes = ['en', 'pl']

class GettextEntity(CustomEntity):
    #'translator','extracted', 'reference', 'flags', 'prev_id', 'prev_ctxt'

    def __init__(self, id, value=None, plural=None):
        self.id = id
        self._value = value
        self.params = {}
        self._plural_func = plural

    def _select_value(self, plural=None):
        if isinstance(self._value, list):
            if plural is None:
                return _extract_value(self._value)
            else:
                return self._value[self._plural_func(plural)]
        return self._value

    def __getitem__(self, key):
        if key==self._locales[1]:
            return self.value
        if key==self._locales[0]:
            return self.id
        raise KeyError()

class GettextStructure(Structure):
    pass
