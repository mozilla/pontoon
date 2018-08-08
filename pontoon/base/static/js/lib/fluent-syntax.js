/* fluent-syntax@0.8.0 */
(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
  typeof define === 'function' && define.amd ? define('fluent-syntax', ['exports'], factory) :
  (factory((global.FluentSyntax = {})));
}(this, (function (exports) { 'use strict';

  /*
   * Base class for all Fluent AST nodes.
   *
   * All productions described in the ASDL subclass BaseNode, including Span and
   * Annotation.
   *
   */
  class BaseNode {
    constructor() {}

  }
  /*
   * Base class for AST nodes which can have Spans.
   */


  class SyntaxNode extends BaseNode {
    addSpan(start, end) {
      this.span = new Span(start, end);
    }

  }

  class Resource extends SyntaxNode {
    constructor() {
      let body = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];
      super();
      this.type = "Resource";
      this.body = body;
    }

  }
  /*
   * An abstract base class for useful elements of Resource.body.
   */

  class Entry extends SyntaxNode {}
  class Message extends Entry {
    constructor(id) {
      let value = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
      let attributes = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : [];
      let comment = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : null;
      super();
      this.type = "Message";
      this.id = id;
      this.value = value;
      this.attributes = attributes;
      this.comment = comment;
    }

  }
  class Term extends Entry {
    constructor(id, value) {
      let attributes = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : [];
      let comment = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : null;
      super();
      this.type = "Term";
      this.id = id;
      this.value = value;
      this.attributes = attributes;
      this.comment = comment;
    }

  }
  class VariantList extends SyntaxNode {
    constructor(variants) {
      super();
      this.type = "VariantList";
      this.variants = variants;
    }

  }
  class Pattern extends SyntaxNode {
    constructor(elements) {
      super();
      this.type = "Pattern";
      this.elements = elements;
    }

  }
  /*
   * An abstract base class for elements of Patterns.
   */

  class PatternElement extends SyntaxNode {}
  class TextElement extends PatternElement {
    constructor(value) {
      super();
      this.type = "TextElement";
      this.value = value;
    }

  }
  class Placeable extends PatternElement {
    constructor(expression) {
      super();
      this.type = "Placeable";
      this.expression = expression;
    }

  }
  /*
   * An abstract base class for expressions.
   */

  class Expression extends SyntaxNode {}
  class StringLiteral extends Expression {
    constructor(value) {
      super();
      this.type = "StringLiteral";
      this.value = value;
    }

  }
  class NumberLiteral extends Expression {
    constructor(value) {
      super();
      this.type = "NumberLiteral";
      this.value = value;
    }

  }
  class MessageReference extends Expression {
    constructor(id) {
      super();
      this.type = "MessageReference";
      this.id = id;
    }

  }
  class TermReference extends Expression {
    constructor(id) {
      super();
      this.type = "TermReference";
      this.id = id;
    }

  }
  class VariableReference extends Expression {
    constructor(id) {
      super();
      this.type = "VariableReference";
      this.id = id;
    }

  }
  class SelectExpression extends Expression {
    constructor(selector, variants) {
      super();
      this.type = "SelectExpression";
      this.selector = selector;
      this.variants = variants;
    }

  }
  class AttributeExpression extends Expression {
    constructor(ref, name) {
      super();
      this.type = "AttributeExpression";
      this.ref = ref;
      this.name = name;
    }

  }
  class VariantExpression extends Expression {
    constructor(ref, key) {
      super();
      this.type = "VariantExpression";
      this.ref = ref;
      this.key = key;
    }

  }
  class CallExpression extends Expression {
    constructor(callee) {
      let positional = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
      let named = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : [];
      super();
      this.type = "CallExpression";
      this.callee = callee;
      this.positional = positional;
      this.named = named;
    }

  }
  class Attribute extends SyntaxNode {
    constructor(id, value) {
      super();
      this.type = "Attribute";
      this.id = id;
      this.value = value;
    }

  }
  class Variant extends SyntaxNode {
    constructor(key, value) {
      let def = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
      super();
      this.type = "Variant";
      this.key = key;
      this.value = value;
      this.default = def;
    }

  }
  class NamedArgument extends SyntaxNode {
    constructor(name, value) {
      super();
      this.type = "NamedArgument";
      this.name = name;
      this.value = value;
    }

  }
  class Identifier extends SyntaxNode {
    constructor(name) {
      super();
      this.type = "Identifier";
      this.name = name;
    }

  }
  class VariantName extends Identifier {
    constructor(name) {
      super(name);
      this.type = "VariantName";
    }

  }
  class BaseComment extends Entry {
    constructor(content) {
      super();
      this.type = "BaseComment";
      this.content = content;
    }

  }
  class Comment extends BaseComment {
    constructor(content) {
      super(content);
      this.type = "Comment";
    }

  }
  class GroupComment extends BaseComment {
    constructor(content) {
      super(content);
      this.type = "GroupComment";
    }

  }
  class ResourceComment extends BaseComment {
    constructor(content) {
      super(content);
      this.type = "ResourceComment";
    }

  }
  class Function extends Identifier {
    constructor(name) {
      super(name);
      this.type = "Function";
    }

  }
  class Junk extends SyntaxNode {
    constructor(content) {
      super();
      this.type = "Junk";
      this.annotations = [];
      this.content = content;
    }

    addAnnotation(annot) {
      this.annotations.push(annot);
    }

  }
  class Span extends BaseNode {
    constructor(start, end) {
      super();
      this.type = "Span";
      this.start = start;
      this.end = end;
    }

  }
  class Annotation extends SyntaxNode {
    constructor(code) {
      let args = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
      let message = arguments.length > 2 ? arguments[2] : undefined;
      super();
      this.type = "Annotation";
      this.code = code;
      this.args = args;
      this.message = message;
    }

  }

  class ParserStream {
    constructor(string) {
      this.string = string;
      this.iter = string[Symbol.iterator]();
      this.buf = [];
      this.peekIndex = 0;
      this.index = 0;
      this.iterEnd = false;
      this.peekEnd = false;
      this.ch = this.iter.next().value;
    }

    next() {
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

    current() {
      return this.ch;
    }

    currentIs(ch) {
      return this.ch === ch;
    }

    currentPeek() {
      if (this.peekEnd) {
        return undefined;
      }

      const diff = this.peekIndex - this.index;

      if (diff === 0) {
        return this.ch;
      }

      return this.buf[diff - 1];
    }

    currentPeekIs(ch) {
      return this.currentPeek() === ch;
    }

    peek() {
      if (this.peekEnd) {
        return undefined;
      }

      this.peekIndex += 1;
      const diff = this.peekIndex - this.index;

      if (diff > this.buf.length) {
        const ch = this.iter.next().value;

        if (ch !== undefined) {
          this.buf.push(ch);
        } else {
          this.peekEnd = true;
          return undefined;
        }
      }

      return this.buf[diff - 1];
    }

    getIndex() {
      return this.index;
    }

    getPeekIndex() {
      return this.peekIndex;
    }

    peekCharIs(ch) {
      if (this.peekEnd) {
        return false;
      }

      const ret = this.peek();
      this.peekIndex -= 1;
      return ret === ch;
    }

    resetPeek(pos) {
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

    skipToPeek() {
      const diff = this.peekIndex - this.index;

      for (let i = 0; i < diff; i++) {
        this.ch = this.buf.shift();
      }

      this.index = this.peekIndex;
    }

    getSlice(start, end) {
      return this.string.substring(start, end);
    }

  }

  function _slicedToArray(arr, i) {
    return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest();
  }

  function _arrayWithHoles(arr) {
    if (Array.isArray(arr)) return arr;
  }

  function _iterableToArrayLimit(arr, i) {
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
        if (!_n && _i["return"] != null) _i["return"]();
      } finally {
        if (_d) throw _e;
      }
    }

    return _arr;
  }

  function _nonIterableRest() {
    throw new TypeError("Invalid attempt to destructure non-iterable instance");
  }

  class ParseError extends Error {
    constructor(code) {
      super();
      this.code = code;

      for (var _len = arguments.length, args = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
        args[_key - 1] = arguments[_key];
      }

      this.args = args;
      this.message = getErrorMessage(code, args);
    }

  }
  /* eslint-disable complexity */

  function getErrorMessage(code, args) {
    switch (code) {
      case "E0001":
        return "Generic error";

      case "E0002":
        return "Expected an entry start";

      case "E0003":
        {
          const _args = _slicedToArray(args, 1),
                token = _args[0];

          return `Expected token: "${token}"`;
        }

      case "E0004":
        {
          const _args2 = _slicedToArray(args, 1),
                range = _args2[0];

          return `Expected a character from range: "${range}"`;
        }

      case "E0005":
        {
          const _args3 = _slicedToArray(args, 1),
                id = _args3[0];

          return `Expected message "${id}" to have a value or attributes`;
        }

      case "E0006":
        {
          const _args4 = _slicedToArray(args, 1),
                id = _args4[0];

          return `Expected term "${id}" to have a value`;
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

      case "E0021":
        return "Positional arguments must not follow named arguments";

      case "E0022":
        return "Named arguments must be unique";

      case "E0023":
        return "VariantLists are only allowed inside of other VariantLists.";

      case "E0024":
        return "Cannot access variants of a message.";

      case "E0025":
        {
          const _args5 = _slicedToArray(args, 1),
                char = _args5[0];

          return `Unknown escape sequence: \\${char}.`;
        }

      case "E0026":
        {
          const _args6 = _slicedToArray(args, 1),
                char = _args6[0];

          return `Invalid Unicode escape sequence: \\u${char}.`;
        }

      default:
        return code;
    }
  }

  function includes(arr, elem) {
    return arr.indexOf(elem) > -1;
  }

  /* eslint no-magic-numbers: "off" */
  const INLINE_WS = [" ", "\t"];
  const SPECIAL_LINE_START_CHARS = ["}", ".", "[", "*"];
  class FTLParserStream extends ParserStream {
    skipInlineWS() {
      while (this.ch) {
        if (!includes(INLINE_WS, this.ch)) {
          break;
        }

        this.next();
      }
    }

    peekInlineWS() {
      let ch = this.currentPeek();

      while (ch) {
        if (!includes(INLINE_WS, ch)) {
          break;
        }

        ch = this.peek();
      }
    }

    skipBlankLines() {
      let lineCount = 0;

      while (true) {
        this.peekInlineWS();

        if (this.currentPeekIs("\n")) {
          this.skipToPeek();
          this.next();
          lineCount++;
        } else {
          this.resetPeek();
          return lineCount;
        }
      }
    }

    peekBlankLines() {
      while (true) {
        const lineStart = this.getPeekIndex();
        this.peekInlineWS();

        if (this.currentPeekIs("\n")) {
          this.peek();
        } else {
          this.resetPeek(lineStart);
          break;
        }
      }
    }

    skipIndent() {
      this.skipBlankLines();
      this.skipInlineWS();
    }

    expectChar(ch) {
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

    expectIndent() {
      this.expectChar("\n");
      this.skipBlankLines();
      this.expectChar(" ");
      this.skipInlineWS();
    }

    expectLineEnd() {
      if (this.ch === undefined) {
        // EOF is a valid line end in Fluent.
        return true;
      }

      return this.expectChar("\n");
    }

    takeChar(f) {
      const ch = this.ch;

      if (ch !== undefined && f(ch)) {
        this.next();
        return ch;
      }

      return undefined;
    }

    isCharIDStart(ch) {
      if (ch === undefined) {
        return false;
      }

      const cc = ch.charCodeAt(0);
      return cc >= 97 && cc <= 122 || // a-z
      cc >= 65 && cc <= 90; // A-Z
    }

    isIdentifierStart() {
      const ch = this.currentPeek();
      const isID = this.isCharIDStart(ch);
      this.resetPeek();
      return isID;
    }

    isNumberStart() {
      if (this.currentIs("-")) {
        this.peek();
      }

      const cc = this.currentPeek().charCodeAt(0);
      const isDigit = cc >= 48 && cc <= 57; // 0-9

      this.resetPeek();
      return isDigit;
    }

    isCharPatternContinuation(ch) {
      if (ch === undefined) {
        return false;
      }

      return !includes(SPECIAL_LINE_START_CHARS, ch);
    }

    isPeekValueStart() {
      this.peekInlineWS();
      const ch = this.currentPeek(); // Inline Patterns may start with any char.

      if (ch !== undefined && ch !== "\n") {
        return true;
      }

      return this.isPeekNextLineValue();
    } // -1 - any
    //  0 - comment
    //  1 - group comment
    //  2 - resource comment


    isPeekNextLineComment() {
      let level = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : -1;

      if (!this.currentPeekIs("\n")) {
        return false;
      }

      let i = 0;

      while (i <= level || level === -1 && i < 3) {
        this.peek();

        if (!this.currentPeekIs("#")) {
          if (i <= level && level !== -1) {
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

    isPeekNextLineVariantStart() {
      if (!this.currentPeekIs("\n")) {
        return false;
      }

      this.peek();
      this.peekBlankLines();
      const ptr = this.getPeekIndex();
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

    isPeekNextLineAttributeStart() {
      if (!this.currentPeekIs("\n")) {
        return false;
      }

      this.peek();
      this.peekBlankLines();
      const ptr = this.getPeekIndex();
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

    isPeekNextLineValue() {
      if (!this.currentPeekIs("\n")) {
        return false;
      }

      this.peek();
      this.peekBlankLines();
      const ptr = this.getPeekIndex();
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

    skipToNextEntryStart() {
      while (this.ch) {
        if (this.currentIs("\n") && !this.peekCharIs("\n")) {
          this.next();

          if (this.ch === undefined || this.isIdentifierStart() || this.currentIs("-") || this.currentIs("#")) {
            break;
          }
        }

        this.next();
      }
    }

    takeIDStart() {
      if (this.isCharIDStart(this.ch)) {
        const ret = this.ch;
        this.next();
        return ret;
      }

      throw new ParseError("E0004", "a-zA-Z");
    }

    takeIDChar() {
      const closure = ch => {
        const cc = ch.charCodeAt(0);
        return cc >= 97 && cc <= 122 || // a-z
        cc >= 65 && cc <= 90 || // A-Z
        cc >= 48 && cc <= 57 || // 0-9
        cc === 95 || cc === 45; // _-
      };

      return this.takeChar(closure);
    }

    takeVariantNameChar() {
      const closure = ch => {
        const cc = ch.charCodeAt(0);
        return cc >= 97 && cc <= 122 || // a-z
        cc >= 65 && cc <= 90 || // A-Z
        cc >= 48 && cc <= 57 || // 0-9
        cc === 95 || cc === 45 || cc === 32; // _-<space>
      };

      return this.takeChar(closure);
    }

    takeDigit() {
      const closure = ch => {
        const cc = ch.charCodeAt(0);
        return cc >= 48 && cc <= 57; // 0-9
      };

      return this.takeChar(closure);
    }

    takeHexDigit() {
      const closure = ch => {
        const cc = ch.charCodeAt(0);
        return cc >= 48 && cc <= 57 || // 0-9
        cc >= 65 && cc <= 70 // A-F
        || cc >= 97 && cc <= 102; // a-f
      };

      return this.takeChar(closure);
    }

  }

  /*  eslint no-magic-numbers: [0]  */
  const trailingWSRe = /[ \t\n\r]+$/;

  function withSpan(fn) {
    return function (ps) {
      for (var _len = arguments.length, args = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
        args[_key - 1] = arguments[_key];
      }

      if (!this.withSpans) {
        return fn.call(this, ps, ...args);
      }

      const start = ps.getIndex();
      const node = fn.call(this, ps, ...args); // Don't re-add the span if the node already has it.  This may happen when
      // one decorated function calls another decorated function.

      if (node.span) {
        return node;
      }

      const end = ps.getIndex();
      node.addSpan(start, end);
      return node;
    };
  }

  class FluentParser {
    constructor() {
      let _ref = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {},
          _ref$withSpans = _ref.withSpans,
          withSpans = _ref$withSpans === void 0 ? true : _ref$withSpans;

      this.withSpans = withSpans; // Poor man's decorators.

      ["getComment", "getMessage", "getTerm", "getAttribute", "getIdentifier", "getTermIdentifier", "getVariant", "getVariantName", "getNumber", "getValue", "getPattern", "getVariantList", "getTextElement", "getPlaceable", "getExpression", "getSelectorExpression", "getCallArg", "getString", "getLiteral", "getVariantList"].forEach(name => this[name] = withSpan(this[name]));
    }

    parse(source) {
      const ps = new FTLParserStream(source);
      ps.skipBlankLines();
      const entries = [];
      let lastComment = null;

      while (ps.current()) {
        const entry = this.getEntryOrJunk(ps);
        const blankLines = ps.skipBlankLines(); // Regular Comments require special logic. Comments may be attached to
        // Messages or Terms if they are followed immediately by them. However
        // they should parse as standalone when they're followed by Junk.
        // Consequently, we only attach Comments once we know that the Message
        // or the Term parsed successfully.

        if (entry.type === "Comment" && blankLines === 0 && ps.current()) {
          // Stash the comment and decide what to do with it in the next pass.
          lastComment = entry;
          continue;
        }

        if (lastComment) {
          if (entry.type === "Message" || entry.type === "Term") {
            entry.comment = lastComment;

            if (this.withSpans) {
              entry.span.start = entry.comment.span.start;
            }
          } else {
            entries.push(lastComment);
          } // In either case, the stashed comment has been dealt with; clear it.


          lastComment = null;
        } // No special logic for other types of entries.


        entries.push(entry);
      }

      const res = new Resource(entries);

      if (this.withSpans) {
        res.addSpan(0, ps.getIndex());
      }

      return res;
    }
    /*
     * Parse the first Message or Term in `source`.
     *
     * Skip all encountered comments and start parsing at the first Message or
     * Term start. Return Junk if the parsing is not successful.
     *
     * Preceding comments are ignored unless they contain syntax errors
     * themselves, in which case Junk for the invalid comment is returned.
     */


    parseEntry(source) {
      const ps = new FTLParserStream(source);
      ps.skipBlankLines();

      while (ps.currentIs("#")) {
        const skipped = this.getEntryOrJunk(ps);

        if (skipped.type === "Junk") {
          // Don't skip Junk comments.
          return skipped;
        }

        ps.skipBlankLines();
      }

      return this.getEntryOrJunk(ps);
    }

    getEntryOrJunk(ps) {
      const entryStartPos = ps.getIndex();

      try {
        const entry = this.getEntry(ps);
        ps.expectLineEnd();
        return entry;
      } catch (err) {
        if (!(err instanceof ParseError)) {
          throw err;
        }

        const errorIndex = ps.getIndex();
        ps.skipToNextEntryStart();
        const nextEntryStart = ps.getIndex(); // Create a Junk instance

        const slice = ps.getSlice(entryStartPos, nextEntryStart);
        const junk = new Junk(slice);

        if (this.withSpans) {
          junk.addSpan(entryStartPos, nextEntryStart);
        }

        const annot = new Annotation(err.code, err.args, err.message);
        annot.addSpan(errorIndex, errorIndex);
        junk.addAnnotation(annot);
        return junk;
      }
    }

    getEntry(ps) {
      if (ps.currentIs("#")) {
        return this.getComment(ps);
      }

      if (ps.currentIs("-")) {
        return this.getTerm(ps);
      }

      if (ps.isIdentifierStart()) {
        return this.getMessage(ps);
      }

      throw new ParseError("E0002");
    }

    getComment(ps) {
      // 0 - comment
      // 1 - group comment
      // 2 - resource comment
      let level = -1;
      let content = "";

      while (true) {
        let i = -1;

        while (ps.currentIs("#") && i < (level === -1 ? 2 : level)) {
          ps.next();
          i++;
        }

        if (level === -1) {
          level = i;
        }

        if (!ps.currentIs("\n")) {
          ps.expectChar(" ");
          let ch;

          while (ch = ps.takeChar(x => x !== "\n")) {
            content += ch;
          }
        }

        if (ps.isPeekNextLineComment(level)) {
          content += ps.current();
          ps.next();
        } else {
          break;
        }
      }

      let Comment$$1;

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

    getMessage(ps) {
      const id = this.getIdentifier(ps);
      ps.skipInlineWS();
      ps.expectChar("=");

      if (ps.isPeekValueStart()) {
        ps.skipIndent();
        var pattern = this.getPattern(ps);
      } else {
        ps.skipInlineWS();
      }

      if (ps.isPeekNextLineAttributeStart()) {
        var attrs = this.getAttributes(ps);
      }

      if (pattern === undefined && attrs === undefined) {
        throw new ParseError("E0005", id.name);
      }

      return new Message(id, pattern, attrs);
    }

    getTerm(ps) {
      const id = this.getTermIdentifier(ps);
      ps.skipInlineWS();
      ps.expectChar("=");

      if (ps.isPeekValueStart()) {
        ps.skipIndent();
        var value = this.getValue(ps);
      } else {
        throw new ParseError("E0006", id.name);
      }

      if (ps.isPeekNextLineAttributeStart()) {
        var attrs = this.getAttributes(ps);
      }

      return new Term(id, value, attrs);
    }

    getAttribute(ps) {
      ps.expectChar(".");
      const key = this.getIdentifier(ps);
      ps.skipInlineWS();
      ps.expectChar("=");

      if (ps.isPeekValueStart()) {
        ps.skipIndent();
        const value = this.getPattern(ps);
        return new Attribute(key, value);
      }

      throw new ParseError("E0012");
    }

    getAttributes(ps) {
      const attrs = [];

      while (true) {
        ps.expectIndent();
        const attr = this.getAttribute(ps);
        attrs.push(attr);

        if (!ps.isPeekNextLineAttributeStart()) {
          break;
        }
      }

      return attrs;
    }

    getIdentifier(ps) {
      let name = ps.takeIDStart();
      let ch;

      while (ch = ps.takeIDChar()) {
        name += ch;
      }

      return new Identifier(name);
    }

    getTermIdentifier(ps) {
      ps.expectChar("-");
      const id = this.getIdentifier(ps);
      return new Identifier(`-${id.name}`);
    }

    getVariantKey(ps) {
      const ch = ps.current();

      if (!ch) {
        throw new ParseError("E0013");
      }

      const cc = ch.charCodeAt(0);

      if (cc >= 48 && cc <= 57 || cc === 45) {
        // 0-9, -
        return this.getNumber(ps);
      }

      return this.getVariantName(ps);
    }

    getVariant(ps, hasDefault) {
      let defaultIndex = false;

      if (ps.currentIs("*")) {
        if (hasDefault) {
          throw new ParseError("E0015");
        }

        ps.next();
        defaultIndex = true;
        hasDefault = true;
      }

      ps.expectChar("[");
      const key = this.getVariantKey(ps);
      ps.expectChar("]");

      if (ps.isPeekValueStart()) {
        ps.skipIndent();
        const value = this.getValue(ps);
        return new Variant(key, value, defaultIndex);
      }

      throw new ParseError("E0012");
    }

    getVariants(ps) {
      const variants = [];
      let hasDefault = false;

      while (true) {
        ps.expectIndent();
        const variant = this.getVariant(ps, hasDefault);

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

    getVariantName(ps) {
      let name = ps.takeIDStart();

      while (true) {
        const ch = ps.takeVariantNameChar();

        if (ch) {
          name += ch;
        } else {
          break;
        }
      }

      return new VariantName(name.replace(trailingWSRe, ""));
    }

    getDigits(ps) {
      let num = "";
      let ch;

      while (ch = ps.takeDigit()) {
        num += ch;
      }

      if (num.length === 0) {
        throw new ParseError("E0004", "0-9");
      }

      return num;
    }

    getNumber(ps) {
      let num = "";

      if (ps.currentIs("-")) {
        num += "-";
        ps.next();
      }

      num = `${num}${this.getDigits(ps)}`;

      if (ps.currentIs(".")) {
        num += ".";
        ps.next();
        num = `${num}${this.getDigits(ps)}`;
      }

      return new NumberLiteral(num);
    }

    getValue(ps) {
      if (ps.currentIs("{")) {
        ps.peek();
        ps.peekInlineWS();

        if (ps.isPeekNextLineVariantStart()) {
          return this.getVariantList(ps);
        }
      }

      return this.getPattern(ps);
    }

    getVariantList(ps) {
      ps.expectChar("{");
      ps.skipInlineWS();
      const variants = this.getVariants(ps);
      ps.expectIndent();
      ps.expectChar("}");
      return new VariantList(variants);
    }

    getPattern(ps) {
      const elements = [];
      ps.skipInlineWS();
      let ch;

      while (ch = ps.current()) {
        // The end condition for getPattern's while loop is a newline
        // which is not followed by a valid pattern continuation.
        if (ch === "\n" && !ps.isPeekNextLineValue()) {
          break;
        }

        if (ch === "{") {
          const element = this.getPlaceable(ps);
          elements.push(element);
        } else {
          const element = this.getTextElement(ps);
          elements.push(element);
        }
      } // Trim trailing whitespace.


      const lastElement = elements[elements.length - 1];

      if (lastElement.type === "TextElement") {
        lastElement.value = lastElement.value.replace(trailingWSRe, "");
      }

      return new Pattern(elements);
    }

    getTextElement(ps) {
      let buffer = "";
      let ch;

      while (ch = ps.current()) {
        if (ch === "{") {
          return new TextElement(buffer);
        }

        if (ch === "\n") {
          if (!ps.isPeekNextLineValue()) {
            return new TextElement(buffer);
          }

          ps.next();
          ps.skipInlineWS(); // Add the new line to the buffer

          buffer += ch;
          continue;
        }

        if (ch === "\\") {
          ps.next();
          buffer += this.getEscapeSequence(ps);
        } else {
          buffer += ch;
          ps.next();
        }
      }

      return new TextElement(buffer);
    }

    getEscapeSequence(ps) {
      let specials = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : ["{", "\\"];
      const next = ps.current();

      if (specials.includes(next)) {
        ps.next();
        return `\\${next}`;
      }

      if (next === "u") {
        let sequence = "";
        ps.next();

        for (let i = 0; i < 4; i++) {
          const ch = ps.takeHexDigit();

          if (ch === undefined) {
            throw new ParseError("E0026", sequence + ps.current());
          }

          sequence += ch;
        }

        return `\\u${sequence}`;
      }

      throw new ParseError("E0025", next);
    }

    getPlaceable(ps) {
      ps.expectChar("{");
      const expression = this.getExpression(ps);
      ps.expectChar("}");
      return new Placeable(expression);
    }

    getExpression(ps) {
      ps.skipInlineWS();
      const selector = this.getSelectorExpression(ps);
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

        if (selector.type === "AttributeExpression" && selector.ref.type === "MessageReference") {
          throw new ParseError("E0018");
        }

        if (selector.type === "VariantExpression") {
          throw new ParseError("E0017");
        }

        ps.next();
        ps.next();
        ps.skipInlineWS();
        const variants = this.getVariants(ps);

        if (variants.length === 0) {
          throw new ParseError("E0011");
        } // VariantLists are only allowed in other VariantLists.


        if (variants.some(v => v.value.type === "VariantList")) {
          throw new ParseError("E0023");
        }

        ps.expectIndent();
        return new SelectExpression(selector, variants);
      } else if (selector.type === "AttributeExpression" && selector.ref.type === "TermReference") {
        throw new ParseError("E0019");
      }

      return selector;
    }

    getSelectorExpression(ps) {
      if (ps.currentIs("{")) {
        return this.getPlaceable(ps);
      }

      const literal = this.getLiteral(ps);

      if (literal.type !== "MessageReference" && literal.type !== "TermReference") {
        return literal;
      }

      const ch = ps.current();

      if (ch === ".") {
        ps.next();
        const attr = this.getIdentifier(ps);
        return new AttributeExpression(literal, attr);
      }

      if (ch === "[") {
        ps.next();

        if (literal.type === "MessageReference") {
          throw new ParseError("E0024");
        }

        const key = this.getVariantKey(ps);
        ps.expectChar("]");
        return new VariantExpression(literal, key);
      }

      if (ch === "(") {
        ps.next();

        if (!/^[A-Z][A-Z_?-]*$/.test(literal.id.name)) {
          throw new ParseError("E0008");
        }

        const args = this.getCallArgs(ps);
        ps.expectChar(")");
        const func = new Function(literal.id.name);

        if (this.withSpans) {
          func.addSpan(literal.span.start, literal.span.end);
        }

        return new CallExpression(func, args.positional, args.named);
      }

      return literal;
    }

    getCallArg(ps) {
      const exp = this.getSelectorExpression(ps);
      ps.skipInlineWS();

      if (ps.current() !== ":") {
        return exp;
      }

      if (exp.type !== "MessageReference") {
        throw new ParseError("E0009");
      }

      ps.next();
      ps.skipInlineWS();
      const val = this.getArgVal(ps);
      return new NamedArgument(exp.id, val);
    }

    getCallArgs(ps) {
      const positional = [];
      const named = [];
      const argumentNames = new Set();
      ps.skipInlineWS();
      ps.skipIndent();

      while (true) {
        if (ps.current() === ")") {
          break;
        }

        const arg = this.getCallArg(ps);

        if (arg.type === "NamedArgument") {
          if (argumentNames.has(arg.name.name)) {
            throw new ParseError("E0022");
          }

          named.push(arg);
          argumentNames.add(arg.name.name);
        } else if (argumentNames.size > 0) {
          throw new ParseError("E0021");
        } else {
          positional.push(arg);
        }

        ps.skipInlineWS();
        ps.skipIndent();

        if (ps.current() === ",") {
          ps.next();
          ps.skipInlineWS();
          ps.skipIndent();
          continue;
        } else {
          break;
        }
      }

      return {
        positional,
        named
      };
    }

    getArgVal(ps) {
      if (ps.isNumberStart()) {
        return this.getNumber(ps);
      } else if (ps.currentIs('"')) {
        return this.getString(ps);
      }

      throw new ParseError("E0012");
    }

    getString(ps) {
      let val = "";
      ps.expectChar('"');
      let ch;

      while (ch = ps.takeChar(x => x !== '"' && x !== "\n")) {
        if (ch === "\\") {
          val += this.getEscapeSequence(ps, ["{", "\\", "\""]);
        } else {
          val += ch;
        }
      }

      if (ps.currentIs("\n")) {
        throw new ParseError("E0020");
      }

      ps.next();
      return new StringLiteral(val);
    }

    getLiteral(ps) {
      const ch = ps.current();

      if (!ch) {
        throw new ParseError("E0014");
      }

      if (ch === "$") {
        ps.next();
        const id = this.getIdentifier(ps);
        return new VariableReference(id);
      }

      if (ps.isIdentifierStart()) {
        const id = this.getIdentifier(ps);
        return new MessageReference(id);
      }

      if (ps.isNumberStart()) {
        return this.getNumber(ps);
      }

      if (ch === "-") {
        const id = this.getTermIdentifier(ps);
        return new TermReference(id);
      }

      if (ch === '"') {
        return this.getString(ps);
      }

      throw new ParseError("E0014");
    }

  }

  function indent(content) {
    return content.split("\n").join("\n    ");
  }

  function includesNewLine(elem) {
    return elem.type === "TextElement" && includes(elem.value, "\n");
  }

  function isSelectExpr(elem) {
    return elem.type === "Placeable" && elem.expression.type === "SelectExpression";
  } // Bit masks representing the state of the serializer.


  const HAS_ENTRIES = 1;
  class FluentSerializer {
    constructor() {
      let _ref = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {},
          _ref$withJunk = _ref.withJunk,
          withJunk = _ref$withJunk === void 0 ? false : _ref$withJunk;

      this.withJunk = withJunk;
    }

    serialize(resource) {
      if (resource.type !== "Resource") {
        throw new Error(`Unknown resource type: ${resource.type}`);
      }

      let state = 0;
      const parts = [];
      var _iteratorNormalCompletion = true;
      var _didIteratorError = false;
      var _iteratorError = undefined;

      try {
        for (var _iterator = resource.body[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
          const entry = _step.value;

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
          if (!_iteratorNormalCompletion && _iterator.return != null) {
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

    serializeEntry(entry) {
      let state = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 0;

      switch (entry.type) {
        case "Message":
        case "Term":
          return serializeMessage(entry);

        case "Comment":
          if (state & HAS_ENTRIES) {
            return `\n${serializeComment(entry, "#")}\n`;
          }

          return `${serializeComment(entry, "#")}\n`;

        case "GroupComment":
          if (state & HAS_ENTRIES) {
            return `\n${serializeComment(entry, "##")}\n`;
          }

          return `${serializeComment(entry, "##")}\n`;

        case "ResourceComment":
          if (state & HAS_ENTRIES) {
            return `\n${serializeComment(entry, "###")}\n`;
          }

          return `${serializeComment(entry, "###")}\n`;

        case "Junk":
          return serializeJunk(entry);

        default:
          throw new Error(`Unknown entry type: ${entry.type}`);
      }
    }

    serializeExpression(expr) {
      return serializeExpression(expr);
    }

  }

  function serializeComment(comment) {
    let prefix = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "#";
    const prefixed = comment.content.split("\n").map(line => line.length ? `${prefix} ${line}` : prefix).join("\n"); // Add the trailing newline.

    return `${prefixed}\n`;
  }

  function serializeJunk(junk) {
    return junk.content;
  }

  function serializeMessage(message) {
    const parts = [];

    if (message.comment) {
      parts.push(serializeComment(message.comment));
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
        const attribute = _step2.value;
        parts.push(serializeAttribute(attribute));
      }
    } catch (err) {
      _didIteratorError2 = true;
      _iteratorError2 = err;
    } finally {
      try {
        if (!_iteratorNormalCompletion2 && _iterator2.return != null) {
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
    const id = serializeIdentifier(attribute.id);
    const value = indent(serializeValue(attribute.value));
    return `\n    .${id} =${value}`;
  }

  function serializeValue(value) {
    switch (value.type) {
      case "Pattern":
        return serializePattern(value);

      case "VariantList":
        return serializeVariantList(value);

      default:
        throw new Error(`Unknown value type: ${value.type}`);
    }
  }

  function serializePattern(pattern) {
    const content = pattern.elements.map(serializeElement).join("");
    const startOnNewLine = pattern.elements.some(isSelectExpr) || pattern.elements.some(includesNewLine);

    if (startOnNewLine) {
      return `\n    ${indent(content)}`;
    }

    return ` ${content}`;
  }

  function serializeVariantList(varlist) {
    const content = varlist.variants.map(serializeVariant).join("");
    return `\n    {${indent(content)}\n    }`;
  }

  function serializeVariant(variant) {
    const key = serializeVariantKey(variant.key);
    const value = indent(serializeValue(variant.value));

    if (variant.default) {
      return `\n   *[${key}]${value}`;
    }

    return `\n    [${key}]${value}`;
  }

  function serializeElement(element) {
    switch (element.type) {
      case "TextElement":
        return serializeTextElement(element);

      case "Placeable":
        return serializePlaceable(element);

      default:
        throw new Error(`Unknown element type: ${element.type}`);
    }
  }

  function serializeTextElement(text) {
    return text.value;
  }

  function serializePlaceable(placeable) {
    const expr = placeable.expression;

    switch (expr.type) {
      case "Placeable":
        return `{${serializePlaceable(expr)}}`;

      case "SelectExpression":
        // Special-case select expression to control the whitespace around the
        // opening and the closing brace.
        return `{ ${serializeSelectExpression(expr)}}`;

      default:
        return `{ ${serializeExpression(expr)} }`;
    }
  }

  function serializeExpression(expr) {
    switch (expr.type) {
      case "StringLiteral":
        return serializeStringLiteral(expr);

      case "NumberLiteral":
        return serializeNumberLiteral(expr);

      case "MessageReference":
      case "TermReference":
        return serializeMessageReference(expr);

      case "VariableReference":
        return serializeVariableReference(expr);

      case "AttributeExpression":
        return serializeAttributeExpression(expr);

      case "VariantExpression":
        return serializeVariantExpression(expr);

      case "CallExpression":
        return serializeCallExpression(expr);

      case "SelectExpression":
        return serializeSelectExpression(expr);

      case "Placeable":
        return serializePlaceable(expr);

      default:
        throw new Error(`Unknown expression type: ${expr.type}`);
    }
  }

  function serializeStringLiteral(expr) {
    return `"${expr.value}"`;
  }

  function serializeNumberLiteral(expr) {
    return expr.value;
  }

  function serializeMessageReference(expr) {
    return serializeIdentifier(expr.id);
  }

  function serializeVariableReference(expr) {
    return `$${serializeIdentifier(expr.id)}`;
  }

  function serializeSelectExpression(expr) {
    const parts = [];
    const selector = `${serializeExpression(expr.selector)} ->`;
    parts.push(selector);
    var _iteratorNormalCompletion3 = true;
    var _didIteratorError3 = false;
    var _iteratorError3 = undefined;

    try {
      for (var _iterator3 = expr.variants[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {
        const variant = _step3.value;
        parts.push(serializeVariant(variant));
      }
    } catch (err) {
      _didIteratorError3 = true;
      _iteratorError3 = err;
    } finally {
      try {
        if (!_iteratorNormalCompletion3 && _iterator3.return != null) {
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

  function serializeAttributeExpression(expr) {
    const ref = serializeExpression(expr.ref);
    const name = serializeIdentifier(expr.name);
    return `${ref}.${name}`;
  }

  function serializeVariantExpression(expr) {
    const ref = serializeExpression(expr.ref);
    const key = serializeVariantKey(expr.key);
    return `${ref}[${key}]`;
  }

  function serializeCallExpression(expr) {
    const fun = serializeFunction(expr.callee);
    const positional = expr.positional.map(serializeExpression).join(", ");
    const named = expr.named.map(serializeNamedArgument).join(", ");

    if (expr.positional.length > 0 && expr.named.length > 0) {
      return `${fun}(${positional}, ${named})`;
    }

    return `${fun}(${positional || named})`;
  }

  function serializeNamedArgument(arg) {
    const name = serializeIdentifier(arg.name);
    const value = serializeArgumentValue(arg.value);
    return `${name}: ${value}`;
  }

  function serializeArgumentValue(argval) {
    switch (argval.type) {
      case "StringLiteral":
        return serializeStringLiteral(argval);

      case "NumberLiteral":
        return serializeNumberLiteral(argval);

      default:
        throw new Error(`Unknown argument type: ${argval.type}`);
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

      case "NumberLiteral":
        return serializeNumberLiteral(key);

      default:
        throw new Error(`Unknown variant key type: ${key.type}`);
    }
  }

  function serializeFunction(fun) {
    return fun.name;
  }

  function parse(source, opts) {
    const parser = new FluentParser(opts);
    return parser.parse(source);
  }
  function serialize(resource, opts) {
    const serializer = new FluentSerializer(opts);
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
    const fromIndex = pos - 1;
    const prevLineBreak = source.lastIndexOf("\n", fromIndex); // pos is a position in the first line of source.

    if (prevLineBreak === -1) {
      return pos;
    } // Subtracting two offsets gives length; subtract 1 to get the offset.


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
  exports.VariantList = VariantList;
  exports.Pattern = Pattern;
  exports.PatternElement = PatternElement;
  exports.TextElement = TextElement;
  exports.Placeable = Placeable;
  exports.Expression = Expression;
  exports.StringLiteral = StringLiteral;
  exports.NumberLiteral = NumberLiteral;
  exports.MessageReference = MessageReference;
  exports.TermReference = TermReference;
  exports.VariableReference = VariableReference;
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
  exports.Function = Function;
  exports.Junk = Junk;
  exports.Span = Span;
  exports.Annotation = Annotation;

  Object.defineProperty(exports, '__esModule', { value: true });

})));
