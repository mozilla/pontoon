# -*- coding: utf-8 -*-

import functools

import pytest

from pontoon.base.models import (
    Entity, Resource, Subpage, TranslatedResource, Translation)
from pontoon.sync import KEY_SEPARATOR


@pytest.fixture
def entity0(resource0):
    """Entity 0"""
    return Entity.objects.get(resource=resource0, string="entity0")


@pytest.fixture
def entity1(resource1):
    """Entity 1"""
    return Entity.objects.get(resource=resource1, string="entity1")


@pytest.fixture
def entity_factory(factory):
    """Entity factory
    create entities in a hurry!

    Provides an entity factory function that accepts the following args:

    :arg int `batch`: number of entities to instantiate, defaults to len of
        `batch_kwargs` or 1
    :arg list `batch_kwargs`: a list of kwargs to instantiate the entities
    """

    def instance_attrs(instance, i):
        if not instance.string:
            instance.string = "Entity %s" % i
        if not instance.order:
            instance.order = i

    return functools.partial(
        factory, Model=Entity, instance_attrs=instance_attrs)


@pytest.fixture
def entity_test_models(translation0, locale1):
    """This fixture provides:

    - 2 translations of a plural entity
    - 1 translation of a non-plural entity
    - A subpage that contains the plural entity
    """

    entity0 = translation0.entity
    locale0 = translation0.locale
    project0 = entity0.resource.project

    locale0.cldr_plurals = "0,1"
    locale0.save()
    translation0.plural_form = 0
    translation0.save()
    resourceX = Resource.objects.create(
        project=project0, path="resourceX.po")
    entity0.string = "Entity zero"
    entity0.key = entity0.string
    entity0.string_plural = "Plural %s" % entity0.string
    entity0.save()
    entityX = Entity.objects.create(
        resource=resourceX,
        string="entityX",
        key='Key%sentityX' % KEY_SEPARATOR)
    translation0pl = Translation.objects.create(
        entity=entity0,
        locale=locale0,
        plural_form=1,
        string="Plural %s" % translation0.string)
    translationX = Translation.objects.create(
        entity=entityX,
        locale=locale0,
        string="Translation %s" % entityX.string)
    subpageX = Subpage.objects.create(
        project=project0, name="Subpage")
    subpageX.resources.add(entity0.resource)
    return translation0, translation0pl, translationX, subpageX


@pytest.fixture
def entity_test_search(entity_factory, translation_factory,
                       resourceX, localeX):
    """This fixture provides:

    - 3 translated entities
    - A lambda for searching for entities using Entity.for_project_locale
    """
    TranslatedResource.objects.create(
        locale=localeX,
        resource=resourceX)
    entities = entity_factory(
        resource=resourceX,
        batch_kwargs=[
            {'key': 'access.key',
             'string': 'First entity string',
             'string_plural': 'First plural string',
             'comment': 'random notes'},
            {'key': 'second.key',
             'string': 'Second entity string',
             'string_plural': 'Second plural string',
             'comment': 'random'},
            {'key': 'third.key',
             'string': u'Third entity string with some twist: ZAŻÓŁĆ GĘŚLĄ',
             'string_plural': 'Third plural',
             'comment': 'even more random notes'}])
    translation_factory(
        locale=localeX,
        batch_kwargs=[
            {'string': 'First translation', 'entity': entities[0]},
            {'string': 'Second translation', 'entity': entities[1]},
            {'string': 'Third translation', 'entity': entities[2]}])
    return (
        entities,
        lambda q: list(
            Entity.for_project_locale(
                resourceX.project,
                localeX,
                search=q)))
