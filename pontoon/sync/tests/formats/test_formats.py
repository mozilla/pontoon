from unittest import TestCase

from pontoon.sync.formats import are_compatible_files


class FormatsTests(TestCase):
    def test_are_compatible_files(self):
        """
        Return True if both extensions use the same file parser.
        """
        # Same extension
        assert are_compatible_files("file_a.dtd", "file_b.dtd")
        assert are_compatible_files("file_a.po", "file_b.po")

        # Same parser
        assert are_compatible_files("file_a.po", "file_b.pot")
        assert are_compatible_files("file_a.xlf", "file_b.xliff")

        # Different parser
        assert not are_compatible_files("file_a.ftl", "file_b.json")

        # Not supported file format
        assert not are_compatible_files("file_a.something", "file_b.else")
