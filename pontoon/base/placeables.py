import re


class PythonFormatNamedString:
    parser = re.compile(
        r"(%\([[\w\d!.,[\]%:$<>+\-= ]*\)[+-0\d+#]?[.\d+]?[sdefgoxc%])",
        re.IGNORECASE,
    )


class PythonFormatString:
    parser = re.compile(r"({{?[\w!.,[\]%:$<>+\-= ]*}?})")


class PythonFormattingVariable:
    parser = re.compile(
        r"(%(%|(\([^)]+\))?[-+0#]?(\d+|\*)?(\.(\d+|\*))?[hlL]?[diouxXeEfFgGcrs]))"
    )
    match_index = 0


class FluentTerm:
    parser = re.compile(r"({ *-[^}]*})")


class FluentParametrizedTerm:
    parser = re.compile(r"({ ?-[^}]*([^}]*: ?[^}]*) ?})")


class FluentFunction:
    parser = re.compile(r"({ *[A-W0-9\-_]+[^}]*})")


class JsonPlaceholder:
    parser = re.compile(r"(\$[A-Z0-9_]+\$)")


def get_placeables(text):
    """Return a list of placeables found in the given string."""
    parsers = [
        PythonFormatNamedString.parser,
        PythonFormatString.parser,
        PythonFormattingVariable.parser,
        FluentTerm.parser,
        FluentParametrizedTerm.parser,
        FluentFunction.parser,
        JsonPlaceholder.parser,
    ]

    placeables = get_placeables_recursively(text, parsers)
    return list(dict.fromkeys(placeables))


def get_placeables_recursively(text, parsers):
    if not parsers:
        return []

    parser = parsers.pop(0)
    placeables = re.findall(parser, text)

    for part in re.split(parser, text):
        placeables += get_placeables_recursively(part, parsers)

    return placeables
