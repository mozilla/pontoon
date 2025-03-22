#
# Copyright 2004-2008 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
Classes that hold units of PHP localisation files :class:`phpunit` or
entire files :class:`phpfile`. These files are used in translating many
PHP based applications.

Only PHP files written with these conventions are supported:

.. code-block:: php

   <?php
   $lang['item'] = "vale";  # Array of values
   $some_entity = "value";  # Named variables
   define("ENTITY", "value");
   $lang = array(
      'item1' => 'value1'    ,   #Supports space before comma
      'item2' => 'value2',
   );
   $lang = array(    # Nested arrays
      'item1' => 'value1',
      'item2' => array(
         'key' => 'value'    ,   #Supports space before comma
         'key2' => 'value2',
      ),
   );

Nested arrays without key for nested array are not supported:

.. code-block:: php

   <?php
   $lang = array(array('key' => 'value'));

The working of PHP strings and specifically the escaping conventions which
differ between single quote (') and double quote (") characters are
implemented as outlined in the PHP documentation for the
`String type <http://www.php.net/language.types.string>`_.
"""

import re

from phply.phpast import (
    Array,
    ArrayElement,
    ArrayOffset,
    Assignment,
    BinaryOp,
    FunctionCall,
    InlineHTML,
    Node,
    Return,
    Variable,
)
from phply.phplex import FilteredLexer, full_lexer
from phply.phpparse import make_parser

from translate.misc.multistring import multistring
from translate.storage import base


def wrap_production(func):
    """Decorator for production functions to store lexer positions."""

    def prod(n):
        func(n)
        if isinstance(n[0], Node):
            startpos = min(getattr(i, "lexpos", 0) for i in n.slice[1:])
            endpos = max(getattr(i, "endlexpos", 0) for i in n.slice[1:])
            n[0].lexpositions = startpos, endpos
        elif isinstance(n[0], list) and n[0] and isinstance(n[0][-1], ArrayElement):
            startpos = min(getattr(i, "lexpos", 0) for i in n.slice[1:])
            endpos = max(getattr(i, "endlexpos", 0) for i in n.slice[1:])
            n[0][-1].lexpositions = startpos, endpos

    return prod


class PHPLexer(FilteredLexer):
    def __init__(self):
        super().__init__(full_lexer.clone())
        self.tokens = []
        self.pos = 0
        self.codepos = 0

    def next_lexer_token(self):
        token = self.lexer.token()
        if token is not None:
            self.tokens.append(token)
        return token

    def extract_comments(self, end):
        """
        Extract comments related to given parser positions.

        Must be called sequentially for consequent statements.
        """
        comments = []
        # Process all tokens to end of statement
        while self.tokens[self.pos].lexpos < end:
            if self.tokens[self.pos].type in {"COMMENT", "DOC_COMMENT"}:
                comments.append(self.tokens[self.pos].value.strip())
            self.pos += 1
        # Skip end of statement
        self.pos += 1
        # Proceed comments till newline
        length = len(self.tokens)
        while self.pos < length and self.tokens[self.pos].type in {
            "COMMENT",
            "WHITESPACE",
        }:
            token_type = self.tokens[self.pos].type
            token_value = self.tokens[self.pos].value
            self.pos += 1
            if token_type == "WHITESPACE":
                if "\n" in token_value:
                    break
                continue
            comments.append(token_value.strip())
            if "\n" in token_value:
                break
        return comments

    def extract_name(self, terminator, start, end):
        """Extract current value name."""
        result = ""
        pos = self.pos
        while self.tokens[pos].lexpos < start:
            pos += 1
        while self.tokens[pos].lexpos < end and self.tokens[pos].type != terminator:
            result += self.tokens[pos].value
            pos += 1
        self.codepos = pos
        return result.rstrip()

    def extract_quote(self):
        """Extract quote style."""
        pos = max(self.pos, self.codepos)
        while self.tokens[pos].type not in {
            "QUOTE",
            "CONSTANT_ENCAPSED_STRING",
            "START_NOWDOC",
        }:
            pos += 1
        if self.tokens[pos].type == "QUOTE":
            return '"'
        return "'"

    def extract_array(self):
        pos = max(self.pos, self.codepos)
        while self.tokens[pos].type not in {"ARRAY", "LBRACKET"}:
            pos += 1
        self.codepos = pos
        if self.tokens[pos].type == "ARRAY":
            return ""
        return "[]"


def phpencode(text, quotechar="'"):
    """
    Convert Python string to PHP escaping.

    The encoding is implemented for
    `'single quote' <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.single>`_
    and `"double quote" <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.double>`_
    syntax.

    heredoc and nowdoc are not implemented and it is not certain whether this
    would ever be needed for PHP localisation needs.
    """
    if not text:
        return text
    if quotechar == '"':
        # \n may be converted to \\n but we don't.  This allows us to preserve
        # pretty layout that might have appeared in muliline entries we might
        # lose some "blah\nblah" layouts but that's probably not the most
        # frequent use case. See bug 588
        escapes = [
            ("\\", "\\\\"),
            ("\r", "\\r"),
            ("\t", "\\t"),
            ("\v", "\\v"),
            ("\f", "\\f"),
            ("\\\\$", "\\$"),
            ('"', '\\"'),
            ("\\\\", "\\"),
        ]
        for a, b in escapes:
            text = text.replace(a, b)
        return text
    return text.replace(f"{quotechar}", f"\\{quotechar}")


def phpdecode(text, quotechar="'"):
    """Convert PHP escaped string to a Python string."""
    escape_encoding = "unicode_escape"

    def decode_octal_hex(match):
        r"""Decode Octal \NNN and Hex values."""
        if "octal" in match.groupdict():
            return match.groupdict()["octal"].encode("latin-1").decode(escape_encoding)
        if "hex" in match.groupdict():
            return match.groupdict()["hex"].encode("latin-1").decode(escape_encoding)
        return match.group

    if not text:
        return text
    if quotechar == '"':
        # We do not escape \$ as it is used by variables and we can't
        # roundtrip that item.
        escapes = [
            ('\\"', '"'),
            ("\\\\", "\\"),
            ("\\n", "\n"),
            ("\\r", "\r"),
            ("\\t", "\t"),
            ("\\v", "\v"),
            ("\\f", "\f"),
        ]
        for a, b in escapes:
            text = text.replace(a, b)
        text = re.sub(r"(?P<octal>\\[0-7]{1,3})", decode_octal_hex, text)
        return re.sub(r"(?P<hex>\\x[0-9A-Fa-f]{1,2})", decode_octal_hex, text)
    return text.replace("\\'", "'").replace("\\\\", "\\")


class phpunit(base.TranslationUnit):
    """A unit of a PHP file: a name, a value, and any comments associated."""

    def __init__(self, source=""):
        """Construct a blank phpunit."""
        self.escape_type = "'"
        super().__init__(source)
        self.name = "$TTK_PLACEHOLDER"
        self.value = ""
        self.translation = ""
        self._comments = []
        self.source = source

    @property
    def source(self):
        return self.value

    @source.setter
    def source(self, source):
        """Set the source AND the target to be equal."""
        self._rich_source = None
        self.value = source

    @property
    def target(self):
        return self.translation

    @target.setter
    def target(self, target):
        self._rich_target = None
        self.translation = target

    def __str__(self):
        """Convert to a string."""
        return self.getoutput()

    def get_raw_value(self):
        return self.translation or self.value

    def getoutput(self, indent="", name=None):
        """Convert the unit back into formatted lines for a php file."""
        if "->" in self.name and name == "[]":
            fmt = "{1}{2}{1},\n"
        elif "->" in self.name:
            fmt = "{0} => {1}{2}{1},\n"
            if name is not None and name[0] == name[-1] and name[0] in {"'", '"'}:
                name = name[0] + phpencode(name[1:-1], name[0]) + name[0]
        elif self.name.startswith("define"):
            fmt = "{0}, {1}{2}{1});\n"
        else:
            fmt = "{0} = {1}{2}{1};\n"
        out = fmt.format(
            name or self.name,
            self.escape_type,
            phpencode(self.get_raw_value(), self.escape_type),
        )
        joiner = "\n" + indent
        return indent + joiner.join([*self._comments, out])

    def addlocation(self, location):
        self.name = location

    def getlocations(self):
        return [self.name]

    def addnote(self, text, origin=None, position="append"):
        if origin in {"programmer", "developer", "source code", None}:
            if position == "append":
                self._comments.append(text)
            else:
                self._comments = [text]
        else:
            super().addnote(text, origin=origin, position=position)

    def getnotes(self, origin=None):
        if origin in {"programmer", "developer", "source code", None}:
            return "\n".join(self._comments)
        return super().getnotes(origin)

    def removenotes(self, origin=None):
        self._comments = []

    def isblank(self):
        """Return whether this is a blank element, containing only comments."""
        return not (self.name or self.value)

    def getid(self):
        return self.name

    def setid(self, value):
        # Sanitize name to produce valid syntax
        if not value.startswith(("$", "define(", "return")):
            self.name = "${}".format(value.replace(" ", "_"))
        else:
            self.name = value


class phpfile(base.TranslationStore):
    """This class represents a PHP file, made up of phpunits."""

    UnitClass = phpunit

    def __init__(self, inputfile=None, **kwargs):
        """Construct a phpfile, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self.filename = getattr(inputfile, "name", "")
        if inputfile is not None:
            phpsrc = inputfile.read()
            inputfile.close()
            self.parse(phpsrc)

    def serialize(self, out):
        """Convert the units back to lines."""

        def write(text):
            out.write(text.encode(self.encoding))

        def handle_array(unit, arrname, handled, indent=0):
            if arrname in handled:
                return
            childs = set()
            # Default to classic array
            init = "array("
            close = ")"
            name = arrname
            # Handle [] style array
            if name.endswith("[]"):
                init = "["
                close = "]"
                name = name[:-2]
            # Handle return, assignment or sub array
            if "->" in arrname:
                separator = " =>"
                name = name.rsplit("->", 1)[-1]
            elif name == "return":
                separator = ""
            else:
                separator = " ="
            # Write array start
            write("{}{}{} {}\n".format(" " * indent, name, separator, init))
            indent += 4
            prefix = f"{arrname}->"
            pref_len = len(prefix)
            for item in self.units:
                if not item.name.startswith(prefix):
                    continue
                name = item.name[pref_len:]
                if "->" in name:
                    handle_array(item, prefix + name.split("->", 1)[0], childs, indent)
                else:
                    write(item.getoutput(" " * indent, name))
            # Write array end
            write(
                "{}{}{}\n".format(
                    " " * (indent - 4), close, "," if "->" in arrname else ";"
                )
            )
            handled.add(arrname)

        write("<?php\n")

        # List of handled arrays
        handled = set()
        for unit in self.units:
            if "->" in unit.name:
                handle_array(unit, unit.name.split("->", 1)[0], handled)
            else:
                write(unit.getoutput())

    def create_and_add_unit(self, name, value, escape_type, comments):
        newunit = self.UnitClass()
        newunit.escape_type = escape_type
        newunit.addlocation(name)
        newunit.source = value
        for comment in comments:
            newunit.addnote(comment, "developer")
        self.addunit(newunit)

    def parse(self, phpsrc):
        """Read the source of a PHP file in and include them as units."""

        def handle_array(prefix, nodes, lexer):
            prefix += lexer.extract_array()
            for item in nodes:
                assert isinstance(item, ArrayElement)
                if item.key is None:
                    name = []
                else:
                    # To update lexer current position
                    lexer.extract_name("DOUBLE_ARROW", *item.lexpositions)
                    if isinstance(item.key, BinaryOp):
                        name = f"'{concatenate(item.key)}'"
                    elif isinstance(item.key, (int, float)):
                        name = f"{item.key}"
                    else:
                        name = f"'{item.key}'"
                if prefix:
                    name = f"{prefix}->{name}"
                if isinstance(item.value, Array):
                    handle_array(name, item.value.nodes, lexer)
                elif isinstance(item.value, str):
                    self.create_and_add_unit(
                        name,
                        item.value,
                        lexer.extract_quote(),
                        lexer.extract_comments(item.lexpositions[1]),
                    )

        def concatenate(item):
            if isinstance(item, str):
                return item
            if isinstance(item, Variable):
                return item.name
            assert isinstance(item, BinaryOp)
            return concatenate(item.left) + concatenate(item.right)

        parser = make_parser()
        for item in parser.productions:
            item.callable = wrap_production(item.callable)
        lexer = PHPLexer()
        tree = parser.parse(phpsrc.decode(self.encoding), lexer=lexer, tracking=True)
        # Handle text without PHP start
        if len(tree) == 1 and isinstance(tree[0], InlineHTML):
            self.parse(b"<?php\n" + phpsrc)
            return
        for item in tree:
            if isinstance(item, FunctionCall):
                if item.name == "define":
                    self.create_and_add_unit(
                        lexer.extract_name("COMMA", *item.lexpositions),
                        item.params[1].node,
                        lexer.extract_quote(),
                        lexer.extract_comments(item.lexpositions[1]),
                    )
            elif isinstance(item, Assignment):
                if isinstance(item.node, (ArrayOffset, Variable)):
                    name = lexer.extract_name("EQUALS", *item.lexpositions)
                    if isinstance(item.expr, Array):
                        handle_array(name, item.expr.nodes, lexer)
                    elif isinstance(item.expr, str):
                        self.create_and_add_unit(
                            name,
                            item.expr,
                            lexer.extract_quote(),
                            lexer.extract_comments(item.lexpositions[1]),
                        )
                    elif isinstance(item.expr, BinaryOp) and item.expr.op == ".":
                        self.create_and_add_unit(
                            name,
                            concatenate(item.expr),
                            lexer.extract_quote(),
                            lexer.extract_comments(item.lexpositions[1]),
                        )
            elif isinstance(item, Return):
                if isinstance(item.node, Array):
                    # Adjustextractor position
                    lexer.extract_name("RETURN", *item.lexpositions)
                    handle_array("return", item.node.nodes, lexer)


class LaravelPHPUnit(phpunit):
    def get_raw_value(self):
        result = self.translation or self.value
        if isinstance(result, multistring):
            return "|".join(result.strings)
        return result


class LaravelPHPFile(phpfile):
    UnitClass = LaravelPHPUnit

    def create_and_add_unit(self, name, value, escape_type, comments):
        if "|" in value:
            value = multistring(value.split("|"))
        super().create_and_add_unit(name, value, escape_type, comments)
