from pontoon.sync.utils import uses_undercore_as_separator
from pontoon.sync.tests import DUMMY_DIRECTORY_PATH


def test_uses_undercore_as_separator():
    assert (uses_undercore_as_separator(DUMMY_DIRECTORY_PATH)) is True
