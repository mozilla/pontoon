
from mock import patch

from pontoon.tags.utils import (
    LatestActivity, LatestActivityUser, TaggedLocale)
from pontoon.tags.utils.tagged import Tagged


def test_util_tag_tagged():
    # Tests the base Tagged class

    # called with no args - defaults
    tagged = Tagged()
    assert tagged.latest_activity is None
    assert tagged.chart is None
    assert tagged.kwargs == {}

    # called with random arg - added to kwargs
    tagged = Tagged(foo='bar')
    assert tagged.latest_activity is None
    assert tagged.chart is None
    assert tagged.kwargs == dict(foo='bar')

    # called with total_strings - chart added
    tagged = Tagged(total_strings=23)
    assert tagged.latest_activity is None
    assert tagged.chart == dict(total_strings=23)

    # called with latest_translation - latest activity added
    tagged = Tagged(latest_translation=23)
    with patch('pontoon.tags.utils.tagged.LatestActivity') as m:
        m.return_value = "y"
        assert tagged.latest_activity == "y"

    assert tagged.chart is None
    assert tagged.kwargs == {}


def test_util_tag_tagged_locale():
    # Tests instantiation of TaggedLocale wrapper

    # defaults
    tagged = TaggedLocale()
    assert tagged.code is None
    assert tagged.name is None
    assert tagged.total_strings is None
    assert tagged.latest_activity is None
    assert tagged.tag is None
    assert tagged.project is None
    assert tagged.population is None
    assert tagged.kwargs == {}

    # call with locale data
    tagged = TaggedLocale(
        slug='bar',
        pk=23,
        code="foo",
        name="A foo",
        project=43,
        population=113)
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
            name="A foo",
            project=43,
            population=113))

    # call with latest_translation and stat data
    tagged = TaggedLocale(latest_translation=7, total_strings=23)
    with patch('pontoon.tags.utils.tagged.LatestActivity') as m:
        m.return_value = "y"
        assert tagged.latest_activity == "y"
        assert tagged.chart == dict(total_strings=23)


def test_util_latest_activity():
    # Tests instantiating the latest_activity wrapper

    # call with random activity - defaults
    activity = LatestActivity(dict(foo='bar'))
    assert activity.activity == dict(foo='bar')
    assert activity.type == 'submitted'
    assert activity.translation is None
    assert activity.user is None

    # check approved_date
    activity = LatestActivity(dict(approved_date=7))
    assert activity.approved_date == 7

    # check data
    activity = LatestActivity(dict(date=23))
    assert activity.date == 23

    # check type is approved
    activity = LatestActivity(
        dict(date=23, approved_date=113))
    assert activity.type == 'approved'

    # check user is created if present
    activity = LatestActivity(dict(user__email=43))
    assert isinstance(activity.user, LatestActivityUser)
    assert activity.user.user == {'user__email': 43}


@patch('pontoon.tags.utils.latest_activity.user_gravatar_url')
def test_util_latest_activity_user(avatar_mock):
    # Tests instantiating a latest activity user wrapper

    avatar_mock.return_value = 113

    # call with random user data - defaults
    user = LatestActivityUser(dict(foo='bar'))
    assert user.email is None
    assert user.first_name is None
    assert user.name_or_email is None
    assert user.gravatar_url(23) is None

    # call with email - user data added
    user = LatestActivityUser(
        dict(user__email='bar@ba.z'))
    assert user.email == 'bar@ba.z'
    assert user.first_name is None
    assert user.name_or_email == 'bar@ba.z'
    assert user.gravatar_url(23) == 113
    assert list(avatar_mock.call_args) == [(user, 23), {}]

    avatar_mock.reset_mock()

    # call with email and name - correct name
    user = LatestActivityUser(
        dict(user__email='bar@ba.z',
             user__name='FOOBAR'))
    assert user.email == 'bar@ba.z'
    assert user.first_name is None
    assert user.name_or_email == 'bar@ba.z'
    assert user.gravatar_url(23) == 113
    assert list(avatar_mock.call_args) == [(user, 23), {}]
