import factory
from factory import LazyAttribute, Sequence, SubFactory, SelfAttribute
from factory.django import DjangoModelFactory

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.template.defaultfilters import slugify

from pontoon.base.models import (
    ChangedEntityLocale,
    Entity,
    Locale,
    Project,
    ProjectLocale,
    Repository,
    Resource,
    Subpage,
    TranslatedResource,
    Translation,
    TranslationMemoryEntry,
)
from pontoon.checks.models import Error, Warning
from pontoon.tags.models import Tag
from pontoon.terminology.models import Term, TermTranslation


class UserFactory(DjangoModelFactory):
    username = Sequence(lambda n: "user%s" % n)
    email = LazyAttribute(lambda o: "%s@example.com" % o.username)

    class Meta:
        model = get_user_model()


class GroupFactory(DjangoModelFactory):
    name = Sequence(lambda n: "group%s" % n)

    class Meta:
        model = Group


class ProjectFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"Project {n}")
    slug = LazyAttribute(lambda p: slugify(p.name))
    links = False
    visibility = Project.Visibility.PUBLIC

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


class ProjectLocaleFactory(DjangoModelFactory):
    class Meta:
        model = ProjectLocale


class RepositoryFactory(DjangoModelFactory):
    project = SubFactory(ProjectFactory)
    type = Repository.Type.GIT
    url = Sequence(lambda n: f"https://example.com/url_{n}.git")

    class Meta:
        model = Repository


class ResourceFactory(DjangoModelFactory):
    project = SubFactory(ProjectFactory)
    path = Sequence(lambda n: f"/fake/path{n}.po")
    format = Resource.Format.PO
    total_strings = 1

    class Meta:
        model = Resource


class SubpageFactory(DjangoModelFactory):
    project = SubFactory(ProjectFactory)
    name = Sequence(lambda n: "subpage%s" % n)

    class Meta:
        model = Subpage


class LocaleFactory(DjangoModelFactory):
    code = Sequence(lambda n: f"en-{n}")
    name = Sequence(lambda n: f"English #{n}")

    class Meta:
        model = Locale


class EntityFactory(DjangoModelFactory):
    resource = SubFactory(ResourceFactory)
    string = Sequence(lambda n: f"string {n}")
    order = Sequence(lambda n: n)

    class Meta:
        model = Entity


class PluralEntityFactory(DjangoModelFactory):
    resource = SubFactory(ResourceFactory)
    string = Sequence(lambda n: f"string {n}")
    string_plural = Sequence(lambda n: f"string plural {n}")

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
    string = Sequence(lambda n: f"translation {n}")
    user = SubFactory(UserFactory)

    class Meta:
        model = Translation


class IdenticalTranslationFactory(TranslationFactory):
    entity = SubFactory(EntityFactory, string=SelfAttribute("..string"))


class TranslationMemoryFactory(DjangoModelFactory):
    source = Sequence(lambda n: f"source {n}")
    target = Sequence(lambda n: f"target {n}")
    entity = SubFactory(EntityFactory, string=SelfAttribute("..source"))
    locale = SubFactory(LocaleFactory)

    class Meta:
        model = TranslationMemoryEntry


class TranslatedResourceFactory(DjangoModelFactory):
    resource = SubFactory(ResourceFactory)
    locale = SubFactory(LocaleFactory)

    class Meta:
        model = TranslatedResource


class ErrorFactory(DjangoModelFactory):
    library = Sequence(lambda n: "pontoon")
    message = Sequence(lambda n: f"Error {n}")
    translation = SubFactory(TranslationFactory)

    class Meta:
        model = Error


class WarningFactory(DjangoModelFactory):
    library = Sequence(lambda n: "pontoon")
    message = Sequence(lambda n: f"Warning {n}")
    translation = SubFactory(TranslationFactory)

    class Meta:
        model = Warning


class TagFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"Tag {n}")
    slug = LazyAttribute(lambda p: slugify(p.name))

    class Meta:
        model = Tag


class TermFactory(DjangoModelFactory):
    text = Sequence(lambda n: f"Term {n}")
    definition = "definition"
    part_of_speech = "part_of_speech"
    case_sensitive = False
    do_not_translate = False

    class Meta:
        model = Term


class TermTranslationFactory(DjangoModelFactory):
    term = SubFactory(TermFactory)
    locale = SubFactory(LocaleFactory)
    text = Sequence(lambda n: f"Term Translation {n}")

    class Meta:
        model = TermTranslation
