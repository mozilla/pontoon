import six

__all__ = ('str_to_bytes',)


def str_to_bytes(value):
    """
    Simply convert a string type to bytes if the value is a string
    and is an instance of six.string_types but not of six.binary_type
    in python2 struct.pack("<Q") is both string_types and binary_type but
    in python3 struct.pack("<Q") is binary_type but not a string_types
    :param value:
    :param binary:
    :return:
    """
    if not isinstance(value, six.binary_type) and isinstance(value, six.string_types):
        return value.encode()
    return value
