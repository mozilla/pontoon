from textwrap import dedent

from pontoon.base.tests import (
    assert_attributes_equal,
    TestCase,
)
from pontoon.sync.formats import ftl
from pontoon.sync.tests.formats import FormatTestsMixin

class FtlTests(FormatTestsMixin, TestCase):
    parse = staticmethod(ftl.parse)
    supports_source = False
    supports_keys = False
    supports_source_string = False