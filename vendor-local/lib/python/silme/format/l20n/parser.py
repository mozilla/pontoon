import re
from .structure import L20nStructure

class L20nParser():
    def __init__(self):
        self.patterns = {}
        self.patterns['ws'] = re.compile('^\s+')
        self.patterns['id'] = re.compile('^\w+')
        self.patterns['entry'] = re.compile('(^<)|(^\/\*)|(\[%%)')
        self.patterns['group'] = (re.compile(u'^\[%%\s*'), re.compile(u'^%%\]'))

    def parse(self, content):
        self.content = content
        self.lol = LOL()
        self.lol.add(self.get_ws())
        while self.content:
            self.get_entry()
        return self.lol

    def get_entry(self):
        entry = None
        match = self.patterns['entry'].match(self.content)
        if not match:
            raise Exception()

        if self.content[0] == '<':
            entry = self.get_entity()
        elif self.content[0] == '/':
            entry = self.get_comment()
        elif self.content[0] == '[':
            entry = self.get_group()
        else:
            raise Exception()
        self.lol.add(entry)
        self.get_ws()
        return entry

    def get_ws(self):
        match = self.patterns['ws'].match(self.content)
        if not match:
            return None
        self.content = self.content[match.end(0):]
        #return WS(match.group(0)) # this line costs a lot

    def get_group(self):
        group = Group()
        match = self.patterns['group'][0].match(self.content)
        if not match:
            raise Exception()
        self.content = self.content[match.end(0):]
        match = self.patterns['group'][1].match(self.content)
        while not match:
            entry = self.get_entry()
            group.add(entry)
            match = self.patterns['group'][1].match(self.content)
        self.content = self.content[match.end(0):]
        return group

    def get_entity(self):
        if self.content[0] != '<':
            raise Exception()
        self.content = self.content[1:]
        id = self.get_id()
        entity = Entity(id)
        self.get_ws()
        if self.content[0] == '[':
            index = self.get_index()
            entity.index = index
        if self.content[0] != ':':
            raise Exception()
        self.content = self.content[1:]
        self.get_ws()
        if self.content[0] == '(':
            value = self.get_macro()
        else:
            value = self.get_value()
        entity.value = value
        self.get_ws()
        while self.content[0] != '>':
            entity.kvplist.append(self.get_key_value_pair())
            self.get_ws()
        self.content = self.content[1:]
        return entity
    
    def get_id(self):
        match = self.patterns['id'].match(self.content)
        if not match:
            raise Exception()
        self.content = self.content[match.end(0):]
        return match.group(0)

    def get_index(self):
        index = Index()
        if self.content[0] != '[':
            raise Exception()
        self.content = self.content[1:]
        self.get_ws()
        expression = self.get_expression()
        index.expression = expression
        self.get_ws()
        if self.content[0] != ']':
            raise Exception()
        self.content = self.content[1:]
        return index
    
    def get_macro(self):
        macro = Macro()
        idlist = []
        if self.content[0]!='(':
            raise Exception()
        self.content = self.content[1:]
        self.get_ws()
        while self.content[0]!=')':
            id = self.get_id()
            idlist.append(id)
            self.get_ws()
            while self.content[0]==',':
                self.content = self.content[1:]
                self.get_ws()
                id=self.get_id()
                idlist.append(id)
                self.get_ws()
        self.content = self.content[1:]
        self.get_ws()
        if self.content[:2]!='->':
            raise Exception()
        self.content = self.content[2:]
        self.get_ws()
        if self.content[0]!='{':
            raise Exception()
        self.content = self.content[1:]
        self.get_ws()
        expression=self.get_expression()
        macro.structure.append(expression)
        self.get_ws()
        if self.content[0]!='}':
            raise Exception()
        self.content = self.content[1:]
        return macro
    
    def get_value(self):
        if self.content[0]=="'" or \
            self.content[0]=='"':
            value = self.get_string()
        elif self.content[0]=='[':
            value = self.get_array()
        elif self.content[0]=='{':
            value = self.get_hash()
        else:
            raise Exception()
        return value

    def get_key_value_pair(self):
        key_value_pair = KeyValuePair()
        key_value_pair.key = self.get_id()
        if self.content[0]!=':':
            raise Exception()
        self.content = self.content[1:]
        key_value_pair.ws.append(self.get_ws())
        value = self.get_value()
        key_value_pair.value = value
        return key_value_pair
    
    def get_comment(self):
        if self.content[:2] != '/*':
            raise Exception()
        pattern = re.compile('\*\/')
        m = pattern.search(self.content)
        if not m:
            raise Exception()
        comment = self.content[2:m.start(0)]
        self.content = self.content[m.end(0):]
        self.lol.add(Comment(comment))
    
    def get_string(self):
        if self.content[0]!='"' and \
             self.content[0]!="'":
            raise Exception()
        str_end = self.content[0]
        buffer = ''
        literal = re.compile('^([^\\\\$'+str_end+']+)')
        self.content = self.content[1:]
        while self.content[0]!=str_end:
            if self.content[0]=='\\':
                self.content = self.content[1:]
                buffer = buffer + this.content[0]
                self.content = self.content[1:]
            if self.content[0]=='$':
                self.content = self.content[1:]
                if self.content[0]!='{':
                    raise Exception()
                self.content = self.content[1:]
                expander = Expander()
                expression = self.getExpression()
                if buffer:
                    string.buffer = buffer
                    buffer = ''
                expander.expression = expression
                if self.content[0]!='}':
                    raise Exception()
                self.content = self.content[1:]
                if not (self.content[0]=='s' or \
                    self.content[0]=='i'):
                    raise Exception()
                expander.flag = self.content[0]
                self.content = self.content[1:]
            m = literal.match(self.content)
            if m:
                buffer = buffer + m.group(1)
                self.content = self.content[m.end(0):]
        self.content = self.content[1:]
        return buffer
    
    def get_array(self):
        array = []
        if self.content[0]!='[':
            raise Exception()
        self.content=self.content[1:]
        self.get_ws()
        value = self.get_value()
        array.append(value)
        while self.content[0]==',':
            self.content=self.content[1:]
            self.get_ws()
            value = self.get_value()
            array.append(value)
            self.get_ws()
        if self.content[0]!=']':
            raise Exception()
        self.content=self.content[1:]
        return array
    
    def get_hash(self):
        hash = Hash()
        if self.content[0]!='{':
            raise Exception()
        self.content = self.content[1:]
        self.get_ws()
        key_value_pair = self.get_key_value_pair()
        hash.key_value_pairs[key_value_pair.key] = key_value_pair
        self.get_ws()
        if self.content[0]==',':
            self.content = self.content[1:]
            self.get_ws()
            keyValuePair = self.get_key_value_pair()
            hash.key_value_pairs[key_value_pair.key] = key_value_pair
            self.get_ws()
        if self.content[0]!='}':
            raise Exception()
        self.content = self.content[1:]
        return hash
    
    def get_expression(self):
        return self.get_conditional_expression()

    
    def get_prefix_expression(self, pattern, type, prefix):
        higher_expression = prefix()
        self.get_ws()
        m = pattern.match(self.content)
        if not m:
            return higher_expression
        operator_expression = type()
        operator_expression.append(higher_expression)
        while m:
            operator_expression.append(Operator(m.group(0)))
            self.content = self.content[m.end(0):]
            self.get_ws()
            higher_expression = prefix()
            operator_expression.append(higher_expression)
            self.get_ws()
            m = pattern.match(self.content)
        return operator_expression
    
    def get_postfix_expression(self, pattern, type, postfix):
        m = pattern.match(self.content)
        if not m:
            return postfix()
        operator_expression = type()
        operator_expression.append(Operator(m.group(0)))
        self.content = self.content[m.end(0):]
        self.get_ws()
        operator_expression2 = type()
        operator_expression.append(operator_expression2)
        return operator_expression
        
        
    def get_conditional_expression(self):
        or_expression = self.get_or_expression()
        self.get_ws()
        pattern = re.compile('^\?')
        m = pattern.match(self.content)
        if not m:
            return or_expression
        conditional_expression = ConditionalExpression()
        conditional_expression.append(or_expression)
        self.content=self.content[m.end(0):]
        self.get_ws()
        expression = self.get_expression()
        conditional_expression.append(expression)
        self.get_ws()
        pattern = re.compile('^:')
        m = pattern.match(self.content)
        if not m:
            raise Exception()
        self.content=self.content[1:]
        self.get_ws()
        conditional_expression2 = self.get_conditional_expression()
        conditional_expression.append(conditional_expression2)
        self.get_ws()
        return conditional_expression

    def get_or_expression(self):
        return self.get_prefix_expression(re.compile('^\|\|'), OrExpression, self.get_and_expression)
    
    def getAndExpression(self):
        return self.get_prefix_expression(re.compile('^\&\&'), AndExpression, self.get_equality_expression)
    
    def getEqualityExpression(self):
        return self.get_prefix_expression(re.compile('^[!=]='), EqualityExpression, self.get_relational_expression)
    
    def getRelationalExpression(self):
        return self.get_prefix_expression(re.compile('^[<>]=?'), RelationalExpression, self.get_additive_expression)

    def getAdditiveExpression(self):
        return self.get_prefix_expression(re.compile('^[\+\-]'), AdditiveExpression, self.get_multiplicative_expression)
    
    def getMultiplicativeExpression(self):
        return self.get_prefix_expression(re.compile('^[\*\/\%]'), MultiplicativeExpression, self.get_unary_expression)
    
    def getUnaryExpression(self):
        return self.get_postfix_expression(re.compile('^[\+\-\!]'), UnaryExpression, self.get_primary_expression)
        
    def get_primary_expression(self):
        if self.content[0]=='(':
            primary_expression = BraceExpression()
            self.content = self.content[1:]
            expression = self.get_expression()
            primary_expression.append(expression)
            self.get_ws()
            if self.content[0]!=')':
                raise Exception()
            self.content = self.content[1:]
            self.get_ws()
            return primary_expression
        # number
        pattern = re.compile('^[0-9]+')
        match = pattern.match(self.content)
        if match:
            self.content = self.content[match.end(0):]
            self.get_ws()
            return int(match.group(0))
        # lookahead for value
        char = self.content[0]
        if char=='"' or char=="'" or char=='[' or char=='{':
            return self.get_value()
        # idref (with index?) or macrocall
        idref = self.get_idref()
        # check for index
        if self.content[0]=='[':
            index=self.get_index()
            idref.append(index)
            return idref
        if self.content[0]!='(':
            return idref
        primary_expression = MacroCall()
        primary_expression.structure.append(idref)
        self.content = self.content[1:]
        self.get_ws()
        if self.content[0]!=')':
            expression = self.get_expression()
            primary_expression.structure.append(expression)
            self.get_ws()
            while self.content[0]==',':
                self.content = self.content[1:]
                self.get_ws()
                expression=self.getExpression()
                primary_expression.structure.append(expression)
                self.get_ws()
        if self.content[0]!=')':
            raise Exception()
        self.content=self.content[1:]
        self.get_ws()
        return primary_expression
    
    def get_idref(self):
        idref = Idref()
        id = self.get_id()
        idref.append(id)
        while self.content[0]=='.':
            self.content = self.content[1:]
            id = self.get_id()
            idref.append(id)
        return idref
