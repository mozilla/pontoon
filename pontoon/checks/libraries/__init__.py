from __future__ import absolute_import

from . import compare_locales
from . import translate_toolkit
from . import pontoon_db, pontoon_non_db
from fluent.syntax import (
    ast,
    FluentParser,
    FluentSerializer,
)


parser = FluentParser()
serializer = FluentSerializer()


def ftl_to_simplified_string(string):
    """Take a Fluent entry and extract a simplified string suitable for running Translate Toolkit checks.
    In particular, pull out text elements, literals, and variable references


    :arg string string: a serialized FTL string

    :returns: a simplified (and possibly incomplete) version of the given FTL string

    """

    class TextAndVariableVisitor(ast.Visitor):
        def __init__(self):
            self.parts = []

        def visit_StringLiteral(self, literal):
            self.parts.append(literal.value)

        def visit_NumberLiteral(self, literal):
            self.parts.append("{}".format(literal.value))

        def visit_TextElement(self, text):
            self.parts.append(text.value)

        def visit_VariableReference(self, variable):
            self.parts.append("{{${}}}".format(variable.id.name))

        def visit_Attribute(self, attribute):
            # Attributes start on a new line. Since we're only taking the text content of the attribute,
            # prepend a space to ensure that there's whitespace between the preceeding text and the attribute's text
            self.parts.append(" ")
            self.generic_visit(attribute)

        def visit_Variant(self, variant):
            # Variants start on a new line. Since we're only taking the text content of the variant,
            # prepend a space to ensure that there's whitespace between the preceeding text and the variant's text
            self.parts.append(" ")
            self.generic_visit(variant)

    visitor = TextAndVariableVisitor()
    node = parser.parse_entry(string)
    visitor.visit(node)
    return "".join(visitor.parts)


def run_checks(
    entity, locale_code, original, string, use_tt_checks,
):
    """
    Main function that performs all quality checks from frameworks handled in Pontoon.

    :arg pontoon.base.models.Entity entity: Source entity
    :arg basestring locale_code: Locale code of a translation
    :arg basestring original: an original string
    :arg basestring string: a translation
    :arg bool use_tt_checks: use Translate Toolkit checks

    :return: Return types:
        * JsonResponse - If there are errors
        * None - If there's no errors and non-omitted warnings.
    """
    pontoon_db_checks = pontoon_db.run_checks(entity, original, string)
    pontoon_non_db_checks = pontoon_non_db.run_checks(entity, string)

    try:
        cl_checks = compare_locales.run_checks(entity, locale_code, string)
    except compare_locales.UnsupportedStringError:
        cl_checks = None
    except compare_locales.UnsupportedResourceTypeError:
        cl_checks = None

    tt_checks = {}
    resource_ext = entity.resource.format

    if use_tt_checks:
        # Always disable checks we don't use. For details, see:
        # https://bugzilla.mozilla.org/show_bug.cgi?id=1410619
        # https://bugzilla.mozilla.org/show_bug.cgi?id=1514691
        tt_disabled_checks = {
            "acronyms",
            "gconf",
            "kdecomments",
            "untranslated",
        }

        # Some compare-locales checks overlap with Translate Toolkit checks
        if cl_checks is not None:
            if resource_ext == "properties":
                tt_disabled_checks.update(["escapes", "nplurals", "printf"])
            elif resource_ext == "xml":
                tt_disabled_checks.update(
                    [
                        "doublespacing",
                        "endwhitespace",
                        "escapes",
                        "newlines",
                        "numbers",
                        "printf",
                        "singlequoting",
                        "startwhitespace",
                    ]
                )
        elif resource_ext == "lang":
            tt_disabled_checks.update(["newlines"])

        if resource_ext == "ftl":
            tt_disabled_checks.update(
                [
                    "doublespacing",
                    "endwhitespace",
                    "escapes",
                    "newlines",
                    "numbers",
                    "printf",
                    "singlequoting",
                    "startwhitespace",
                    "pythonbraceformat",
                    "doublequoting",
                ]
            )
            tt_checks = translate_toolkit.run_checks(
                ftl_to_simplified_string(original),
                ftl_to_simplified_string(string),
                locale_code,
                tt_disabled_checks,
                None,
                {"varmatches": [("{$", "}")]},
            )
        else:
            tt_checks = translate_toolkit.run_checks(
                original, string, locale_code, tt_disabled_checks
            )

    checks = dict(tt_checks, **(cl_checks or {}))

    checks.update(pontoon_db_checks)
    checks.update(pontoon_non_db_checks)

    return checks
