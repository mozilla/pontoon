from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, cast

from django.db import models
from django.db.models import Prefetch, QuerySet

from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    ProjectLocale,
    Section,
    Translation,
)


if TYPE_CHECKING:

    class EntityWithExtra(Entity):
        active_translations: QuerySet[Translation]
        alternative_originals: QuerySet[Translation]
        section_comment: str | None

    class ProjectWithExtra(Project):
        projectlocale: list[ProjectLocale]
else:
    EntityWithExtra = Entity
    ProjectWithExtra = Project


def map_entities_to_json(
    locale: Locale,
    preferred_source_locale: str | None,
    entities: QuerySet[Entity],
    is_sibling: bool = False,
    requested_entity: int | None = None,
) -> list[dict[str, Any]]:
    entities_ = prefetch_entities_data(entities, locale, preferred_source_locale)

    # If requested entity not in the current page
    if requested_entity and requested_entity not in [e.pk for e in entities_]:
        entities_ = list(entities_) + list(
            prefetch_entities_data(
                Entity.objects.filter(pk=requested_entity),
                locale,
                preferred_source_locale,
            )
        )

    entities_array = []
    for entity in entities_:
        try:
            readonly = (
                cast(ProjectWithExtra, entity.resource.project)
                .projectlocale[0]
                .readonly
            )
        except IndexError:
            # Entities explicitly requested using `string` or `list` URL parameters
            # might not be enabled for localization for the given locale. If the
            # project is given in the URL, the 404 page shows up, but if the All
            # Projects view is used, we hit the IndexError here, because the
            # `projectlocale` list is empty. In this case, we skip the entity.
            continue

        source_entity = (
            entity.alternative_originals[0]
            if preferred_source_locale and entity.alternative_originals
            else entity
        )

        ed = {
            "pk": entity.pk,
            "key": entity.key,
            "format": entity.resource.format,
            "date_created": entity.date_created,
            "path": entity.resource.path,
            "project": entity.resource.project.serialize(),
            "comment": entity.comment,
            "original": source_entity.string,
            "value": source_entity.value,
        }

        if source_entity.properties:
            ed["properties"] = source_entity.properties
        if entity.section_comment:
            ed["group_comment"] = entity.section_comment
        if entity.resource.comment:
            ed["resource_comment"] = entity.resource.comment
        if entity.meta:
            ed["meta"] = entity.meta
        if readonly:
            ed["readonly"] = True
        if is_sibling:
            ed["is_sibling"] = True
        if source_entity != entity:
            ed["machinery_value"] = entity.value
            if entity.properties:
                ed["machinery_properties"] = entity.properties
        if entity.active_translations:
            ed["translation"] = entity.active_translations[0].serialize()

        entities_array.append(ed)

    return entities_array


def prefetch_entities_data(
    entities: QuerySet[Entity], locale: Locale, preferred_source_locale: str | None
) -> Iterable[EntityWithExtra]:
    """
    Prefetch related Translations, Section comments, and ProjectLocales
    """

    active_translations = Translation.objects.filter(
        locale=locale, active=True
    ).prefetch_related("errors", "warnings")
    entities = cast(
        QuerySet[EntityWithExtra],
        entities.prefetch_related(
            Prefetch(
                "translation_set",
                queryset=active_translations,
                to_attr="active_translations",
            )
        )
        .annotate(
            section_comment=models.Subquery(
                Section.objects.filter(id=models.OuterRef("section_id")).values(
                    "comment"
                )
            )
        )
        .prefetch_related(
            Prefetch(
                "resource__project__project_locale",
                queryset=ProjectLocale.objects.filter(locale=locale),
                to_attr="projectlocale",
            )
        ),
    )

    # Prefetch approved translations for given preferred source locale
    if preferred_source_locale:
        alternative_originals = Translation.objects.filter(
            locale__code=preferred_source_locale, approved=True
        )
        entities = entities.prefetch_related(
            Prefetch(
                "translation_set",
                queryset=alternative_originals,
                to_attr="alternative_originals",
            )
        )

    return entities
