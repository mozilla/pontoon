import pytest

from datetime import timedelta

from pontoon.base.templatetags.helpers import (
    format_datetime,
    format_timedelta,
    nospam,
    to_json,
    metric_prefix,
)
from pontoon.base.utils import aware_datetime


def test_helper_to_json():
    obj = {
        "a": "foo",
        "b": aware_datetime(2015, 1, 1),
    }
    string = '{"a": "foo", "b": "2015-01-01T00:00:00Z"}'
    assert to_json(obj) == string


def test_helper_base_metric_prefix():
    assert metric_prefix(123) == "123"
    assert metric_prefix(1234) == "1.2k"
    assert metric_prefix(759878) == "759.9k"
    assert metric_prefix(299792458) == "299.8M"


def test_helper_base_format_dt_none():
    assert format_datetime(None) == "---"


def test_helper_base_format_dt_custom():
    datetime = aware_datetime(2015, 1, 1, 5, 7)
    assert format_datetime(datetime, "%H:%M") == "05:07"


@pytest.mark.django_db
def test_helper_base_format_dt_builtin(settings):
    """
    Test that there exist built-in formats. We're not interested in
    testing "all" of them, just that the capability exists.
    """
    settings.TIME_ZONE = "UTC"
    datetime = aware_datetime(2015, 1, 1, 5, 7)
    assert format_datetime(datetime, "time") == "05:07 UTC"


def test_helper_base_format_timedelta_none(settings):
    assert format_timedelta(None) == "---"


def test_helper_base_format_timedelta_seconds(settings):
    assert format_timedelta(timedelta(seconds=5)) == "5 seconds"


def test_helper_base_format_timedelta_minutes(settings):
    duration = timedelta(minutes=1, seconds=7)
    assert format_timedelta(duration) == "1 minutes, 7 seconds"


def test_helper_base_format_timedelta_days(settings):
    duration = timedelta(days=2, minutes=1, seconds=8)
    assert format_timedelta(duration) == "2 days, 1 minutes, 8 seconds"


def test_helper_base_format_timedelta_0(settings):
    assert format_timedelta(timedelta(seconds=0)) == "0 seconds"


def test_helper_base_nospam_unicode(settings):
    assert str(nospam("<łążźćń>")) == "&lt;łążźćń&gt;"


def test_helper_base_nospam_escape(settings):
    assert str(nospam("<>'\"@&")) == "&lt;&gt;&#x27;&quot;&#64;&amp;"
