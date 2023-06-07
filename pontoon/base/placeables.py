import re


class PythonFormatNamedString:
    parser = r"(%\([[\w\d!.,[\]%:$<>+\-= ]*\)[+|-|0\d+|#]?[.\d+]?[s|d|e|f|g|o|x|c|%])"


class PythonFormatString:
    parser = r"(\{{?[\w\d!.,[\]%:$<>+-= ]*\}?})"


class PythonFormattingVariable:
    parser = r"(%(%|(\([^)]+\)){0,1}[-+0#]{0,1}(\d+|\*){0,1}(\.(\d+|\*)){0,1}[hlL]{0,1}[diouxXeEfFgGcrs]{1}))"
    match_index = 0


class FluentTerm:
    parser = r"({ ?-[^}]* ?})"


class FluentParametrizedTerm:
    parser = r"({ ?-[^}]*([^}]*: ?[^}]*) ?})"


class FluentFunction:
    parser = r"({ ?[A-W0-9\-_]+[^}]* ?})"


def get_placeables(text):
    """Return a list of placeables found in the given string."""
    parsers = [
        PythonFormatNamedString.parser,
        PythonFormatString.parser,
        PythonFormattingVariable.parser,
        FluentTerm.parser,
        FluentParametrizedTerm.parser,
        FluentFunction.parser,
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
