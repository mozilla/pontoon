from unittest.mock import patch

from factory import LazyAttribute, Sequence, SubFactory, post_generation
from factory.django import DjangoModelFactory

from django.contrib.auth.models import (
    User,
)
from django.template.defaultfilters import slugify
from django.test import Client as BaseClient, TestCase as BaseTestCase

from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    ProjectLocale,
    Repository,
    Resource,
    TranslatedResource,
    Translation,
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


class ProjectFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"Project {n}")
    slug = LazyAttribute(lambda p: slugify(p.name))

    class Meta:
        model = Project

    @post_generation
    def locales(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for locale in extracted:
                ProjectLocaleFactory.create(project=self, locale=locale)

    @post_generation
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
    type = Repository.Type.GIT
    url = Sequence(lambda n: f"https://example.com/url_{n}.git")

    class Meta:
        model = Repository


class ResourceFactory(DjangoModelFactory):
    project = SubFactory(ProjectFactory)
    path = Sequence(lambda n: f"/fake/path{n}.po")
    format = Resource.Format.GETTEXT
    total_strings = 1

    class Meta:
        model = Resource


class LocaleFactory(DjangoModelFactory):
    code = Sequence(lambda n: f"en-{n}")
    name = Sequence(lambda n: f"English #{n}")

    class Meta:
        model = Locale


class ProjectLocaleFactory(DjangoModelFactory):
    project = SubFactory(ProjectFactory)
    locale = SubFactory(LocaleFactory)

    class Meta:
        model = ProjectLocale


class EntityFactory(DjangoModelFactory):
    resource = SubFactory(ResourceFactory)
    string = Sequence(lambda n: f"string {n}")

    class Meta:
        model = Entity


class TranslationFactory(DjangoModelFactory):
    entity = SubFactory(EntityFactory)
    locale = SubFactory(LocaleFactory)
    string = Sequence(lambda n: f"translation {n}")
    user = SubFactory(UserFactory)

    class Meta:
        model = Translation


class TranslatedResourceFactory(DjangoModelFactory):
    resource = SubFactory(ResourceFactory)
    locale = SubFactory(LocaleFactory)

    class Meta:
        model = TranslatedResource
