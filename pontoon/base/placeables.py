import re


class PythonFormatNamedString:
    parser = re.compile(
        r"(%\([[\w\d!.,[\]%:$<>+\-= ]*\)[+|-|0\d+|#]?[.\d+]?[s|d|e|f|g|o|x|c|%])",
        re.IGNORECASE,
    )


class PythonFormatString:
    parser = re.compile(r"(\{{?[\w\d!.,[\]%:$<>+-= ]*\}?})")


class PythonFormattingVariable:
    parser = re.compile(
        r"(%(%|(\([^)]+\)){0,1}[-+0#]{0,1}(\d+|\*){0,1}(\.(\d+|\*)){0,1}[hlL]{0,1}[diouxXeEfFgGcrs]{1}))"
    )
    match_index = 0


class FluentTerm:
    parser = re.compile(r"({ ?-[^}]* ?})")


class FluentParametrizedTerm:
    parser = re.compile(r"({ ?-[^}]*([^}]*: ?[^}]*) ?})")


class FluentFunction:
    parser = re.compile(r"({ ?[A-W0-9\-_]+[^}]* ?})")


class JavaFormattingVariable:
    parser = re.compile(
        r"(?x){[0-9]+(,\s*(number(,\s*(integer|currency|percent|[-0#.,E;%\u2030\u00a4']+)?)?|(date|time)(,\s*(short|medium|long|full|.+?))?|choice,([^{]+({.+})?)+)?)?}"
    )


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
        JavaFormattingVariable.parser,
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
