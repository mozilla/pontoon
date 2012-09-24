from ..core import Entity as L10nEntity, Structure

class LOL(Structure):
    def add(self, element):
        if element is not None:
            self.add_element(element)

    def add_element(self, element, pos=None):
        """
        overwrite silme.core.L10nObject.add_element
        """
        if element == None:
            return 0
        t = type(element).__name__[0]
        if t == 's' or t == 'u': # s - str, u - unicode
            return self.add_string(element, pos)
        elif t == 'E': # E - Entity
            return self.add_entity(element, pos)
        elif t == 'C': # C - Comment
            return self.add_comment(element, pos)
        else:
            self.append(element)

class WS():
    def __init__(self, content):
        self.content = content

class Group():
    def __init__(self):
        self.structure = []

    def add(self, entry):
        self.structure.append(entry)

class Entity(L10nEntity):
    def __init__(self, id, value=None):
        L10nEntity.__init__(self, id)
        self.kvplist = []
        if isinstance(value, unicode):
            self._value['default'] = String(value)
        else:
            self._value['default'] = None
    
    def get_value(self, fallback=None):
        return self._value[self.default_code]

class Comment():
    def __init__(self, content=None):
        self.content = content

class Expression():
    pass

class Index():
    def __init__(self):
        self.expression = None

class Hash():
    def __init__(self):
        self.key_value_pairs = {}

class Expander():
    pass

class Macro():
    def __init__(self):
        self.structure=[]

class Operator(str):
    pass

class KeyValuePair():
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.ws = []
    
    def add(self, value):
        if isinstance(self.value, list):
            self.value.append(value)
        elif self.value is not None:
            self.value = [self.value, value]
        else:
            self.value = value
        

class OperatorExpression(list):
    pass

class ConditionalExpression(OperatorExpression):
    pass

class OrExpression(OperatorExpression):
    pass

class AndExpression(OperatorExpression):
    pass

class EqualityExpression(OperatorExpression):
    pass

class RelationalExpression(OperatorExpression):
    pass

class AdditiveExpression(OperatorExpression):
    pass

class MultiplicativeExpression(OperatorExpression):
    pass

class UnaryExpression(OperatorExpression):
    pass

class BraceExpression(list):
    pass

class MacroCall():
    def __init__(self):
        self.structure=[]

class Idref(list):
    pass

