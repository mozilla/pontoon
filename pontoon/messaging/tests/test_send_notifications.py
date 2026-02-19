import pytest

from pontoon.messaging.management.commands.send_suggestion_notifications import Command
from pontoon.test.factories import (
    EntityFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    TranslationFactory,
)


@pytest.mark.django_db
def test_get_suggestions_excludes_system_projects(
    locale_a, project_a, system_project_a
):
    # regular project with suggestions included
    resource_regular = ResourceFactory.create(project=project_a)
    ProjectLocaleFactory.create(project=project_a, locale=locale_a)
    entity_regular = EntityFactory.create(resource=resource_regular)
    regular_translation = TranslationFactory.create(
        locale=locale_a,
        entity=entity_regular,
        approved=False,
        pretranslated=False,
        rejected=False,
        fuzzy=False,
    )

    # system suggestions excluded
    resource_system = ResourceFactory.create(project=system_project_a)
    ProjectLocaleFactory.create(project=system_project_a, locale=locale_a)
    entity_system = EntityFactory.create(resource=resource_system)
    system_translation = TranslationFactory.create(
        locale=locale_a,
        entity=entity_system,
        approved=False,
        pretranslated=False,
        rejected=False,
        fuzzy=False,
    )

    suggestions = Command().get_suggestions()
    assert regular_translation in suggestions
    assert system_translation not in suggestions
