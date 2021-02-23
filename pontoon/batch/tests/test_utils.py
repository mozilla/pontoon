from fluent.syntax import FluentParser, FluentSerializer

from pontoon.batch.utils import ftl_find_and_replace


parser = FluentParser()
serializer = FluentSerializer()


def normalize(string):
    # Serialize strings using default Fluent serializer rules
    # to avoid differences caused by different formatting style.
    return serializer.serialize_entry(parser.parse_entry(string))


def test_ftl_find_and_replace():
    simple_string = normalize("key = find")
    simple_replaced = normalize("key = replace")

    assert ftl_find_and_replace(simple_string, "find", "replace") == simple_replaced

    # Perform find and replace on text values only
    complex_string = normalize(
        """find =
        .placeholder = find
    """
    )
    complex_replaced = normalize(
        """find =
        .placeholder = replace
    """
    )

    assert ftl_find_and_replace(complex_string, "find", "replace") == complex_replaced
