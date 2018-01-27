
from datetime import datetime

from mock import MagicMock, PropertyMock, patch

from pontoon.base.templatetags.helpers import naturaltime
from pontoon.base.models import user_gravatar_url
from pontoon.tags.utils import (
    LatestActivity, LatestActivityUser, TaggedLocale)
from pontoon.tags.utils.tagged import Tagged


def test_util_tag_tagged():
    tagged = Tagged()
    assert tagged.latest_activity is None
    assert tagged.chart is None
    assert tagged.kwargs == {}

    tagged = Tagged(foo='bar')
    assert tagged.latest_activity is None
    assert tagged.chart is None
    assert tagged.kwargs == dict(foo='bar')

    tagged = Tagged(total_strings=23)
    assert tagged.latest_activity is None
    assert tagged.chart == dict(total_strings=23)

    tagged = Tagged(latest_translation=23)
    with patch('pontoon.tags.utils.tagged.LatestActivity') as m:
        m.return_value = "y"
        assert tagged.latest_activity == "y"

    assert tagged.chart is None
    assert tagged.kwargs == {}


def test_util_tag_tagged_locale():
    tagged = TaggedLocale()
    assert tagged.code is None
    assert tagged.name is None
    assert tagged.total_strings is None
    assert tagged.latest_activity is None
    assert tagged.tag is None
    assert tagged.kwargs == {}

    tagged = TaggedLocale(
        slug='bar',
        pk=23,
        code="foo",
        name="A foo")
    assert tagged.tag == 'bar'
    assert tagged.code == "foo"
    assert tagged.name == "A foo"
    assert tagged.total_strings is None
    assert tagged.latest_activity is None
    assert (
        tagged.kwargs
        == dict(
            slug='bar',
            pk=23,
            code="foo",
            name="A foo"))

    tagged = TaggedLocale(latest_translation=7, total_strings=23)
    with patch('pontoon.tags.utils.tagged.LatestActivity') as m:
        m.return_value = "y"
        assert tagged.latest_activity == "y"
        assert tagged.chart == dict(total_strings=23)


@patch(
    'pontoon.tags.utils.tagged.TaggedLocale.latest_activity',
    new_callable=PropertyMock)
def test_util_tag_tagged_locale_as_dict(activity_p):
    activity_p.return_value = None
    tagged = TaggedLocale()
    result = tagged.as_dict()
    assert (
        result
        == {'activity': None,
            'url': '',
            'code': None,
            'chart': None,
            'population': None,
            'name': None})
    assert activity_p.called
    activity_p.reset_mock()

    activity_m = MagicMock()
    activity_m.as_dict.return_value = 23
    activity_p.return_value = activity_m

    tagged = TaggedLocale(name='FOO', code='BAR', total_strings=7)
    result = tagged.as_dict()
    assert (
        result
        == {'code': 'BAR',
            'activity': 23,
            'url': '',
            'population': None,
            'chart': {'total_strings': 7},
            'name': 'FOO'})


def test_util_latest_activity():
    activity = LatestActivity(dict(foo='bar'))
    assert activity.activity == dict(foo='bar')
    assert activity.type == 'submitted'
    assert activity.translation is None
    assert activity.user is None

    activity = LatestActivity(dict(approved_date=7))
    assert activity.approved_date == 7

    activity = LatestActivity(dict(date=23))
    assert activity.date == 23

    activity = LatestActivity(
        dict(date=23, approved_date=113))
    assert activity.type == 'approved'

    activity = LatestActivity(dict(user__email=43))
    assert isinstance(activity.user, LatestActivityUser)
    assert activity.user.user == {'user__email': 43}


@patch('pontoon.tags.utils.activity.as_simple_translation')
def test_util_latest_activity_as_dict(trans_m):
    trans_m.return_value = 23
    date = datetime.now()
    activity = LatestActivity(dict(date=date))
    assert (
        activity.as_dict()
        == {'action': 'submitted',
            'ago': naturaltime(date),
            'translation': None,
            'date': date.isoformat(),
            'user': None})
    activity = LatestActivity(dict(date=date, user__email='X'))
    result = activity.as_dict()
    user = result['user']
    del result['user']
    assert user['name'] == 'X'
    assert (
        result
        == {'action': 'submitted',
            'ago': naturaltime(date),
            'translation': None,
            'date': date.isoformat()})
    approved_date = datetime.now()
    activity = LatestActivity(dict(date=date, approved_date=approved_date))
    assert activity.as_dict()['action'] == 'approved'

    activity = LatestActivity(dict(date=date, string='FOO'))
    assert activity.as_dict()['translation']['string'] == 23
    assert list(trans_m.call_args) == [('FOO',), {}]


def test_util_latest_activity_user():
    user = LatestActivityUser(dict(foo='bar'))
    assert user.email is None
    assert user.first_name is None
    assert user.name_or_email is None
    assert user.gravatar_url(23) is None

    with patch('pontoon.tags.utils.activity.user_gravatar_url') as m:
        m.return_value = 113
        user = LatestActivityUser(
            dict(user__email='bar@ba.z'))
        assert user.email == 'bar@ba.z'
        assert user.first_name is None
        assert user.name_or_email == 'bar@ba.z'
        assert user.gravatar_url(23) == 113
        assert list(m.call_args) == [(user, 23), {}]

    with patch('pontoon.tags.utils.activity.user_gravatar_url') as m:
        m.return_value = 113
        user = LatestActivityUser(
            dict(user__email='bar@ba.z',
                 user__name='FOOBAR'))
        assert user.email == 'bar@ba.z'
        assert user.first_name is None
        assert user.name_or_email == 'bar@ba.z'
        assert user.gravatar_url(23) == 113
        assert list(m.call_args) == [(user, 23), {}]


def test_util_latest_activity_user_as_dict():
    user = LatestActivityUser(dict(foo='bar'))
    assert user.as_dict() == {'name': None, 'avatar': None}

    user = LatestActivityUser(dict(user__first_name='FOO'))
    assert user.as_dict() == {'name': 'FOO', 'avatar': None}

    user = LatestActivityUser(dict(user__email='FOO@BAR.BAZ'))
    assert (
        user.as_dict()
        == {'name': 'FOO@BAR.BAZ',
            'avatar': user_gravatar_url(user, 44)})
