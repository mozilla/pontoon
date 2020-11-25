from pontoon.base.tests import TestCase
from pontoon.sync.formats import are_compatible_formats


class CompareLocalesResourceTests(TestCase):
    def test_are_compatible_formats(self):
        """
        Return True if both extensions use the same file parser.
        """
        # Same extension
        assert are_compatible_formats(".dtd", ".dtd")
        assert are_compatible_formats(".po", ".po")

        # Same parser
        assert are_compatible_formats(".po", ".pot")
        assert are_compatible_formats(".xlf", ".xliff")

        # Different parser
        assert not are_compatible_formats(".ftl", ".json")

        # Not supported file format
        assert not are_compatible_formats(".something", ".else")
