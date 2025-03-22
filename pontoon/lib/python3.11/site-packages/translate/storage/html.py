#
# Copyright 2004-2006,2008 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#

"""module for parsing html files for translation."""

import html.parser
import re
from html.entities import html5

from translate.storage import base
from translate.storage.base import ParseError

# Override the piclose tag from simple > to ?> otherwise we consume HTML
# within the processing instructions
html.parser.piclose = re.compile(r"\?>")


class htmlunit(base.TranslationUnit):
    """A unit of translatable/localisable HTML content."""

    def __init__(self, source=None):
        super().__init__(source)
        self.locations = []

    def addlocation(self, location):
        self.locations.append(location)

    def getlocations(self):
        return self.locations


class htmlfile(html.parser.HTMLParser, base.TranslationStore):
    UnitClass = htmlunit

    TRANSLATABLE_ELEMENTS = [
        "address",
        "article",
        "aside",
        "blockquote",
        "caption",
        "dd",
        "dt",
        "div",
        "figcaption",
        "footer",
        "header",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "label",
        "li",
        "main",
        "nav",
        "option",
        "p",
        "pre",
        "section",
        "td",
        "th",
        "title",
    ]
    """These HTML elements (tags) will be extracted as translation units, unless
    they lack translatable text content.
    In case one translatable element is embedded in another, the outer translation
    unit will be split into the parts before and after the inner translation unit."""

    TRANSLATABLE_ATTRIBUTES = [
        "abbr",  # abbreviation for a table header cell
        "alt",
        "lang",  # only for the html element -- see extract_translatable_attributes()
        "summary",
        "title",  # tooltip text for an element
        "value",
    ]
    """Text from these HTML attributes will be extracted as translation units.
    Note: the content attribute of meta tags is a special case."""

    TRANSLATABLE_METADATA = ["description", "keywords"]
    """Document metadata from meta elements with these names will be extracted as translation units.
    Reference `<https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta/name>`_"""

    EMPTY_HTML_ELEMENTS = [
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    ]
    """An empty element is an element that cannot have any child nodes (i.e., nested
    elements or text nodes). In HTML, using a closing tag on an empty element is
    usually invalid.
    Reference `<https://developer.mozilla.org/en-US/docs/Glossary/Empty_element>`_"""

    WHITESPACE_RE = re.compile(r"\s+")

    LEADING_WHITESPACE_RE = re.compile(r"^(\s+)")

    TRAILING_WHITESPACE_RE = re.compile(r"(\s+)$")

    ENCODING_RE = re.compile(
        rb"""<meta.*
                                content.*=.*?charset.*?=\s*?
                                ([^\s]*)
                                \s*?["']\s*?>
                             """,
        re.VERBOSE | re.IGNORECASE,
    )

    def __init__(self, inputfile=None, callback=None):
        super().__init__(convert_charrefs=False)
        base.TranslationStore.__init__(self)

        # store parameters
        self.filename = getattr(inputfile, "name", None)
        if callback is None:
            self.callback = self._simple_callback
        else:
            self.callback = callback

        # initialize state
        self.filesrc = ""
        self.tag_path = []
        self.tu_content = []
        self.tu_location = None

        # parse
        if inputfile is not None:
            htmlsrc = inputfile.read()
            inputfile.close()
            self.parse(htmlsrc)

    @staticmethod
    def _simple_callback(string):
        return string

    def guess_encoding(self, htmlsrc):
        """
        Returns the encoding of the html text.

        We look for 'charset=' within a meta tag to do this.
        """
        result = self.ENCODING_RE.findall(htmlsrc)
        if result:
            self.encoding = result[0].decode("ascii")
        return self.encoding

    def do_encoding(self, htmlsrc):
        """Return the html text properly encoded based on a charset."""
        self.guess_encoding(htmlsrc)
        return htmlsrc.decode(self.encoding)

    def parse(self, htmlsrc):
        htmlsrc = self.do_encoding(htmlsrc)
        self.feed(htmlsrc)

    def begin_translation_unit(self):
        # at the start of a translation unit:
        # this interrupts any translation unit in progress, so process the queue
        # and prepare for the new.
        self.emit_translation_unit()
        self.tu_content = []
        self.tu_location = "%s+%s:%d-%d" % (
            self.filename,
            ".".join(self.tag_path),
            self.getpos()[0],
            self.getpos()[1] + 1,
        )

    def end_translation_unit(self):
        # at the end of a translation unit:
        # process the queue and reset state.
        self.emit_translation_unit()
        self.tu_content = []
        self.tu_location = None

    def append_markup(self, markup):
        # if within a translation unit: add to the queue to be processed later.
        # otherwise handle immediately.
        if self.tu_location:
            self.tu_content.append(markup)
        else:
            self.emit_attribute_translation_units(markup)
            self.filesrc += markup["html_content"]

    def emit_translation_unit(self):
        # scan through the queue:
        # - find the first and last translatable markup elements: the captured
        #   interval [start, end)
        # - match start and end tags
        start = 0
        end = 0
        tagstack = []
        tagmap = {}
        tag = None
        do_normalize = True
        for pos, content in enumerate(self.tu_content):
            if content["type"] != "endtag" and tag in self.EMPTY_HTML_ELEMENTS:
                match = tagstack.pop()
                tag = None

            if self.has_translatable_content(content):
                if end == 0:
                    start = pos
                end = pos + 1
            elif content["type"] == "starttag":
                tagstack.append(pos)
                tag = content["tag"]
                if tag == "pre":
                    do_normalize = False
            elif content["type"] == "endtag":
                if tagstack:
                    match = tagstack.pop()
                    tagmap[match] = pos
                    tagmap[pos] = match
                tag = None

        # if no translatable content found: process all the content in the queue
        # as if the translation unit didn't exist.
        if end == 0:
            for markup in self.tu_content:
                self.emit_attribute_translation_units(markup)
                self.filesrc += markup["html_content"]
            return

        # scan the start and end tags captured between translatable content;
        # extend the captured interval to include the matching tags
        for pos in range(start + 1, end - 1):
            if self.tu_content[pos]["type"] in {"starttag", "endtag"} and pos in tagmap:
                match = tagmap[pos]
                start = min(start, match)
                end = max(end, match + 1)

        # emit leading uncaptured markup elements
        for markup in self.tu_content[0:start]:
            if markup["type"] != "comment":
                self.emit_attribute_translation_units(markup)
                self.filesrc += markup["html_content"]

        # emit captured markup elements
        if start < end:
            html_content = []
            for markup in self.tu_content[start:end]:
                if markup["type"] != "comment":
                    if "untranslated_html" in markup:
                        html_content.append(markup["untranslated_html"])
                    else:
                        html_content.append(markup["html_content"])
            html_content = "".join(html_content)
            if do_normalize:
                normalized_content = self.WHITESPACE_RE.sub(" ", html_content.strip())
            else:
                normalized_content = html_content.strip()
            assert normalized_content  # shouldn't be here otherwise

            unit = self.addsourceunit(normalized_content)
            unit.addlocation(self.tu_location)
            comments = [
                markup["note"]
                for markup in self.tu_content
                if markup["type"] == "comment"
            ]
            if comments:
                unit.addnote("\n".join(comments))

            html_content = (
                self.get_leading_whitespace(html_content)
                + self.callback(normalized_content)
                + self.get_trailing_whitespace(html_content)
            )
            self.filesrc += html_content

        # emit trailing uncaptured markup elements
        for markup in self.tu_content[end : len(self.tu_content)]:
            if markup["type"] != "comment":
                self.emit_attribute_translation_units(markup)
                self.filesrc += markup["html_content"]

    @staticmethod
    def has_translatable_content(markup):
        # processing instructions count as translatable content, because PHP
        return markup["type"] in {"data", "pi"} and markup["html_content"].strip()

    def extract_translatable_attributes(self, tag, attrs):
        result = []
        if tag == "meta":
            tu = self.create_metadata_attribute_tu(attrs)
            if tu:
                result.append(tu)
        else:
            for attrname, attrvalue in attrs:
                if (
                    attrname in self.TRANSLATABLE_ATTRIBUTES
                    and self.translatable_attribute_matches_tag(attrname, tag)
                ):
                    tu = self.create_attribute_tu(attrname, attrvalue)
                    if tu:
                        result.append(tu)
        return result

    def create_metadata_attribute_tu(self, attrs):
        attrs_dict = dict(attrs)
        name = attrs_dict["name"].lower() if "name" in attrs_dict else None
        if name in self.TRANSLATABLE_METADATA and "content" in attrs_dict:
            return self.create_attribute_tu("content", attrs_dict["content"])
        return None

    @staticmethod
    def translatable_attribute_matches_tag(attrname, tag):
        if attrname == "lang":
            return tag == "html"
        return True

    def create_attribute_tu(self, attrname, attrvalue):
        normalized_value = self.WHITESPACE_RE.sub(" ", attrvalue).strip()
        if normalized_value:
            return {
                "html_content": normalized_value,
                "location": "%s+%s:%d-%d"
                % (
                    self.filename,
                    ".".join(self.tag_path) + "[" + attrname + "]",
                    self.getpos()[0],
                    self.getpos()[1] + 1,
                ),
            }
        return None

    def emit_attribute_translation_units(self, markup):
        if "attribute_tus" in markup:
            for tu in markup["attribute_tus"]:
                unit = self.addsourceunit(tu["html_content"])
                unit.addlocation(tu["location"])

    def translate_attributes(self, attrs):
        result = []
        for attrname, attrvalue in attrs:
            if attrvalue:
                normalized_value = self.WHITESPACE_RE.sub(" ", attrvalue).strip()
                translated_value = self.callback(normalized_value)
                if translated_value != normalized_value:
                    result.append((attrname, translated_value))
                    continue
            result.append((attrname, attrvalue))
        return result

    @staticmethod
    def create_start_tag(tag, attrs=None, startend=False):
        attr_strings = []
        for attrname, attrvalue in attrs:
            if attrvalue is None:
                attr_strings.append(" " + attrname)
            else:
                attr_strings.append(f' {attrname}="{attrvalue}"')
        return "<{}{}{}>".format(tag, "".join(attr_strings), " /" if startend else "")

    def auto_close_empty_element(self):
        if self.tag_path and self.tag_path[-1] in self.EMPTY_HTML_ELEMENTS:
            self.tag_path.pop()

    def get_leading_whitespace(self, str):
        match = self.LEADING_WHITESPACE_RE.search(str)
        return match.group(1) if match else ""

    def get_trailing_whitespace(self, str):
        match = self.TRAILING_WHITESPACE_RE.search(str)
        return match.group(1) if match else ""

    # From here on below, follows the methods of the HTMLParser

    def handle_starttag(self, tag, attrs):
        self.auto_close_empty_element()
        self.tag_path.append(tag)

        if tag in self.TRANSLATABLE_ELEMENTS:
            self.begin_translation_unit()

        translated_attrs = self.translate_attributes(attrs)
        markup = {
            "type": "starttag",
            "tag": tag,
            "html_content": self.create_start_tag(tag, translated_attrs),
            "untranslated_html": self.create_start_tag(tag, attrs),
            "attribute_tus": self.extract_translatable_attributes(tag, attrs),
        }
        self.append_markup(markup)

    def handle_endtag(self, tag):
        try:
            popped = self.tag_path.pop()
        except IndexError:
            raise ParseError(f"Mismatched tags: no more tags: line {self.getpos()[0]}")
        if popped != tag and popped in self.EMPTY_HTML_ELEMENTS:
            popped = self.tag_path.pop()
        if popped != tag:
            raise ParseError(
                "Mismatched closing tag: "
                f"expected '{popped}' got '{tag}' at line {self.getpos()[0]}"
            )

        self.append_markup({"type": "endtag", "html_content": f"</{tag}>"})

        if tag in self.TRANSLATABLE_ELEMENTS:
            self.end_translation_unit()
            if any(t in self.TRANSLATABLE_ELEMENTS for t in self.tag_path):
                self.begin_translation_unit()

    def handle_startendtag(self, tag, attrs):
        self.auto_close_empty_element()
        self.tag_path.append(tag)

        if tag in self.TRANSLATABLE_ELEMENTS:
            self.begin_translation_unit()

        translated_attrs = self.translate_attributes(attrs)
        markup = {
            "type": "startendtag",
            "html_content": self.create_start_tag(tag, translated_attrs, startend=True),
            "untranslated_html": self.create_start_tag(tag, attrs, startend=True),
            "attribute_tus": self.extract_translatable_attributes(tag, attrs),
        }
        self.append_markup(markup)

        if tag in self.TRANSLATABLE_ELEMENTS:
            self.end_translation_unit()
            if any(t in self.TRANSLATABLE_ELEMENTS for t in self.tag_path):
                self.begin_translation_unit()

        self.tag_path.pop()

    def handle_data(self, data):
        self.auto_close_empty_element()
        self.append_markup({"type": "data", "html_content": data})

    def handle_charref(self, name):
        """Handle entries in the form &#NNNN; e.g. &#8417;."""
        if name.lower().startswith("x"):
            self.handle_data(chr(int(name[1:], 16)))
        else:
            self.handle_data(chr(int(name)))

    def handle_entityref(self, name):
        """Handle named entities of the form &aaaa; e.g. &rsquo;."""
        converted = html5.get(name + ";")
        if name in {"gt", "lt", "amp"} or not converted:
            self.handle_data(f"&{name};")
        else:
            self.handle_data(converted)

    def handle_comment(self, data):
        self.auto_close_empty_element()
        self.append_markup(
            {"type": "comment", "html_content": f"<!--{data}-->", "note": data}
        )

    def handle_decl(self, decl):
        self.auto_close_empty_element()
        self.append_markup({"type": "decl", "html_content": f"<!{decl}>"})

    def handle_pi(self, data):
        self.auto_close_empty_element()
        self.append_markup({"type": "pi", "html_content": f"<?{data}?>"})

    def unknown_decl(self, data):
        self.auto_close_empty_element()
        self.append_markup({"type": "cdecl", "html_content": f"<![{data}]>"})


class POHTMLParser(htmlfile):
    pass
