
import pytest

from pontoon.base.models import (
    Locale, ProjectLocale, TranslatedResource)


@pytest.fixture
def locale0():
    return Locale.objects.create(code="locale0", name="Locale 0")


@pytest.fixture
def locale1():
    return Locale.objects.create(code="locale1", name="Locale 1")


@pytest.fixture
def localeX():
    return Locale.objects.create(code="localeX", name="Locale X")


@pytest.fixture
def locale_parts(locale0, locale1, entity0):
    project = entity0.resource.project
    resource = entity0.resource
    resource.total_strings = 1
    resource.save()
    ProjectLocale.objects.create(
        project=project, locale=locale0)
    ProjectLocale.objects.create(
        project=project, locale=locale1)
    TranslatedResource.objects.create(
        locale=locale0, resource=entity0.resource)
    return locale0, locale1, entity0
