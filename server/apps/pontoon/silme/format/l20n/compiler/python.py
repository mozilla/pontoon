from silme.core.entity import is_string
import l20n.ast as l20n
from ..ast import py as py
from silme.format.l20n.serializer.python import Serializer

class Compiler(object):
    def __init__(self):
        self.entities = {}

    def compile(self, lol):
        py = self.transform_into_py(lol)
        serializer = Serializer()
        string = serializer.dump_element(py)
        return string

    def transform_into_py(self, lol):
        script = py.Script()
        for elem in lol:
            if isinstance(elem, l20n.Entity):
                self.transform_entity(elem, script)
        return script

    def transform_entity(self, entity, script):
        name = py.Idref(entity.id)
        l20nval = entity.values
        is_static = True

        (pyval, breaks_static) = self.transform_value(l20nval)

        if breaks_static:
            is_static = False
        if is_static:
            script.append(py.Assignment(name, pyval))
        else:
            func = py.Function(name)
            func.args = ['env',]
            ret = py.Return(pyval)
            func.append(ret)
            script.append(func)

    def transform_value(self, l20nval):
        val = None
        breaks_static = False

        if is_string(l20nval):
            if isinstance(l20nval, l20n.ComplexStringValue):
                s = self.transform_complex_string(l20nval)
                if not isinstance(s, py.Idref):
                    s = py.Str(s)
                breaks_static = True
            else:
                s = py.Str(l20nval)
            val = s
        return (val, breaks_static)

    def transform_complex_string(self, val):
        if len(val.pieces)<2:
            piece = val.pieces[0]
            if isinstance(piece, l20n.Expander):
                return self.transform_expression(piece)
            else:
                return val.pieces[0]
        pieces = val.pieces[:]
        r = self.transform_expression(pieces.pop())
        while len(pieces)>0:
            l = self.transform_expression(pieces.pop())
            r = py.AdditiveExpression([l, '+', r])
        return r

    def transform_expression(self, exp):
        if isinstance(exp, l20n.Expander):
            return self.transform_expression(exp.expression)
        if isinstance(exp, l20n.ConditionalExpression):
            jsexp = py.ConditionalExpression()
            jsexp.append(self.transform_expression(exp[0]))
            jsexp.append(self.transform_expression(exp[1]))
            jsexp.append(self.transform_expression(exp[2]))
            return jsexp
        if isinstance(exp, l20n.EqualityExpression):
            jsexp = py.EqualityExpression()
        if isinstance(exp, l20n.RelationalExpression):
            jsexp = py.RelationalExpression()
        if isinstance(exp, l20n.OrExpression):
            jsexp = py.OrExpression()
        if isinstance(exp, l20n.AndExpression):
            jsexp = py.AndExpression()
        if isinstance(exp, l20n.MultiplicativeExpression):
            jsexp = py.MultiplicativeExpression()
        if isinstance(exp, l20n.UnaryExpression):
            jsexp = py.UnaryExpression()
        if isinstance(exp, l20n.OperatorExpression):
            for n,i in enumerate(exp):
                if n%2==1:
                    jsexp.append(i)
                else:
                    jsexp.append(self.transform_expression(i))
            return jsexp
        if isinstance(exp, l20n.BraceExpression):
            jsexp = py.BraceExpression()
            jsexp.append(self.transform_expression(exp[0]))
            return jsexp 
        if isinstance(exp, l20n.Idref):
            if len(exp)==1:
                index = py.Index(py.Idref('env'), py.Str(exp[0]))
                index.idref = py.Idref('env')
            return index
        if is_string(exp):
            return py.Str(unicode(exp))
        if isinstance(exp, int):
            return py.Int(exp)
        if isinstance(exp, l20n.MacroCall):
            args = map(self.transform_expression, exp.args)
            args2 = [py.Idref('env'), py.Array(args)]
            return py.Call(self.transform_expression(exp.idref), args2)
        if isinstance(exp, l20n.ObjectIndex):
            return py.Index(self.transform_expression(exp.idref),
                            self.transform_expression(exp.arg))
