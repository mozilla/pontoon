
from pontoon.sync.utils import uses_undercore_as_separator
dir = "pontoon/sync/tests/dummy_directory"


def test_uses_undercore_as_separator():
    assert (uses_undercore_as_separator(dir)) == True
