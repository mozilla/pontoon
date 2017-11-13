
import pytest


# This test is a placeholder to ensure that the default fixtures work.
# It can be removed once other tests are added
@pytest.mark.django_db
def test_fixtures0(entity0, resource0, project0):
    assert entity0
    assert entity0.resource == resource0
    assert entity0.resource.project == project0


# This test is a placeholder to ensure that the default fixtures work.
# It can be removed once other tests are added
@pytest.mark.django_db
def test_fixtures1(entity1, resource1, project1):
    assert entity1
    assert entity1.resource == resource1
    assert entity1.resource.project == project1


# This test is a placeholder to ensure that the default fixtures work.
# It can be removed once other tests are added
@pytest.mark.django_db
def test_locales(locale0, locale1):
    assert locale0
    assert locale1
