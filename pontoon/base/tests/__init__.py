import factory
from factory import LazyAttribute, Sequence, SubFactory
from factory.django import DjangoModelFactory

from django.template.defaultfilters import slugify
from django.test import TestCase as BaseTestCase

from django_nose.tools import assert_equal

from pontoon.base.models import Locale, Project, Resource


class TestCase(BaseTestCase):
    pass


class ProjectFactory(DjangoModelFactory):
    name = Sequence(lambda n: 'Project {0}'.format(n))
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
                self.locales.add(locale)


class ResourceFactory(DjangoModelFactory):
    project = SubFactory(ProjectFactory)
    path = '/fake/path.po'
    format = 'po'

    class Meta:
        model = Resource


class LocaleFactory(DjangoModelFactory):
    code = Sequence(lambda n: 'en-{0}'.format(n))
    name = Sequence(lambda n: 'English #{0}'.format(n))

    class Meta:
        model = Locale


def assert_redirects(response, expected_url, status_code=302, host=None):
    """
    Assert that the given response redirects to the expected URL.

    The main difference between this and TestCase.assertRedirects is
    that this version doesn't follow the redirect.
    """
    host = host or 'http://testserver'
    assert_equal(response.status_code, status_code)
    assert_equal(response['Location'], host + expected_url)
