"""
Parser for the strings.xml file format.
"""

from __future__ import annotations

from compare_locales import parser

from .common import ParseError, VCSTranslation


def parse(path: str):
    try:
        xml_parser = parser.getParser(path)
        xml_parser.readFile(path)
    except (OSError, UserWarning) as err:
        raise ParseError(err)

    translations: list[VCSTranslation] = []
    order = 0
    for entity in xml_parser.walk():
        if isinstance(entity, parser.Entity):
            key = entity.key
            string = entity.unwrap().replace("\\'", "'")
            comments = entity.pre_comment.val.split("\n") if entity.pre_comment else []
            translations.append(
                VCSTranslation(
                    key=key,
                    context=key,
                    order=order,
                    strings={None: string} if string is not None else {},
                    source_string=string,
                    comments=comments,
                )
            )
            order += 1
    return translations
