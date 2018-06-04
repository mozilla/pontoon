# -*- coding: utf-8 -*-

import pytest

from pontoon.base.models import (
    Entity,
    Translation,
)
from pontoon.test.factories import (
    EntityFactory,
    TranslatedResourceFactory,
    TranslationFactory,
)


@pytest.fixture
def entity_test_search(resource_a, locale_a):
    """This fixture provides:

    - 7 translated entities
    - A lambda for searching for entities using Entity.for_project_locale
    """
    TranslatedResourceFactory.create(
        locale=locale_a,
        resource=resource_a,
    )

    entity_args = [
        {
            'string': 'First entity string',
            'string_plural': 'First plural string',
            'comment': 'random notes',
        }, {
            'string': 'Second entity string',
            'string_plural': 'Second plural string',
            'comment': 'random',
        }, {
            'string': u'Third entity string with some twist: ZAŻÓŁĆ GĘŚLĄ',
            'string_plural': 'Third plural',
            'comment': 'even more random notes',
        }, {
            'string': 'Entity with first string',
            'string_plural': 'Entity with plural first string',
            'comment': 'random notes',
        }, {
            'string': 'First Entity',
            'string_plural': 'First plural entity',
            'comment': 'random notes',
        }, {
            'string': 'First Entity with string',
            'string_plural': 'First plural entity',
            'comment': 'random notes',
        }, {
            'string': 'Entity with quoted "string"',
            'string_plural': 'plural entity',
            'comment': 'random notes',
        },
    ]
    entities = [
        EntityFactory(
            resource=resource_a,
            string=x['string'],
            string_plural=x['string_plural'],
            comment=x['comment'],
            order=i,
        ) for i, x in enumerate(entity_args)
    ]

    translation_args = [
        {'string': 'First translation', 'entity': entities[0]},
        {'string': 'Second translation', 'entity': entities[1]},
        {'string': 'Third translation', 'entity': entities[2]},
        {'string': 'Fourth translation', 'entity': entities[3]},
        {'string': 'Fifth translation', 'entity': entities[4]},
        {'string': 'Sixth translation', 'entity': entities[5]},
        {'string': 'Seventh translation', 'entity': entities[6]},
    ]
    for x in translation_args:
        TranslationFactory.create(
            locale=locale_a,
            string=x['string'],
            entity=x['entity'],
        )

    return (
        entities,
        lambda q: list(
            Entity.for_project_locale(
                resource_a.project,
                locale_a,
                search=q,
            )
        )
    )


@pytest.mark.django_db
def test_mgr_entity_filter_translated(resource_a, locale_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i
        ) for i in range(0, 3)
    ]
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        approved=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=False,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        approved=True,
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.translated(locale_a)
        )) == {entities[0], entities[2]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_translated_plurals(resource_a, locale_a):
    locale_a.cldr_plurals = '1,5'
    locale_a.save()
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i,
        ) for i in range(0, 3)
    ]
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        plural_form=0,
        approved=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        plural_form=1,
        approved=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        plural_form=0,
        approved=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        plural_form=0,
        approved=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        plural_form=1,
        approved=True,
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.translated(locale_a)
        )) == {entities[0], entities[2]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_fuzzy(resource_a, locale_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
        ) for i in range(0, 3)
    ]
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        fuzzy=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        fuzzy=True,
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.fuzzy(locale_a)
        )) == {entities[0], entities[2]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_fuzzy_plurals(resource_a, locale_a):
    locale_a.cldr_plurals = '1,5'
    locale_a.save()
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i,
        ) for i in range(0, 3)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        plural_form=0,
        fuzzy=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        plural_form=1,
        fuzzy=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        plural_form=0,
        fuzzy=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        plural_form=0,
        fuzzy=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        plural_form=1,
        fuzzy=True,
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.fuzzy(locale_a)
        )) == {entities[0], entities[2]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_missing(resource_a, locale_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
        ) for i in range(0, 3)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        approved=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.missing(locale_a)
        )) == {entities[1]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_partially_translated_plurals(resource_a, locale_a):
    locale_a.cldr_plurals = '1,5'
    locale_a.save()
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string='Unchanged string',
            string_plural='Unchanged plural string',
        ) for i in range(0, 3)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        plural_form=0,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        plural_form=1,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        plural_form=0,
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.missing(locale_a)
        )) == {entities[1], entities[2]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_suggested(resource_b, locale_b):
    entities = [
        EntityFactory.create(
            resource=resource_b,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i,
        ) for i in range(0, 3)
    ]
    TranslationFactory.create(
        locale=locale_b,
        entity=entities[1],
        approved=False,
        fuzzy=False,
    )
    TranslationFactory.create(
        locale=locale_b,
        entity=entities[2],
        approved=False,
        fuzzy=False,
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.suggested(locale_b)
        )) == {entities[1], entities[2]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_unchanged(resource_a, locale_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string='Unchanged string',
        ) for i in range(0, 3)
    ]
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        approved=True,
        string='Unchanged string',
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        fuzzy=True,
        string='Unchanged string',
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.unchanged(locale_a)
        )) == {entities[0], entities[2]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_missing_plural(resource_a, locale_a):
    locale_a.cldr_plurals = '1,5'
    locale_a.save()
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i,
        ) for i in range(0, 3)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        fuzzy=True,
        plural_form=0,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        fuzzy=True,
        plural_form=1,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        approved=True,
        plural_form=0,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        approved=True,
        plural_form=1,
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.missing(locale_a)
        )) == {entities[1]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_suggested_plural(resource_b, locale_b):
    locale_b.cldr_plurals = '1,5'
    locale_b.save()
    entities = [
        EntityFactory.create(
            resource=resource_b,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i,
        ) for i in range(0, 3)
    ]

    TranslationFactory.create(
        locale=locale_b,
        entity=entities[0],
        approved=False,
        fuzzy=False,
        plural_form=0,
    )
    TranslationFactory.create(
        locale=locale_b,
        entity=entities[0],
        approved=False,
        fuzzy=False,
        plural_form=1,
    )
    TranslationFactory.create(
        locale=locale_b,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        plural_form=0,
    )
    TranslationFactory.create(
        locale=locale_b,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        plural_form=1,
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.suggested(locale_b)
        )) == {entities[0], entities[2]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_unchanged_plural(resource_a, locale_a):
    locale_a.cldr_plurals = '1,5'
    locale_a.save()
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string='Unchanged string',
            string_plural='Unchanged plural string',
        ) for i in range(0, 3)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        approved=True,
        plural_form=0,
        string='Unchanged string',
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        approved=True,
        plural_form=1,
        string='Unchanged plural string',
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        fuzzy=True,
        plural_form=0,
        string='Unchanged string',
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        fuzzy=True,
        plural_form=1,
        string='Unchanged plural string',
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.unchanged(locale_a)
        )) == {entities[0], entities[2]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_has_suggestion_plural(resource_b, locale_b):
    locale_b.cldr_plurals = '1,5'
    locale_b.save()
    entities = [
        EntityFactory.create(
            resource=resource_b,
            string='Unchanged string',
            string_plural='Unchanged plural string',
        ) for i in range(0, 3)
    ]

    TranslationFactory.create(
        locale=locale_b,
        entity=entities[0],
        approved=True,
        fuzzy=False,
        plural_form=0,
    )
    TranslationFactory.create(
        locale=locale_b,
        entity=entities[0],
        approved=False,
        fuzzy=False,
        plural_form=1,
    )
    TranslationFactory.create(
        locale=locale_b,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        plural_form=0,
    )
    TranslationFactory.create(
        locale=locale_b,
        entity=entities[2],
        approved=True,
        fuzzy=False,
        plural_form=1,
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.has_suggestions(locale_b)
        )) == {entities[0], entities[2]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_rejected(resource_a, locale_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
        ) for i in range(0, 3)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        approved=False,
        fuzzy=False,
        rejected=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        approved=True,
        fuzzy=False,
        rejected=False,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=True,
        fuzzy=False,
        rejected=False,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=False,
        fuzzy=False,
        rejected=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        rejected=False,
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.rejected(locale_a)
        )) == {entities[0], entities[1]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_rejected_plural(resource_a, locale_a):
    locale_a.cldr_plurals = '1,5'
    locale_a.save()
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
            string_plural="testpluralentity%s" % i,
        ) for i in range(0, 3)
    ]
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        approved=True,
        fuzzy=False,
        rejected=False,
        plural_form=0,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        approved=True,
        fuzzy=False,
        rejected=False,
        plural_form=1,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=True,
        fuzzy=False,
        rejected=False,
        plural_form=0,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=False,
        fuzzy=False,
        rejected=True,
        plural_form=1,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        rejected=True,
        plural_form=0,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        approved=False,
        fuzzy=False,
        rejected=True,
        plural_form=1,
    )
    assert (
        set(Entity.objects.filter(
            Entity.objects.rejected(locale_a)
        )) == {entities[1], entities[2]}
    )


@pytest.mark.django_db
def test_mgr_entity_filter_combined(resource_b, locale_b, user_a):
    """
    All filters should be joined by AND instead of OR.
    Tests filters against bug introduced by bug 1243115.
    """
    entities = [
        EntityFactory.create(
            resource=resource_b,
            string="testentity%s" % i,
        ) for i in range(0, 2)
    ]

    TranslationFactory.create(
        locale=locale_b,
        entity=entities[0],
        approved=True,
        fuzzy=False,
        user=user_a,
    )
    TranslationFactory.create(
        locale=locale_b,
        entity=entities[1],
        approved=True,
        fuzzy=False,
        user=user_a,
    )
    TranslationFactory.create(
        locale=locale_b,
        entity=entities[1],
        approved=False,
        fuzzy=False,
        user=user_a,
    )
    assert (
        list(Entity.for_project_locale(
            resource_b.project,
            locale_b,
            status='suggested',
            author=user_a.email,
        )) == []
    )
    assert (
        list(Entity.for_project_locale(
            resource_b.project,
            locale_b,
            status='suggested',
            time='201001010100-205001010100',
        )) == []
    )


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

    # list of of (index, entity) used in this test
    #
    # 0, First entity string
    # 1, Second entity string
    # 2, Third entity string with some twist: ZAŻÓŁĆ GĘŚLĄ
    # 3, Entity with first string
    # 4, First Entity
    # 5, First Entity with string
    # 6, Entity with quoted "string"

    assert search(u'e') == entities
    assert search(u'entity string') == [
        entities[i] for i in [0, 1, 2, 3, 5, 6]
    ]

    assert search(u'second entity') == [entities[1]]
    assert search(u'third entity') == [entities[2]]

    # Check if quoted queries use full string string and
    # unquoted use full text search
    assert search(u'first entity') == [entities[i] for i in [0, 3, 4, 5]]
    assert search(u'"first entity"') == [entities[i] for i in [0, 4, 5]]

    assert search(u'first entity string') == [entities[i] for i in [0, 3, 5]]
    assert search(u'"first entity" string') == [entities[0], entities[5]]
    assert search(u'"first entity string"') == [entities[0]]

    # Check if escaped quoted searches for quoted string
    assert search(r'entity \"string\"') == [entities[6]]

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
def test_lookup_collation(resource_a, locale_a):
    """
    Filter translations according to collation.
    """
    entity = EntityFactory.create(
        resource=resource_a,
        string="string",
    )
    entity_args = [
        {
            'string': u'First string',
            'comment': u'random Strıng',
        }, {
            'string': u'Second strİng',
            'comment': u'random string',
        }, {
            'string': u'Third Strıng',
            'comment': u'random strİng',
        },
    ]
    entities = [
        EntityFactory(
            resource=resource_a,
            string=x['string'],
            comment=x['comment'],
        ) for x in entity_args
    ]

    translation_args = [
        u'this is string',
        u'this is STRİNG',
        u'this is Strıng',
        u'this is StrInG',
        u'this is sTriNg'
    ]
    translations = [
        TranslationFactory(
            entity=entity,
            locale=locale_a,
            string=s,
        ) for s in translation_args
    ]

    # Check if 'Iı' and 'İi' are appropriately distinguished and filtered
    # according to turkish(tr_tr) collation
    assert (
        set(Entity.objects.filter(
            string__icontains_collate=(u'string', 'tr_tr')
        )) == set([entities[n] for n in [0, 1]] + [entity])
    )
    assert (
        set(Entity.objects.filter(
            comment__icontains_collate=(u'strİng', 'tr_tr')
        )) == set([entities[n] for n in [1, 2]])
    )
    assert (
        set(Translation.objects.filter(
            string__icontains_collate=(u'string', 'tr_tr')
        )) == set([translations[n] for n in [0, 1, 4]])
    )
    assert (
        set(Translation.objects.filter(
            string__icontains_collate=(u'string', 'tr_tr')
        )) == set([translations[n] for n in [0, 1, 4]])
    )
    assert (
        set(Translation.objects.filter(
            string__icontains_collate=(u'strİng', 'tr_tr')
        )) == set([translations[n] for n in [0, 1, 4]])
    )
    assert (
        set(Translation.objects.filter(
            string__icontains_collate=(u'strıng', 'tr_tr')
        )) == set([translations[n] for n in [2, 3]])
    )
    # Check if differentiation fails without any collation(C)
    assert (
        set(Translation.objects.filter(
            string__icontains_collate=(u'string', 'C')
        )) == set([translations[n] for n in [0, 3, 4]])
    )
    # Compare the icontains_collate query with regular i_contains query
    assert (
        list(Translation.objects.filter(
            string__icontains=u'string'
        )) == [translations[n] for n in [0, 2, 3, 4]]
    )
