
import pytest

from django.db.models import Max

from pontoon.base.models import (
    Entity, ProjectLocale, Resource, Translation, User)


@pytest.mark.django_db
def test_fixtures_base0(entity0, resource0, project0, project_locale0,
                        translation0, locale0):
    assert entity0.resource == resource0
    assert entity0.resource.project == project0
    assert translation0.entity == entity0
    assert project_locale0.project == project0
    assert project_locale0.locale == locale0


@pytest.mark.django_db
def test_fixtures_base1(entity1, resource1, project1, project_locale1,
                        translation1, locale1):
    assert entity1.resource == resource1
    assert entity1.resource.project == project1
    assert translation1.entity == entity1
    assert project_locale1.project == project1
    assert project_locale1.locale == locale1


@pytest.mark.django_db
def test_fixtures_baseX(projectX, localeX):
    assert projectX.slug == "projectX"
    assert localeX.code == "localeX"
    assert not ProjectLocale.objects.filter(project=projectX).exists()
    assert not ProjectLocale.objects.filter(locale=localeX).exists()
    assert not Resource.objects.filter(path="resourceX.po").exists()


@pytest.mark.django_db
def test_fixtures_resourceX(projectX, resourceX):
    assert resourceX.project == projectX
    assert resourceX.path == "resourceX.po"


@pytest.mark.django_db
def test_fixtures_users(user0, user1, userX, member0):
    assert user0.translation_set.exists() is True
    assert user1.translation_set.exists() is True
    assert userX.translation_set.exists() is False
    assert member0.client.session.items()
    assert member0.user == user0


@pytest.mark.django_db
def test_fixtures_factory_entity(entity_factory, resourceX):
    current_pk = Entity.objects.aggregate(pk=Max("pk"))['pk']

    entities = entity_factory(resource=resourceX)
    assert len(entities) == 1
    assert entities[0].string == "Entity %s" % (current_pk + 1)
    assert entities[0].string_plural == u""
    assert entities[0].obsolete is False

    entities = entity_factory(resource=resourceX, batch=2)
    assert len(entities) == 2

    entities = entity_factory(
        resource=resourceX,
        batch_kwargs=[dict(string="_1_"), dict(string="_2_")])
    assert len(entities) == 2
    assert entities[0].string == "_1_"
    assert entities[1].string == "_2_"


@pytest.mark.django_db
def test_fixtures_factory_user(user_factory):
    current_pk = User.objects.aggregate(pk=Max("pk"))['pk']

    users = user_factory()
    assert len(users) == 1
    assert users[0].username == "testuser%s" % (current_pk + 1)
    assert users[0].email == "%s@example.not" % users[0].username

    users = user_factory(batch=2)
    assert len(users) == 2

    users = user_factory(
        batch_kwargs=[
            dict(username="specialuser1"),
            dict(username="specialuser2")])
    assert len(users) == 2
    assert users[0].username == "specialuser1"
    assert users[1].username == "specialuser2"


@pytest.mark.django_db
def test_fixtures_factory_translation(entity_factory, translation_factory,
                                      localeX, resourceX):
    current_pk = Translation.objects.aggregate(pk=Max("pk"))['pk']
    entities = entity_factory(resource=resourceX, batch=2)

    translations = translation_factory(
        locale=localeX,
        batch_kwargs=[dict(entity=entities[0])])
    assert len(translations) == 1
    assert (
        translations[0].string
        == "Translation for: %s" % (current_pk + 1))

    translations = translation_factory(
        locale=localeX,
        batch_kwargs=[
            dict(entity=entities[0], string="_1_"),
            dict(entity=entities[1], string="_2_")])
    assert len(translations) == 2
    assert translations[0].string == "_1_"
    assert translations[1].string == "_2_"
