"""
Parser for the .lang translation format.
"""
import codecs
import re

from parsimonious.exceptions import (
    ParseError as ParsimoniousParseError,
    VisitationError,
)
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

from pontoon.sync.exceptions import ParseError
from pontoon.sync.formats.base import ParsedResource
from pontoon.sync.vcs.models import VCSTranslation


BLANK_LINE = "blank_line"
TAG_REGEX = re.compile(r"\{(ok|l10n-extra)\}")


class LangComment(object):
    def __init__(self, marker, content, end):
        self.marker = marker
        self.raw_content = content
        self.end = end

    @property
    def content(self):
        return self.raw_content.strip()

    @property
    def raw(self):
        return self.marker + self.raw_content + self.end


class LangEntity(VCSTranslation):
    def __init__(self, source_string, translation_string, tags):
        super(LangEntity, self).__init__(
            key=source_string,  # Langfiles use the source as the key.
            source_string=source_string,
            strings={None: translation_string},  # Langfiles lack plural support
            comments=[],
            fuzzy=False,  # Langfiles don't support fuzzy status
        )

        self.tags = set(tags)

        # If the translation matches the source string without the {ok}
        # tag, then the translation isn't actually valid, so we remove
        # it.
        if source_string == translation_string and "ok" not in tags:
            del self.strings[None]

    @property
    def extra(self):
        return {"tags": list(self.tags)}


class LangResource(ParsedResource):
    def __init__(self, path, children):
        self.path = path
        self.children = children

    @property
    def translations(self):
        return [c for c in self.children if isinstance(c, LangEntity)]

    def save(self, locale):
        with codecs.open(self.path, "w", "utf-8") as f:
            for child in self.children:
                if isinstance(child, LangEntity):
                    self.write_entity(f, child)
                elif isinstance(child, LangComment):
                    f.write(child.raw)
                elif child == BLANK_LINE:
                    f.write(u"\n")

    def write_entity(self, f, entity):
        f.write(u";{0}\n".format(entity.source_string))

        translation = entity.strings.get(None, None)
        if translation is None:
            # No translation? Output the source string and remove {ok}.
            translation = entity.source_string
            entity.tags.discard("ok")
        elif translation == entity.source_string:
            # Translation is equal to the source? Include {ok}.
            entity.tags.add("ok")
        elif translation != entity.source_string:
            # Translation is different? Remove {ok}, it's unneeded.
            entity.tags.discard("ok")

        if entity.extra.get("tags"):
            tags = [u"{{{tag}}}".format(tag=t) for t in entity.tags]
            translation = u"{translation} {tags}".format(
                translation=translation, tags=u" ".join(tags)
            )

        f.write(u"{0}\n".format(translation))


class LangVisitor(NodeVisitor):
    grammar = Grammar(
        r"""
        lang_file = (comment / entity / blank_line)*

        comment = "#"+ line_content line_ending
        line_content = ~r".*"
        line_ending = ~r"$\n?"m # Match at EOL and EOF without newline.

        blank_line = ~r"((?!\n)\s)*" line_ending

        entity = string translation
        string = ";" line_content line_ending
        translation = line_content line_ending
    """
    )

    def visit_lang_file(self, node, children):
        """
        Find comments that are associated with an entity and add them
        to the entity's comments list. Also assign order to entities.
        """
        comments = []
        order = 0
        for child in children:
            if isinstance(child, LangComment):
                comments.append(child)
                continue

            if isinstance(child, LangEntity):
                child.comments = [c.content for c in comments]
                child.order = order
                order += 1

            comments = []

        return children

    def visit_comment(self, node, node_info):
        marker, content, end = node_info
        return LangComment(node_text(marker), node_text(content), node_text(end))

    def visit_blank_line(self, node, _):
        return BLANK_LINE

    def visit_entity(self, node, node_info):
        string, translation = node_info

        # Strip tags out of translation if they exist.
        tags = []
        tag_matches = list(re.finditer(TAG_REGEX, translation))
        if tag_matches:
            tags = [m.group(1) for m in tag_matches]
            translation = translation[: tag_matches[0].start()].strip()

        if translation == "":
            raise ParsimoniousParseError(
                "Blank translation for key {key} is not allowed in langfiles.".format(
                    key=string
                )
            )

        return LangEntity(string, translation, tags)

    def visit_string(self, node, node_info):
        marker, content, end = node_info
        return content.text.strip()

    def visit_translation(self, node, node_info):
        content, end = node_info
        return content.text.strip()

    def generic_visit(self, node, children):
        if children and len(children) == 1:
            return children[0]
        else:
            return children or node


def node_text(node):
    """
    Convert a Parsimonious node into text, including nodes that may
    actually be a list of nodes due to repetition.
    """
    if node is None:
        return u""
    elif isinstance(node, list):
        return "".join([n.text for n in node])
    else:
        return node.text


def parse(path, source_path=None, locale=None):
    # Read as utf-8-sig in case there's a BOM at the start of the file
    # that we want to remove.
    with codecs.open(path, "r", "utf-8-sig") as f:
        content = f.read()

    try:
        children = LangVisitor().parse(content)
    except (ParsimoniousParseError, VisitationError) as err:
        raise ParseError(
            u"Failed to parse {path}: {err}".format(path=path, err=err)
        ) from err

    return LangResource(path, children)
