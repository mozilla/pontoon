/* fluent-syntax@0.3.0 */
(function (global, factory) {
	typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
	typeof define === 'function' && define.amd ? define('fluent-syntax', ['exports'], factory) :
	(factory((global.FluentSyntax = global.FluentSyntax || {})));
}(this, (function (exports) { 'use strict';

class Node {
  constructor() {}
}

class Resource extends Node {
  constructor(body = [], comment = null) {
    super();
    this.type = 'Resource';
    this.body = body;
    this.comment = comment;
  }
}

class Entry extends Node {
  constructor(span = null, annotations = []) {
    super();
    this.type = 'Entry';
    this.span = span;
    this.annotations = annotations;
  }

  addSpan(start, end) {
    this.span = new Span(start, end);
  }

  addAnnotation(annot) {
    this.annotations.push(annot);
  }
}

class Message extends Entry {
  constructor(
    id, value = null, attributes = null, tags = null, comment = null,
    span, annotations
  ) {
    super(span, annotations);
    this.type = 'Message';
    this.id = id;
    this.value = value;
    this.attributes = attributes;
    this.tags = tags;
    this.comment = comment;
  }
}

class Pattern extends Node {
  constructor(elements) {
    super();
    this.type = 'Pattern';
    this.elements = elements;
  }
}

class TextElement extends Node {
  constructor(value) {
    super();
    this.type = 'TextElement';
    this.value = value;
  }
}

class Expression extends Node {
  constructor() {
    super();
    this.type = 'Expression';
  }
}

class StringExpression extends Expression {
  constructor(value) {
    super();
    this.type = 'StringExpression';
    this.value = value;
  }
}

class NumberExpression extends Expression {
  constructor(value) {
    super();
    this.type = 'NumberExpression';
    this.value = value;
  }
}

class MessageReference extends Expression {
  constructor(id) {
    super();
    this.type = 'MessageReference';
    this.id = id;
  }
}

class ExternalArgument extends Expression {
  constructor(id) {
    super();
    this.type = 'ExternalArgument';
    this.id = id;
  }
}

class SelectExpression extends Expression {
  constructor(expression, variants) {
    super();
    this.type = 'SelectExpression';
    this.expression = expression;
    this.variants = variants;
  }
}

class AttributeExpression extends Expression {
  constructor(id, name) {
    super();
    this.type = 'AttributeExpression';
    this.id = id;
    this.name = name;
  }
}

class VariantExpression extends Expression {
  constructor(id, key) {
    super();
    this.type = 'VariantExpression';
    this.id = id;
    this.key = key;
  }
}

class CallExpression extends Expression {
  constructor(callee, args) {
    super();
    this.type = 'CallExpression';
    this.callee = callee;
    this.args = args;
  }
}

class Attribute extends Node {
  constructor(id, value) {
    super();
    this.type = 'Attribute';
    this.id = id;
    this.value = value;
  }
}

class Tag extends Node {
  constructor(name) {
    super();
    this.type = 'Tag';
    this.name = name;
  }
}

class Variant extends Node {
  constructor(key, value, def = false) {
    super();
    this.type = 'Variant';
    this.key = key;
    this.value = value;
    this.default = def;
  }
}

class NamedArgument extends Node {
  constructor(name, val) {
    super();
    this.type = 'NamedArgument';
    this.name = name;
    this.val = val;
  }
}

class Identifier extends Node {
  constructor(name) {
    super();
    this.type = 'Identifier';
    this.name = name;
  }
}

class Symbol$1 extends Identifier {
  constructor(name) {
    super(name);
    this.type = 'Symbol';
  }
}

class Comment extends Entry {
  constructor(content, span, annotations) {
    super(span, annotations);
    this.type = 'Comment';
    this.content = content;
  }
}

class Section extends Entry {
  constructor(name, comment = null, span, annotations) {
    super(span, annotations);
    this.type = 'Section';
    this.name = name;
    this.comment = comment;
  }
}

class Function extends Identifier {
  constructor(name) {
    super(name);
    this.type = 'Function';
  }
}

class Junk extends Entry {
  constructor(content, span, annotations) {
    super(span, annotations);
    this.type = 'Junk';
    this.content = content;
  }
}

class Span extends Node {
  constructor(start, end) {
    super();
    this.type = 'Span';
    this.start = start;
    this.end = end;
  }
}

class Annotation extends Node {
  constructor(code, args = [], message) {
    super();
    this.type = 'Annotation';
    this.code = code;
    this.args = args;
    this.message = message;
  }

  addSpan(start, end) {
    this.span = new Span(start, end);
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

  resetPeek() {
    this.peekIndex = this.index;
    this.peekEnd = this.iterEnd;
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

class ParseError extends Error {
  constructor(code, ...args) {
    super();
    this.code = code;
    this.args = args;
    this.message = getErrorMessage(code, args);
  }
}

function getErrorMessage(code, args) {
  switch (code) {
    case 'E0001':
      return 'Generic error';
    case 'E0002':
      return 'Expected an entry start';
    case 'E0003': {
      const [token] = args;
      return `Expected token: "${token}"`;
    }
    case 'E0004': {
      const [range] = args;
      return `Expected a character from range: "${range}"`;
    }
    case 'E0005': {
      const [id] = args;
      return `Expected entry "${id}" to have a value, attributes or tags`;
    }
    case 'E0006': {
      const [field] = args;
      return `Expected field: "${field}"`;
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

class FTLParserStream extends ParserStream {
  peekLineWS() {
    let ch = this.currentPeek();
    while (ch) {
      if (ch !== ' ' && ch !== '\t') {
        break;
      }
      ch = this.peek();
    }
  }

  skipWSLines() {
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

  skipLineWS() {
    while (this.ch) {
      if (this.ch !== ' ' && this.ch !== '\t') {
        break;
      }
      this.next();
    }
  }

  expectChar(ch) {
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

  takeCharIf(ch) {
    if (this.ch === ch) {
      this.next();
      return true;
    }
    return false;
  }

  takeChar(f) {
    const ch = this.ch;
    if (ch !== undefined && f(ch)) {
      this.next();
      return ch;
    }
    return undefined;
  }

  isIDStart() {
    if (this.ch === undefined) {
      return false;
    }

    const cc = this.ch.charCodeAt(0);
    return ((cc >= 97 && cc <= 122) || // a-z
            (cc >= 65 && cc <= 90) ||  // A-Z
             cc === 95);               // _
  }

  isNumberStart() {
    const cc = this.ch.charCodeAt(0);
    return ((cc >= 48 && cc <= 57) || cc === 45); // 0-9
  }

  isPeekNextLineIndented() {
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

  isPeekNextLineVariantStart() {
    if (!this.currentPeekIs('\n')) {
      return false;
    }

    this.peek();

    const ptr = this.getPeekIndex();

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

  isPeekNextLineAttributeStart() {
    if (!this.currentPeekIs('\n')) {
      return false;
    }

    this.peek();

    const ptr = this.getPeekIndex();

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

  isPeekNextLinePattern() {
    if (!this.currentPeekIs('\n')) {
      return false;
    }

    this.peek();

    const ptr = this.getPeekIndex();

    this.peekLineWS();

    if (this.getPeekIndex() - ptr === 0) {
      this.resetPeek();
      return false;
    }

    if (this.currentPeekIs('}') ||
        this.currentPeekIs('.') ||
        this.currentPeekIs('#') ||
        this.currentPeekIs('[') ||
        this.currentPeekIs('*') ||
        this.currentPeekIs('{')) {
      this.resetPeek();
      return false;
    }

    this.resetPeek();
    return true;
  }

  isPeekNextLineTagStart() {
    if (!this.currentPeekIs('\n')) {
      return false;
    }

    this.peek();

    const ptr = this.getPeekIndex();

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

  skipToNextEntryStart() {
    while (this.next()) {
      if (this.currentIs('\n') && !this.peekCharIs('\n')) {
        this.next();
        if (this.ch === undefined || this.isIDStart() ||
            (this.currentIs('/') && this.peekCharIs('/')) ||
            (this.currentIs('[') && this.peekCharIs('['))) {
          break;
        }
      }
    }
  }

  takeIDStart() {
    if (this.isIDStart()) {
      const ret = this.ch;
      this.next();
      return ret;
    }
    throw new ParseError('E0004', 'a-zA-Z');
  }

  takeIDChar() {
    const closure = ch => {
      const cc = ch.charCodeAt(0);
      return ((cc >= 97 && cc <= 122) || // a-z
              (cc >= 65 && cc <= 90) || // A-Z
              (cc >= 48 && cc <= 57) || // 0-9
               cc === 95 || cc === 45);  // _-
    };

    return this.takeChar(closure);
  }

  takeSymbChar() {
    const closure = ch => {
      if (ch === undefined) {
        return false;
      }

      const cc = ch.charCodeAt(0);
      return ((cc >= 97 && cc <= 122) || // a-z
              (cc >= 65 && cc <= 90) || // A-Z
              (cc >= 48 && cc <= 57) || // 0-9
               cc === 95 || cc === 45 || cc === 32);  // _-
    };

    return this.takeChar(closure);
  }

  takeDigit() {
    const closure = ch => {
      const cc = ch.charCodeAt(0);
      return (cc >= 48 && cc <= 57); // 0-9
    };

    return this.takeChar(closure);
  }
}

/*  eslint no-magic-numbers: [0]  */

function parse(source) {
  let comment = null;

  const ps = new FTLParserStream(source);
  ps.skipWSLines();

  const entries = [];

  while (ps.current()) {
    const entry = getEntryOrJunk(ps);

    if (entry.type === 'Comment' && entries.length === 0) {
      comment = entry;
    } else {
      entries.push(entry);
    }

    ps.skipWSLines();
  }

  return new Resource(entries, comment);
}

function parseEntry(source) {
  const ps = new FTLParserStream(source);
  ps.skipWSLines();
  return getEntryOrJunk(ps);
}

function getEntryOrJunk(ps) {
  const entryStartPos = ps.getIndex();

  try {
    const entry = getEntry(ps);
    entry.addSpan(entryStartPos, ps.getIndex());
    return entry;
  } catch (err) {
    if (!(err instanceof ParseError)) {
      throw err;
    }

    const annot = new Annotation(err.code, err.args, err.message);
    annot.addSpan(ps.getIndex(), ps.getIndex());

    ps.skipToNextEntryStart();
    const nextEntryStart = ps.getIndex();

    // Create a Junk instance
    const slice = ps.getSlice(entryStartPos, nextEntryStart);
    const junk = new Junk(slice);
    junk.addSpan(entryStartPos, nextEntryStart);
    junk.addAnnotation(annot);
    return junk;
  }
}

function getEntry(ps) {
  let comment;

  if (ps.currentIs('/')) {
    comment = getComment(ps);
  }

  if (ps.currentIs('[')) {
    return getSection(ps, comment);
  }

  if (ps.isIDStart()) {
    return getMessage(ps, comment);
  }

  if (comment) {
    return comment;
  }
  throw new ParseError('E0002');
}

function getComment(ps) {
  ps.expectChar('/');
  ps.expectChar('/');
  ps.takeCharIf(' ');

  let content = '';

  while (true) {
    let ch;
    while ((ch = ps.takeChar(x => x !== '\n'))) {
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

function getSection(ps, comment) {
  ps.expectChar('[');
  ps.expectChar('[');

  ps.skipLineWS();

  const symb = getSymbol(ps);

  ps.skipLineWS();

  ps.expectChar(']');
  ps.expectChar(']');

  ps.skipLineWS();

  ps.expectChar('\n');

  return new Section(symb, comment);
}

function getMessage(ps, comment) {
  const id = getIdentifier(ps);

  ps.skipLineWS();

  let pattern;
  let attrs;
  let tags;

  if (ps.currentIs('=')) {
    ps.next();
    ps.skipLineWS();

    pattern = getPattern(ps);
  }

  if (ps.isPeekNextLineAttributeStart()) {
    attrs = getAttributes(ps);
  }

  if (ps.isPeekNextLineTagStart()) {
    if (attrs !== undefined) {
      throw new ParseError('E0012');
    }
    tags = getTags(ps);
  }

  if (pattern === undefined && attrs === undefined && tags === undefined) {
    throw new ParseError('E0005', id.name);
  }

  return new Message(id, pattern, attrs, tags, comment);
}

function getAttributes(ps) {
  const attrs = [];

  while (true) {
    ps.expectChar('\n');
    ps.skipLineWS();

    ps.expectChar('.');

    const key = getIdentifier(ps);

    ps.skipLineWS();

    ps.expectChar('=');

    ps.skipLineWS();

    const value = getPattern(ps);

    if (value === undefined) {
      throw new ParseError('E0006', 'value');
    }

    attrs.push(new Attribute(key, value));

    if (!ps.isPeekNextLineAttributeStart()) {
      break;
    }
  }
  return attrs;
}

function getTags(ps) {
  const tags = [];

  while (true) {
    ps.expectChar('\n');
    ps.skipLineWS();

    ps.expectChar('#');

    const symbol = getSymbol(ps);

    tags.push(new Tag(symbol));

    if (!ps.isPeekNextLineTagStart()) {
      break;
    }
  }
  return tags;
}

function getIdentifier(ps) {
  let name = '';

  name += ps.takeIDStart();

  let ch;
  while ((ch = ps.takeIDChar())) {
    name += ch;
  }

  return new Identifier(name);
}

function getVariantKey(ps) {
  const ch = ps.current();

  if (!ch) {
    throw new ParseError('E0013');
  }

  const cc = ch.charCodeAt(0);

  if ((cc >= 48 && cc <= 57) || cc === 45) { // 0-9, -
    return getNumber(ps);
  }

  return getSymbol(ps);
}

function getVariants(ps) {
  const variants = [];
  let hasDefault = false;

  while (true) {
    let defaultIndex = false;

    ps.expectChar('\n');
    ps.skipLineWS();

    if (ps.currentIs('*')) {
      if (hasDefault) {
        throw new ParseError('E0015');
      }
      ps.next();
      defaultIndex = true;
      hasDefault = true;
    }

    ps.expectChar('[');

    const key = getVariantKey(ps);

    ps.expectChar(']');

    ps.skipLineWS();

    const value = getPattern(ps);

    if (!value) {
      throw new ParseError('E0006', 'value');
    }

    variants.push(new Variant(key, value, defaultIndex));

    if (!ps.isPeekNextLineVariantStart()) {
      break;
    }
  }

  if (!hasDefault) {
    throw new ParseError('E0010');
  }

  return variants;
}

function getSymbol(ps) {
  let name = '';

  name += ps.takeIDStart();

  while (true) {
    const ch = ps.takeSymbChar();
    if (ch) {
      name += ch;
    } else {
      break;
    }
  }

  return new Symbol$1(name.trimRight());
}

function getDigits(ps) {
  let num = '';

  let ch;
  while ((ch = ps.takeDigit())) {
    num += ch;
  }

  if (num.length === 0) {
    throw new ParseError('E0004', '0-9');
  }

  return num;
}

function getNumber(ps) {
  let num = '';

  if (ps.currentIs('-')) {
    num += '-';
    ps.next();
  }

  num = `${num}${getDigits(ps)}`;

  if (ps.currentIs('.')) {
    num += '.';
    ps.next();
    num = `${num}${getDigits(ps)}`;
  }

  return new NumberExpression(num);
}

function getPattern(ps) {
  let buffer = '';
  const elements = [];
  let firstLine = true;

  let ch;
  while ((ch = ps.current())) {
    if (ch === '\n') {
      if (firstLine && buffer.length !== 0) {
        break;
      }

      if (!ps.isPeekNextLinePattern()) {
        break;
      }

      ps.next();
      ps.skipLineWS();

      firstLine = false;

      if (buffer.length !== 0) {
        buffer += ch;
      }
      continue;
    } else if (ch === '\\') {
      const ch2 = ps.peek();
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
        elements.push(new TextElement(buffer));
      }

      buffer = '';

      elements.push(getExpression(ps));

      ps.expectChar('}');

      continue;
    } else {
      buffer += ps.ch;
    }
    ps.next();
  }

  if (buffer.length !== 0) {
    elements.push(new TextElement(buffer));
  }

  return new Pattern(elements);
}

function getExpression(ps) {
  if (ps.isPeekNextLineVariantStart()) {
    const variants = getVariants(ps);

    ps.expectChar('\n');
    ps.expectChar(' ');
    ps.skipLineWS();

    return new SelectExpression(null, variants);
  }

  const selector = getSelectorExpression(ps);

  ps.skipLineWS();

  if (ps.currentIs('-')) {
    ps.peek();
    if (!ps.currentPeekIs('>')) {
      ps.resetPeek();
    } else {
      ps.next();
      ps.next();

      ps.skipLineWS();

      const variants = getVariants(ps);

      if (variants.length === 0) {
        throw new ParseError('E0011');
      }

      ps.expectChar('\n');
      ps.expectChar(' ');
      ps.skipLineWS();

      return new SelectExpression(selector, variants);
    }
  }

  return selector;
}

function getSelectorExpression(ps) {
  const literal = getLiteral(ps);

  if (literal.type !== 'MessageReference') {
    return literal;
  }

  const ch = ps.current();

  if (ch === '.') {
    ps.next();

    const attr = getIdentifier(ps);
    return new AttributeExpression(literal.id, attr);
  }

  if (ch === '[') {
    ps.next();

    const key = getVariantKey(ps);

    ps.expectChar(']');

    return new VariantExpression(literal.id, key);
  }

  if (ch === '(') {
    ps.next();

    const args = getCallArgs(ps);

    ps.expectChar(')');

    return new CallExpression(literal.id, args);
  }

  return literal;
}

function getCallArgs(ps) {
  const args = [];

  ps.skipLineWS();

  while (true) {
    if (ps.current() === ')') {
      break;
    }

    const exp = getSelectorExpression(ps);

    ps.skipLineWS();

    if (ps.current() === ':') {
      if (exp.type !== 'MessageReference') {
        throw new ParseError('E0009');
      }

      ps.next();
      ps.skipLineWS();

      const val = getArgVal(ps);

      args.push(new NamedArgument(exp.id, val));
    } else {
      args.push(exp);
    }

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

function getArgVal(ps) {
  if (ps.isNumberStart()) {
    return getNumber(ps);
  } else if (ps.currentIs('"')) {
    return getString(ps);
  }
  throw new ParseError('E0006', 'value');
}

function getString(ps) {
  let val = '';

  ps.expectChar('"');

  let ch;
  while ((ch = ps.takeChar(x => x !== '"'))) {
    val += ch;
  }

  ps.next();

  return new StringExpression(val);

}

function getLiteral(ps) {
  const ch = ps.current();

  if (!ch) {
    throw new ParseError('E0014');
  }

  if (ps.isNumberStart()) {
    return getNumber(ps);
  } else if (ch === '"') {
    return getString(ps);
  } else if (ch === '$') {
    ps.next();
    const name = getIdentifier(ps);
    return new ExternalArgument(name);
  }

  const name = getIdentifier(ps);
  return new MessageReference(name);
}

function indent(content) {
  return content.split('\n').join('\n    ');
}


function containNewLine(elems) {
  const withNewLine = elems.filter(
    elem => (elem.type === 'TextElement' && elem.value.includes('\n'))
  );
  return !!withNewLine.length;
}


function serialize(resource, withJunk = false) {
  const parts = [];

  if (resource.comment) {
    parts.push(
      `${serializeComment(resource.comment)}\n\n`
    );
  }

  for (const entry of resource.body) {
    if (entry.types !== 'Junk' || withJunk) {
      parts.push(serializeEntry(entry));
    }
  }

  return parts.join('');
}


function serializeEntry(entry) {
  switch (entry.type) {
    case 'Message':
      return serializeMessage(entry);
    case 'Section':
      return serializeSection(entry);
    case 'Comment':
      return serializeComment(entry);
    case 'Junk':
      return serializeJunk(entry);
    default :
      throw new Error(`Unknown entry type: ${entry.type}`);
  }
}


function serializeComment(comment) {
  return comment.content.split('\n').map(
    line => `// ${line}`
  ).join('\n');
}


function serializeSection(section) {
  const name = serializeSymbol(section.name);

  if (section.comment) {
    const comment = serializeComment(section.comment);
    return `\n\n${comment}\n[[ ${name} ]]\n\n`;
  }

  return `\n\n[[ ${name} ]]\n\n`;
}


function serializeJunk(junk) {
  return junk.content;
}


function serializeMessage(message) {
  const parts = [];

  if (message.comment) {
    parts.push(serializeComment(message.comment));
    parts.push('\n');
  }

  parts.push(serializeIdentifier(message.id));

  if (message.value) {
    parts.push(' =');
    parts.push(serializeValue(message.value));
  }

  if (message.tags) {
    for (const tag of message.tags) {
      parts.push(serializeTag(tag));
    }
  }

  if (message.attributes) {
    for (const attribute of message.attributes) {
      parts.push(serializeAttribute(attribute));
    }
  }

  parts.push('\n');
  return parts.join('');
}


function serializeTag(tag) {
  const name = serializeSymbol(tag.name);
  return `\n    #${name}`;
}


function serializeAttribute(attribute) {
  const id = serializeIdentifier(attribute.id);
  const value = indent(serializeValue(attribute.value));
  return `\n    .${id} =${value}`;
}


function serializeValue(pattern) {
  const content = indent(serializePattern(pattern));
  const multi = containNewLine(pattern.elements);

  if (multi) {
    return `\n    ${content}`;
  }

  return ` ${content}`;
}


function serializePattern(pattern) {
  return pattern.elements.map(serializeElement).join('');
}


function serializeElement(element) {
  switch (element.type) {
    case 'TextElement':
      return serializeTextElement(element);
    case 'SelectExpression':
      return `{${serializeSelectExpression(element)}}`;
    default:
      return `{ ${serializeExpression(element)} }`;
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
      throw new Error(`Unknown expression type: ${expr.type}`);
  }
}


function serializeStringExpression(expr) {
  return `"${expr.value}"`;
}


function serializeNumberExpression(expr) {
  return expr.value;
}


function serializeMessageReference(expr) {
  return serializeIdentifier(expr.id);
}


function serializeExternalArgument(expr) {
  return `$${serializeIdentifier(expr.id)}`;
}


function serializeSelectExpression(expr) {
  const parts = [];

  if (expr.expression) {
    const selector = ` ${serializeExpression(expr.expression)} ->`;
    parts.push(selector);
  }

  for (const variant of expr.variants) {
    parts.push(serializeVariant(variant));
  }

  parts.push('\n');
  return parts.join('');
}


function serializeVariant(variant) {
  const key = serializeVariantKey(variant.key);
  const value = indent(serializeValue(variant.value));

  if (variant.default) {
    return `\n   *[${key}]${value}`;
  }

  return `\n    [${key}]${value}`;
}


function serializeAttributeExpression(expr) {
  const id = serializeIdentifier(expr.id);
  const name = serializeIdentifier(expr.name);
  return `${id}.${name}`;
}


function serializeVariantExpression(expr) {
  const id = serializeIdentifier(expr.id);
  const key = serializeVariantKey(expr.key);
  return `${id}[${key}]`;
}


function serializeCallExpression(expr) {
  const fun = serializeFunction(expr.callee);
  const args = expr.args.map(serializeCallArgument).join(', ');
  return `${fun}(${args})`;
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
  const name = serializeIdentifier(arg.name);
  const value = serializeArgumentValue(arg.val);
  return `${name}: ${value}`;
}


function serializeArgumentValue(argval) {
  switch (argval.type) {
    case 'StringExpression':
      return serializeStringExpression(argval);
    case 'NumberExpression':
      return serializeNumberExpression(argval);
    default:
      throw new Error(`Unknown argument type: ${argval.type}`);
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
      throw new Error(`Unknown variant key type: ${key.type}`);
  }
}


function serializeFunction(fun) {
  return fun.name;
}

function lineOffset(source, pos) {
  // Substract 1 to get the offset.
  return source.substring(0, pos).split('\n').length - 1;
}

function columnOffset(source, pos) {
  const lastLineBreak = source.lastIndexOf('\n', pos);
  return lastLineBreak === -1
    ? pos
    // Substracting two offsets gives length; substract 1 to get the offset.
    : pos - lastLineBreak - 1;
}

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
exports.Symbol = Symbol$1;
exports.Comment = Comment;
exports.Section = Section;
exports.Function = Function;
exports.Junk = Junk;
exports.Span = Span;
exports.Annotation = Annotation;
exports.parse = parse;
exports.parseEntry = parseEntry;
exports.serialize = serialize;
exports.serializeEntry = serializeEntry;

Object.defineProperty(exports, '__esModule', { value: true });

})));
