import errno
import os


def escape_apostrophes(value: str) -> str:
    """
    Apostrophes (straight single quotes) have special meaning in Android strings.xml files,
    so they need to be escaped using a preceding backslash.

    Learn more:
    https://developer.android.com/guide/topics/resources/string-resource.html#escaping_quotes
    """
    return value.replace("'", "\\'")


def unescape_apostrophes(value: str) -> str:
    return value.replace("\\'", "'")


def escape_quotes(value: str) -> str:
    """
    DTD files can use single or double quotes for identifying strings,
    so &quot; and &apos; are the safe bet that will work in both cases.
    """
    value = value.replace('"', "\\&quot;")
    value = value.replace("'", "\\&apos;")

    return value


def unescape_quotes(value: str) -> str:
    value = value.replace("\\&quot;", '"')
    value = value.replace("\\u0022", '"')  # Bug 1390111
    value = value.replace('\\"', '"')

    value = value.replace("\\&apos;", "'")
    value = value.replace("\\u0027", "'")  # Bug 1390111
    value = value.replace("\\'", "'")

    return value


def create_parent_directory(path: str) -> None:
    """
    Create parent directory of the given path if it doesn't exist yet.
    """
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as e:
        # Directory already exists
        if e.errno == errno.EEXIST:
            pass
        else:
            raise
