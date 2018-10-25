/* fluent-syntax@0.9.0 */
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
  class ParserStream {
    constructor(string) {
      this.string = string;
      this.index = 0;
      this.peekOffset = 0;
    }

    charAt(offset) {
      // When the cursor is at CRLF, return LF but don't move the cursor.
      // The cursor still points to the EOL position, which in this case is the
      // beginning of the compound CRLF sequence. This ensures slices of
      // [inclusive, exclusive) continue to work properly.
      if (this.string[offset] === "\r" && this.string[offset + 1] === "\n") {
        return "\n";
      }

      return this.string[offset];
    }

    get currentChar() {
      return this.charAt(this.index);
    }

    get currentPeek() {
      return this.charAt(this.index + this.peekOffset);
    }

    next() {
      this.peekOffset = 0; // Skip over the CRLF as if it was a single character.

      if (this.string[this.index] === "\r" && this.string[this.index + 1] === "\n") {
        this.index++;
      }

      this.index++;
      return this.string[this.index];
    }

    peek() {
      // Skip over the CRLF as if it was a single character.
      if (this.string[this.index + this.peekOffset] === "\r" && this.string[this.index + this.peekOffset + 1] === "\n") {
        this.peekOffset++;
      }

      this.peekOffset++;
      return this.string[this.index + this.peekOffset];
    }

    resetPeek() {
      let offset = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 0;
      this.peekOffset = offset;
    }

    skipToPeek() {
      this.index += this.peekOffset;
      this.peekOffset = 0;
    }

  }
  const EOL = "\n";
  const EOF = undefined;
  const SPECIAL_LINE_START_CHARS = ["}", ".", "[", "*"];
  class FluentParserStream extends ParserStream {
    skipBlankInline() {
      while (this.currentChar === " ") {
        this.next();
      }
    }

    peekBlankInline() {
      while (this.currentPeek === " ") {
        this.peek();
      }
    }

    skipBlankBlock() {
      let lineCount = 0;

      while (true) {
        this.peekBlankInline();

        if (this.currentPeek === EOL) {
          this.next();
          lineCount++;
        } else {
          this.resetPeek();
          return lineCount;
        }
      }
    }

    peekBlankBlock() {
      while (true) {
        const lineStart = this.peekOffset;
        this.peekBlankInline();

        if (this.currentPeek === EOL) {
          this.peek();
        } else {
          this.resetPeek(lineStart);
          break;
        }
      }
    }

    skipBlank() {
      while (this.currentChar === " " || this.currentChar === EOL) {
        this.next();
      }
    }

    peekBlank() {
      while (this.currentPeek === " " || this.currentPeek === EOL) {
        this.peek();
      }
    }

    expectChar(ch) {
      if (this.currentChar === ch) {
        this.next();
        return true;
      }

      throw new ParseError("E0003", ch);
    }

    expectLineEnd() {
      if (this.currentChar === EOF) {
        // EOF is a valid line end in Fluent.
        return true;
      }

      if (this.currentChar === EOL) {
        this.next();
        return true;
      } // Unicode Character 'SYMBOL FOR NEWLINE' (U+2424)


      throw new ParseError("E0003", "\u2424");
    }

    takeChar(f) {
      const ch = this.currentChar;

      if (ch === EOF) {
        return EOF;
      }

      if (f(ch)) {
        this.next();
        return ch;
      }

      return null;
    }

    isCharIDStart(ch) {
      if (ch === EOF) {
        return false;
      }

      const cc = ch.charCodeAt(0);
      return cc >= 97 && cc <= 122 || // a-z
      cc >= 65 && cc <= 90; // A-Z
    }

    isIdentifierStart() {
      return this.isCharIDStart(this.currentPeek);
    }

    isNumberStart() {
      const ch = this.currentChar === "-" ? this.peek() : this.currentChar;

      if (ch === EOF) {
        this.resetPeek();
        return false;
      }

      const cc = ch.charCodeAt(0);
      const isDigit = cc >= 48 && cc <= 57; // 0-9

      this.resetPeek();
      return isDigit;
    }

    isCharPatternContinuation(ch) {
      if (ch === EOF) {
        return false;
      }

      return !includes(SPECIAL_LINE_START_CHARS, ch);
    }

    isValueStart(_ref) {
      let _ref$skip = _ref.skip,
          skip = _ref$skip === void 0 ? true : _ref$skip;
      if (skip === false) throw new Error("Unimplemented");
      this.peekBlankInline();
      const ch = this.currentPeek; // Inline Patterns may start with any char.

      if (ch !== EOF && ch !== EOL) {
        this.skipToPeek();
        return true;
      }

      return this.isNextLineValue({
        skip
      });
    } // -1 - any
    //  0 - comment
    //  1 - group comment
    //  2 - resource comment


    isNextLineComment() {
      let level = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : -1;

      let _ref2 = arguments.length > 1 ? arguments[1] : undefined,
          _ref2$skip = _ref2.skip,
          skip = _ref2$skip === void 0 ? false : _ref2$skip;

      if (skip === true) throw new Error("Unimplemented");

      if (this.currentPeek !== EOL) {
        return false;
      }

      let i = 0;

      while (i <= level || level === -1 && i < 3) {
        if (this.peek() !== "#") {
          if (i <= level && level !== -1) {
            this.resetPeek();
            return false;
          }

          break;
        }

        i++;
      } // The first char after #, ## or ###.


      const ch = this.peek();

      if (ch === " " || ch === EOL) {
        this.resetPeek();
        return true;
      }

      this.resetPeek();
      return false;
    }

    isNextLineVariantStart(_ref3) {
      let _ref3$skip = _ref3.skip,
          skip = _ref3$skip === void 0 ? false : _ref3$skip;
      if (skip === true) throw new Error("Unimplemented");

      if (this.currentPeek !== EOL) {
        return false;
      }

      this.peekBlank();

      if (this.currentPeek === "*") {
        this.peek();
      }

      if (this.currentPeek === "[") {
        this.resetPeek();
        return true;
      }

      this.resetPeek();
      return false;
    }

    isNextLineAttributeStart(_ref4) {
      let _ref4$skip = _ref4.skip,
          skip = _ref4$skip === void 0 ? true : _ref4$skip;
      if (skip === false) throw new Error("Unimplemented");
      this.peekBlank();

      if (this.currentPeek === ".") {
        this.skipToPeek();
        return true;
      }

      this.resetPeek();
      return false;
    }

    isNextLineValue(_ref5) {
      let _ref5$skip = _ref5.skip,
          skip = _ref5$skip === void 0 ? true : _ref5$skip;

      if (this.currentPeek !== EOL) {
        return false;
      }

      this.peekBlankBlock();
      const ptr = this.peekOffset;
      this.peekBlankInline();

      if (this.currentPeek !== "{") {
        if (this.peekOffset - ptr === 0) {
          this.resetPeek();
          return false;
        }

        if (!this.isCharPatternContinuation(this.currentPeek)) {
          this.resetPeek();
          return false;
        }
      }

      if (skip) {
        this.skipToPeek();
      } else {
        this.resetPeek();
      }

      return true;
    }

    skipToNextEntryStart(junkStart) {
      let lastNewline = this.string.lastIndexOf(EOL, this.index);

      if (junkStart < lastNewline) {
        // Last seen newline is _after_ the junk start. It's safe to rewind
        // without the risk of resuming at the same broken entry.
        this.index = lastNewline;
      }

      while (this.currentChar) {
        // We're only interested in beginnings of line.
        if (this.currentChar !== EOL) {
          this.next();
          continue;
        } // Break if the first char in this line looks like an entry start.


        const first = this.next();

        if (this.isCharIDStart(first) || first === "-" || first === "#") {
          break;
        }
      }
    }

    takeIDStart() {
      if (this.isCharIDStart(this.currentChar)) {
        const ret = this.currentChar;
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

      const start = ps.index;
      const node = fn.call(this, ps, ...args); // Don't re-add the span if the node already has it.  This may happen when
      // one decorated function calls another decorated function.

      if (node.span) {
        return node;
      }

      const end = ps.index;
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

      const methodNames = ["getComment", "getMessage", "getTerm", "getAttribute", "getIdentifier", "getTermIdentifier", "getVariant", "getNumber", "getValue", "getPattern", "getVariantList", "getTextElement", "getPlaceable", "getExpression", "getSelectorExpression", "getCallArg", "getString", "getLiteral"];

      for (var _i = 0; _i < methodNames.length; _i++) {
        const name = methodNames[_i];
        this[name] = withSpan(this[name]);
      }
    }

    parse(source) {
      const ps = new FluentParserStream(source);
      ps.skipBlankBlock();
      const entries = [];
      let lastComment = null;

      while (ps.currentChar) {
        const entry = this.getEntryOrJunk(ps);
        const blankLines = ps.skipBlankBlock(); // Regular Comments require special logic. Comments may be attached to
        // Messages or Terms if they are followed immediately by them. However
        // they should parse as standalone when they're followed by Junk.
        // Consequently, we only attach Comments once we know that the Message
        // or the Term parsed successfully.

        if (entry.type === "Comment" && blankLines === 0 && ps.currentChar) {
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
        res.addSpan(0, ps.index);
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
      const ps = new FluentParserStream(source);
      ps.skipBlankBlock();

      while (ps.currentChar === "#") {
        const skipped = this.getEntryOrJunk(ps);

        if (skipped.type === "Junk") {
          // Don't skip Junk comments.
          return skipped;
        }

        ps.skipBlankBlock();
      }

      return this.getEntryOrJunk(ps);
    }

    getEntryOrJunk(ps) {
      const entryStartPos = ps.index;

      try {
        const entry = this.getEntry(ps);
        ps.expectLineEnd();
        return entry;
      } catch (err) {
        if (!(err instanceof ParseError)) {
          throw err;
        }

        let errorIndex = ps.index;
        ps.skipToNextEntryStart(entryStartPos);
        const nextEntryStart = ps.index;

        if (nextEntryStart < errorIndex) {
          // The position of the error must be inside of the Junk's span.
          errorIndex = nextEntryStart;
        } // Create a Junk instance


        const slice = ps.string.substring(entryStartPos, nextEntryStart);
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
      if (ps.currentChar === "#") {
        return this.getComment(ps);
      }

      if (ps.currentChar === "-") {
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

        while (ps.currentChar === "#" && i < (level === -1 ? 2 : level)) {
          ps.next();
          i++;
        }

        if (level === -1) {
          level = i;
        }

        if (ps.currentChar !== EOL) {
          ps.expectChar(" ");
          let ch;

          while (ch = ps.takeChar(x => x !== EOL)) {
            content += ch;
          }
        }

        if (ps.isNextLineComment(level, {
          skip: false
        })) {
          content += ps.currentChar;
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
      ps.skipBlankInline();
      ps.expectChar("=");

      if (ps.isValueStart({
        skip: true
      })) {
        var pattern = this.getPattern(ps);
      }

      if (ps.isNextLineAttributeStart({
        skip: true
      })) {
        var attrs = this.getAttributes(ps);
      }

      if (pattern === undefined && attrs === undefined) {
        throw new ParseError("E0005", id.name);
      }

      return new Message(id, pattern, attrs);
    }

    getTerm(ps) {
      const id = this.getTermIdentifier(ps);
      ps.skipBlankInline();
      ps.expectChar("=");

      if (ps.isValueStart({
        skip: true
      })) {
        var value = this.getValue(ps);
      } else {
        throw new ParseError("E0006", id.name);
      }

      if (ps.isNextLineAttributeStart({
        skip: true
      })) {
        var attrs = this.getAttributes(ps);
      }

      return new Term(id, value, attrs);
    }

    getAttribute(ps) {
      ps.expectChar(".");
      const key = this.getIdentifier(ps);
      ps.skipBlankInline();
      ps.expectChar("=");

      if (ps.isValueStart({
        skip: true
      })) {
        const value = this.getPattern(ps);
        return new Attribute(key, value);
      }

      throw new ParseError("E0012");
    }

    getAttributes(ps) {
      const attrs = [];

      while (true) {
        const attr = this.getAttribute(ps);
        attrs.push(attr);

        if (!ps.isNextLineAttributeStart({
          skip: true
        })) {
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
      const ch = ps.currentChar;

      if (ch === EOF) {
        throw new ParseError("E0013");
      }

      const cc = ch.charCodeAt(0);

      if (cc >= 48 && cc <= 57 || cc === 45) {
        // 0-9, -
        return this.getNumber(ps);
      }

      return this.getIdentifier(ps);
    }

    getVariant(ps, hasDefault) {
      let defaultIndex = false;

      if (ps.currentChar === "*") {
        if (hasDefault) {
          throw new ParseError("E0015");
        }

        ps.next();
        defaultIndex = true;
        hasDefault = true;
      }

      ps.expectChar("[");
      ps.skipBlank();
      const key = this.getVariantKey(ps);
      ps.skipBlank();
      ps.expectChar("]");

      if (ps.isValueStart({
        skip: true
      })) {
        const value = this.getValue(ps);
        return new Variant(key, value, defaultIndex);
      }

      throw new ParseError("E0012");
    }

    getVariants(ps) {
      const variants = [];
      let hasDefault = false;

      while (true) {
        const variant = this.getVariant(ps, hasDefault);

        if (variant.default) {
          hasDefault = true;
        }

        variants.push(variant);

        if (!ps.isNextLineVariantStart({
          skip: false
        })) {
          break;
        }

        ps.skipBlank();
      }

      if (!hasDefault) {
        throw new ParseError("E0010");
      }

      return variants;
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

      if (ps.currentChar === "-") {
        num += "-";
        ps.next();
      }

      num = `${num}${this.getDigits(ps)}`;

      if (ps.currentChar === ".") {
        num += ".";
        ps.next();
        num = `${num}${this.getDigits(ps)}`;
      }

      return new NumberLiteral(num);
    }

    getValue(ps) {
      if (ps.currentChar === "{") {
        ps.peek();
        ps.peekBlankInline();

        if (ps.isNextLineVariantStart({
          skip: false
        })) {
          return this.getVariantList(ps);
        }

        ps.resetPeek();
      }

      return this.getPattern(ps);
    }

    getVariantList(ps) {
      ps.expectChar("{");
      ps.skipBlankInline();
      ps.expectLineEnd();
      ps.skipBlank();
      const variants = this.getVariants(ps);
      ps.expectLineEnd();
      ps.skipBlank();
      ps.expectChar("}");
      return new VariantList(variants);
    }

    getPattern(ps) {
      const elements = [];
      let ch;

      while (ch = ps.currentChar) {
        // The end condition for getPattern's while loop is a newline
        // which is not followed by a valid pattern continuation.
        if (ch === EOL && !ps.isNextLineValue({
          skip: false
        })) {
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

        if (lastElement.value === "") {
          elements.pop();
        }
      }

      return new Pattern(elements);
    }

    getTextElement(ps) {
      let buffer = "";
      let ch;

      while (ch = ps.currentChar) {
        if (ch === "{") {
          return new TextElement(buffer);
        }

        if (ch === EOL) {
          if (!ps.isNextLineValue({
            skip: false
          })) {
            return new TextElement(buffer);
          }

          ps.next();
          ps.skipBlankInline();
          buffer += EOL;
          continue;
        }

        if (ch === "\\") {
          ps.next();
          buffer += this.getEscapeSequence(ps);
          continue;
        }

        buffer += ch;
        ps.next();
      }

      return new TextElement(buffer);
    }

    getEscapeSequence(ps) {
      let specials = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : ["{", "\\"];
      const next = ps.currentChar;

      if (specials.includes(next)) {
        ps.next();
        return `\\${next}`;
      }

      if (next === "u") {
        let sequence = "";
        ps.next();

        for (let i = 0; i < 4; i++) {
          const ch = ps.takeHexDigit();

          if (!ch) {
            throw new ParseError("E0026", sequence + ps.currentChar);
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
      ps.skipBlank();
      const selector = this.getSelectorExpression(ps);
      ps.skipBlank();

      if (ps.currentChar === "-") {
        if (ps.peek() !== ">") {
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
        ps.skipBlankInline();
        ps.expectLineEnd();
        ps.skipBlank();
        const variants = this.getVariants(ps);
        ps.skipBlank();

        if (variants.length === 0) {
          throw new ParseError("E0011");
        } // VariantLists are only allowed in other VariantLists.


        if (variants.some(v => v.value.type === "VariantList")) {
          throw new ParseError("E0023");
        }

        return new SelectExpression(selector, variants);
      } else if (selector.type === "AttributeExpression" && selector.ref.type === "TermReference") {
        throw new ParseError("E0019");
      }

      ps.skipBlank();
      return selector;
    }

    getSelectorExpression(ps) {
      if (ps.currentChar === "{") {
        return this.getPlaceable(ps);
      }

      const literal = this.getLiteral(ps);

      if (literal.type !== "MessageReference" && literal.type !== "TermReference") {
        return literal;
      }

      const ch = ps.currentChar;

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
      ps.skipBlank();

      if (ps.currentChar !== ":") {
        return exp;
      }

      if (exp.type !== "MessageReference") {
        throw new ParseError("E0009");
      }

      ps.next();
      ps.skipBlank();
      const val = this.getArgVal(ps);
      return new NamedArgument(exp.id, val);
    }

    getCallArgs(ps) {
      const positional = [];
      const named = [];
      const argumentNames = new Set();
      ps.skipBlank();

      while (true) {
        if (ps.currentChar === ")") {
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

        ps.skipBlank();

        if (ps.currentChar === ",") {
          ps.next();
          ps.skipBlank();
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
      } else if (ps.currentChar === '"') {
        return this.getString(ps);
      }

      throw new ParseError("E0012");
    }

    getString(ps) {
      let val = "";
      ps.expectChar("\"");
      let ch;

      while (ch = ps.takeChar(x => x !== '"' && x !== EOL)) {
        if (ch === "\\") {
          val += this.getEscapeSequence(ps, ["{", "\\", "\""]);
        } else {
          val += ch;
        }
      }

      if (ps.currentChar === EOL) {
        throw new ParseError("E0020");
      }

      ps.expectChar("\"");
      return new StringLiteral(val);
    }

    getLiteral(ps) {
      const ch = ps.currentChar;

      if (ch === EOF) {
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

  function serializeVariantKey(key) {
    switch (key.type) {
      case "Identifier":
        return serializeIdentifier(key);

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
