import re


class MozillaPrintfString:
    parser = re.compile(r"%(?:[1-9]\$)?[S@]")


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


class FluentPlaceable:
    parser = re.compile(r"{ *[A-Z0-9\-_][^}]*}")


class JsonPlaceholder:
    parser = re.compile(r"(\$[A-Z0-9_]+\$)")


def get_placeables(text):
    """Return a list of placeables found in the given string."""
    parsers = [
        JsonPlaceholder.parser,
        MozillaPrintfString.parser,
        PythonPrintfString.parser,
        PythonFormatString.parser,
        FluentPlaceable.parser,
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
