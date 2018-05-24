from __future__ import absolute_import

import pytest

from pontoon.checks.utils import save_failed_checks
from pontoon.checks.models import (
    Error,
    Warning,
)


@pytest.mark.django_db
def test_save_failed_checks(translation0):
    save_failed_checks(translation0, {
        'clErrors': [
            'compare-locales error 1',
            'compare-locales error 2',
        ],
        'clWarnings': [
            'compare-locales warning 1',
        ],
        'ttWarnings': [
            'translate-toolkit warning 1',
            'translate-toolkit warning 2',
        ]
    })

    error1, error2 = Error.objects.order_by('message')

    assert error1.library == 'cl'
    assert error1.message == 'compare-locales error 1'
    assert error2.library == 'cl'
    assert error2.message == 'compare-locales error 2'

    cl_warning, tt_warning1, tt_warning2 = Warning.objects.order_by('library', 'message')

    assert cl_warning.library == 'cl'
    assert cl_warning.message == 'compare-locales warning 1'
    assert tt_warning1.library == 'tt'
    assert tt_warning1.message == 'translate-toolkit warning 1'
    assert tt_warning2.library == 'tt'
    assert tt_warning2.message == 'translate-toolkit warning 2'


@pytest.mark.django_db
def test_save_no_checks(translation0):
    save_failed_checks(
        translation0,
        {}
    )
    assert not Warning.objects.all().exists()
    assert not Error.objects.all().exists()
