
import pytest

from pontoon.base.models import Entity, Translation


@pytest.fixture
def translation0(locale0, entity0, user0):
    return Translation.objects.create(
        entity=entity0,
        string="Translation for entity0",
        locale=locale0,
        user=user0)


def _create_translations(entities, **kwargs):
    batch_kwargs = kwargs.pop("batch_kwargs", {})
    n = (
        Entity.objects.values_list("pk", flat=True)
                      .order_by("-pk").first()
        or 0) + 1
    translations = []
    for i, entity in enumerate(entities):
        string = "Translation for: %s" % (n + i)
        translation_kwargs = kwargs.copy()
        if batch_kwargs:
            translation_kwargs.update(batch_kwargs[i])
        translations.append(
            Translation(
                entity=entity,
                string=string,
                **translation_kwargs))
    Translation.objects.bulk_create(translations)
    return translations


def _create_entities(**kwargs):
    batch_kwargs = kwargs.pop("batch_kwargs", {})
    batch = kwargs.pop("batch", len(batch_kwargs) or 1)
    n = (
        Entity.objects.values_list("pk", flat=True)
                      .order_by("-pk").first()
        or 0) + 1
    entities = []
    for i in range(0, batch):
        string = "Entity %s" % (n + i)
        entity_kwargs = kwargs.copy()
        if batch_kwargs:
            entity_kwargs.update(batch_kwargs[i])
        entities.append(
            Entity(
                string=string,
                **entity_kwargs))
    Entity.objects.bulk_create(entities)
    return entities


@pytest.fixture
def translation_factory():
    return _create_translations


@pytest.fixture
def entity_factory():
    return _create_entities
