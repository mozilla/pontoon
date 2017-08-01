# coding: utf-8
from datetime import timedelta
from six import text_type

from django_nose.tools import assert_equal

from pontoon.base.templatetags.helpers import format_datetime, format_timedelta, nospam
from pontoon.base.tests import TestCase
from pontoon.base.utils import aware_datetime


class FormatDatetimeTests(TestCase):
    def test_format_datetime_none(self):
        assert_equal(format_datetime(None), '---')

    def test_format_datetime_custom(self):
        datetime = aware_datetime(2015, 1, 1, 5, 7)
        assert_equal(format_datetime(datetime, '%H:%M'), '05:07')

    def test_format_builtin(self):
        """
        Test that there exist built-in formats. We're not interested in
        testing "all" of them, just that the capability exists.
        """
        with self.settings(TIME_ZONE='UTC'):
            datetime = aware_datetime(2015, 1, 1, 5, 7)
        assert_equal(format_datetime(datetime, 'time'), '05:07 UTC')


class FormatTimedeltaTests(TestCase):
    def test_format_timedelta_none(self):
        assert_equal(format_timedelta(None), '---')

    def test_format_timedelta_seconds(self):
        assert_equal(format_timedelta(timedelta(seconds=5)), '5 seconds')

    def test_format_timedelta_minutes(self):
        duration = timedelta(minutes=1, seconds=7)
        assert_equal(format_timedelta(duration), '1 minutes, 7 seconds')

    def test_format_timedelta_days(self):
        duration = timedelta(days=2, minutes=1, seconds=8)
        assert_equal(format_timedelta(duration), '2 days, 1 minutes, 8 seconds')

    def test_format_timedelta_0(self):
        assert_equal(format_timedelta(timedelta(seconds=0)), '0 seconds')


class NoSpamTests(TestCase):
    """Tests related to the no_spam template filter."""

    def test_unicode(self):
        assert_equal(text_type(nospam(u'<łążźćń>')), u'&lt;łążźćń&gt;')

    def test_escape(self):
        assert_equal(str(nospam('<>\'"@&')), '&lt;&gt;&quot;&quot;&#64;&amp;')
