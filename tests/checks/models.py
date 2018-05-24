from __future__ import absolute_import

import pytest

from pontoon.checks.utils import save_failed_checks
from pontoon.checks.models import (
    Error,
    FailedCheck,
    Warning,
)

# Some of tests should be executed for every supported library
LIBRARIES = (
    library_code
    for library_code in FailedCheck._meta.get_field('library').choices
)

@pytest.mark.django_db
@pytest.mark.parametrize('library', LIBRARIES)
def test_save_failed_checks(translation0, library):
    assert False



@pytest.mark.parametrize('library', LIBRARIES)
@pytest.mark.django_db
def test_save_failed_only_errors(translation0, library):
    assert False



@pytest.mark.parametrize('library', LIBRARIES)
@pytest.mark.django_db
def test_save_failed_only_warnings(translation0, library):
    assert False



@pytest.mark.parametrize('library', LIBRARIES)
@pytest.mark.django_db
def test_save_failed_idempotency(translation0, library):
    assert False


@pytest.mark.django_db
def test_save_no_checks(translation0):
    """
    No checks shouldn't save any instances of
    """
    save_failed_checks(
        translation0,
        {}
    )
    assert not Warning.objects.all().exists()
    assert not Error.objects.all().exists()
