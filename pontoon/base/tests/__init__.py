import json
import os
import tempfile
from contextlib import contextmanager
from unittest.mock import patch

from django.contrib.auth.models import (
    Group,
    User,
)
from django.template.defaultfilters import slugify
from django.test import TestCase as BaseTestCase, Client as BaseClient

import factory
from factory import LazyAttribute, Sequence, SubFactory, SelfAttribute
from factory.django import DjangoModelFactory

from pontoon.base.models import (
    ChangedEntityLocale,
    Entity,
    Locale,
    Project,
    ProjectLocale,
    Repository,
    Resource,
    TranslatedResource,
    Translation,
    TranslationMemoryEntry,
)


class PontoonClient(BaseClient):
    """Useful helper methods that can be used in tests."""

    def ajax_post(self, url, params):
        """Send data to the ajax-type view."""
        return self.post(url, params, HTTP_X_REQUESTED_WITH="XMLHttpRequest")


class TestCase(BaseTestCase):
    client_class = PontoonClient

    def patch(self, *args, **kwargs):
        """
        Wrapper around mock.patch that automatically cleans up the patch
        in the test cleanup phase.
        """
        patch_obj = patch(*args, **kwargs)
        self.addCleanup(patch_obj.stop)
        return patch_obj.start()

    def patch_object(self, *args, **kwargs):
        """
        Wrapper around mock.patch.object that automatically cleans up
        the patch in the test cleanup phase.
        """
        patch_obj = patch.object(*args, **kwargs)
        self.addCleanup(patch_obj.stop)
        return patch_obj.start()


class UserFactory(DjangoModelFactory):
    username = Sequence(lambda n: "test%s" % n)
    email = Sequence(lambda n: "test%s@example.com" % n)

    class Meta:
        model = User


class GroupFactory(DjangoModelFactory):
    name = Sequence(lambda n: "group%s" % n)

    class Meta:
        model = Group


class ProjectFactory(DjangoModelFactory):
    name = Sequence(lambda n: "Project {0}".format(n))
    slug = LazyAttribute(lambda p: slugify(p.name))
    links = False

    class Meta:
        model = Project

    @factory.post_generation
    def locales(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for locale in extracted:
                ProjectLocaleFactory.create(project=self, locale=locale)

    @factory.post_generation
    def repositories(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted is not None:
            for repository in extracted:
                self.repositories.add(repository)
        else:  # Default to a single valid repo.
            self.repositories.add(RepositoryFactory.build(), bulk=False)


class RepositoryFactory(DjangoModelFactory):
    project = SubFactory(ProjectFactory)
    type = "git"
    url = Sequence(lambda n: "https://example.com/url_{0}.git".format(n))

    class Meta:
        model = Repository


class ResourceFactory(DjangoModelFactory):
    project = SubFactory(ProjectFactory)
    path = Sequence(lambda n: "/fake/path{0}.po".format(n))
    format = "po"
    total_strings = 1

    class Meta:
        model = Resource


class LocaleFactory(DjangoModelFactory):
    code = Sequence(lambda n: "en-{0}".format(n))
    name = Sequence(lambda n: "English #{0}".format(n))

    class Meta:
        model = Locale


class ProjectLocaleFactory(DjangoModelFactory):
    project = SubFactory(ProjectFactory)
    locale = SubFactory(LocaleFactory)

    class Meta:
        model = ProjectLocale


class EntityFactory(DjangoModelFactory):
    resource = SubFactory(ResourceFactory)
    string = Sequence(lambda n: "string {0}".format(n))

    class Meta:
        model = Entity


class PluralEntityFactory(DjangoModelFactory):
    resource = SubFactory(ResourceFactory)
    string = Sequence(lambda n: "string {0}".format(n))
    string_plural = Sequence(lambda n: "string plural {0}".format(n))

    class Meta:
        model = Entity


class ChangedEntityLocaleFactory(DjangoModelFactory):
    entity = SubFactory(EntityFactory)
    locale = SubFactory(LocaleFactory)

    class Meta:
        model = ChangedEntityLocale


class TranslationFactory(DjangoModelFactory):
    entity = SubFactory(EntityFactory)
    locale = SubFactory(LocaleFactory)
    string = Sequence(lambda n: "translation {0}".format(n))
    user = SubFactory(UserFactory)

    class Meta:
        model = Translation


class IdenticalTranslationFactory(TranslationFactory):
    entity = SubFactory(EntityFactory, string=SelfAttribute("..string"))


class TranslationMemoryFactory(DjangoModelFactory):
    source = Sequence(lambda n: "source {0}".format(n))
    target = Sequence(lambda n: "target {0}".format(n))
    entity = SubFactory(EntityFactory, string=SelfAttribute("..source"))
    locale = SubFactory(LocaleFactory)

    class Meta:
        model = TranslationMemoryEntry


class TranslatedResourceFactory(DjangoModelFactory):
    resource = SubFactory(ResourceFactory)
    locale = SubFactory(LocaleFactory)

    class Meta:
        model = TranslatedResource


def assert_redirects(response, expected_url, status_code=302, host=None, secure=False):
    """
    Assert that the given response redirects to the expected URL.

    The main difference between this and TestCase.assertRedirects is
    that this version doesn't follow the redirect.
    """
    if host is None:
        host = "{}://{}".format("https" if secure else "http", host or "testserver")
    assert response.status_code == status_code
    assert response["Location"] == host + expected_url


def assert_attributes_equal(original, **expected_attrs):
    """
    Assert that the given object has attributes matching the given
    values.
    """
    if not expected_attrs:
        raise ValueError("Expected some attributes to check.")

    for key, value in expected_attrs.items():
        original_value = getattr(original, key)
        assert (
            original_value == value
        ), "Attribute `{key}` does not match: {original_value} != {value}".format(
            key=key, original_value=original_value, value=value
        )


class NOT(object):
    """
    A helper class that compares equal to everything except its given
    values.

    >>> mock_function('foobarbaz')
    >>> mock_function.assert_called_with(NOT('fizzbarboff'))  # Passes
    >>> mock_function.assert_called_with(NOT('foobarbaz'))  # Fails
    """

    def __init__(self, *values):
        self.values = values

    def __eq__(self, other):
        return other not in self.values

    def __ne__(self, other):
        return other in self.values

    def __repr__(self):
        return "<NOT %r>" % self.values


class CONTAINS(object):
    """
    Helper class that is considered equal to any object that contains
    elements the elements passed to it.

    Used mostly in conjunction with Mock.assert_called_with to test if
    a string argument contains certain substrings:

    >>> mock_function('foobarbaz')
    >>> mock_function.assert_called_with(CONTAINS('bar'))  # Passes
    """

    def __init__(self, *args):
        self.items = args

    def __eq__(self, other):
        return all(item in other for item in self.items)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<CONTAINS {0}>".format(",".join(repr(item) for item in self.items))


def create_tempfile(contents):
    """
    Create a temporary file with the given contents, and return the path
    to the created file.
    """
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as f:
        f.write(contents)
    return path


def create_named_tempfile(contents, prefix=None, suffix=None, directory=None):
    """
    Create a temporary file with the given contents, prefix, suffix and
    directory, and return the path to the created file.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", prefix=prefix, suffix=suffix, dir=directory, delete=False,
    ) as temp:
        temp.write(contents)
        temp.flush()

    return temp.name


def assert_json(response, expected_obj):
    """
    Checks if response contains a expected json object.
    """
    assert json.loads(response.content) == expected_obj


@contextmanager
def po_file(**entries):
    """
    Create a temporary .po file
    :arg dict entries: keys map to msgids and values map to msgstrs
    :return: read-only file object
    """
    po_contents = "\n".join(
        'msgid "{}"\nmsgstr "{}"'.format(key, val) for key, val in entries.items()
    )
    with tempfile.NamedTemporaryFile("w+", suffix=".po") as fp:
        fp.write(po_contents)
        fp.flush()

        yield open(fp.name, "r")
