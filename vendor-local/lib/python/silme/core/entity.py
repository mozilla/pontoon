"""
silme.core.Entity represents single key:value pair (with possibility of having different values for different locale codes)
"""

class Entity(object):
    default_code = None

    def __init__(self, id, value=None, code='default'):
        """
        It is possible to initialize Entity only with id:
        Entity('id')
        
        or giving an initial value (and optionally locale_code):
        Entity('id', 'value'[, 'ab-CD'])
        """
        self.id = id
        self.params = {}
        if value is None:
            self._value = {}
        else:
            self.default_code = code
            self._value = {code: value}
            

    def __repr__(self):
        """Prints entity debug text representation."""
        if len(self._value) == 0:
            return '<entity: "%s">' % self.id
        elif len(self._value) == 1:
            if self.default_code == 'default':
                return '<entity: "%s", value: "%s">' % (self.id, self.get_value())
            else:
                return '<entity: "%s", value[%s]: "%s">' % \
                        (self.id, self.default_code, self.get_value())
        else:
            keys = self._value.keys()
            l = len(self.default_code)
            string = '<entity: "%s", value[%s]: "%s",\n' % \
                    (self.id, self.default_code, self.get_value())
            while len(keys):
                i = keys.pop()
                if not i == self.default_code:
                    string += ' '*(18 + len(self.id) + l - len(i)) + \
                            '[%s]: "%s"' % (i, self._value[i])
                    if len(keys):
                        string += ',\n'
                    else:
                        string += '>'
            return string

    def set_value(self, value, code=None):
        """Sets an entity value in given locale code.
        If not locale code is given, the default is 'default'."""
        # the code in this function is not the most pretty
        # but the fastest. This is a potential bottle neck and
        # we have to make sure its as fast as possible
        if code:
            if not self.default_code:
                self.default_code = code
            self._value[code] = value
        else:
            if not self.default_code:
                self.default_code = 'default'
                self._value['default'] = value
            else:
                self._value[self.default_code] = value

    def get_value(self, fallback=None):
        """Returns entity value.
        
        fallback options makes it possible to declare a list of
        optional codes to try in the order.
        If fallback is not declared default code is used.
        
        Raises KeyError in case no code will work."""
        try:
            return self._value[fallback]
        except:
            if not fallback:
                if not self._value:
                    return ''
                return self._value[self.default_code]
            else:
                for code in fallback:
                    try:
                        return self._value[code]
                    except:
                        pass
                raise KeyError()

    def remove_value(self, code=None):
        """Removes value from entity.
        
        It also clears default_code to first available or None.
        """
        if code:
            del self._value[code]
        else:
            del self._value[self.default_code]
        if not code or self.default_code == code:
            try:
                self.default_code = self._value.keys()[0]
            except:
                self.default_code = None

    value = property(get_value, set_value, remove_value)

    def __setitem__(self, code, value): self.set_value(value, code)
    __getitem__ = get_value
    __delitem__ = remove_value

    def get_value_with_code(self, fallback=None):
        """Returns entity value together with used locale_code
        in form of tuple (value, code).
        
        fallback options makes it possible to declare a list of
        optional codes to try in the order.
        If not fallback is declared default code is used.
        
        Raises KeyError in case no code will work."""
        try:
            return (self._value[fallback], fallback)
        except:
            if not fallback:
                return (self._value[self.default_code], self.default_code)
            else:
                for code in fallback:
                    try:
                        return (self._value[code], code)
                    except:
                        pass
                raise KeyError()

    def locale_codes(self):
        """Returns list of all locale codes available in this entity."""
        return self._value.keys()

    def locales(self, list):
        """Returns new Entity with locales filtered by
        list argument of locale codes."""
        entity = Entity(self.id)
        entity.params = self.params
        for (key, value) in self._value.items():
            if key in list:
                if not entity.default_code:
                    entity.default_code = key
                entity._value[key] = value
        return entity

    def merge(self, entity):
        """Merges entity with another by adding and
        overwriting all values from argument."""
        for (key, value) in entity._value.items():
            self.set_value(value, key)
