"""
Parser for the .lang translation format.
"""
import codecs
import re
from collections import namedtuple

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

from pontoon.base.formats.base import ParsedResource
from pontoon.base.vcs_models import VCSTranslation


# Use a class to store comments so we can distinguish them from entities.
LangComment = namedtuple('LangComment', ['content'])


TAG_REGEX = re.compile(r'\{(ok|l10n-extra)\}')


class LangEntity(VCSTranslation):
    def __init__(self, source_string, translation_string, comments, tags):
        super(LangEntity, self).__init__(
            source_string=source_string,
            strings={None: translation_string},  # Langfiles lack plural support
            comments=comments,
            fuzzy=False,  # Langfiles don't support fuzzy status.
            extra={'tags': tags},  # Tags are a langfile-specific feature.
        )

    @property
    def key(self):
        return self.source_string


class LangFile(ParsedResource):
    def __init__(self, path, children):
        self.path = path
        self.children = children

    @property
    def translations(self):
        return [c for c in self.children if isinstance(c, LangEntity)]

    def save(self, path=None):
        path = path or self.path
        with codecs.open(path, 'w', 'utf-8') as f:
            for child in self.children:
                if isinstance(child, LangEntity):
                    self.write_entity(f, child)
                elif isinstance(child, LangComment):
                    self.write_comment(f, child)

                f.write(u'\n\n')

    def write_entity(self, f, entity):
        for comment in entity.comments:
            f.write(u'# {0}\n'.format(comment))
        f.write(u';{0}\n'.format(entity.source_string))

        # If no translation exists, use the source string and remove the
        # {ok} tag if present. Or, if the translation exists and is
        # identical to the source, add the {ok} tag if it's missing.
        translation = entity.strings.get(None, None)
        if translation is None:
            translation = entity.source_string
            entity.extra['tags'].remove('ok')
        elif translation == entity.source_string and 'ok' not in entity.extra['tags']:
            entity.extra['tags'].append('ok')

        if entity.extra.get('tags'):
            tags = [u'{{{tag}}}'.format(tag=t) for t in entity.extra['tags']]
            translation = u'{translation} {tags}'.format(
                translation=translation,
                tags=u' '.join(tags)
            )

        f.write(u'{0}\n'.format(translation))

    def write_comment(self, f, comment):
        f.write(u'## {0}\n'.format(comment.content))


class LangVisitor(NodeVisitor):
    grammar = Grammar("""
        lang_file = (comment / entity)*

        comment = "##" line_content line_end
        line_content = ~r".*"
        line_end = ("\\n" / ~r"\s")+

        entity = entity_comment* string translation
        entity_comment = "#" line_content line_end
        string = ";" line_content line_end
        translation = line_content line_end
    """)

    def visit_lang_file(self, node, children):
        return children

    def visit_comment(self, node, (marker, content, end)):
        return LangComment(content.text.strip())

    def visit_entity(self, node, (comments, string, translation)):
        comments = self.normalize_zero_or_more_strings(comments)

        # Strip tags out of translation if they exist.
        tags = []
        tag_matches = list(re.finditer(TAG_REGEX, translation))
        if tag_matches:
            tags = [m.group(1) for m in tag_matches]
            translation = translation[:tag_matches[0].start()].strip()

        return LangEntity(string, translation, comments, tags)

    def visit_entity_comment(self, node, (marker, content, end)):
        return content.text.strip()

    def visit_string(self, node, (marker, content, end)):
        return content.text.strip()

    def visit_translation(self, node, (content, end)):
        return content.text.strip()

    def generic_visit(self, node, children):
        if children and len(children) == 1:
            return children[0]
        else:
            return children or node

    def normalize_zero_or_more_strings(self, strings):
        if isinstance(strings, basestring):
            return [strings]
        elif isinstance(strings, list):
            return strings
        else:
            return []


def parse(path):
    with codecs.open(path, 'r', 'utf-8') as f:
        content = f.read()

    children = LangVisitor().parse(content)
    return LangFile(path, children)
