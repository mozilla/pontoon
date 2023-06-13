import re


class PythonPrintfString:
    parser = re.compile(
        r"""
            %
            (?:\(.*?\))?  # mapping key
            [\#0\-\ +]*   # conversion flags
            [\d*]*        # minimum field width
            (?:\.[\d*])?  # precision
            [hlL]?        # length modifier
            [acdEeFfGgiorsuXx%]  # conversion type
        """,
        re.X,
    )


class PythonFormatString:
    parser = re.compile(r"{{|}}|{[\w!.,[\]%:$<>+\-= ]*}")


class FluentTerm:
    parser = re.compile(r"({ *-[^}]*})")


class FluentFunction:
    parser = re.compile(r"({ *[A-W0-9\-_]+[^}]*})")


class JsonPlaceholder:
    parser = re.compile(r"(\$[A-Z0-9_]+\$)")


def get_placeables(text):
    """Return a list of placeables found in the given string."""
    parsers = [
        PythonPrintfString.parser,
        PythonFormatString.parser,
        FluentTerm.parser,
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
