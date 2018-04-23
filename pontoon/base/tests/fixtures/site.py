import math
from datetime import datetime, timedelta

import pytest

from django.utils import timezone


def _get_project_resources(project):
    # this somewhat arbitrarily spreads the string count
    # among projects
    return [
        dict(project=project, total_strings=(i + 5) ** 3)
        for i in range(0, 7)]


def _get_project_locales(locales, project):
    return [
        dict(project=project, locale=locale)
        for locale in locales]


def _get_translated_resources(locales, project, resources):
    _kwargs = []
    for i, resource in enumerate(resources):
        for locale in locales:
            # this again spreads the stats counts in a kinda
            # arbitrary fashion
            _kwargs.append(
                dict(locale=locale,
                     approved_strings=(i + 2) ** 3,
                     translated_strings=(i + 1) ** 3,
                     fuzzy_strings=i ** 3))
    return _kwargs


def _create_site_root(factories):
    # creates the root objects for the site:
    # - projects
    # - locales
    # - project_locales
    # also returns kwarg lists for creating resources and
    # translated resources
    projects = factories['project'](batch=3)
    locales = factories['locale'](batch=3)
    project_locale_kwargs = []
    resource_kwargs = []
    translated_resource_kwargs = []
    for project in projects:
        resources = _get_project_resources(project)
        project_locale_kwargs += _get_project_locales(locales, project)
        translated_resource_kwargs += _get_translated_resources(
            locales, project, resources)
        resource_kwargs += resources
    project_locales = factories['project_locale'](
        batch_kwargs=project_locale_kwargs)
    return (
        projects,
        locales,
        project_locales,
        resource_kwargs,
        translated_resource_kwargs)


def _get_resource_key(resources, translated_resources, i):
    # this normalizes i to an index of a resource
    # effectively iterating through the resources
    return int(
        math.floor(
            i / float(len(translated_resources))
            * len(resources)))


def _create_resources(factories, resource_kwargs, translated_resource_kwargs):
    # creates resources and associates them to translated resources
    resources = factories['resource'](batch_kwargs=resource_kwargs)
    for i, translated_resource in enumerate(translated_resource_kwargs):
        resource = _get_resource_key(resources, translated_resource_kwargs, i)
        # associate the translated_resource with its resource
        translated_resource.update(dict(resource=resources[resource]))
    return resources, translated_resource_kwargs


def _get_translation(entities, locale, i):
    # spread the translations over the previous 17 days
    return dict(
        date=timezone.make_aware(
            datetime.now()
            - timedelta(days=i % 17)),
        entity=entities[i % len(entities)],
        locale=locale)


def _create_translations(factories, resources, locales):
    entities = factories['entity'](
        batch_kwargs=[
            dict(resource=resources[i % len(resources)])
            for i in range(0, 2 * len(resources))])
    translation_batch_kwargs = []
    # the number of translations we want to create
    translation_count = len(locales) * len(entities) * 2
    for i in range(0, translation_count):
        # spread the translations between locales
        locale = int(
            math.floor(float(i) / translation_count * len(locales)))
        translation_batch_kwargs.append(
            _get_translation(entities, locales[locale], i))
    translations = factories['translation'](
        batch_kwargs=translation_batch_kwargs)
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
            locale,
            (timezone.make_aware(datetime.min), None))
        if translation.date > date:
            latest_translations[resource][locale] = (
                translation.date, translation)
    return latest_translations


def _get_latest_translation(latest, kwargs):
    # find the latest translation for a resource
    return latest.get(kwargs['resource'].pk, {}).get(
        kwargs['locale'].code, (None, None))[1]


def _create_translated_resources(factories, translations,
                                 translated_resource_kwargs):
    # creates translated resources from pre-calculated kwargs
    latest = _get_latest_translations(translations)
    for kwargs in translated_resource_kwargs:
        # set calculated latest translation for resource
        kwargs["latest_translation"] = _get_latest_translation(latest, kwargs)
    translated_resources = (
        factories['translated_resource'](
            batch_kwargs=translated_resource_kwargs))
    return translated_resources


@pytest.fixture
def site_matrix(factories):
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
    (projects,
     locales,
     project_locales,
     resource_kwargs,
     translated_resource_kwargs) = _create_site_root(factories)
    resources, translated_resource_kwargs = _create_resources(
        factories, resource_kwargs, translated_resource_kwargs)
    entities, translations = _create_translations(
        factories, resources, locales)
    translated_resources = _create_translated_resources(
        factories, translations, translated_resource_kwargs)
    return dict(
        factories=factories,
        entities=entities,
        projects=projects,
        locales=locales,
        project_locales=project_locales,
        resources=resources,
        translations=translations,
        translated_resources=translated_resources)
