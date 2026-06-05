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

        if preferred_source_locale and entity.alternative_originals:
            original = entity.alternative_originals[0].string
        else:
            original = entity.string

        translation = (
            entity.active_translations[0].serialize()
            if entity.active_translations
            else None
        )

        entities_array.append(
            {
                "pk": entity.pk,
                "original": original,
                "machinery_original": entity.string,
                "key": entity.key,
                "path": entity.resource.path,
                "project": entity.resource.project.serialize(),
                "format": entity.resource.format,
                "comment": entity.comment,
                "group_comment": entity.section_comment or "",
                "resource_comment": entity.resource.comment or "",
                "meta": entity.meta,
                "obsolete": entity.obsolete,
                "translation": translation,
                "readonly": readonly,
                "is_sibling": is_sibling,
                "date_created": entity.date_created,
            }
        )

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
