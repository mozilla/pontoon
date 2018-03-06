# -*- coding: utf-8 -*-

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
def test_mgr_entity_filter_missing(resource0, locale0, entity1):
    entity1.delete()
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
def test_mgr_entity_filter_partially_translated_plurals(resource0,
                                                        locale0, entity1):
    entity1.delete()
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
def test_mgr_entity_filter_suggested(resourceX, localeX):
    entities = [
        Entity.objects.create(
            resource=resourceX,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i)
        for i in range(0, 3)]
    Translation.objects.create(
        locale=localeX,
        entity=entities[1],
        approved=False,
        fuzzy=False)
    Translation.objects.create(
        locale=localeX,
        entity=entities[2],
        approved=False,
        fuzzy=False)
    assert (
        set(Entity.objects.filter(
            Entity.objects.suggested(localeX)))
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
def test_mgr_entity_filter_missing_plural(resource0, locale0, entity1):
    entity1.delete()
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
def test_mgr_entity_filter_suggested_plural(resourceX, localeX):
    localeX.cldr_plurals = '1,5'
    localeX.save()
    entities = [
        Entity.objects.create(
            resource=resourceX,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i)
        for i in range(0, 3)]

    Translation.objects.create(
        locale=localeX,
        entity=entities[0],
        approved=False,
        fuzzy=False,
        plural_form=0)
    Translation.objects.create(
        locale=localeX,
        entity=entities[0],
        approved=False,
        fuzzy=False,
        plural_form=1)
    Translation.objects.create(
        locale=localeX,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        plural_form=0)
    Translation.objects.create(
        locale=localeX,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        plural_form=1)
    assert (
        set(Entity.objects.filter(
            Entity.objects.suggested(localeX)))
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
def test_mgr_entity_filter_has_suggestion_plural(resourceX, localeX):
    localeX.cldr_plurals = '1,5'
    localeX.save()
    entities = [
        Entity.objects.create(
            resource=resourceX,
            string='Unchanged string',
            string_plural='Unchanged plural string')
        for i in range(0, 3)]

    Translation.objects.create(
        locale=localeX,
        entity=entities[0],
        approved=True,
        fuzzy=False,
        plural_form=0)
    Translation.objects.create(
        locale=localeX,
        entity=entities[0],
        approved=False,
        fuzzy=False,
        plural_form=1)
    Translation.objects.create(
        locale=localeX,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        plural_form=0)
    Translation.objects.create(
        locale=localeX,
        entity=entities[2],
        approved=True,
        fuzzy=False,
        plural_form=1)
    assert (
        set(Entity.objects.filter(
            Entity.objects.has_suggestions(localeX)))
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
def test_mgr_entity_filter_combined(resourceX, localeX, user0):
    """
    All filters should be joined by AND instead of OR.
    Tests filters against bug introduced by bug 1243115.
    """
    entities = [
        Entity.objects.create(
            resource=resourceX,
            string="testentity%s" % i)
        for i in range(0, 2)]

    Translation.objects.create(
        locale=localeX,
        entity=entities[0],
        approved=True,
        fuzzy=False,
        user=user0)
    Translation.objects.create(
        locale=localeX,
        entity=entities[1],
        approved=True,
        fuzzy=False,
        user=user0)
    Translation.objects.create(
        locale=localeX,
        entity=entities[1],
        approved=False,
        fuzzy=False,
        user=user0)
    assert (
        list(Entity.for_project_locale(
            resourceX.project,
            localeX,
            status='suggested',
            author=user0.email))
        == [])
    assert (
        list(Entity.for_project_locale(
            resourceX.project,
            localeX,
            status='suggested',
            time='201001010100-205001010100'))
        == [])


@pytest.mark.django_db
def test_mgr_entity_search_invalid_query(entity_test_search):
    """
    We shouldn't return any records if there aren't any matching rows.
    """
    entities, search = entity_test_search

    assert search('localization') == []
    assert search('testing search queries') == []
    assert search(u"Ń") == []


@pytest.mark.django_db
def test_mgr_entity_search_entities(entity_test_search):
    """
    Search via querystrings available in entities.
    """
    entities, search = entity_test_search

    assert search(u'e') == entities
    assert search(u'entity string') == entities

    assert search(u'first entity') == [entities[0]]
    assert search(u'second entity') == [entities[1]]
    assert search(u'third entity') == [entities[2]]

    # Check if we're able search by unicode characters.
    assert search(u'gęślą') == [entities[2]]


@pytest.mark.django_db
def test_mgr_entity_search_translation(entity_test_search):
    """
    Search entities by contents of their translations.
    """
    entities, search = entity_test_search

    assert search('translation') == entities
    assert search('first translation') == [entities[0]]
    assert search('second translation') == [entities[1]]
    assert search('third translation') == [entities[2]]


@pytest.mark.django_db
def test_lookup_collation(resource0, locale0, entity_factory, translation_factory):
    """
    Filter translations according to collation.
    """
    entity = Entity.objects.create(
        resource=resource0,
        string="string")
    entities = entity_factory(
        resource=resource0,
        batch_kwargs=[
            {'string': u'First string',
             'comment': u'random Strıng'},
            {'string': u'Second strİng',
             'comment': u'random string'},
            {'string': u'Third Strıng',
             'comment': u'random strİng'}])

    batch_kwargs = [dict(entity=entity, locale=locale0, string=s)
                    for s in [u'this is string',
                              u'this is STRİNG',
                              u'this is Strıng',
                              u'this is StrInG',
                              u'this is sTriNg']]
    translations = translation_factory(
        batch_kwargs=batch_kwargs)
    # Check if 'Iı' and 'İi' are appropriately distinguished and filtered
    # according to turkish(tr_tr) collation
    assert (
        set(Entity.objects.filter(
            string__icontains_collate=(u'string', 'tr_tr')))
        == set([entities[n] for n in [0, 1]] + [entity]))
    assert (
        set(Entity.objects.filter(
            comment__icontains_collate=(u'strİng', 'tr_tr')))
        == set([entities[n] for n in [1, 2]]))
    assert (
        set(Translation.objects.filter(
            string__icontains_collate=(u'string', 'tr_tr')))
        == set([translations[n] for n in [0, 1, 4]]))
    assert (
        set(Translation.objects.filter(
            string__icontains_collate=(u'string', 'tr_tr')))
        == set([translations[n] for n in [0, 1, 4]]))
    assert (
        set(Translation.objects.filter(
            string__icontains_collate=(u'strıng', 'tr_tr')))
        == set([translations[n] for n in [2, 3]]))
    # Check if differentiation fails without any collation(C)
    assert (
        set(Translation.objects.filter(
            string__icontains_collate=(u'string', 'C')))
        == set([translations[n] for n in [0, 3, 4]]))
    # Compare the icontains_collate query with regular i_contains query
    assert (
        list(Translation.objects.filter(
            string__icontains=u'string'))
        == [translations[n] for n in [0, 2, 3, 4]])
