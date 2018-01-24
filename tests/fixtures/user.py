
import functools

import pytest

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


@pytest.fixture
def member0(client, user0):
    """Provides a `LoggedInMember` with the attributes `user` and `client`
    the `client` is authenticated
    """

    class LoggedInMember(object):

        def __init__(self, user, client):
            client.force_login(user)
            self.client = client
            self.user = user

    return LoggedInMember(user0, client)


@pytest.fixture
def user0():
    """User 0"""
    return get_user_model().objects.get(username="user0")


@pytest.fixture
def user1():
    """User 1"""
    return get_user_model().objects.get(username="user1")


@pytest.fixture
def userX():
    """User X - user with no history"""
    return get_user_model().objects.get(username="userX")


@pytest.fixture
def user_factory(factory):
    """User factory
    create users in a hurry!

    Provides a user factory function that accepts the following args:

    :arg int `batch`: number of users to instantiate, defaults to len of
        `batch_kwargs` or 1
    :arg list `batch_kwargs`: a list of kwargs to instantiate the users
    """

    def instance_attrs(instance, i):
        if not instance.username:
            instance.username = "testuser%s" % i
        if not instance.email:
            instance.email = "%s@example.not" % instance.username

    return functools.partial(
        factory, Model=get_user_model(), instance_attrs=instance_attrs)


@pytest.fixture
def translators_group0():
    """Translators group 0"""
    return Group.objects.get(name='locale0 translators')


@pytest.fixture
def managers_group0():
    """Managers group 0"""
    return Group.objects.get(name='locale0 managers')


@pytest.fixture
def translators_group1():
    """Translators group 1"""
    return Group.objects.get(name='locale1 translators')


@pytest.fixture
def managers_group1():
    """Translators group 0"""
    return Group.objects.get(name='locale1 managers')


@pytest.fixture
def group_factory(factory):
    """Group factory

    Provides a group factory function that accepts the following args:

    :arg int `batch`: number of groups to instantiate, defaults to len of
        `batch_kwargs` or 1
    :arg list `batch_kwargs`: a list of groups to instantiate the groups
    """
    def instance_attrs(instance, i):
        instance.name = "Group %d" % i

    return functools.partial(
        factory,
        Model=Group,
        instance_attrs=instance_attrs
    )
