/* fluent-syntax@0.7.0 */
(function (global, factory) {
	typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
	typeof define === 'function' && define.amd ? define('fluent-syntax', ['exports'], factory) :
	(factory((global.FluentSyntax = {})));
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
    key: "addSpan",
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
    classCallCheck(this, Resource);

    var _this2 = possibleConstructorReturn(this, (Resource.__proto__ || Object.getPrototypeOf(Resource)).call(this));

    _this2.type = "Resource";
    _this2.body = body;
    return _this2;
  }

  return Resource;
}(SyntaxNode);

var Entry = function (_SyntaxNode2) {
  inherits(Entry, _SyntaxNode2);

  function Entry() {
    classCallCheck(this, Entry);

    var _this3 = possibleConstructorReturn(this, (Entry.__proto__ || Object.getPrototypeOf(Entry)).call(this));

    _this3.type = "Entry";
    _this3.annotations = [];
    return _this3;
  }

  createClass(Entry, [{
    key: "addAnnotation",
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
    var comment = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : null;
    classCallCheck(this, Message);

    var _this4 = possibleConstructorReturn(this, (Message.__proto__ || Object.getPrototypeOf(Message)).call(this));

    _this4.type = "Message";
    _this4.id = id;
    _this4.value = value;
    _this4.attributes = attributes;
    _this4.comment = comment;
    return _this4;
  }

  return Message;
}(Entry);

var Term = function (_Entry2) {
  inherits(Term, _Entry2);

  function Term(id, value) {
    var attributes = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : [];
    var comment = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : null;
    classCallCheck(this, Term);

    var _this5 = possibleConstructorReturn(this, (Term.__proto__ || Object.getPrototypeOf(Term)).call(this));

    _this5.type = "Term";
    _this5.id = id;
    _this5.value = value;
    _this5.attributes = attributes;
    _this5.comment = comment;
    return _this5;
  }

  return Term;
}(Entry);

var Pattern = function (_SyntaxNode3) {
  inherits(Pattern, _SyntaxNode3);

  function Pattern(elements) {
    classCallCheck(this, Pattern);

    var _this6 = possibleConstructorReturn(this, (Pattern.__proto__ || Object.getPrototypeOf(Pattern)).call(this));

    _this6.type = "Pattern";
    _this6.elements = elements;
    return _this6;
  }

  return Pattern;
}(SyntaxNode);

var TextElement = function (_SyntaxNode4) {
  inherits(TextElement, _SyntaxNode4);

  function TextElement(value) {
    classCallCheck(this, TextElement);

    var _this7 = possibleConstructorReturn(this, (TextElement.__proto__ || Object.getPrototypeOf(TextElement)).call(this));

    _this7.type = "TextElement";
    _this7.value = value;
    return _this7;
  }

  return TextElement;
}(SyntaxNode);

var Placeable = function (_SyntaxNode5) {
  inherits(Placeable, _SyntaxNode5);

  function Placeable(expression) {
    classCallCheck(this, Placeable);

    var _this8 = possibleConstructorReturn(this, (Placeable.__proto__ || Object.getPrototypeOf(Placeable)).call(this));

    _this8.type = "Placeable";
    _this8.expression = expression;
    return _this8;
  }

  return Placeable;
}(SyntaxNode);

var Expression = function (_SyntaxNode6) {
  inherits(Expression, _SyntaxNode6);

  function Expression() {
    classCallCheck(this, Expression);

    var _this9 = possibleConstructorReturn(this, (Expression.__proto__ || Object.getPrototypeOf(Expression)).call(this));

    _this9.type = "Expression";
    return _this9;
  }

  return Expression;
}(SyntaxNode);

var StringExpression = function (_Expression) {
  inherits(StringExpression, _Expression);

  function StringExpression(value) {
    classCallCheck(this, StringExpression);

    var _this10 = possibleConstructorReturn(this, (StringExpression.__proto__ || Object.getPrototypeOf(StringExpression)).call(this));

    _this10.type = "StringExpression";
    _this10.value = value;
    return _this10;
  }

  return StringExpression;
}(Expression);

var NumberExpression = function (_Expression2) {
  inherits(NumberExpression, _Expression2);

  function NumberExpression(value) {
    classCallCheck(this, NumberExpression);

    var _this11 = possibleConstructorReturn(this, (NumberExpression.__proto__ || Object.getPrototypeOf(NumberExpression)).call(this));

    _this11.type = "NumberExpression";
    _this11.value = value;
    return _this11;
  }

  return NumberExpression;
}(Expression);

var MessageReference = function (_Expression3) {
  inherits(MessageReference, _Expression3);

  function MessageReference(id) {
    classCallCheck(this, MessageReference);

    var _this12 = possibleConstructorReturn(this, (MessageReference.__proto__ || Object.getPrototypeOf(MessageReference)).call(this));

    _this12.type = "MessageReference";
    _this12.id = id;
    return _this12;
  }

  return MessageReference;
}(Expression);

var ExternalArgument = function (_Expression4) {
  inherits(ExternalArgument, _Expression4);

  function ExternalArgument(id) {
    classCallCheck(this, ExternalArgument);

    var _this13 = possibleConstructorReturn(this, (ExternalArgument.__proto__ || Object.getPrototypeOf(ExternalArgument)).call(this));

    _this13.type = "ExternalArgument";
    _this13.id = id;
    return _this13;
  }

  return ExternalArgument;
}(Expression);

var SelectExpression = function (_Expression5) {
  inherits(SelectExpression, _Expression5);

  function SelectExpression(expression, variants) {
    classCallCheck(this, SelectExpression);

    var _this14 = possibleConstructorReturn(this, (SelectExpression.__proto__ || Object.getPrototypeOf(SelectExpression)).call(this));

    _this14.type = "SelectExpression";
    _this14.expression = expression;
    _this14.variants = variants;
    return _this14;
  }

  return SelectExpression;
}(Expression);

var AttributeExpression = function (_Expression6) {
  inherits(AttributeExpression, _Expression6);

  function AttributeExpression(id, name) {
    classCallCheck(this, AttributeExpression);

    var _this15 = possibleConstructorReturn(this, (AttributeExpression.__proto__ || Object.getPrototypeOf(AttributeExpression)).call(this));

    _this15.type = "AttributeExpression";
    _this15.id = id;
    _this15.name = name;
    return _this15;
  }

  return AttributeExpression;
}(Expression);

var VariantExpression = function (_Expression7) {
  inherits(VariantExpression, _Expression7);

  function VariantExpression(ref, key) {
    classCallCheck(this, VariantExpression);

    var _this16 = possibleConstructorReturn(this, (VariantExpression.__proto__ || Object.getPrototypeOf(VariantExpression)).call(this));

    _this16.type = "VariantExpression";
    _this16.ref = ref;
    _this16.key = key;
    return _this16;
  }

  return VariantExpression;
}(Expression);

var CallExpression = function (_Expression8) {
  inherits(CallExpression, _Expression8);

  function CallExpression(callee) {
    var args = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
    classCallCheck(this, CallExpression);

    var _this17 = possibleConstructorReturn(this, (CallExpression.__proto__ || Object.getPrototypeOf(CallExpression)).call(this));

    _this17.type = "CallExpression";
    _this17.callee = callee;
    _this17.args = args;
    return _this17;
  }

  return CallExpression;
}(Expression);

var Attribute = function (_SyntaxNode7) {
  inherits(Attribute, _SyntaxNode7);

  function Attribute(id, value) {
    classCallCheck(this, Attribute);

    var _this18 = possibleConstructorReturn(this, (Attribute.__proto__ || Object.getPrototypeOf(Attribute)).call(this));

    _this18.type = "Attribute";
    _this18.id = id;
    _this18.value = value;
    return _this18;
  }

  return Attribute;
}(SyntaxNode);

var Variant = function (_SyntaxNode8) {
  inherits(Variant, _SyntaxNode8);

  function Variant(key, value) {
    var def = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
    classCallCheck(this, Variant);

    var _this19 = possibleConstructorReturn(this, (Variant.__proto__ || Object.getPrototypeOf(Variant)).call(this));

    _this19.type = "Variant";
    _this19.key = key;
    _this19.value = value;
    _this19.default = def;
    return _this19;
  }

  return Variant;
}(SyntaxNode);

var NamedArgument = function (_SyntaxNode9) {
  inherits(NamedArgument, _SyntaxNode9);

  function NamedArgument(name, val) {
    classCallCheck(this, NamedArgument);

    var _this20 = possibleConstructorReturn(this, (NamedArgument.__proto__ || Object.getPrototypeOf(NamedArgument)).call(this));

    _this20.type = "NamedArgument";
    _this20.name = name;
    _this20.val = val;
    return _this20;
  }

  return NamedArgument;
}(SyntaxNode);

var Identifier = function (_SyntaxNode10) {
  inherits(Identifier, _SyntaxNode10);

  function Identifier(name) {
    classCallCheck(this, Identifier);

    var _this21 = possibleConstructorReturn(this, (Identifier.__proto__ || Object.getPrototypeOf(Identifier)).call(this));

    _this21.type = "Identifier";
    _this21.name = name;
    return _this21;
  }

  return Identifier;
}(SyntaxNode);

var VariantName = function (_Identifier) {
  inherits(VariantName, _Identifier);

  function VariantName(name) {
    classCallCheck(this, VariantName);

    var _this22 = possibleConstructorReturn(this, (VariantName.__proto__ || Object.getPrototypeOf(VariantName)).call(this, name));

    _this22.type = "VariantName";
    return _this22;
  }

  return VariantName;
}(Identifier);

var BaseComment = function (_Entry3) {
  inherits(BaseComment, _Entry3);

  function BaseComment(content) {
    classCallCheck(this, BaseComment);

    var _this23 = possibleConstructorReturn(this, (BaseComment.__proto__ || Object.getPrototypeOf(BaseComment)).call(this));

    _this23.type = "BaseComment";
    _this23.content = content;
    return _this23;
  }

  return BaseComment;
}(Entry);

var Comment = function (_BaseComment) {
  inherits(Comment, _BaseComment);

  function Comment(content) {
    classCallCheck(this, Comment);

    var _this24 = possibleConstructorReturn(this, (Comment.__proto__ || Object.getPrototypeOf(Comment)).call(this, content));

    _this24.type = "Comment";
    return _this24;
  }

  return Comment;
}(BaseComment);

var GroupComment = function (_BaseComment2) {
  inherits(GroupComment, _BaseComment2);

  function GroupComment(content) {
    classCallCheck(this, GroupComment);

    var _this25 = possibleConstructorReturn(this, (GroupComment.__proto__ || Object.getPrototypeOf(GroupComment)).call(this, content));

    _this25.type = "GroupComment";
    return _this25;
  }

  return GroupComment;
}(BaseComment);
var ResourceComment = function (_BaseComment3) {
  inherits(ResourceComment, _BaseComment3);

  function ResourceComment(content) {
    classCallCheck(this, ResourceComment);

    var _this26 = possibleConstructorReturn(this, (ResourceComment.__proto__ || Object.getPrototypeOf(ResourceComment)).call(this, content));

    _this26.type = "ResourceComment";
    return _this26;
  }

  return ResourceComment;
}(BaseComment);

var Function$1 = function (_Identifier2) {
  inherits(Function, _Identifier2);

  function Function(name) {
    classCallCheck(this, Function);

    var _this27 = possibleConstructorReturn(this, (Function.__proto__ || Object.getPrototypeOf(Function)).call(this, name));

    _this27.type = "Function";
    return _this27;
  }

  return Function;
}(Identifier);

var Junk = function (_Entry4) {
  inherits(Junk, _Entry4);

  function Junk(content) {
    classCallCheck(this, Junk);

    var _this28 = possibleConstructorReturn(this, (Junk.__proto__ || Object.getPrototypeOf(Junk)).call(this));

    _this28.type = "Junk";
    _this28.content = content;
    return _this28;
  }

  return Junk;
}(Entry);

var Span = function (_BaseNode2) {
  inherits(Span, _BaseNode2);

  function Span(start, end) {
    classCallCheck(this, Span);

    var _this29 = possibleConstructorReturn(this, (Span.__proto__ || Object.getPrototypeOf(Span)).call(this));

    _this29.type = "Span";
    _this29.start = start;
    _this29.end = end;
    return _this29;
  }

  return Span;
}(BaseNode);

var Annotation = function (_SyntaxNode11) {
  inherits(Annotation, _SyntaxNode11);

  function Annotation(code) {
    var args = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
    var message = arguments[2];
    classCallCheck(this, Annotation);

    var _this30 = possibleConstructorReturn(this, (Annotation.__proto__ || Object.getPrototypeOf(Annotation)).call(this));

    _this30.type = "Annotation";
    _this30.code = code;
    _this30.args = args;
    _this30.message = message;
    return _this30;
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
    value: function resetPeek(pos) {
      if (pos) {
        if (pos < this.peekIndex) {
          this.peekEnd = false;
        }
        this.peekIndex = pos;
      } else {
        this.peekIndex = this.index;
        this.peekEnd = this.iterEnd;
      }
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

/* eslint-disable complexity */
function getErrorMessage(code, args) {
  switch (code) {
    case "E0001":
      return "Generic error";
    case "E0002":
      return "Expected an entry start";
    case "E0003":
      {
        var _args = slicedToArray(args, 1),
            token = _args[0];

        return "Expected token: \"" + token + "\"";
      }
    case "E0004":
      {
        var _args2 = slicedToArray(args, 1),
            range = _args2[0];

        return "Expected a character from range: \"" + range + "\"";
      }
    case "E0005":
      {
        var _args3 = slicedToArray(args, 1),
            id = _args3[0];

        return "Expected message \"" + id + "\" to have a value or attributes";
      }
    case "E0006":
      {
        var _args4 = slicedToArray(args, 1),
            _id = _args4[0];

        return "Expected term \"" + _id + "\" to have a value";
      }
    case "E0007":
      return "Keyword cannot end with a whitespace";
    case "E0008":
      return "The callee has to be a simple, upper-case identifier";
    case "E0009":
      return "The key has to be a simple identifier";
    case "E0010":
      return "Expected one of the variants to be marked as default (*)";
    case "E0011":
      return 'Expected at least one variant after "->"';
    case "E0012":
      return "Expected value";
    case "E0013":
      return "Expected variant key";
    case "E0014":
      return "Expected literal";
    case "E0015":
      return "Only one variant can be marked as default (*)";
    case "E0016":
      return "Message references cannot be used as selectors";
    case "E0017":
      return "Variants cannot be used as selectors";
    case "E0018":
      return "Attributes of messages cannot be used as selectors";
    case "E0019":
      return "Attributes of terms cannot be used as placeables";
    case "E0020":
      return "Unterminated string expression";
    default:
      return code;
  }
}

function includes(arr, elem) {
  return arr.indexOf(elem) > -1;
}

/* eslint no-magic-numbers: "off" */

var INLINE_WS = [" ", "\t"];
var SPECIAL_LINE_START_CHARS = ["}", ".", "[", "*"];

var FTLParserStream = function (_ParserStream) {
  inherits(FTLParserStream, _ParserStream);

  function FTLParserStream() {
    classCallCheck(this, FTLParserStream);
    return possibleConstructorReturn(this, (FTLParserStream.__proto__ || Object.getPrototypeOf(FTLParserStream)).apply(this, arguments));
  }

  createClass(FTLParserStream, [{
    key: "skipInlineWS",
    value: function skipInlineWS() {
      while (this.ch) {
        if (!includes(INLINE_WS, this.ch)) {
          break;
        }
        this.next();
      }
    }
  }, {
    key: "peekInlineWS",
    value: function peekInlineWS() {
      var ch = this.currentPeek();
      while (ch) {
        if (!includes(INLINE_WS, ch)) {
          break;
        }
        ch = this.peek();
      }
    }
  }, {
    key: "skipBlankLines",
    value: function skipBlankLines() {
      while (true) {
        this.peekInlineWS();

        if (this.currentPeekIs("\n")) {
          this.skipToPeek();
          this.next();
        } else {
          this.resetPeek();
          break;
        }
      }
    }
  }, {
    key: "peekBlankLines",
    value: function peekBlankLines() {
      while (true) {
        var lineStart = this.getPeekIndex();

        this.peekInlineWS();

        if (this.currentPeekIs("\n")) {
          this.peek();
        } else {
          this.resetPeek(lineStart);
          break;
        }
      }
    }
  }, {
    key: "skipIndent",
    value: function skipIndent() {
      this.skipBlankLines();
      this.skipInlineWS();
    }
  }, {
    key: "expectChar",
    value: function expectChar(ch) {
      if (this.ch === ch) {
        this.next();
        return true;
      }

      if (ch === "\n") {
        // Unicode Character 'SYMBOL FOR NEWLINE' (U+2424)
        throw new ParseError("E0003", "\u2424");
      }

      throw new ParseError("E0003", ch);
    }
  }, {
    key: "expectIndent",
    value: function expectIndent() {
      this.expectChar("\n");
      this.skipBlankLines();
      this.expectChar(" ");
      this.skipInlineWS();
    }
  }, {
    key: "takeCharIf",
    value: function takeCharIf(ch) {
      if (this.ch === ch) {
        this.next();
        return true;
      }
      return false;
    }
  }, {
    key: "takeChar",
    value: function takeChar(f) {
      var ch = this.ch;
      if (ch !== undefined && f(ch)) {
        this.next();
        return ch;
      }
      return undefined;
    }
  }, {
    key: "isCharIDStart",
    value: function isCharIDStart(ch) {
      if (ch === undefined) {
        return false;
      }

      var cc = ch.charCodeAt(0);
      return cc >= 97 && cc <= 122 || // a-z
      cc >= 65 && cc <= 90; // A-Z
    }
  }, {
    key: "isEntryIDStart",
    value: function isEntryIDStart() {
      if (this.currentIs("-")) {
        this.peek();
      }

      var ch = this.currentPeek();
      var isID = this.isCharIDStart(ch);
      this.resetPeek();
      return isID;
    }
  }, {
    key: "isNumberStart",
    value: function isNumberStart() {
      if (this.currentIs("-")) {
        this.peek();
      }

      var cc = this.currentPeek().charCodeAt(0);
      var isDigit = cc >= 48 && cc <= 57; // 0-9
      this.resetPeek();
      return isDigit;
    }
  }, {
    key: "isCharPatternContinuation",
    value: function isCharPatternContinuation(ch) {
      if (ch === undefined) {
        return false;
      }

      return !includes(SPECIAL_LINE_START_CHARS, ch);
    }
  }, {
    key: "isPeekPatternStart",
    value: function isPeekPatternStart() {
      this.peekInlineWS();
      var ch = this.currentPeek();

      // Inline Patterns may start with any char.
      if (ch !== undefined && ch !== "\n") {
        return true;
      }

      return this.isPeekNextLinePatternStart();
    }
  }, {
    key: "isPeekNextLineZeroFourStyleComment",
    value: function isPeekNextLineZeroFourStyleComment() {
      if (!this.currentPeekIs("\n")) {
        return false;
      }

      this.peek();

      if (this.currentPeekIs("/")) {
        this.peek();
        if (this.currentPeekIs("/")) {
          this.resetPeek();
          return true;
        }
      }

      this.resetPeek();
      return false;
    }

    // -1 - any
    //  0 - comment
    //  1 - group comment
    //  2 - resource comment

  }, {
    key: "isPeekNextLineComment",
    value: function isPeekNextLineComment() {
      var level = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : -1;

      if (!this.currentPeekIs("\n")) {
        return false;
      }

      var i = 0;

      while (i <= level || level === -1 && i < 3) {
        this.peek();
        if (!this.currentPeekIs("#")) {
          if (i !== level && level !== -1) {
            this.resetPeek();
            return false;
          }
          break;
        }
        i++;
      }

      this.peek();
      if ([" ", "\n"].includes(this.currentPeek())) {
        this.resetPeek();
        return true;
      }

      this.resetPeek();
      return false;
    }
  }, {
    key: "isPeekNextLineVariantStart",
    value: function isPeekNextLineVariantStart() {
      if (!this.currentPeekIs("\n")) {
        return false;
      }

      this.peek();

      this.peekBlankLines();

      var ptr = this.getPeekIndex();

      this.peekInlineWS();

      if (this.getPeekIndex() - ptr === 0) {
        this.resetPeek();
        return false;
      }

      if (this.currentPeekIs("*")) {
        this.peek();
      }

      if (this.currentPeekIs("[") && !this.peekCharIs("[")) {
        this.resetPeek();
        return true;
      }
      this.resetPeek();
      return false;
    }
  }, {
    key: "isPeekNextLineAttributeStart",
    value: function isPeekNextLineAttributeStart() {
      if (!this.currentPeekIs("\n")) {
        return false;
      }

      this.peek();

      this.peekBlankLines();

      var ptr = this.getPeekIndex();

      this.peekInlineWS();

      if (this.getPeekIndex() - ptr === 0) {
        this.resetPeek();
        return false;
      }

      if (this.currentPeekIs(".")) {
        this.resetPeek();
        return true;
      }

      this.resetPeek();
      return false;
    }
  }, {
    key: "isPeekNextLinePatternStart",
    value: function isPeekNextLinePatternStart() {
      if (!this.currentPeekIs("\n")) {
        return false;
      }

      this.peek();

      this.peekBlankLines();

      var ptr = this.getPeekIndex();

      this.peekInlineWS();

      if (this.getPeekIndex() - ptr === 0) {
        this.resetPeek();
        return false;
      }

      if (!this.isCharPatternContinuation(this.currentPeek())) {
        this.resetPeek();
        return false;
      }

      this.resetPeek();
      return true;
    }
  }, {
    key: "skipToNextEntryStart",
    value: function skipToNextEntryStart() {
      while (this.ch) {
        if (this.currentIs("\n") && !this.peekCharIs("\n")) {
          this.next();
          if (this.ch === undefined || this.isEntryIDStart() || this.currentIs("#") || this.currentIs("/") && this.peekCharIs("/") || this.currentIs("[") && this.peekCharIs("[")) {
            break;
          }
        }
        this.next();
      }
    }
  }, {
    key: "takeIDStart",
    value: function takeIDStart(allowTerm) {
      if (allowTerm && this.currentIs("-")) {
        this.next();
        return "-";
      }

      if (this.isCharIDStart(this.ch)) {
        var ret = this.ch;
        this.next();
        return ret;
      }

      var allowedRange = allowTerm ? "a-zA-Z-" : "a-zA-Z";
      throw new ParseError("E0004", allowedRange);
    }
  }, {
    key: "takeIDChar",
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
    key: "takeVariantNameChar",
    value: function takeVariantNameChar() {
      var closure = function closure(ch) {
        var cc = ch.charCodeAt(0);
        return cc >= 97 && cc <= 122 || // a-z
        cc >= 65 && cc <= 90 || // A-Z
        cc >= 48 && cc <= 57 || // 0-9
        cc === 95 || cc === 45 || cc === 32; // _-<space>
      };

      return this.takeChar(closure);
    }
  }, {
    key: "takeDigit",
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
    if (node.type === "Message") {
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
    ["getComment", "getMessage", "getAttribute", "getIdentifier", "getVariant", "getVariantName", "getNumber", "getPattern", "getTextElement", "getPlaceable", "getExpression", "getSelectorExpression", "getCallArg", "getString", "getLiteral", "getGroupCommentFromSection"].forEach(function (name) {
      return _this[name] = withSpan(_this[name]);
    });
  }

  createClass(FluentParser, [{
    key: "parse",
    value: function parse(source) {
      var ps = new FTLParserStream(source);
      ps.skipBlankLines();

      var entries = [];

      while (ps.current()) {
        var entry = this.getEntryOrJunk(ps);

        if (entry === null) {
          // That happens when we get a 0.4 style section
          continue;
        }

        if (entry.type === "Comment" && ps.lastCommentZeroFourSyntax && entries.length === 0) {
          var comment = new ResourceComment(entry.content);
          comment.span = entry.span;
          entries.push(comment);
        } else {
          entries.push(entry);
        }

        ps.lastCommentZeroFourSyntax = false;
        ps.skipBlankLines();
      }

      var res = new Resource(entries);

      if (this.withSpans) {
        res.addSpan(0, ps.getIndex());
      }

      return res;
    }
  }, {
    key: "parseEntry",
    value: function parseEntry(source) {
      var ps = new FTLParserStream(source);
      ps.skipBlankLines();
      return this.getEntryOrJunk(ps);
    }
  }, {
    key: "getEntryOrJunk",
    value: function getEntryOrJunk(ps) {
      var entryStartPos = ps.getIndex();

      try {
        return this.getEntry(ps);
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
    key: "getEntry",
    value: function getEntry(ps) {
      var comment = void 0;

      if (ps.currentIs("/") || ps.currentIs("#")) {
        comment = this.getComment(ps);

        // The Comment content doesn't include the trailing newline. Consume
        // this newline here to be ready for the next entry.  undefined stands
        // for EOF.
        ps.expectChar(ps.current() ? "\n" : undefined);
      }

      if (ps.currentIs("[")) {
        var groupComment = this.getGroupCommentFromSection(ps, comment);
        if (comment && this.withSpans) {
          // The Group Comment should start where the section comment starts.
          groupComment.span.start = comment.span.start;
        }
        return groupComment;
      }

      if (ps.isEntryIDStart() && (!comment || comment.type === "Comment")) {
        return this.getMessage(ps, comment);
      }

      if (comment) {
        return comment;
      }

      throw new ParseError("E0002");
    }
  }, {
    key: "getZeroFourStyleComment",
    value: function getZeroFourStyleComment(ps) {
      ps.expectChar("/");
      ps.expectChar("/");
      ps.takeCharIf(" ");

      var content = "";

      while (true) {
        var ch = void 0;
        while (ch = ps.takeChar(function (x) {
          return x !== "\n";
        })) {
          content += ch;
        }

        if (ps.isPeekNextLineZeroFourStyleComment()) {
          content += "\n";
          ps.next();
          ps.expectChar("/");
          ps.expectChar("/");
          ps.takeCharIf(" ");
        } else {
          break;
        }
      }

      var comment = new Comment(content);
      ps.lastCommentZeroFourSyntax = true;
      return comment;
    }
  }, {
    key: "getComment",
    value: function getComment(ps) {
      if (ps.currentIs("/")) {
        return this.getZeroFourStyleComment(ps);
      }

      // 0 - comment
      // 1 - group comment
      // 2 - resource comment
      var level = -1;
      var content = "";

      while (true) {
        var i = -1;
        while (ps.currentIs("#") && i < (level === -1 ? 2 : level)) {
          ps.next();
          i++;
        }

        if (level === -1) {
          level = i;
        }

        if (!ps.currentIs("\n")) {
          ps.expectChar(" ");
          var ch = void 0;
          while (ch = ps.takeChar(function (x) {
            return x !== "\n";
          })) {
            content += ch;
          }
        }

        if (ps.isPeekNextLineComment(level, false)) {
          content += "\n";
          ps.next();
        } else {
          break;
        }
      }

      var Comment$$1 = void 0;
      switch (level) {
        case 0:
          Comment$$1 = Comment;
          break;
        case 1:
          Comment$$1 = GroupComment;
          break;
        case 2:
          Comment$$1 = ResourceComment;
          break;
      }
      return new Comment$$1(content);
    }
  }, {
    key: "getGroupCommentFromSection",
    value: function getGroupCommentFromSection(ps, comment) {
      ps.expectChar("[");
      ps.expectChar("[");

      ps.skipInlineWS();

      this.getVariantName(ps);

      ps.skipInlineWS();

      ps.expectChar("]");
      ps.expectChar("]");

      if (comment) {
        return new GroupComment(comment.content);
      }

      // A Section without a comment is like an empty Group Comment. Semantically
      // it ends the previous group and starts a new one.
      return new GroupComment("");
    }
  }, {
    key: "getMessage",
    value: function getMessage(ps, comment) {
      var id = this.getEntryIdentifier(ps);

      ps.skipInlineWS();

      var pattern = void 0;
      var attrs = void 0;

      // XXX Syntax 0.4 compatibility.
      // XXX Replace with ps.expectChar('=').
      if (ps.currentIs("=")) {
        ps.next();

        if (ps.isPeekPatternStart()) {
          ps.skipIndent();
          pattern = this.getPattern(ps);
        } else {
          ps.skipInlineWS();
        }
      }

      if (id.name.startsWith("-") && pattern === undefined) {
        throw new ParseError("E0006", id.name);
      }

      if (ps.isPeekNextLineAttributeStart()) {
        attrs = this.getAttributes(ps);
      }

      if (id.name.startsWith("-")) {
        return new Term(id, pattern, attrs, comment);
      }

      if (pattern === undefined && attrs === undefined) {
        throw new ParseError("E0005", id.name);
      }

      return new Message(id, pattern, attrs, comment);
    }
  }, {
    key: "getAttribute",
    value: function getAttribute(ps) {
      ps.expectChar(".");

      var key = this.getIdentifier(ps);

      ps.skipInlineWS();
      ps.expectChar("=");

      if (ps.isPeekPatternStart()) {
        ps.skipIndent();
        var value = this.getPattern(ps);
        return new Attribute(key, value);
      }

      throw new ParseError("E0012");
    }
  }, {
    key: "getAttributes",
    value: function getAttributes(ps) {
      var attrs = [];

      while (true) {
        ps.expectIndent();
        var attr = this.getAttribute(ps);
        attrs.push(attr);

        if (!ps.isPeekNextLineAttributeStart()) {
          break;
        }
      }
      return attrs;
    }
  }, {
    key: "getEntryIdentifier",
    value: function getEntryIdentifier(ps) {
      return this.getIdentifier(ps, true);
    }
  }, {
    key: "getIdentifier",
    value: function getIdentifier(ps) {
      var allowTerm = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;

      var name = "";
      name += ps.takeIDStart(allowTerm);

      var ch = void 0;
      while (ch = ps.takeIDChar()) {
        name += ch;
      }

      return new Identifier(name);
    }
  }, {
    key: "getVariantKey",
    value: function getVariantKey(ps) {
      var ch = ps.current();

      if (!ch) {
        throw new ParseError("E0013");
      }

      var cc = ch.charCodeAt(0);

      if (cc >= 48 && cc <= 57 || cc === 45) {
        // 0-9, -
        return this.getNumber(ps);
      }

      return this.getVariantName(ps);
    }
  }, {
    key: "getVariant",
    value: function getVariant(ps, hasDefault) {
      var defaultIndex = false;

      if (ps.currentIs("*")) {
        if (hasDefault) {
          throw new ParseError("E0015");
        }
        ps.next();
        defaultIndex = true;
        hasDefault = true;
      }

      ps.expectChar("[");

      var key = this.getVariantKey(ps);

      ps.expectChar("]");

      if (ps.isPeekPatternStart()) {
        ps.skipIndent();
        var value = this.getPattern(ps);
        return new Variant(key, value, defaultIndex);
      }

      throw new ParseError("E0012");
    }
  }, {
    key: "getVariants",
    value: function getVariants(ps) {
      var variants = [];
      var hasDefault = false;

      while (true) {
        ps.expectIndent();
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
        throw new ParseError("E0010");
      }

      return variants;
    }
  }, {
    key: "getVariantName",
    value: function getVariantName(ps) {
      var name = "";

      name += ps.takeIDStart(false);

      while (true) {
        var ch = ps.takeVariantNameChar();
        if (ch) {
          name += ch;
        } else {
          break;
        }
      }

      return new VariantName(name.trimRight());
    }
  }, {
    key: "getDigits",
    value: function getDigits(ps) {
      var num = "";

      var ch = void 0;
      while (ch = ps.takeDigit()) {
        num += ch;
      }

      if (num.length === 0) {
        throw new ParseError("E0004", "0-9");
      }

      return num;
    }
  }, {
    key: "getNumber",
    value: function getNumber(ps) {
      var num = "";

      if (ps.currentIs("-")) {
        num += "-";
        ps.next();
      }

      num = "" + num + this.getDigits(ps);

      if (ps.currentIs(".")) {
        num += ".";
        ps.next();
        num = "" + num + this.getDigits(ps);
      }

      return new NumberExpression(num);
    }
  }, {
    key: "getPattern",
    value: function getPattern(ps) {
      var elements = [];
      ps.skipInlineWS();

      var ch = void 0;
      while (ch = ps.current()) {

        // The end condition for getPattern's while loop is a newline
        // which is not followed by a valid pattern continuation.
        if (ch === "\n" && !ps.isPeekNextLinePatternStart()) {
          break;
        }

        if (ch === "{") {
          var element = this.getPlaceable(ps);
          elements.push(element);
        } else {
          var _element = this.getTextElement(ps);
          elements.push(_element);
        }
      }

      return new Pattern(elements);
    }
  }, {
    key: "getTextElement",
    value: function getTextElement(ps) {
      var buffer = "";

      var ch = void 0;
      while (ch = ps.current()) {
        if (ch === "{") {
          return new TextElement(buffer);
        }

        if (ch === "\n") {
          if (!ps.isPeekNextLinePatternStart()) {
            return new TextElement(buffer);
          }

          ps.next();
          ps.skipInlineWS();

          // Add the new line to the buffer
          buffer += ch;
          continue;
        }

        if (ch === "\\") {
          var ch2 = ps.next();

          if (ch2 === "{" || ch2 === '"') {
            buffer += ch2;
          } else {
            buffer += ch + ch2;
          }
        } else {
          buffer += ps.ch;
        }

        ps.next();
      }

      return new TextElement(buffer);
    }
  }, {
    key: "getPlaceable",
    value: function getPlaceable(ps) {
      ps.expectChar("{");
      var expression = this.getExpression(ps);
      ps.expectChar("}");
      return new Placeable(expression);
    }
  }, {
    key: "getExpression",
    value: function getExpression(ps) {
      if (ps.isPeekNextLineVariantStart()) {
        var variants = this.getVariants(ps);

        ps.expectIndent();

        return new SelectExpression(null, variants);
      }

      ps.skipInlineWS();

      var selector = this.getSelectorExpression(ps);

      ps.skipInlineWS();

      if (ps.currentIs("-")) {
        ps.peek();

        if (!ps.currentPeekIs(">")) {
          ps.resetPeek();
          return selector;
        }

        if (selector.type === "MessageReference") {
          throw new ParseError("E0016");
        }

        if (selector.type === "AttributeExpression" && !selector.id.name.startsWith("-")) {
          throw new ParseError("E0018");
        }

        if (selector.type === "VariantExpression") {
          throw new ParseError("E0017");
        }

        ps.next();
        ps.next();

        ps.skipInlineWS();

        var _variants = this.getVariants(ps);

        if (_variants.length === 0) {
          throw new ParseError("E0011");
        }

        ps.expectIndent();

        return new SelectExpression(selector, _variants);
      } else if (selector.type === "AttributeExpression" && selector.id.name.startsWith("-")) {
        throw new ParseError("E0019");
      }

      return selector;
    }
  }, {
    key: "getSelectorExpression",
    value: function getSelectorExpression(ps) {
      var literal = this.getLiteral(ps);

      if (literal.type !== "MessageReference") {
        return literal;
      }

      var ch = ps.current();

      if (ch === ".") {
        ps.next();

        var attr = this.getIdentifier(ps);
        return new AttributeExpression(literal.id, attr);
      }

      if (ch === "[") {
        ps.next();

        var key = this.getVariantKey(ps);

        ps.expectChar("]");

        return new VariantExpression(literal, key);
      }

      if (ch === "(") {
        ps.next();

        var args = this.getCallArgs(ps);

        ps.expectChar(")");

        if (!/^[A-Z][A-Z_?-]*$/.test(literal.id.name)) {
          throw new ParseError("E0008");
        }

        var func = new Function$1(literal.id.name);
        if (this.withSpans) {
          func.addSpan(literal.span.start, literal.span.end);
        }

        return new CallExpression(func, args);
      }

      return literal;
    }
  }, {
    key: "getCallArg",
    value: function getCallArg(ps) {
      var exp = this.getSelectorExpression(ps);

      ps.skipInlineWS();

      if (ps.current() !== ":") {
        return exp;
      }

      if (exp.type !== "MessageReference") {
        throw new ParseError("E0009");
      }

      ps.next();
      ps.skipInlineWS();

      var val = this.getArgVal(ps);

      return new NamedArgument(exp.id, val);
    }
  }, {
    key: "getCallArgs",
    value: function getCallArgs(ps) {
      var args = [];

      ps.skipInlineWS();

      while (true) {
        if (ps.current() === ")") {
          break;
        }

        var arg = this.getCallArg(ps);
        args.push(arg);

        ps.skipInlineWS();

        if (ps.current() === ",") {
          ps.next();
          ps.skipInlineWS();
          continue;
        } else {
          break;
        }
      }
      return args;
    }
  }, {
    key: "getArgVal",
    value: function getArgVal(ps) {
      if (ps.isNumberStart()) {
        return this.getNumber(ps);
      } else if (ps.currentIs('"')) {
        return this.getString(ps);
      }
      throw new ParseError("E0012");
    }
  }, {
    key: "getString",
    value: function getString(ps) {
      var val = "";

      ps.expectChar('"');

      var ch = void 0;
      while (ch = ps.takeChar(function (x) {
        return x !== '"' && x !== "\n";
      })) {
        val += ch;
      }

      if (ps.currentIs("\n")) {
        throw new ParseError("E0020");
      }

      ps.next();

      return new StringExpression(val);
    }
  }, {
    key: "getLiteral",
    value: function getLiteral(ps) {
      var ch = ps.current();

      if (!ch) {
        throw new ParseError("E0014");
      }

      if (ch === "$") {
        ps.next();
        var name = this.getIdentifier(ps);
        return new ExternalArgument(name);
      }

      if (ps.isEntryIDStart()) {
        var _name = this.getEntryIdentifier(ps);
        return new MessageReference(_name);
      }

      if (ps.isNumberStart()) {
        return this.getNumber(ps);
      }

      if (ch === '"') {
        return this.getString(ps);
      }

      throw new ParseError("E0014");
    }
  }]);
  return FluentParser;
}();

function indent(content) {
  return content.split("\n").join("\n    ");
}

function includesNewLine(elem) {
  return elem.type === "TextElement" && includes(elem.value, "\n");
}

function isSelectExpr(elem) {
  return elem.type === "Placeable" && elem.expression.type === "SelectExpression";
}

// Bit masks representing the state of the serializer.
var HAS_ENTRIES = 1;

var FluentSerializer = function () {
  function FluentSerializer() {
    var _ref = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {},
        _ref$withJunk = _ref.withJunk,
        withJunk = _ref$withJunk === undefined ? false : _ref$withJunk;

    classCallCheck(this, FluentSerializer);

    this.withJunk = withJunk;
  }

  createClass(FluentSerializer, [{
    key: "serialize",
    value: function serialize(resource) {
      if (resource.type !== "Resource") {
        throw new Error("Unknown resource type: " + resource.type);
      }

      var state = 0;
      var parts = [];

      var _iteratorNormalCompletion = true;
      var _didIteratorError = false;
      var _iteratorError = undefined;

      try {
        for (var _iterator = resource.body[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
          var entry = _step.value;

          if (entry.type !== "Junk" || this.withJunk) {
            parts.push(this.serializeEntry(entry, state));
            if (!(state & HAS_ENTRIES)) {
              state |= HAS_ENTRIES;
            }
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

      return parts.join("");
    }
  }, {
    key: "serializeEntry",
    value: function serializeEntry(entry) {
      var state = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 0;

      switch (entry.type) {
        case "Message":
        case "Term":
          return serializeMessage(entry);
        case "Comment":
          if (state & HAS_ENTRIES) {
            return "\n" + serializeComment(entry) + "\n\n";
          }
          return serializeComment(entry) + "\n\n";
        case "GroupComment":
          if (state & HAS_ENTRIES) {
            return "\n" + serializeGroupComment(entry) + "\n\n";
          }
          return serializeGroupComment(entry) + "\n\n";
        case "ResourceComment":
          if (state & HAS_ENTRIES) {
            return "\n" + serializeResourceComment(entry) + "\n\n";
          }
          return serializeResourceComment(entry) + "\n\n";
        case "Junk":
          return serializeJunk(entry);
        default:
          throw new Error("Unknown entry type: " + entry.type);
      }
    }
  }, {
    key: "serializeExpression",
    value: function serializeExpression(expr) {
      return _serializeExpression(expr);
    }
  }]);
  return FluentSerializer;
}();


function serializeComment(comment) {
  return comment.content.split("\n").map(function (line) {
    return line.length ? "# " + line : "#";
  }).join("\n");
}

function serializeGroupComment(comment) {
  return comment.content.split("\n").map(function (line) {
    return line.length ? "## " + line : "##";
  }).join("\n");
}

function serializeResourceComment(comment) {
  return comment.content.split("\n").map(function (line) {
    return line.length ? "### " + line : "###";
  }).join("\n");
}

function serializeJunk(junk) {
  return junk.content;
}

function serializeMessage(message) {
  var parts = [];

  if (message.comment) {
    parts.push(serializeComment(message.comment));
    parts.push("\n");
  }

  parts.push(serializeIdentifier(message.id));
  parts.push(" =");

  if (message.value) {
    parts.push(serializeValue(message.value));
  }

  var _iteratorNormalCompletion2 = true;
  var _didIteratorError2 = false;
  var _iteratorError2 = undefined;

  try {
    for (var _iterator2 = message.attributes[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
      var attribute = _step2.value;

      parts.push(serializeAttribute(attribute));
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

  parts.push("\n");
  return parts.join("");
}

function serializeAttribute(attribute) {
  var id = serializeIdentifier(attribute.id);
  var value = indent(serializeValue(attribute.value));
  return "\n    ." + id + " =" + value;
}

function serializeValue(pattern) {
  var content = indent(serializePattern(pattern));

  var startOnNewLine = pattern.elements.some(includesNewLine) || pattern.elements.some(isSelectExpr);

  if (startOnNewLine) {
    return "\n    " + content;
  }

  return " " + content;
}

function serializePattern(pattern) {
  return pattern.elements.map(serializeElement).join("");
}

function serializeElement(element) {
  switch (element.type) {
    case "TextElement":
      return serializeTextElement(element);
    case "Placeable":
      return serializePlaceable(element);
    default:
      throw new Error("Unknown element type: " + element.type);
  }
}

function serializeTextElement(text) {
  return text.value;
}

function serializePlaceable(placeable) {
  var expr = placeable.expression;

  switch (expr.type) {
    case "Placeable":
      return "{" + serializePlaceable(expr) + "}";
    case "SelectExpression":
      // Special-case select expression to control the whitespace around the
      // opening and the closing brace.
      return expr.expression
      // A select expression with a selector.
      ? "{ " + serializeSelectExpression(expr) + "}"
      // A variant list without a selector.
      : "{" + serializeSelectExpression(expr) + "}";
    default:
      return "{ " + _serializeExpression(expr) + " }";
  }
}

function _serializeExpression(expr) {
  switch (expr.type) {
    case "StringExpression":
      return serializeStringExpression(expr);
    case "NumberExpression":
      return serializeNumberExpression(expr);
    case "MessageReference":
      return serializeMessageReference(expr);
    case "ExternalArgument":
      return serializeExternalArgument(expr);
    case "AttributeExpression":
      return serializeAttributeExpression(expr);
    case "VariantExpression":
      return serializeVariantExpression(expr);
    case "CallExpression":
      return serializeCallExpression(expr);
    case "SelectExpression":
      return serializeSelectExpression(expr);
    default:
      throw new Error("Unknown expression type: " + expr.type);
  }
}

function serializeStringExpression(expr) {
  return "\"" + expr.value + "\"";
}

function serializeNumberExpression(expr) {
  return expr.value;
}

function serializeMessageReference(expr) {
  return serializeIdentifier(expr.id);
}

function serializeExternalArgument(expr) {
  return "$" + serializeIdentifier(expr.id);
}

function serializeSelectExpression(expr) {
  var parts = [];

  if (expr.expression) {
    var selector = _serializeExpression(expr.expression) + " ->";
    parts.push(selector);
  }

  var _iteratorNormalCompletion3 = true;
  var _didIteratorError3 = false;
  var _iteratorError3 = undefined;

  try {
    for (var _iterator3 = expr.variants[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {
      var variant = _step3.value;

      parts.push(serializeVariant(variant));
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

  parts.push("\n");
  return parts.join("");
}

function serializeVariant(variant) {
  var key = serializeVariantKey(variant.key);
  var value = indent(serializeValue(variant.value));

  if (variant.default) {
    return "\n   *[" + key + "]" + value;
  }

  return "\n    [" + key + "]" + value;
}

function serializeAttributeExpression(expr) {
  var id = serializeIdentifier(expr.id);
  var name = serializeIdentifier(expr.name);
  return id + "." + name;
}

function serializeVariantExpression(expr) {
  var ref = _serializeExpression(expr.ref);
  var key = serializeVariantKey(expr.key);
  return ref + "[" + key + "]";
}

function serializeCallExpression(expr) {
  var fun = serializeFunction(expr.callee);
  var args = expr.args.map(serializeCallArgument).join(", ");
  return fun + "(" + args + ")";
}

function serializeCallArgument(arg) {
  switch (arg.type) {
    case "NamedArgument":
      return serializeNamedArgument(arg);
    default:
      return _serializeExpression(arg);
  }
}

function serializeNamedArgument(arg) {
  var name = serializeIdentifier(arg.name);
  var value = serializeArgumentValue(arg.val);
  return name + ": " + value;
}

function serializeArgumentValue(argval) {
  switch (argval.type) {
    case "StringExpression":
      return serializeStringExpression(argval);
    case "NumberExpression":
      return serializeNumberExpression(argval);
    default:
      throw new Error("Unknown argument type: " + argval.type);
  }
}

function serializeIdentifier(identifier) {
  return identifier.name;
}

function serializeVariantName(VariantName) {
  return VariantName.name;
}

function serializeVariantKey(key) {
  switch (key.type) {
    case "VariantName":
      return serializeVariantName(key);
    case "NumberExpression":
      return serializeNumberExpression(key);
    default:
      throw new Error("Unknown variant key type: " + key.type);
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
  // Subtract 1 to get the offset.
  return source.substring(0, pos).split("\n").length - 1;
}

function columnOffset(source, pos) {
  // Find the last line break starting backwards from the index just before
  // pos.  This allows us to correctly handle ths case where the character at
  // pos  is a line break as well.
  var fromIndex = pos - 1;
  var prevLineBreak = source.lastIndexOf("\n", fromIndex);

  // pos is a position in the first line of source.
  if (prevLineBreak === -1) {
    return pos;
  }

  // Subtracting two offsets gives length; subtract 1 to get the offset.
  return pos - prevLineBreak - 1;
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
exports.Term = Term;
exports.Pattern = Pattern;
exports.TextElement = TextElement;
exports.Placeable = Placeable;
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
exports.Variant = Variant;
exports.NamedArgument = NamedArgument;
exports.Identifier = Identifier;
exports.VariantName = VariantName;
exports.BaseComment = BaseComment;
exports.Comment = Comment;
exports.GroupComment = GroupComment;
exports.ResourceComment = ResourceComment;
exports.Function = Function$1;
exports.Junk = Junk;
exports.Span = Span;
exports.Annotation = Annotation;

Object.defineProperty(exports, '__esModule', { value: true });

})));
