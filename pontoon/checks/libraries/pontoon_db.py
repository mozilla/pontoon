import html
import re

import bleach

from collections import defaultdict
from fluent.syntax import FluentParser, ast

from pontoon.sync.formats.ftl import localizable_entries


MAX_LENGTH_RE = re.compile(r"MAX_LENGTH:( *)(\d+)", re.MULTILINE)
parser = FluentParser()


def get_max_length(comment):
    """
    Return max length value for an entity with MAX_LENTH.
    """
    max_length = re.findall(MAX_LENGTH_RE, comment or "")

    if max_length:
        return int(max_length[0][1])

    return None


def run_checks(entity, original, string):
    """
    Group all checks related to the base UI that get stored in the DB
    :arg pontoon.base.models.Entity entity: Source entity
    :arg basestring original: an original string
    :arg basestring string: a translation
    """
    checks = defaultdict(list)
    resource_ext = entity.resource.format

    if resource_ext == "lang":
        # Newlines are not allowed in .lang files (bug 1190754)
        if "\n" in string:
            checks["pErrors"].append("Newline characters are not allowed")

        # Prevent translations exceeding the given length limit
        max_length = get_max_length(entity.comment)

        if max_length:
            string_length = len(
                html.unescape(bleach.clean(string, strip=True, tags=()))
            )

            if string_length > max_length:
                checks["pErrors"].append("Translation too long")

    # Bug 1599056: Original and translation must either both end in a newline,
    # or none of them should.
    if resource_ext == "po":
        if original.endswith("\n") != string.endswith("\n"):
            checks["pErrors"].append("Ending newline mismatch")

    # Prevent empty translation submissions if not supported
    if string == "" and not entity.resource.allows_empty_translations:
        checks["pErrors"].append("Empty translations are not allowed")

    # FTL checks
    if resource_ext == "ftl" and string != "":
        translation_ast = parser.parse_entry(string)
        entity_ast = parser.parse_entry(entity.string)

        # Parse error
        if isinstance(translation_ast, ast.Junk):
            checks["pErrors"].append(translation_ast.annotations[0].message)

        # Not a localizable entry
        elif not isinstance(translation_ast, localizable_entries):
            checks["pErrors"].append(
                "Translation needs to be a valid localizable entry"
            )

        # Message ID mismatch
        elif entity_ast.id.name != translation_ast.id.name:
            checks["pErrors"].append("Translation key needs to match source string key")

    return checks
