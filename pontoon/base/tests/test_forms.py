# -*- coding: utf-8 -*-
from django_nose.tools import (
    assert_equal,
    assert_true,
)

from pontoon.base.tests import TestCase
from pontoon.base.forms import GetEntitiesForm


class TestGetEntitiesForm(TestCase):
    def test_search_with_whitespace(self):
        input_data = {
            'project': 'firefox',
            'locale': 'kl',
            'search': ' z',
        }
        form = GetEntitiesForm(input_data)

        assert_true(form.is_valid())
        assert_equal(form.cleaned_data['search'], ' z')
