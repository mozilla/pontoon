import pytest

from pontoon.test.factories import (
    EntityFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    TranslatedResourceFactory,
)


@pytest.fixture
def settings_debug(settings):
    """Make the settings.DEBUG for this test"""
    settings.DEBUG = True


@pytest.fixture
def locale_parts(project_b, locale_c, locale_b):
    ProjectLocaleFactory.create(project=project_b, locale=locale_c)
    ProjectLocaleFactory.create(project=project_b, locale=locale_b)
    resourceX = ResourceFactory.create(
        project=project_b,
        path="resourceX.po",
        format="gettext",
    )
    entityX = EntityFactory.create(resource=resourceX, string="entityX")
    resourceX.total_strings = 1
    resourceX.save()
    TranslatedResourceFactory.create(locale=locale_c, resource=resourceX)
    return locale_c, locale_b, entityX
