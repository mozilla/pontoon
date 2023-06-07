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
        # PythonFormattingVariable.parser,
        FluentTerm.parser,
        # FluentParametrizedTerm.parser,
        FluentFunction.parser,
    ]

    placeables = []

    for parser in parsers:
        placeables += re.findall(parser, text)

    return list(dict.fromkeys(placeables))
