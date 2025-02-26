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
