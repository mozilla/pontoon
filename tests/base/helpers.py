# coding: utf-8

import pytest

from datetime import timedelta
from six import text_type

from pontoon.base.templatetags.helpers import (
    format_datetime, format_timedelta, nospam)
from pontoon.base.utils import aware_datetime


def test_helper_base_format_dt_none():
    assert format_datetime(None) == '---'


def test_helper_base_format_dt_custom():
    datetime = aware_datetime(2015, 1, 1, 5, 7)
    assert format_datetime(datetime, '%H:%M') == '05:07'


@pytest.mark.django_db
def test_helper_base_format_dt_builtin(settings):
    """
    Test that there exist built-in formats. We're not interested in
    testing "all" of them, just that the capability exists.
    """
    settings.TIME_ZONE = 'UTC'
    datetime = aware_datetime(2015, 1, 1, 5, 7)
    assert format_datetime(datetime, 'time') == '05:07 UTC'


def test_helper_base_format_timedelta_none(settings):
    assert format_timedelta(None) == '---'


def test_helper_base_format_timedelta_seconds(settings):
    assert format_timedelta(timedelta(seconds=5)) == '5 seconds'


def test_helper_base_format_timedelta_minutes(settings):
    duration = timedelta(minutes=1, seconds=7)
    assert format_timedelta(duration) == '1 minutes, 7 seconds'


def test_helper_base_format_timedelta_days(settings):
    duration = timedelta(days=2, minutes=1, seconds=8)
    assert format_timedelta(duration) == '2 days, 1 minutes, 8 seconds'


def test_helper_base_format_timedelta_0(settings):
    assert format_timedelta(timedelta(seconds=0)) == '0 seconds'


def test_helper_base_nospam_unicode(settings):
    assert text_type(nospam(u'<łążźćń>')) == u'&lt;łążźćń&gt;'


def test_helper_base_nospam_escape(settings):
    assert str(nospam('<>\'"@&')) == '&lt;&gt;&quot;&quot;&#64;&amp;'
