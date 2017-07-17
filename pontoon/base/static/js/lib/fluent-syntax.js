/* fluent-syntax@0.5.0 */
(function (global, factory) {
	typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
	typeof define === 'function' && define.amd ? define('fluent-syntax', ['exports'], factory) :
	(factory((global.FluentSyntax = global.FluentSyntax || {})));
}(this, (function (exports) { 'use strict';

var classCallCheck = function (instance, Constructor) {
  if (!(instance instanceof Constructor)) {
    throw new TypeError("Cannot call a class as a function");
  }
};

var createClass = function () {
  function defineProperties(target, props) {
    for (var i = 0; i < props.length; i++) {
      var descriptor = props[i];
      descriptor.enumerable = descriptor.enumerable || false;
      descriptor.configurable = true;
      if ("value" in descriptor) descriptor.writable = true;
      Object.defineProperty(target, descriptor.key, descriptor);
    }
  }

  return function (Constructor, protoProps, staticProps) {
    if (protoProps) defineProperties(Constructor.prototype, protoProps);
    if (staticProps) defineProperties(Constructor, staticProps);
    return Constructor;
  };
}();









var inherits = function (subClass, superClass) {
  if (typeof superClass !== "function" && superClass !== null) {
    throw new TypeError("Super expression must either be null or a function, not " + typeof superClass);
  }

  subClass.prototype = Object.create(superClass && superClass.prototype, {
    constructor: {
      value: subClass,
      enumerable: false,
      writable: true,
      configurable: true
    }
  });
  if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass;
};











var possibleConstructorReturn = function (self, call) {
  if (!self) {
    throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  }

  return call && (typeof call === "object" || typeof call === "function") ? call : self;
};





var slicedToArray = function () {
  function sliceIterator(arr, i) {
    var _arr = [];
    var _n = true;
    var _d = false;
    var _e = undefined;

    try {
      for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) {
        _arr.push(_s.value);

        if (i && _arr.length === i) break;
      }
    } catch (err) {
      _d = true;
      _e = err;
    } finally {
      try {
        if (!_n && _i["return"]) _i["return"]();
      } finally {
        if (_d) throw _e;
      }
    }

    return _arr;
  }

  return function (arr, i) {
    if (Array.isArray(arr)) {
      return arr;
    } else if (Symbol.iterator in Object(arr)) {
      return sliceIterator(arr, i);
    } else {
      throw new TypeError("Invalid attempt to destructure non-iterable instance");
    }
  };
}();

/*
 * Base class for all Fluent AST nodes.
 *
 * All productions described in the ASDL subclass BaseNode, including Span and
 * Annotation.
 *
 */
var BaseNode = function BaseNode() {
  classCallCheck(this, BaseNode);
};

/*
 * Base class for AST nodes which can have Spans.
 */


var SyntaxNode = function (_BaseNode) {
  inherits(SyntaxNode, _BaseNode);

  function SyntaxNode() {
    classCallCheck(this, SyntaxNode);
    return possibleConstructorReturn(this, (SyntaxNode.__proto__ || Object.getPrototypeOf(SyntaxNode)).apply(this, arguments));
  }

  createClass(SyntaxNode, [{
    key: 'addSpan',
    value: function addSpan(start, end) {
      this.span = new Span(start, end);
    }
  }]);
  return SyntaxNode;
}(BaseNode);

var Resource = function (_SyntaxNode) {
  inherits(Resource, _SyntaxNode);

  function Resource() {
    var body = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];
    var comment = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
    classCallCheck(this, Resource);

    var _this2 = possibleConstructorReturn(this, (Resource.__proto__ || Object.getPrototypeOf(Resource)).call(this));

    _this2.type = 'Resource';
    _this2.body = body;
    _this2.comment = comment;
    return _this2;
  }

  return Resource;
}(SyntaxNode);

var Entry = function (_SyntaxNode2) {
  inherits(Entry, _SyntaxNode2);

  function Entry() {
    classCallCheck(this, Entry);

    var _this3 = possibleConstructorReturn(this, (Entry.__proto__ || Object.getPrototypeOf(Entry)).call(this));

    _this3.type = 'Entry';
    _this3.annotations = [];
    return _this3;
  }

  createClass(Entry, [{
    key: 'addAnnotation',
    value: function addAnnotation(annot) {
      this.annotations.push(annot);
    }
  }]);
  return Entry;
}(SyntaxNode);

var Message = function (_Entry) {
  inherits(Message, _Entry);

  function Message(id) {
    var value = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
    var attributes = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : [];
    var tags = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : [];
    var comment = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : null;
    classCallCheck(this, Message);

    var _this4 = possibleConstructorReturn(this, (Message.__proto__ || Object.getPrototypeOf(Message)).call(this));

    _this4.type = 'Message';
    _this4.id = id;
    _this4.value = value;
    _this4.attributes = attributes;
    _this4.tags = tags;
    _this4.comment = comment;
    return _this4;
  }

  return Message;
}(Entry);

var Pattern = function (_SyntaxNode3) {
  inherits(Pattern, _SyntaxNode3);

  function Pattern(elements) {
    classCallCheck(this, Pattern);

    var _this5 = possibleConstructorReturn(this, (Pattern.__proto__ || Object.getPrototypeOf(Pattern)).call(this));

    _this5.type = 'Pattern';
    _this5.elements = elements;
    return _this5;
  }

  return Pattern;
}(SyntaxNode);

var TextElement = function (_SyntaxNode4) {
  inherits(TextElement, _SyntaxNode4);

  function TextElement(value) {
    classCallCheck(this, TextElement);

    var _this6 = possibleConstructorReturn(this, (TextElement.__proto__ || Object.getPrototypeOf(TextElement)).call(this));

    _this6.type = 'TextElement';
    _this6.value = value;
    return _this6;
  }

  return TextElement;
}(SyntaxNode);

var Expression = function (_SyntaxNode5) {
  inherits(Expression, _SyntaxNode5);

  function Expression() {
    classCallCheck(this, Expression);

    var _this7 = possibleConstructorReturn(this, (Expression.__proto__ || Object.getPrototypeOf(Expression)).call(this));

    _this7.type = 'Expression';
    return _this7;
  }

  return Expression;
}(SyntaxNode);

var StringExpression = function (_Expression) {
  inherits(StringExpression, _Expression);

  function StringExpression(value) {
    classCallCheck(this, StringExpression);

    var _this8 = possibleConstructorReturn(this, (StringExpression.__proto__ || Object.getPrototypeOf(StringExpression)).call(this));

    _this8.type = 'StringExpression';
    _this8.value = value;
    return _this8;
  }

  return StringExpression;
}(Expression);

var NumberExpression = function (_Expression2) {
  inherits(NumberExpression, _Expression2);

  function NumberExpression(value) {
    classCallCheck(this, NumberExpression);

    var _this9 = possibleConstructorReturn(this, (NumberExpression.__proto__ || Object.getPrototypeOf(NumberExpression)).call(this));

    _this9.type = 'NumberExpression';
    _this9.value = value;
    return _this9;
  }

  return NumberExpression;
}(Expression);

var MessageReference = function (_Expression3) {
  inherits(MessageReference, _Expression3);

  function MessageReference(id) {
    classCallCheck(this, MessageReference);

    var _this10 = possibleConstructorReturn(this, (MessageReference.__proto__ || Object.getPrototypeOf(MessageReference)).call(this));

    _this10.type = 'MessageReference';
    _this10.id = id;
    return _this10;
  }

  return MessageReference;
}(Expression);

var ExternalArgument = function (_Expression4) {
  inherits(ExternalArgument, _Expression4);

  function ExternalArgument(id) {
    classCallCheck(this, ExternalArgument);

    var _this11 = possibleConstructorReturn(this, (ExternalArgument.__proto__ || Object.getPrototypeOf(ExternalArgument)).call(this));

    _this11.type = 'ExternalArgument';
    _this11.id = id;
    return _this11;
  }

  return ExternalArgument;
}(Expression);

var SelectExpression = function (_Expression5) {
  inherits(SelectExpression, _Expression5);

  function SelectExpression(expression, variants) {
    classCallCheck(this, SelectExpression);

    var _this12 = possibleConstructorReturn(this, (SelectExpression.__proto__ || Object.getPrototypeOf(SelectExpression)).call(this));

    _this12.type = 'SelectExpression';
    _this12.expression = expression;
    _this12.variants = variants;
    return _this12;
  }

  return SelectExpression;
}(Expression);

var AttributeExpression = function (_Expression6) {
  inherits(AttributeExpression, _Expression6);

  function AttributeExpression(id, name) {
    classCallCheck(this, AttributeExpression);

    var _this13 = possibleConstructorReturn(this, (AttributeExpression.__proto__ || Object.getPrototypeOf(AttributeExpression)).call(this));

    _this13.type = 'AttributeExpression';
    _this13.id = id;
    _this13.name = name;
    return _this13;
  }

  return AttributeExpression;
}(Expression);

var VariantExpression = function (_Expression7) {
  inherits(VariantExpression, _Expression7);

  function VariantExpression(id, key) {
    classCallCheck(this, VariantExpression);

    var _this14 = possibleConstructorReturn(this, (VariantExpression.__proto__ || Object.getPrototypeOf(VariantExpression)).call(this));

    _this14.type = 'VariantExpression';
    _this14.id = id;
    _this14.key = key;
    return _this14;
  }

  return VariantExpression;
}(Expression);

var CallExpression = function (_Expression8) {
  inherits(CallExpression, _Expression8);

  function CallExpression(callee, args) {
    classCallCheck(this, CallExpression);

    var _this15 = possibleConstructorReturn(this, (CallExpression.__proto__ || Object.getPrototypeOf(CallExpression)).call(this));

    _this15.type = 'CallExpression';
    _this15.callee = callee;
    _this15.args = args;
    return _this15;
  }

  return CallExpression;
}(Expression);

var Attribute = function (_SyntaxNode6) {
  inherits(Attribute, _SyntaxNode6);

  function Attribute(id, value) {
    classCallCheck(this, Attribute);

    var _this16 = possibleConstructorReturn(this, (Attribute.__proto__ || Object.getPrototypeOf(Attribute)).call(this));

    _this16.type = 'Attribute';
    _this16.id = id;
    _this16.value = value;
    return _this16;
  }

  return Attribute;
}(SyntaxNode);

var Tag = function (_SyntaxNode7) {
  inherits(Tag, _SyntaxNode7);

  function Tag(name) {
    classCallCheck(this, Tag);

    var _this17 = possibleConstructorReturn(this, (Tag.__proto__ || Object.getPrototypeOf(Tag)).call(this));

    _this17.type = 'Tag';
    _this17.name = name;
    return _this17;
  }

  return Tag;
}(SyntaxNode);

var Variant = function (_SyntaxNode8) {
  inherits(Variant, _SyntaxNode8);

  function Variant(key, value) {
    var def = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
    classCallCheck(this, Variant);

    var _this18 = possibleConstructorReturn(this, (Variant.__proto__ || Object.getPrototypeOf(Variant)).call(this));

    _this18.type = 'Variant';
    _this18.key = key;
    _this18.value = value;
    _this18.default = def;
    return _this18;
  }

  return Variant;
}(SyntaxNode);

var NamedArgument = function (_SyntaxNode9) {
  inherits(NamedArgument, _SyntaxNode9);

  function NamedArgument(name, val) {
    classCallCheck(this, NamedArgument);

    var _this19 = possibleConstructorReturn(this, (NamedArgument.__proto__ || Object.getPrototypeOf(NamedArgument)).call(this));

    _this19.type = 'NamedArgument';
    _this19.name = name;
    _this19.val = val;
    return _this19;
  }

  return NamedArgument;
}(SyntaxNode);

var Identifier = function (_SyntaxNode10) {
  inherits(Identifier, _SyntaxNode10);

  function Identifier(name) {
    classCallCheck(this, Identifier);

    var _this20 = possibleConstructorReturn(this, (Identifier.__proto__ || Object.getPrototypeOf(Identifier)).call(this));

    _this20.type = 'Identifier';
    _this20.name = name;
    return _this20;
  }

  return Identifier;
}(SyntaxNode);

var _Symbol = function (_Identifier) {
  inherits(_Symbol, _Identifier);

  function _Symbol(name) {
    classCallCheck(this, _Symbol);

    var _this21 = possibleConstructorReturn(this, (_Symbol.__proto__ || Object.getPrototypeOf(_Symbol)).call(this, name));

    _this21.type = 'Symbol';
    return _this21;
  }

  return _Symbol;
}(Identifier);

var Comment = function (_Entry2) {
  inherits(Comment, _Entry2);

  function Comment(content) {
    classCallCheck(this, Comment);

    var _this22 = possibleConstructorReturn(this, (Comment.__proto__ || Object.getPrototypeOf(Comment)).call(this));

    _this22.type = 'Comment';
    _this22.content = content;
    return _this22;
  }

  return Comment;
}(Entry);

var Section = function (_Entry3) {
  inherits(Section, _Entry3);

  function Section(name) {
    var comment = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
    classCallCheck(this, Section);

    var _this23 = possibleConstructorReturn(this, (Section.__proto__ || Object.getPrototypeOf(Section)).call(this));

    _this23.type = 'Section';
    _this23.name = name;
    _this23.comment = comment;
    return _this23;
  }

  return Section;
}(Entry);

var Function$1 = function (_Identifier2) {
  inherits(Function, _Identifier2);

  function Function(name) {
    classCallCheck(this, Function);

    var _this24 = possibleConstructorReturn(this, (Function.__proto__ || Object.getPrototypeOf(Function)).call(this, name));

    _this24.type = 'Function';
    return _this24;
  }

  return Function;
}(Identifier);

var Junk = function (_Entry4) {
  inherits(Junk, _Entry4);

  function Junk(content) {
    classCallCheck(this, Junk);

    var _this25 = possibleConstructorReturn(this, (Junk.__proto__ || Object.getPrototypeOf(Junk)).call(this));

    _this25.type = 'Junk';
    _this25.content = content;
    return _this25;
  }

  return Junk;
}(Entry);

var Span = function (_BaseNode2) {
  inherits(Span, _BaseNode2);

  function Span(start, end) {
    classCallCheck(this, Span);

    var _this26 = possibleConstructorReturn(this, (Span.__proto__ || Object.getPrototypeOf(Span)).call(this));

    _this26.type = 'Span';
    _this26.start = start;
    _this26.end = end;
    return _this26;
  }

  return Span;
}(BaseNode);

var Annotation = function (_SyntaxNode11) {
  inherits(Annotation, _SyntaxNode11);

  function Annotation(code) {
    var args = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
    var message = arguments[2];
    classCallCheck(this, Annotation);

    var _this27 = possibleConstructorReturn(this, (Annotation.__proto__ || Object.getPrototypeOf(Annotation)).call(this));

    _this27.type = 'Annotation';
    _this27.code = code;
    _this27.args = args;
    _this27.message = message;
    return _this27;
  }

  return Annotation;
}(SyntaxNode);

var ParserStream = function () {
  function ParserStream(string) {
    classCallCheck(this, ParserStream);

    this.string = string;
    this.iter = string[Symbol.iterator]();
    this.buf = [];
    this.peekIndex = 0;
    this.index = 0;

    this.iterEnd = false;
    this.peekEnd = false;

    this.ch = this.iter.next().value;
  }

  createClass(ParserStream, [{
    key: "next",
    value: function next() {
      if (this.iterEnd) {
        return undefined;
      }

      if (this.buf.length === 0) {
        this.ch = this.iter.next().value;
      } else {
        this.ch = this.buf.shift();
      }

      this.index++;

      if (this.ch === undefined) {
        this.iterEnd = true;
        this.peekEnd = true;
      }

      this.peekIndex = this.index;

      return this.ch;
    }
  }, {
    key: "current",
    value: function current() {
      return this.ch;
    }
  }, {
    key: "currentIs",
    value: function currentIs(ch) {
      return this.ch === ch;
    }
  }, {
    key: "currentPeek",
    value: function currentPeek() {
      if (this.peekEnd) {
        return undefined;
      }

      var diff = this.peekIndex - this.index;

      if (diff === 0) {
        return this.ch;
      }
      return this.buf[diff - 1];
    }
  }, {
    key: "currentPeekIs",
    value: function currentPeekIs(ch) {
      return this.currentPeek() === ch;
    }
  }, {
    key: "peek",
    value: function peek() {
      if (this.peekEnd) {
        return undefined;
      }

      this.peekIndex += 1;

      var diff = this.peekIndex - this.index;

      if (diff > this.buf.length) {
        var ch = this.iter.next().value;
        if (ch !== undefined) {
          this.buf.push(ch);
        } else {
          this.peekEnd = true;
          return undefined;
        }
      }

      return this.buf[diff - 1];
    }
  }, {
    key: "getIndex",
    value: function getIndex() {
      return this.index;
    }
  }, {
    key: "getPeekIndex",
    value: function getPeekIndex() {
      return this.peekIndex;
    }
  }, {
    key: "peekCharIs",
    value: function peekCharIs(ch) {
      if (this.peekEnd) {
        return false;
      }

      var ret = this.peek();

      this.peekIndex -= 1;

      return ret === ch;
    }
  }, {
    key: "resetPeek",
    value: function resetPeek() {
      this.peekIndex = this.index;
      this.peekEnd = this.iterEnd;
    }
  }, {
    key: "skipToPeek",
    value: function skipToPeek() {
      var diff = this.peekIndex - this.index;

      for (var i = 0; i < diff; i++) {
        this.ch = this.buf.shift();
      }

      this.index = this.peekIndex;
    }
  }, {
    key: "getSlice",
    value: function getSlice(start, end) {
      return this.string.substring(start, end);
    }
  }]);
  return ParserStream;
}();

function _extendableBuiltin(cls) {
  function ExtendableBuiltin() {
    var instance = Reflect.construct(cls, Array.from(arguments));
    Object.setPrototypeOf(instance, Object.getPrototypeOf(this));
    return instance;
  }

  ExtendableBuiltin.prototype = Object.create(cls.prototype, {
    constructor: {
      value: cls,
      enumerable: false,
      writable: true,
      configurable: true
    }
  });

  if (Object.setPrototypeOf) {
    Object.setPrototypeOf(ExtendableBuiltin, cls);
  } else {
    ExtendableBuiltin.__proto__ = cls;
  }

  return ExtendableBuiltin;
}

var ParseError = function (_extendableBuiltin2) {
  inherits(ParseError, _extendableBuiltin2);

  function ParseError(code) {
    classCallCheck(this, ParseError);

    var _this = possibleConstructorReturn(this, (ParseError.__proto__ || Object.getPrototypeOf(ParseError)).call(this));

    _this.code = code;

    for (var _len = arguments.length, args = Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
      args[_key - 1] = arguments[_key];
    }

    _this.args = args;
    _this.message = getErrorMessage(code, args);
    return _this;
  }

  return ParseError;
}(_extendableBuiltin(Error));

function getErrorMessage(code, args) {
  switch (code) {
    case 'E0001':
      return 'Generic error';
    case 'E0002':
      return 'Expected an entry start';
    case 'E0003':
      {
        var _args = slicedToArray(args, 1),
            token = _args[0];

        return 'Expected token: "' + token + '"';
      }
    case 'E0004':
      {
        var _args2 = slicedToArray(args, 1),
            range = _args2[0];

        return 'Expected a character from range: "' + range + '"';
      }
    case 'E0005':
      {
        var _args3 = slicedToArray(args, 1),
            id = _args3[0];

        return 'Expected entry "' + id + '" to have a value, attributes or tags';
      }
    case 'E0006':
      {
        var _args4 = slicedToArray(args, 1),
            field = _args4[0];

        return 'Expected field: "' + field + '"';
      }
    case 'E0007':
      return 'Keyword cannot end with a whitespace';
    case 'E0008':
      return 'Callee has to be a simple identifier';
    case 'E0009':
      return 'Key has to be a simple identifier';
    case 'E0010':
      return 'Expected one of the variants to be marked as default (*)';
    case 'E0011':
      return 'Expected at least one variant after "->"';
    case 'E0012':
      return 'Tags cannot be added to messages with attributes';
    case 'E0013':
      return 'Expected variant key';
    case 'E0014':
      return 'Expected literal';
    case 'E0015':
      return 'Only one variant can be marked as default (*)';
    default:
      return code;
  }
}

/* eslint no-magic-numbers: "off" */

var FTLParserStream = function (_ParserStream) {
  inherits(FTLParserStream, _ParserStream);

  function FTLParserStream() {
    classCallCheck(this, FTLParserStream);
    return possibleConstructorReturn(this, (FTLParserStream.__proto__ || Object.getPrototypeOf(FTLParserStream)).apply(this, arguments));
  }

  createClass(FTLParserStream, [{
    key: 'peekLineWS',
    value: function peekLineWS() {
      var ch = this.currentPeek();
      while (ch) {
        if (ch !== ' ' && ch !== '\t') {
          break;
        }
        ch = this.peek();
      }
    }
  }, {
    key: 'skipWSLines',
    value: function skipWSLines() {
      while (true) {
        this.peekLineWS();

        if (this.currentPeek() === '\n') {
          this.skipToPeek();
          this.next();
        } else {
          this.resetPeek();
          break;
        }
      }
    }
  }, {
    key: 'skipLineWS',
    value: function skipLineWS() {
      while (this.ch) {
        if (this.ch !== ' ' && this.ch !== '\t') {
          break;
        }
        this.next();
      }
    }
  }, {
    key: 'expectChar',
    value: function expectChar(ch) {
      if (this.ch === ch) {
        this.next();
        return true;
      }

      if (ch === '\n') {
        // Unicode Character 'SYMBOL FOR NEWLINE' (U+2424)
        throw new ParseError('E0003', '\u2424');
      }

      throw new ParseError('E0003', ch);
    }
  }, {
    key: 'takeCharIf',
    value: function takeCharIf(ch) {
      if (this.ch === ch) {
        this.next();
        return true;
      }
      return false;
    }
  }, {
    key: 'takeChar',
    value: function takeChar(f) {
      var ch = this.ch;
      if (ch !== undefined && f(ch)) {
        this.next();
        return ch;
      }
      return undefined;
    }
  }, {
    key: 'isIDStart',
    value: function isIDStart() {
      if (this.ch === undefined) {
        return false;
      }

      var cc = this.ch.charCodeAt(0);
      return cc >= 97 && cc <= 122 || // a-z
      cc >= 65 && cc <= 90 || // A-Z
      cc === 95; // _
    }
  }, {
    key: 'isNumberStart',
    value: function isNumberStart() {
      var cc = this.ch.charCodeAt(0);
      return cc >= 48 && cc <= 57 || cc === 45; // 0-9
    }
  }, {
    key: 'isPeekNextLineIndented',
    value: function isPeekNextLineIndented() {
      if (!this.currentPeekIs('\n')) {
        return false;
      }

      this.peek();

      if (this.currentPeekIs(' ')) {
        this.resetPeek();
        return true;
      }

      this.resetPeek();
      return false;
    }
  }, {
    key: 'isPeekNextLineVariantStart',
    value: function isPeekNextLineVariantStart() {
      if (!this.currentPeekIs('\n')) {
        return false;
      }

      this.peek();

      var ptr = this.getPeekIndex();

      this.peekLineWS();

      if (this.getPeekIndex() - ptr === 0) {
        this.resetPeek();
        return false;
      }

      if (this.currentPeekIs('*')) {
        this.peek();
      }

      if (this.currentPeekIs('[') && !this.peekCharIs('[')) {
        this.resetPeek();
        return true;
      }
      this.resetPeek();
      return false;
    }
  }, {
    key: 'isPeekNextLineAttributeStart',
    value: function isPeekNextLineAttributeStart() {
      if (!this.currentPeekIs('\n')) {
        return false;
      }

      this.peek();

      var ptr = this.getPeekIndex();

      this.peekLineWS();

      if (this.getPeekIndex() - ptr === 0) {
        this.resetPeek();
        return false;
      }

      if (this.currentPeekIs('.')) {
        this.resetPeek();
        return true;
      }

      this.resetPeek();
      return false;
    }
  }, {
    key: 'isPeekNextLinePattern',
    value: function isPeekNextLinePattern() {
      if (!this.currentPeekIs('\n')) {
        return false;
      }

      this.peek();

      var ptr = this.getPeekIndex();

      this.peekLineWS();

      if (this.getPeekIndex() - ptr === 0) {
        this.resetPeek();
        return false;
      }

      if (this.currentPeekIs('}') || this.currentPeekIs('.') || this.currentPeekIs('#') || this.currentPeekIs('[') || this.currentPeekIs('*')) {
        this.resetPeek();
        return false;
      }

      this.resetPeek();
      return true;
    }
  }, {
    key: 'isPeekNextLineTagStart',
    value: function isPeekNextLineTagStart() {
      if (!this.currentPeekIs('\n')) {
        return false;
      }

      this.peek();

      var ptr = this.getPeekIndex();

      this.peekLineWS();

      if (this.getPeekIndex() - ptr === 0) {
        this.resetPeek();
        return false;
      }

      if (this.currentPeekIs('#')) {
        this.resetPeek();
        return true;
      }

      this.resetPeek();
      return false;
    }
  }, {
    key: 'skipToNextEntryStart',
    value: function skipToNextEntryStart() {
      while (this.next()) {
        if (this.currentIs('\n') && !this.peekCharIs('\n')) {
          this.next();
          if (this.ch === undefined || this.isIDStart() || this.currentIs('/') && this.peekCharIs('/') || this.currentIs('[') && this.peekCharIs('[')) {
            break;
          }
        }
      }
    }
  }, {
    key: 'takeIDStart',
    value: function takeIDStart() {
      if (this.isIDStart()) {
        var ret = this.ch;
        this.next();
        return ret;
      }
      throw new ParseError('E0004', 'a-zA-Z');
    }
  }, {
    key: 'takeIDChar',
    value: function takeIDChar() {
      var closure = function closure(ch) {
        var cc = ch.charCodeAt(0);
        return cc >= 97 && cc <= 122 || // a-z
        cc >= 65 && cc <= 90 || // A-Z
        cc >= 48 && cc <= 57 || // 0-9
        cc === 95 || cc === 45; // _-
      };

      return this.takeChar(closure);
    }
  }, {
    key: 'takeSymbChar',
    value: function takeSymbChar() {
      var closure = function closure(ch) {
        if (ch === undefined) {
          return false;
        }

        var cc = ch.charCodeAt(0);
        return cc >= 97 && cc <= 122 || // a-z
        cc >= 65 && cc <= 90 || // A-Z
        cc >= 48 && cc <= 57 || // 0-9
        cc === 95 || cc === 45 || cc === 32; // _-
      };

      return this.takeChar(closure);
    }
  }, {
    key: 'takeDigit',
    value: function takeDigit() {
      var closure = function closure(ch) {
        var cc = ch.charCodeAt(0);
        return cc >= 48 && cc <= 57; // 0-9
      };

      return this.takeChar(closure);
    }
  }]);
  return FTLParserStream;
}(ParserStream);

/*  eslint no-magic-numbers: [0]  */

function withSpan(fn) {
  return function (ps) {
    for (var _len = arguments.length, args = Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
      args[_key - 1] = arguments[_key];
    }

    if (!this.withSpans) {
      return fn.call.apply(fn, [this, ps].concat(args));
    }

    var start = ps.getIndex();
    var node = fn.call.apply(fn, [this, ps].concat(args));

    // Don't re-add the span if the node already has it.  This may happen when
    // one decorated function calls another decorated function.
    if (node.span) {
      return node;
    }

    // Spans of Messages and Sections should include the attached Comment.
    if (node.type === 'Message' || node.type === 'Section') {
      if (node.comment !== null) {
        start = node.comment.span.start;
      }
    }

    var end = ps.getIndex();
    node.addSpan(start, end);
    return node;
  };
}

var FluentParser = function () {
  function FluentParser() {
    var _this = this;

    var _ref = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {},
        _ref$withSpans = _ref.withSpans,
        withSpans = _ref$withSpans === undefined ? true : _ref$withSpans;

    classCallCheck(this, FluentParser);

    this.withSpans = withSpans;

    // Poor man's decorators.
    ['getComment', 'getSection', 'getMessage', 'getAttribute', 'getTag', 'getIdentifier', 'getVariant', 'getSymbol', 'getNumber', 'getPattern', 'getExpression', 'getSelectorExpression', 'getCallArg', 'getString', 'getLiteral'].forEach(function (name) {
      return _this[name] = withSpan(_this[name]);
    });
  }

  createClass(FluentParser, [{
    key: 'parse',
    value: function parse(source) {
      var comment = null;

      var ps = new FTLParserStream(source);
      ps.skipWSLines();

      var entries = [];

      while (ps.current()) {
        var entry = this.getEntryOrJunk(ps);

        if (entry.type === 'Comment' && entries.length === 0) {
          comment = entry;
        } else {
          entries.push(entry);
        }

        ps.skipWSLines();
      }

      var res = new Resource(entries, comment);

      if (this.withSpans) {
        res.addSpan(0, ps.getIndex());
      }

      return res;
    }
  }, {
    key: 'parseEntry',
    value: function parseEntry(source) {
      var ps = new FTLParserStream(source);
      ps.skipWSLines();
      return this.getEntryOrJunk(ps);
    }
  }, {
    key: 'getEntryOrJunk',
    value: function getEntryOrJunk(ps) {
      var entryStartPos = ps.getIndex();

      try {
        var entry = this.getEntry(ps);
        if (this.withSpans) {
          entry.addSpan(entryStartPos, ps.getIndex());
        }
        return entry;
      } catch (err) {
        if (!(err instanceof ParseError)) {
          throw err;
        }

        var errorIndex = ps.getIndex();
        ps.skipToNextEntryStart();
        var nextEntryStart = ps.getIndex();

        // Create a Junk instance
        var slice = ps.getSlice(entryStartPos, nextEntryStart);
        var junk = new Junk(slice);
        if (this.withSpans) {
          junk.addSpan(entryStartPos, nextEntryStart);
        }
        var annot = new Annotation(err.code, err.args, err.message);
        annot.addSpan(errorIndex, errorIndex);
        junk.addAnnotation(annot);
        return junk;
      }
    }
  }, {
    key: 'getEntry',
    value: function getEntry(ps) {
      var comment = void 0;

      if (ps.currentIs('/')) {
        comment = this.getComment(ps);
      }

      if (ps.currentIs('[')) {
        return this.getSection(ps, comment);
      }

      if (ps.isIDStart()) {
        return this.getMessage(ps, comment);
      }

      if (comment) {
        return comment;
      }
      throw new ParseError('E0002');
    }
  }, {
    key: 'getComment',
    value: function getComment(ps) {
      ps.expectChar('/');
      ps.expectChar('/');
      ps.takeCharIf(' ');

      var content = '';

      while (true) {
        var ch = void 0;
        while (ch = ps.takeChar(function (x) {
          return x !== '\n';
        })) {
          content += ch;
        }

        ps.next();

        if (ps.current() === '/') {
          content += '\n';
          ps.next();
          ps.expectChar('/');
          ps.takeCharIf(' ');
        } else {
          break;
        }
      }
      return new Comment(content);
    }
  }, {
    key: 'getSection',
    value: function getSection(ps, comment) {
      ps.expectChar('[');
      ps.expectChar('[');

      ps.skipLineWS();

      var symb = this.getSymbol(ps);

      ps.skipLineWS();

      ps.expectChar(']');
      ps.expectChar(']');

      ps.skipLineWS();

      ps.expectChar('\n');

      return new Section(symb, comment);
    }
  }, {
    key: 'getMessage',
    value: function getMessage(ps, comment) {
      var id = this.getIdentifier(ps);

      ps.skipLineWS();

      var pattern = void 0;
      var attrs = void 0;
      var tags = void 0;

      if (ps.currentIs('=')) {
        ps.next();
        ps.skipLineWS();

        pattern = this.getPattern(ps);
      }

      if (ps.isPeekNextLineAttributeStart()) {
        attrs = this.getAttributes(ps);
      }

      if (ps.isPeekNextLineTagStart()) {
        if (attrs !== undefined) {
          throw new ParseError('E0012');
        }
        tags = this.getTags(ps);
      }

      if (pattern === undefined && attrs === undefined && tags === undefined) {
        throw new ParseError('E0005', id.name);
      }

      return new Message(id, pattern, attrs, tags, comment);
    }
  }, {
    key: 'getAttribute',
    value: function getAttribute(ps) {
      ps.expectChar('.');

      var key = this.getIdentifier(ps);

      ps.skipLineWS();
      ps.expectChar('=');
      ps.skipLineWS();

      var value = this.getPattern(ps);

      if (value === undefined) {
        throw new ParseError('E0006', 'value');
      }

      return new Attribute(key, value);
    }
  }, {
    key: 'getAttributes',
    value: function getAttributes(ps) {
      var attrs = [];

      while (true) {
        ps.expectChar('\n');
        ps.skipLineWS();

        var attr = this.getAttribute(ps);
        attrs.push(attr);

        if (!ps.isPeekNextLineAttributeStart()) {
          break;
        }
      }
      return attrs;
    }
  }, {
    key: 'getTag',
    value: function getTag(ps) {
      ps.expectChar('#');
      var symb = this.getSymbol(ps);
      return new Tag(symb);
    }
  }, {
    key: 'getTags',
    value: function getTags(ps) {
      var tags = [];

      while (true) {
        ps.expectChar('\n');
        ps.skipLineWS();

        var tag = this.getTag(ps);
        tags.push(tag);

        if (!ps.isPeekNextLineTagStart()) {
          break;
        }
      }
      return tags;
    }
  }, {
    key: 'getIdentifier',
    value: function getIdentifier(ps) {
      var name = '';

      name += ps.takeIDStart();

      var ch = void 0;
      while (ch = ps.takeIDChar()) {
        name += ch;
      }

      return new Identifier(name);
    }
  }, {
    key: 'getVariantKey',
    value: function getVariantKey(ps) {
      var ch = ps.current();

      if (!ch) {
        throw new ParseError('E0013');
      }

      var cc = ch.charCodeAt(0);

      if (cc >= 48 && cc <= 57 || cc === 45) {
        // 0-9, -
        return this.getNumber(ps);
      }

      return this.getSymbol(ps);
    }
  }, {
    key: 'getVariant',
    value: function getVariant(ps, hasDefault) {
      var defaultIndex = false;

      if (ps.currentIs('*')) {
        if (hasDefault) {
          throw new ParseError('E0015');
        }
        ps.next();
        defaultIndex = true;
        hasDefault = true;
      }

      ps.expectChar('[');

      var key = this.getVariantKey(ps);

      ps.expectChar(']');

      ps.skipLineWS();

      var value = this.getPattern(ps);

      if (!value) {
        throw new ParseError('E0006', 'value');
      }

      return new Variant(key, value, defaultIndex);
    }
  }, {
    key: 'getVariants',
    value: function getVariants(ps) {
      var variants = [];
      var hasDefault = false;

      while (true) {
        ps.expectChar('\n');
        ps.skipLineWS();

        var variant = this.getVariant(ps, hasDefault);

        if (variant.default) {
          hasDefault = true;
        }

        variants.push(variant);

        if (!ps.isPeekNextLineVariantStart()) {
          break;
        }
      }

      if (!hasDefault) {
        throw new ParseError('E0010');
      }

      return variants;
    }
  }, {
    key: 'getSymbol',
    value: function getSymbol(ps) {
      var name = '';

      name += ps.takeIDStart();

      while (true) {
        var ch = ps.takeSymbChar();
        if (ch) {
          name += ch;
        } else {
          break;
        }
      }

      return new _Symbol(name.trimRight());
    }
  }, {
    key: 'getDigits',
    value: function getDigits(ps) {
      var num = '';

      var ch = void 0;
      while (ch = ps.takeDigit()) {
        num += ch;
      }

      if (num.length === 0) {
        throw new ParseError('E0004', '0-9');
      }

      return num;
    }
  }, {
    key: 'getNumber',
    value: function getNumber(ps) {
      var num = '';

      if (ps.currentIs('-')) {
        num += '-';
        ps.next();
      }

      num = '' + num + this.getDigits(ps);

      if (ps.currentIs('.')) {
        num += '.';
        ps.next();
        num = '' + num + this.getDigits(ps);
      }

      return new NumberExpression(num);
    }
  }, {
    key: 'getPattern',
    value: function getPattern(ps) {
      var buffer = '';
      var elements = [];
      var firstLine = true;

      if (this.withSpans) {
        var spanStart = ps.getIndex();
      }

      var ch = void 0;
      while (ch = ps.current()) {
        if (ch === '\n') {
          if (firstLine && buffer.length !== 0) {
            break;
          }

          if (!ps.isPeekNextLinePattern()) {
            break;
          }

          ps.next();
          ps.skipLineWS();

          if (!firstLine) {
            buffer += ch;
          }
          firstLine = false;
          continue;
        } else if (ch === '\\') {
          var ch2 = ps.peek();
          if (ch2 === '{' || ch2 === '"') {
            buffer += ch2;
          } else {
            buffer += ch + ch2;
          }
          ps.next();
        } else if (ch === '{') {
          ps.next();

          ps.skipLineWS();

          if (buffer.length !== 0) {
            var text = new TextElement(buffer);
            if (this.withSpans) {
              text.addSpan(spanStart, ps.getIndex());
            }
            elements.push(text);
          }

          buffer = '';

          elements.push(this.getExpression(ps));

          ps.expectChar('}');

          if (this.withSpans) {
            spanStart = ps.getIndex();
          }

          continue;
        } else {
          buffer += ps.ch;
        }
        ps.next();
      }

      if (buffer.length !== 0) {
        var _text = new TextElement(buffer);
        if (this.withSpans) {
          _text.addSpan(spanStart, ps.getIndex());
        }
        elements.push(_text);
      }

      return new Pattern(elements);
    }
  }, {
    key: 'getExpression',
    value: function getExpression(ps) {
      if (ps.isPeekNextLineVariantStart()) {
        var variants = this.getVariants(ps);

        ps.expectChar('\n');
        ps.expectChar(' ');
        ps.skipLineWS();

        return new SelectExpression(null, variants);
      }

      var selector = this.getSelectorExpression(ps);

      ps.skipLineWS();

      if (ps.currentIs('-')) {
        ps.peek();
        if (!ps.currentPeekIs('>')) {
          ps.resetPeek();
        } else {
          ps.next();
          ps.next();

          ps.skipLineWS();

          var _variants = this.getVariants(ps);

          if (_variants.length === 0) {
            throw new ParseError('E0011');
          }

          ps.expectChar('\n');
          ps.expectChar(' ');
          ps.skipLineWS();

          return new SelectExpression(selector, _variants);
        }
      }

      return selector;
    }
  }, {
    key: 'getSelectorExpression',
    value: function getSelectorExpression(ps) {
      var literal = this.getLiteral(ps);

      if (literal.type !== 'MessageReference') {
        return literal;
      }

      var ch = ps.current();

      if (ch === '.') {
        ps.next();

        var attr = this.getIdentifier(ps);
        return new AttributeExpression(literal.id, attr);
      }

      if (ch === '[') {
        ps.next();

        var key = this.getVariantKey(ps);

        ps.expectChar(']');

        return new VariantExpression(literal.id, key);
      }

      if (ch === '(') {
        ps.next();

        var args = this.getCallArgs(ps);

        ps.expectChar(')');

        return new CallExpression(literal.id, args);
      }

      return literal;
    }
  }, {
    key: 'getCallArg',
    value: function getCallArg(ps) {
      var exp = this.getSelectorExpression(ps);

      ps.skipLineWS();

      if (ps.current() !== ':') {
        return exp;
      }

      if (exp.type !== 'MessageReference') {
        throw new ParseError('E0009');
      }

      ps.next();
      ps.skipLineWS();

      var val = this.getArgVal(ps);

      return new NamedArgument(exp.id, val);
    }
  }, {
    key: 'getCallArgs',
    value: function getCallArgs(ps) {
      var args = [];

      ps.skipLineWS();

      while (true) {
        if (ps.current() === ')') {
          break;
        }

        var arg = this.getCallArg(ps);
        args.push(arg);

        ps.skipLineWS();

        if (ps.current() === ',') {
          ps.next();
          ps.skipLineWS();
          continue;
        } else {
          break;
        }
      }
      return args;
    }
  }, {
    key: 'getArgVal',
    value: function getArgVal(ps) {
      if (ps.isNumberStart()) {
        return this.getNumber(ps);
      } else if (ps.currentIs('"')) {
        return this.getString(ps);
      }
      throw new ParseError('E0006', 'value');
    }
  }, {
    key: 'getString',
    value: function getString(ps) {
      var val = '';

      ps.expectChar('"');

      var ch = void 0;
      while (ch = ps.takeChar(function (x) {
        return x !== '"';
      })) {
        val += ch;
      }

      ps.next();

      return new StringExpression(val);
    }
  }, {
    key: 'getLiteral',
    value: function getLiteral(ps) {
      var ch = ps.current();

      if (!ch) {
        throw new ParseError('E0014');
      }

      if (ps.isNumberStart()) {
        return this.getNumber(ps);
      } else if (ch === '"') {
        return this.getString(ps);
      } else if (ch === '$') {
        ps.next();
        var _name = this.getIdentifier(ps);
        return new ExternalArgument(_name);
      }

      var name = this.getIdentifier(ps);
      return new MessageReference(name);
    }
  }]);
  return FluentParser;
}();

function indent(content) {
  return content.split('\n').join('\n    ');
}

function containNewLine(elems) {
  var withNewLine = elems.filter(function (elem) {
    return elem.type === 'TextElement' && elem.value.includes('\n');
  });
  return !!withNewLine.length;
}

var FluentSerializer = function () {
  function FluentSerializer() {
    var _ref = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {},
        _ref$withJunk = _ref.withJunk,
        withJunk = _ref$withJunk === undefined ? false : _ref$withJunk;

    classCallCheck(this, FluentSerializer);

    this.withJunk = withJunk;
  }

  createClass(FluentSerializer, [{
    key: 'serialize',
    value: function serialize(resource) {
      var parts = [];

      if (resource.comment) {
        parts.push(serializeComment(resource.comment) + '\n\n');
      }

      var _iteratorNormalCompletion = true;
      var _didIteratorError = false;
      var _iteratorError = undefined;

      try {
        for (var _iterator = resource.body[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
          var entry = _step.value;

          if (entry.types !== 'Junk' || this.withJunk) {
            parts.push(this.serializeEntry(entry));
          }
        }
      } catch (err) {
        _didIteratorError = true;
        _iteratorError = err;
      } finally {
        try {
          if (!_iteratorNormalCompletion && _iterator.return) {
            _iterator.return();
          }
        } finally {
          if (_didIteratorError) {
            throw _iteratorError;
          }
        }
      }

      return parts.join('');
    }
  }, {
    key: 'serializeEntry',
    value: function serializeEntry(entry) {
      switch (entry.type) {
        case 'Message':
          return serializeMessage(entry);
        case 'Section':
          return serializeSection(entry);
        case 'Comment':
          return serializeComment(entry);
        case 'Junk':
          return serializeJunk(entry);
        default:
          throw new Error('Unknown entry type: ' + entry.type);
      }
    }
  }]);
  return FluentSerializer;
}();

function serializeComment(comment) {
  return comment.content.split('\n').map(function (line) {
    return '// ' + line;
  }).join('\n');
}

function serializeSection(section) {
  var name = serializeSymbol(section.name);

  if (section.comment) {
    var comment = serializeComment(section.comment);
    return '\n\n' + comment + '\n[[ ' + name + ' ]]\n\n';
  }

  return '\n\n[[ ' + name + ' ]]\n\n';
}

function serializeJunk(junk) {
  return junk.content;
}

function serializeMessage(message) {
  var parts = [];

  if (message.comment) {
    parts.push(serializeComment(message.comment));
    parts.push('\n');
  }

  parts.push(serializeIdentifier(message.id));

  if (message.value) {
    parts.push(' =');
    parts.push(serializeValue(message.value));
  }

  var _iteratorNormalCompletion2 = true;
  var _didIteratorError2 = false;
  var _iteratorError2 = undefined;

  try {
    for (var _iterator2 = message.tags[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
      var tag = _step2.value;

      parts.push(serializeTag(tag));
    }
  } catch (err) {
    _didIteratorError2 = true;
    _iteratorError2 = err;
  } finally {
    try {
      if (!_iteratorNormalCompletion2 && _iterator2.return) {
        _iterator2.return();
      }
    } finally {
      if (_didIteratorError2) {
        throw _iteratorError2;
      }
    }
  }

  var _iteratorNormalCompletion3 = true;
  var _didIteratorError3 = false;
  var _iteratorError3 = undefined;

  try {
    for (var _iterator3 = message.attributes[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {
      var attribute = _step3.value;

      parts.push(serializeAttribute(attribute));
    }
  } catch (err) {
    _didIteratorError3 = true;
    _iteratorError3 = err;
  } finally {
    try {
      if (!_iteratorNormalCompletion3 && _iterator3.return) {
        _iterator3.return();
      }
    } finally {
      if (_didIteratorError3) {
        throw _iteratorError3;
      }
    }
  }

  parts.push('\n');
  return parts.join('');
}

function serializeTag(tag) {
  var name = serializeSymbol(tag.name);
  return '\n    #' + name;
}

function serializeAttribute(attribute) {
  var id = serializeIdentifier(attribute.id);
  var value = indent(serializeValue(attribute.value));
  return '\n    .' + id + ' =' + value;
}

function serializeValue(pattern) {
  var content = indent(serializePattern(pattern));
  var multi = containNewLine(pattern.elements);

  if (multi) {
    return '\n    ' + content;
  }

  return ' ' + content;
}

function serializePattern(pattern) {
  return pattern.elements.map(serializeElement).join('');
}

function serializeElement(element) {
  switch (element.type) {
    case 'TextElement':
      return serializeTextElement(element);
    case 'SelectExpression':
      return '{' + serializeSelectExpression(element) + '}';
    default:
      return '{ ' + serializeExpression(element) + ' }';
  }
}

function serializeTextElement(text) {
  return text.value;
}

function serializeExpression(expr) {
  switch (expr.type) {
    case 'StringExpression':
      return serializeStringExpression(expr);
    case 'NumberExpression':
      return serializeNumberExpression(expr);
    case 'MessageReference':
      return serializeMessageReference(expr);
    case 'ExternalArgument':
      return serializeExternalArgument(expr);
    case 'AttributeExpression':
      return serializeAttributeExpression(expr);
    case 'VariantExpression':
      return serializeVariantExpression(expr);
    case 'CallExpression':
      return serializeCallExpression(expr);
    default:
      throw new Error('Unknown expression type: ' + expr.type);
  }
}

function serializeStringExpression(expr) {
  return '"' + expr.value + '"';
}

function serializeNumberExpression(expr) {
  return expr.value;
}

function serializeMessageReference(expr) {
  return serializeIdentifier(expr.id);
}

function serializeExternalArgument(expr) {
  return '$' + serializeIdentifier(expr.id);
}

function serializeSelectExpression(expr) {
  var parts = [];

  if (expr.expression) {
    var selector = ' ' + serializeExpression(expr.expression) + ' ->';
    parts.push(selector);
  }

  var _iteratorNormalCompletion4 = true;
  var _didIteratorError4 = false;
  var _iteratorError4 = undefined;

  try {
    for (var _iterator4 = expr.variants[Symbol.iterator](), _step4; !(_iteratorNormalCompletion4 = (_step4 = _iterator4.next()).done); _iteratorNormalCompletion4 = true) {
      var variant = _step4.value;

      parts.push(serializeVariant(variant));
    }
  } catch (err) {
    _didIteratorError4 = true;
    _iteratorError4 = err;
  } finally {
    try {
      if (!_iteratorNormalCompletion4 && _iterator4.return) {
        _iterator4.return();
      }
    } finally {
      if (_didIteratorError4) {
        throw _iteratorError4;
      }
    }
  }

  parts.push('\n');
  return parts.join('');
}

function serializeVariant(variant) {
  var key = serializeVariantKey(variant.key);
  var value = indent(serializeValue(variant.value));

  if (variant.default) {
    return '\n   *[' + key + ']' + value;
  }

  return '\n    [' + key + ']' + value;
}

function serializeAttributeExpression(expr) {
  var id = serializeIdentifier(expr.id);
  var name = serializeIdentifier(expr.name);
  return id + '.' + name;
}

function serializeVariantExpression(expr) {
  var id = serializeIdentifier(expr.id);
  var key = serializeVariantKey(expr.key);
  return id + '[' + key + ']';
}

function serializeCallExpression(expr) {
  var fun = serializeFunction(expr.callee);
  var args = expr.args.map(serializeCallArgument).join(', ');
  return fun + '(' + args + ')';
}

function serializeCallArgument(arg) {
  switch (arg.type) {
    case 'NamedArgument':
      return serializeNamedArgument(arg);
    default:
      return serializeExpression(arg);
  }
}

function serializeNamedArgument(arg) {
  var name = serializeIdentifier(arg.name);
  var value = serializeArgumentValue(arg.val);
  return name + ': ' + value;
}

function serializeArgumentValue(argval) {
  switch (argval.type) {
    case 'StringExpression':
      return serializeStringExpression(argval);
    case 'NumberExpression':
      return serializeNumberExpression(argval);
    default:
      throw new Error('Unknown argument type: ' + argval.type);
  }
}

function serializeIdentifier(identifier) {
  return identifier.name;
}

function serializeSymbol(symbol) {
  return symbol.name;
}

function serializeVariantKey(key) {
  switch (key.type) {
    case 'Symbol':
      return serializeSymbol(key);
    case 'NumberExpression':
      return serializeNumberExpression(key);
    default:
      throw new Error('Unknown variant key type: ' + key.type);
  }
}

function serializeFunction(fun) {
  return fun.name;
}

function parse(source, opts) {
  var parser = new FluentParser(opts);
  return parser.parse(source);
}

function serialize(resource, opts) {
  var serializer = new FluentSerializer(opts);
  return serializer.serialize(resource);
}

function lineOffset(source, pos) {
  // Substract 1 to get the offset.
  return source.substring(0, pos).split('\n').length - 1;
}

function columnOffset(source, pos) {
  var lastLineBreak = source.lastIndexOf('\n', pos);
  return lastLineBreak === -1 ? pos
  // Substracting two offsets gives length; substract 1 to get the offset.
  : pos - lastLineBreak - 1;
}

exports.FluentParser = FluentParser;
exports.FluentSerializer = FluentSerializer;
exports.parse = parse;
exports.serialize = serialize;
exports.lineOffset = lineOffset;
exports.columnOffset = columnOffset;
exports.Resource = Resource;
exports.Entry = Entry;
exports.Message = Message;
exports.Pattern = Pattern;
exports.TextElement = TextElement;
exports.Expression = Expression;
exports.StringExpression = StringExpression;
exports.NumberExpression = NumberExpression;
exports.MessageReference = MessageReference;
exports.ExternalArgument = ExternalArgument;
exports.SelectExpression = SelectExpression;
exports.AttributeExpression = AttributeExpression;
exports.VariantExpression = VariantExpression;
exports.CallExpression = CallExpression;
exports.Attribute = Attribute;
exports.Tag = Tag;
exports.Variant = Variant;
exports.NamedArgument = NamedArgument;
exports.Identifier = Identifier;
exports.Symbol = _Symbol;
exports.Comment = Comment;
exports.Section = Section;
exports.Function = Function$1;
exports.Junk = Junk;
exports.Span = Span;
exports.Annotation = Annotation;

Object.defineProperty(exports, '__esModule', { value: true });

})));
