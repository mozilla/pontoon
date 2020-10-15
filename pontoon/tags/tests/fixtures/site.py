import functools
import math
from datetime import datetime, timedelta

import pytest

from django.db.models import Max
from django.utils import timezone

from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    ProjectLocale,
    Resource,
    TranslatedResource,
    Translation,
)


def _factory(Model=None, instance_attrs=None, number=None, args=None, **kwargs):
    # batch_kwargs is a list of dictionaries to pass as kwargs
    # when instantiating the objects
    batch_kwargs = args or {}

    # how many of the given Model to create
    batch = number or len(batch_kwargs) or 1

    n = (Model.objects.aggregate(pk=Max("pk"))["pk"] or 0) + 1
    instances = []
    for i in range(0, batch):
        model_kwargs = kwargs.copy()
        if batch_kwargs:
            model_kwargs.update(batch_kwargs[i])
        instance = Model(**model_kwargs)
        if instance_attrs:
            instance_attrs(instance, n + i)
        instances.append(instance)
    Model.objects.bulk_create(instances)
    return instances


def entity_factory():
    def instance_attrs(instance, i):
        if not instance.string:
            instance.string = "Entity %s" % i
        if not instance.order:
            instance.order = i

    return functools.partial(_factory, Model=Entity, instance_attrs=instance_attrs)


def locale_factory():
    def instance_attrs(instance, i):
        if not instance.code:
            instance.code = "factorylocale%s" % i

    return functools.partial(_factory, Model=Locale, instance_attrs=instance_attrs)


def project_factory():
    def instance_attrs(instance, i):
        if not instance.slug:
            instance.slug = "factoryproject%s" % i
        if not instance.name:
            instance.name = "Factory Project %s" % i

    return functools.partial(_factory, Model=Project, instance_attrs=instance_attrs)


def project_locale_factory():
    return functools.partial(_factory, Model=ProjectLocale)


def resource_factory():
    def instance_attrs(instance, i):
        if not instance.path:
            instance.path = "resource%s.po" % i

    return functools.partial(_factory, Model=Resource, instance_attrs=instance_attrs)


def translated_resource_factory():
    return functools.partial(_factory, Model=TranslatedResource)


def translation_factory():
    def instance_attrs(instance, i):
        if not instance.string:
            instance.string = "Translation for: %s" % i

    return functools.partial(_factory, Model=Translation, instance_attrs=instance_attrs)


factories = {
    "entity": entity_factory(),
    "locale": locale_factory(),
    "project": project_factory(),
    "project_locale": project_locale_factory(),
    "resource": resource_factory(),
    "translated_resource": translated_resource_factory(),
    "translation": translation_factory(),
}


def _get_project_resources(project):
    # this somewhat arbitrarily spreads the string count
    # among projects
    return [dict(project=project, total_strings=(i + 5) ** 3) for i in range(0, 7)]


def _get_project_locales(locales, project):
    return [dict(project=project, locale=locale) for locale in locales]


def _get_translated_resources(locales, project, resources):
    _kwargs = []
    for i, resource in enumerate(resources):
        for locale in locales:
            # this again spreads the stats counts in a kind of
            # arbitrary fashion
            _kwargs.append(
                {
                    "locale": locale,
                    "approved_strings": (i + 2) ** 3,
                    "unreviewed_strings": (i + 1) ** 3,
                    "fuzzy_strings": i ** 3,
                }
            )
    return _kwargs


def _create_site_root(factories):
    # creates the root objects for the site:
    # - projects
    # - locales
    # - project_locales
    # also returns kwarg lists for creating resources and
    # translated resources
    projects = factories["project"](number=3)
    locales = factories["locale"](number=3)
    project_locale_kwargs = []
    resource_kwargs = []
    translated_resource_kwargs = []
    for project in projects:
        resources = _get_project_resources(project)
        project_locale_kwargs += _get_project_locales(locales, project)
        translated_resource_kwargs += _get_translated_resources(
            locales, project, resources
        )
        resource_kwargs += resources
    project_locales = factories["project_locale"](args=project_locale_kwargs)
    return (
        projects,
        locales,
        project_locales,
        resource_kwargs,
        translated_resource_kwargs,
    )


def _get_resource_key(resources, translated_resources, i):
    # this normalizes i to an index of a resource
    # effectively iterating through the resources
    return int(math.floor(i / float(len(translated_resources)) * len(resources)))


def _create_resources(factories, resource_kwargs, translated_resource_kwargs):
    # creates resources and associates them to translated resources
    resources = factories["resource"](args=resource_kwargs)
    for i, translated_resource in enumerate(translated_resource_kwargs):
        resource = _get_resource_key(resources, translated_resource_kwargs, i)
        # associate the translated_resource with its resource
        translated_resource.update(dict(resource=resources[resource]))
    return resources, translated_resource_kwargs


def _get_translation(entities, locale, i):
    # spread the translations over the previous 17 days
    return {
        "date": timezone.make_aware(datetime.now() - timedelta(days=i % 17)),
        "entity": entities[i % len(entities)],
        "locale": locale,
    }


def _create_translations(factories, resources, locales):
    entities = factories["entity"](
        args=[
            dict(resource=resources[i % len(resources)])
            for i in range(0, 2 * len(resources))
        ]
    )
    translation_batch_kwargs = []
    # the number of translations we want to create
    translation_count = len(locales) * len(entities) * 2
    for i in range(0, translation_count):
        # spread the translations between locales
        locale = int(math.floor(float(i) / translation_count * len(locales)))
        translation_batch_kwargs.append(_get_translation(entities, locales[locale], i))
    translations = factories["translation"](args=translation_batch_kwargs)
    return entities, translations


def _get_latest_translations(translations):
    # get the latest translations per resource from list
    # of created translations
    latest_translations = {}
    for translation in translations:
        resource = translation.entity.resource.pk
        locale = translation.locale.code
        latest_translations[resource] = latest_translations.get(resource, {})
        date, _translation = latest_translations[resource].get(
            locale, (timezone.make_aware(datetime.min), None)
        )
        if translation.date > date:
            latest_translations[resource][locale] = (translation.date, translation)
    return latest_translations


def _get_latest_translation(latest, kwargs):
    # find the latest translation for a resource
    return latest.get(kwargs["resource"].pk, {}).get(
        kwargs["locale"].code, (None, None)
    )[1]


def _create_translated_resources(
    factories, translations, translated_resource_kwargs,
):
    # creates translated resources from pre-calculated kwargs
    latest = _get_latest_translations(translations)
    for kwargs in translated_resource_kwargs:
        # set calculated latest translation for resource
        kwargs["latest_translation"] = _get_latest_translation(latest, kwargs)

    translated_resources = factories["translated_resource"](
        args=translated_resource_kwargs,
    )
    return translated_resources


@pytest.fixture
def site_matrix():
    """This fixture provides a matrix of pre-installed objects
    Specifically:
     - projects
     - locales
     - project_locales
     - resources
     - translated_resources
     - entities
     - translations

    It uses bulk loading to speed up test runs, but ideally we
    should move this fixture inside pytests db_setup so that
    it only loads once.

    """
    (
        projects,
        locales,
        project_locales,
        resource_kwargs,
        translated_resource_kwargs,
    ) = _create_site_root(factories)
    resources, translated_resource_kwargs = _create_resources(
        factories, resource_kwargs, translated_resource_kwargs
    )
    entities, translations = _create_translations(factories, resources, locales)
    translated_resources = _create_translated_resources(
        factories, translations, translated_resource_kwargs
    )
    return {
        "factories": factories,
        "entities": entities,
        "projects": projects,
        "locales": locales,
        "project_locales": project_locales,
        "resources": resources,
        "translations": translations,
        "translated_resources": translated_resources,
    }
