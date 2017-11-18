
import pytest

from pontoon.base.models import Entity, Translation


@pytest.mark.django_db
def test_mgr_entity_filter_translated(resource0, locale0):
    entities = [
        Entity.objects.create(
            resource=resource0,
            string="testentity%s" % i)
        for i in range(0, 3)]
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[1],
        approved=False)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        approved=True)
    assert (
        set(Entity.objects.filter(
            Entity.objects.translated(locale0)))
        == {entities[0], entities[2]})


@pytest.mark.django_db
def test_mgr_entity_filter_translated_plurals(resource0, locale0):
    locale0.cldr_plurals = '1,5'
    locale0.save()
    entities = [
        Entity.objects.create(
            resource=resource0,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i)
        for i in range(0, 3)]
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        plural_form=0,
        approved=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        plural_form=1,
        approved=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[1],
        plural_form=0,
        approved=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        plural_form=0,
        approved=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        plural_form=1,
        approved=True)
    assert (
        set(Entity.objects.filter(
            Entity.objects.translated(locale0)))
        == {entities[0], entities[2]})


@pytest.mark.django_db
def test_mgr_entity_filter_fuzzy(resource0, locale0):
    entities = [
        Entity.objects.create(
            resource=resource0,
            string="testentity%s" % i)
        for i in range(0, 3)]
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        fuzzy=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[1],
        approved=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        fuzzy=True)
    assert (
        set(Entity.objects.filter(
            Entity.objects.fuzzy(locale0)))
        == {entities[0], entities[2]})


@pytest.mark.django_db
def test_mgr_entity_filter_fuzzy_plurals(resource0, locale0):
    locale0.cldr_plurals = '1,5'
    locale0.save()
    entities = [
        Entity.objects.create(
            resource=resource0,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i)
        for i in range(0, 3)]

    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        plural_form=0,
        fuzzy=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        plural_form=1,
        fuzzy=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[1],
        plural_form=0,
        fuzzy=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        plural_form=0,
        fuzzy=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        plural_form=1,
        fuzzy=True)
    assert (
        set(Entity.objects.filter(
            Entity.objects.fuzzy(locale0)))
        == {entities[0], entities[2]})


@pytest.mark.django_db
def test_mgr_entity_filter_missing(resource0, locale0):
    entities = [
        Entity.objects.create(
            resource=resource0,
            string="testentity%s" % i)
        for i in range(0, 3)]

    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2])
    Translation.objects.create(
        locale=locale0,
        entity=entities[2])
    assert (
        set(Entity.objects.filter(
            Entity.objects.missing(locale0)))
        == {entities[1]})


@pytest.mark.django_db
def test_mgr_entity_filter_partially_translated_plurals(resource0, locale0):
    locale0.cldr_plurals = '1,5'
    locale0.save()
    entities = [
        Entity.objects.create(
            resource=resource0,
            string='Unchanged string',
            string_plural='Unchanged plural string')
        for i in range(0, 3)]

    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        plural_form=0)
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        plural_form=1)
    Translation.objects.create(
        locale=locale0,
        entity=entities[1],
        plural_form=0)
    assert (
        set(Entity.objects.filter(
            Entity.objects.missing(locale0)))
        == {entities[1], entities[2]})


@pytest.mark.django_db
def test_mgr_entity_filter_suggested(resource0, locale0):
    entities = [
        Entity.objects.create(
            resource=resource0,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i)
        for i in range(0, 3)]
    Translation.objects.create(
        locale=locale0,
        entity=entities[1],
        approved=False,
        fuzzy=False)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        approved=False,
        fuzzy=False)
    assert (
        set(Entity.objects.filter(
            Entity.objects.suggested(locale0)))
        == {entities[1], entities[2]})


@pytest.mark.django_db
def test_mgr_entity_filter_unchanged(resource0, locale0):
    entities = [
        Entity.objects.create(
            resource=resource0,
            string='Unchanged string')
        for i in range(0, 3)]
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=True,
        string='Unchanged string')
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        fuzzy=True,
        string='Unchanged string')
    assert (
        set(Entity.objects.filter(
            Entity.objects.unchanged(locale0)))
        == {entities[0], entities[2]})


@pytest.mark.django_db
def test_mgr_entity_filter_missing_plural(resource0, locale0):
    locale0.cldr_plurals = '1,5'
    locale0.save()
    entities = [
        Entity.objects.create(
            resource=resource0,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i)
        for i in range(0, 3)]

    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        fuzzy=True,
        plural_form=0)
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        fuzzy=True,
        plural_form=1)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        approved=True,
        plural_form=0)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        approved=True,
        plural_form=1)
    assert (
        set(Entity.objects.filter(
            Entity.objects.missing(locale0)))
        == {entities[1]})


@pytest.mark.django_db
def test_mgr_entity_filter_suggested_plural(resource0, locale0):
    locale0.cldr_plurals = '1,5'
    locale0.save()
    entities = [
        Entity.objects.create(
            resource=resource0,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i)
        for i in range(0, 3)]

    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=False,
        fuzzy=False,
        plural_form=0)
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=False,
        fuzzy=False,
        plural_form=1)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        plural_form=0)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        plural_form=1)
    assert (
        set(Entity.objects.filter(
            Entity.objects.suggested(locale0)))
        == {entities[0], entities[2]})


@pytest.mark.django_db
def test_mgr_entity_filter_unchanged_plural(resource0, locale0):
    locale0.cldr_plurals = '1,5'
    locale0.save()
    entities = [
        Entity.objects.create(
            resource=resource0,
            string='Unchanged string',
            string_plural='Unchanged plural string')
        for i in range(0, 3)]

    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=True,
        plural_form=0,
        string='Unchanged string')
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=True,
        plural_form=1,
        string='Unchanged plural string')
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        fuzzy=True,
        plural_form=0,
        string='Unchanged string')
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        fuzzy=True,
        plural_form=1,
        string='Unchanged plural string')
    assert (
        set(Entity.objects.filter(
            Entity.objects.unchanged(locale0)))
        == {entities[0], entities[2]})


@pytest.mark.django_db
def test_mgr_entity_filter_has_suggestion_plural(resource0, locale0):
    locale0.cldr_plurals = '1,5'
    locale0.save()
    entities = [
        Entity.objects.create(
            resource=resource0,
            string='Unchanged string',
            string_plural='Unchanged plural string')
        for i in range(0, 3)]

    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=True,
        fuzzy=False,
        plural_form=0)
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=False,
        fuzzy=False,
        plural_form=1)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        plural_form=0)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        approved=True,
        fuzzy=False,
        plural_form=1)
    assert (
        set(Entity.objects.filter(
            Entity.objects.has_suggestions(locale0)))
        == {entities[0], entities[2]})


@pytest.mark.django_db
def test_mgr_entity_filter_rejected(resource0, locale0):
    entities = [
        Entity.objects.create(
            resource=resource0,
            string="testentity%s" % i)
        for i in range(0, 3)]

    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=False,
        fuzzy=False,
        rejected=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=True,
        fuzzy=False,
        rejected=False)
    Translation.objects.create(
        locale=locale0,
        entity=entities[1],
        approved=True,
        fuzzy=False,
        rejected=False)
    Translation.objects.create(
        locale=locale0,
        entity=entities[1],
        approved=False,
        fuzzy=False,
        rejected=True)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        rejected=False)
    assert (
        set(Entity.objects.filter(
            Entity.objects.rejected(locale0)))
        == {entities[0], entities[1]})


@pytest.mark.django_db
def test_mgr_entity_filter_rejected_plural(resource0, locale0):
    locale0.cldr_plurals = '1,5'
    locale0.save()
    entities = [
        Entity.objects.create(
            resource=resource0,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i)
        for i in range(0, 3)]
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=True,
        fuzzy=False,
        rejected=False,
        plural_form=0)
    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=True,
        fuzzy=False,
        rejected=False,
        plural_form=1)
    Translation.objects.create(
        locale=locale0,
        entity=entities[1],
        approved=True,
        fuzzy=False,
        rejected=False,
        plural_form=0)
    Translation.objects.create(
        locale=locale0,
        entity=entities[1],
        approved=False,
        fuzzy=False,
        rejected=True,
        plural_form=1)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        rejected=True,
        plural_form=0)
    Translation.objects.create(
        locale=locale0,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        rejected=True,
        plural_form=1)
    assert (
        set(Entity.objects.filter(
            Entity.objects.rejected(locale0)))
        == {entities[1], entities[2]})


@pytest.mark.django_db
def test_mgr_entity_filter_combined(resource0, locale0, user0):
    """
    All filters should be joined by AND instead of OR.
    Tests filters against bug introduced by bug 1243115.
    """
    entities = [
        Entity.objects.create(
            resource=resource0,
            string="testentity%s" % i)
        for i in range(0, 2)]

    Translation.objects.create(
        locale=locale0,
        entity=entities[0],
        approved=True,
        fuzzy=False,
        user=user0)
    Translation.objects.create(
        locale=locale0,
        entity=entities[1],
        approved=True,
        fuzzy=False,
        user=user0)
    Translation.objects.create(
        locale=locale0,
        entity=entities[1],
        approved=False,
        fuzzy=False,
        user=user0)
    assert (
        list(Entity.for_project_locale(
            resource0.project,
            locale0,
            status='suggested',
            author=user0.email))
        == [])
    assert (
        list(Entity.for_project_locale(
            resource0.project,
            locale0,
            status='suggested',
            time='201001010100-205001010100'))
        == [])
