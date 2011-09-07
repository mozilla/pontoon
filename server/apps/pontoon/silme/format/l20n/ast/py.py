from copy import deepcopy

class Script(list):
    def __init__(self, code=None):
        list.__init__(self)
        if code:
            if not isinstance(code, list):
                code = [code,]
            self.extend(code)

class Idref(list):
    def __init__(self, *args):
        for i in args:
            self.append(i)

    def __repr__(self):
        return '.'.join(self)

    def __add__(self, val):
        if is_string(val):
            x= deepcopy(self)
            x.append(val)
            return x
        elif isinstance(val, list):
            x= deepcopy(self)
            for i in val:
                x.append(i)
            return x
        raise NotImplemented()


class Str(object):
    def __init__(self, s):
        object.__init__(self)
        self.data = s

    def __repr__(self):
        return self.data

class Function(Script):
    def __init__(self, name, args=None, code=None):
        Script.__init__(self, code=code)
        self.name = name
        self.args = args if args else []

class Return(object):
    def __init__(self, entry):
        self.entry = entry

    def __repr__(self):
        return 'return %s' % self.idref

class Call(object):
    def __init__(self, idref, args=None):
        self.idref = idref
        self.args = args if args else []

    def __repr__(self):
        return '%s(%r)' % (self.idref, self.args)

class Index(object):
    def __init__(self, idref, arg=None):
        self.idref = idref
        self.arg = arg

    def __repr__(self):
        return '%s[%s]' % (self.idref, self.arg)

class Assignment(object):
    def __init__(self, l, r):
        self.left = l
        self.right = r

class OperatorExpression(list):
    def __repr__(self):
        return ''.join([str(i) for i in self])

class ConditionalExpression(OperatorExpression):
    pass

class AndExpression(OperatorExpression):
    pass

class OrExpression(OperatorExpression):
    pass

class AdditiveExpression(OperatorExpression):
    pass

class EqualityExpression(OperatorExpression):
    pass

class RelationalExpression(OperatorExpression):
    pass

class MultiplicativeExpression(OperatorExpression):
    pass

class UnaryExpression(OperatorExpression):
    pass

class BraceExpression(list):
    pass

