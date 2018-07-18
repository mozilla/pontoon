from __future__ import absolute_import

import pytest

from pontoon.checks.utils import save_failed_checks
from pontoon.checks.models import (
    Error,
    Warning,
)


@pytest.mark.django_db
def test_save_failed_checks(translation_a):
    save_failed_checks(translation_a, {
        'clErrors': [
            'compare-locales error 1',
            'compare-locales error 2',
        ],
        'clWarnings': [
            'compare-locales warning 1',
        ],

        # Warnings from Translate Toolkit can't be stored in the Database
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

    cl_warning, = (
        Warning.objects.order_by('library', 'message')
    )

    assert cl_warning.library == 'cl'
    assert cl_warning.message == 'compare-locales warning 1'


@pytest.mark.django_db
def test_save_no_checks(translation_a):
    save_failed_checks(translation_a, {})
    assert not Warning.objects.all().exists()
    assert not Error.objects.all().exists()
