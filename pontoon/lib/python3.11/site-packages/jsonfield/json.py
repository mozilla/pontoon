import json


class JSONString(str):
    pass


def checked_loads(value, **kwargs):
    """
    Ensure that values aren't loaded twice, resulting in an encoding error.

    Loaded strings are wrapped in JSONString, as it is otherwise not possible
    to differentiate between a loaded and unloaded string.
    """
    if isinstance(value, (list, dict, int, float, JSONString, type(None))):
        return value

    value = json.loads(value, **kwargs)
    if isinstance(value, str):
        value = JSONString(value)

    return value
