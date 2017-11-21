
import pytest

from pontoon.base.models import ProjectLocale


@pytest.fixture
def project_locale0(project0, locale0):
    """Project locale 0"""
    return ProjectLocale.objects.get(project=project0, locale=locale0)


@pytest.fixture
def project_locale1(project1, locale1):
    """Project locale 1"""
    return ProjectLocale.objects.get(project=project1, locale=locale1)
