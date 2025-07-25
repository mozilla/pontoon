import pytest

from pontoon.base.models import (
    Entity,
    TranslatedResource,
    Translation,
)
from pontoon.test.factories import (
    EntityFactory,
    ErrorFactory,
    TranslatedResourceFactory,
    TranslationFactory,
    WarningFactory,
)


@pytest.fixture
def entity_test_search(admin, resource_a, locale_a):
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
            "string": "First entity string",
            "comment": "random notes",
        },
        {
            "string": "Second entity string",
            "comment": "random",
        },
        {
            "string": "Third entity string with some twist: ZAŻÓŁĆ GĘŚLĄ",
            "comment": "even more random notes",
        },
        {
            "string": "Entity with first string",
            "comment": "random notes",
        },
        {
            "string": "First Entity",
            "comment": "random notes",
        },
        {
            "string": "First Entity with string",
            "comment": "random notes",
        },
        {
            "string": 'Entity with quoted "string"',
            "comment": "random notes",
        },
    ]
    entities = [
        EntityFactory(
            resource=resource_a,
            string=x["string"],
            comment=x["comment"],
            order=i,
        )
        for i, x in enumerate(entity_args)
    ]

    translation_args = [
        {"string": "First translation", "entity": entities[0]},
        {"string": "Second translation", "entity": entities[1]},
        {"string": "Third translation", "entity": entities[2]},
        {"string": "Fourth translation", "entity": entities[3]},
        {"string": "Fifth translation", "entity": entities[4]},
        {"string": "Sixth translation", "entity": entities[5]},
        {"string": "Seventh translation", "entity": entities[6]},
    ]
    for x in translation_args:
        TranslationFactory.create(
            locale=locale_a,
            string=x["string"],
            entity=x["entity"],
        )

    return (
        entities,
        lambda q: list(
            Entity.for_project_locale(
                admin,
                resource_a.project,
                locale_a,
                search=q,
            )
        ),
    )


@pytest.mark.django_db
def test_mgr_entity_filter_translated(resource_a, locale_a):
    entities = [
        EntityFactory.create(resource=resource_a, string="testentity%s" % i)
        for i in range(0, 3)
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
    assert set(
        Entity.objects.filter(Entity.objects.translated(locale_a, resource_a.project))
    ) == {entities[0], entities[2]}


@pytest.mark.django_db
def test_mgr_entity_filter_errors(resource_a, locale_a):
    entities = [
        EntityFactory.create(resource=resource_a, string="testentity%s" % i)
        for i in range(0, 3)
    ]

    translations = [
        TranslationFactory.create(
            locale=locale_a,
            entity=entities[i],
            approved=True,
        )
        for i in range(0, 3)
    ]

    ErrorFactory.create(translation=translations[0])
    ErrorFactory.create(translation=translations[2])

    assert set(Entity.objects.filter(Entity.objects.errors(locale_a))) == {
        entities[0],
        entities[2],
    }


@pytest.mark.django_db
def test_mgr_entity_filter_warnings(resource_a, locale_a):
    entities = [
        EntityFactory.create(resource=resource_a, string="testentity%s" % i)
        for i in range(0, 3)
    ]

    translations = [
        TranslationFactory.create(
            locale=locale_a,
            entity=entities[i],
            fuzzy=True,
        )
        for i in range(0, 3)
    ]

    WarningFactory.create(translation=translations[1])
    WarningFactory.create(translation=translations[2])
    TranslatedResource.objects.get(
        resource=translations[2].entity.resource,
        locale=translations[2].locale,
    ).calculate_stats()

    translations[2].fuzzy = False
    translations[2].save()

    assert set(Entity.objects.filter(Entity.objects.warnings(locale_a))) == {
        entities[1]
    }


@pytest.mark.django_db
def test_mgr_entity_filter_fuzzy(resource_a, locale_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
        )
        for i in range(0, 3)
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
    assert set(Entity.objects.filter(Entity.objects.fuzzy(locale_a))) == {
        entities[0],
        entities[2],
    }


@pytest.mark.django_db
def test_mgr_entity_filter_pretranslated(resource_a, locale_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
        )
        for i in range(0, 3)
    ]
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        pretranslated=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        pretranslated=True,
    )
    assert set(Entity.objects.filter(Entity.objects.pretranslated(locale_a))) == {
        entities[0],
        entities[2],
    }


@pytest.mark.django_db
def test_mgr_entity_filter_missing(resource_a, locale_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
        )
        for i in range(0, 3)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        approved=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        pretranslated=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
    )
    assert set(resource_a.entities.filter(Entity.objects.missing(locale_a))) == {
        entities[1]
    }


@pytest.mark.django_db
def test_mgr_entity_filter_unreviewed(resource_a, locale_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
        )
        for i in range(0, 3)
    ]
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        approved=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        fuzzy=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        string="translation for 1",
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        pretranslated=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        string="translation for 2",
    )
    assert set(Entity.objects.filter(Entity.objects.unreviewed(locale_a))) == {
        entities[1],
        entities[2],
    }


@pytest.mark.django_db
def test_mgr_entity_filter_unchanged(resource_a, locale_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="Unchanged string",
        )
        for i in range(0, 4)
    ]
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        active=True,
        approved=True,
        string="Unchanged string",
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        active=False,
        approved=True,
        string="Unchanged string",
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        active=True,
        fuzzy=True,
        string="Unchanged string",
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[3],
        active=True,
        pretranslated=True,
        string="Unchanged string",
    )
    assert set(Entity.objects.filter(Entity.objects.unchanged(locale_a))) == {
        entities[0],
        entities[2],
        entities[3],
    }


@pytest.mark.django_db
def test_mgr_entity_filter_rejected(resource_a, locale_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
        )
        for i in range(0, 3)
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
    assert set(Entity.objects.filter(Entity.objects.rejected(locale_a))) == {
        entities[0],
        entities[1],
    }


@pytest.mark.django_db
def test_mgr_entity_filter_missing_without_unreviewed(resource_a, locale_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
        )
        for i in range(0, 5)
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
        approved=False,
        fuzzy=False,
        rejected=True,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[2],
        approved=True,
        fuzzy=False,
        rejected=False,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[3],
        approved=False,
        fuzzy=True,
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
        entity=entities[1],
        approved=False,
        fuzzy=False,
        rejected=False,
    )

    assert set(
        resource_a.entities.filter(Entity.objects.missing_without_unreviewed(locale_a))
    ) == {entities[0], entities[4]}


@pytest.mark.django_db
def test_mgr_entity_filter_combined(admin, resource_a, locale_a, user_a):
    """
    All filters should be joined by AND instead of OR.
    Tests filters against bug introduced by bug 1243115.
    """
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="testentity%s" % i,
        )
        for i in range(0, 2)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        approved=True,
        user=user_a,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        fuzzy=True,
        user=user_a,
    )
    assert (
        list(
            Entity.for_project_locale(
                admin,
                resource_a.project,
                locale_a,
                status="unreviewed",
                author=user_a.email,
            )
        )
        == []
    )
    assert (
        list(
            Entity.for_project_locale(
                admin,
                resource_a.project,
                locale_a,
                status="unreviewed",
                time="201001010100-205001010100",
            )
        )
        == []
    )


@pytest.mark.django_db
def test_mgr_entity_option_match_case(admin, resource_a, locale_a, user_a):
    entities = [
        EntityFactory.create(
            key=["key %s" % i],
            resource=resource_a,
            string="TestEntity%s" % i,
        )
        for i in range(0, 2)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        rejected=True,
        user=user_a,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=True,
        user=user_a,
    )

    args = [admin, resource_a.project, locale_a]
    kwargs = {"search": "testentity", "author": user_a.email}

    # Base case
    assert list(
        Entity.for_project_locale(
            *args,
            **kwargs,
        )
    ) == [entities[i] for i in range(0, 2)]

    # Test search_match_case
    kwargs["search_match_case"] = True
    assert (
        list(
            Entity.for_project_locale(
                *args,
                **kwargs,
            )
        )
        == []
    )


@pytest.mark.django_db
def test_mgr_entity_option_match_whole_word(admin, resource_a, locale_a, user_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="TestEntity%s" % i,
        )
        for i in range(0, 2)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        rejected=True,
        user=user_a,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=True,
        user=user_a,
    )

    args = [admin, resource_a.project, locale_a]
    kwargs = {"search": "TestEntity", "author": user_a.email}

    # Base case
    assert list(
        Entity.for_project_locale(
            *args,
            **kwargs,
        )
    ) == [entities[i] for i in range(0, 2)]

    kwargs["search_match_whole_word"] = True
    # Test search_match_whole_word
    assert (
        list(
            Entity.for_project_locale(
                admin,
                resource_a.project,
                locale_a,
                search="TestEntity",
                search_match_whole_word=True,
                author=user_a.email,
            )
        )
        == []
    )


@pytest.mark.django_db
def test_mgr_entity_option_identifiers(admin, resource_a, locale_a, user_a):
    entities = [
        EntityFactory.create(
            key=["key %s" % i],
            resource=resource_a,
            string="TestEntity%s" % i,
        )
        for i in range(0, 2)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        rejected=True,
        user=user_a,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=True,
        user=user_a,
    )

    args = [admin, resource_a.project, locale_a]
    kwargs = {"search": "key", "author": user_a.email}

    # Base case
    assert (
        list(
            Entity.for_project_locale(
                *args,
                **kwargs,
            )
        )
        == []
    )

    kwargs["search_identifiers"] = True
    # Test search_identifiers
    assert list(
        Entity.for_project_locale(
            *args,
            **kwargs,
        )
    ) == [entities[i] for i in range(0, 2)]


@pytest.mark.django_db
def test_mgr_entity_option_rejected_translations(admin, resource_a, locale_a, user_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="TestEntity%s" % i,
        )
        for i in range(0, 2)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        rejected=True,
        string="TestString",
        user=user_a,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=True,
        string="TestString",
        user=user_a,
    )

    args = [admin, resource_a.project, locale_a]
    kwargs = {"search": "TestString", "author": user_a.email}

    # Base case
    assert list(
        Entity.for_project_locale(
            *args,
            **kwargs,
        )
    ) == [entities[1]]

    kwargs["search_rejected_translations"] = True
    # Test search_rejected_translations
    assert list(
        Entity.for_project_locale(
            *args,
            **kwargs,
        )
    ) == [entities[i] for i in range(0, 2)]


@pytest.mark.django_db
def test_mgr_entity_option_exclude_source_strings(admin, resource_a, locale_a, user_a):
    entities = [
        EntityFactory.create(
            resource=resource_a,
            string="TestEntity%s" % i,
        )
        for i in range(0, 2)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        rejected=True,
        user=user_a,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=True,
        user=user_a,
    )

    args = [admin, resource_a.project, locale_a]
    kwargs = {"search": "TestEntity", "author": user_a.email}

    # Base case
    assert list(
        Entity.for_project_locale(
            *args,
            **kwargs,
        )
    ) == [entities[i] for i in range(0, 2)]

    kwargs["search_exclude_source_strings"] = True
    # Test search_exclude_source_strings
    assert (
        list(
            Entity.for_project_locale(
                *args,
                **kwargs,
            )
        )
        == []
    )


@pytest.mark.django_db
def test_mgr_entity_option_combined(admin, resource_a, locale_a, user_a):
    """
    Test combinations of filters
    """

    entities = [
        EntityFactory.create(
            key=["key %s" % i],
            resource=resource_a,
            string="TestEntity%s" % i,
        )
        for i in range(0, 2)
    ]

    TranslationFactory.create(
        locale=locale_a,
        entity=entities[0],
        rejected=True,
        string="Translation 0",
        user=user_a,
    )
    TranslationFactory.create(
        locale=locale_a,
        entity=entities[1],
        approved=True,
        string="Translation 1",
        user=user_a,
    )

    args = [admin, resource_a.project, locale_a]
    kwargs = {}

    # Base case
    kwargs = {
        "search": "",
        "author": user_a.email,
    }
    assert list(
        Entity.for_project_locale(
            *args,
            **kwargs,
        )
    ) == [entities[i] for i in range(0, 2)]

    # Test exclude_source_strings with identifiers
    kwargs = {
        "search": "key",
        "search_exclude_source_strings": True,
        "search_identifiers": True,
        "author": user_a.email,
    }
    assert list(
        Entity.for_project_locale(
            *args,
            **kwargs,
        )
    ) == [entities[i] for i in range(0, 2)]

    # Test identifiers with match_whole_word
    kwargs = {
        "search": "key",
        "search_match_whole_word": True,
        "search_identifiers": True,
        "author": user_a.email,
    }
    assert list(
        Entity.for_project_locale(
            *args,
            **kwargs,
        )
    ) == [entities[i] for i in range(0, 2)]

    # Test match_case with match_whole_word
    kwargs = {
        "search": "translation",
        "search_match_case": True,
        "search_match_whole_word": True,
        "author": user_a.email,
    }
    assert (
        list(
            Entity.for_project_locale(
                *args,
                **kwargs,
            )
        )
        == []
    )

    # Test all options at once
    kwargs = {
        "search": "Translation",
        "search_match_case": True,
        "search_match_whole_word": True,
        "search_identifiers": True,
        "search_rejected_translations": True,
        "search_exclude_source_strings": True,
        "author": user_a.email,
    }
    assert list(
        Entity.for_project_locale(
            *args,
            **kwargs,
        )
    ) == [entities[i] for i in range(0, 2)]


@pytest.mark.django_db
def test_mgr_entity_search_invalid_query(entity_test_search):
    """
    We shouldn't return any records if there aren't any matching rows.
    """
    entities, search = entity_test_search

    assert search("localization") == []
    assert search("testing search queries") == []
    assert search("Ń") == []


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

    assert search("e") == entities
    assert search("entity string") == [entities[i] for i in [0, 1, 2, 3, 5, 6]]

    assert search("second entity") == [entities[1]]
    assert search("third entity") == [entities[2]]

    # Check if quoted queries use full string string and
    # unquoted use full text search
    assert search("first entity") == [entities[i] for i in [0, 3, 4, 5]]
    assert search('"first entity"') == [entities[i] for i in [0, 4, 5]]

    assert search("first entity string") == [entities[i] for i in [0, 3, 5]]
    assert search('"first entity" string') == [entities[0], entities[5]]
    assert search('"first entity string"') == [entities[0]]

    # Check if escaped quoted searches for quoted string
    assert search(r"entity \"string\"") == [entities[6]]

    # Check if we're able search by unicode characters.
    assert search("gęślą") == [entities[2]]


@pytest.mark.django_db
def test_mgr_entity_search_translation(entity_test_search):
    """
    Search entities by contents of their translations.
    """
    entities, search = entity_test_search

    assert search("translation") == entities
    assert search("first translation") == [entities[0]]
    assert search("second translation") == [entities[1]]
    assert search("third translation") == [entities[2]]


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
        {"string": "First string", "comment": "random Strıng"},
        {"string": "Second strİng", "comment": "random string"},
        {"string": "Third Strıng", "comment": "random strİng"},
    ]
    entities = [
        EntityFactory(
            resource=resource_a,
            string=x["string"],
            comment=x["comment"],
        )
        for x in entity_args
    ]

    translation_args = [
        "this is string",
        "this is STRİNG",
        "this is Strıng",
        "this is StrInG",
        "this is sTriNg",
    ]
    translations = [
        TranslationFactory(
            entity=entity,
            locale=locale_a,
            string=s,
        )
        for s in translation_args
    ]

    # Check if 'Iı' and 'İi' are appropriately distinguished and filtered
    # according to Turkish (tr) collation
    assert set(
        resource_a.entities.filter(string__icontains_collate=("string", "tr-x-icu"))
    ) == set([entities[n] for n in [0, 1]] + [entity])
    assert set(
        resource_a.entities.filter(comment__icontains_collate=("strİng", "tr-x-icu"))
    ) == {entities[n] for n in [1, 2]}
    assert set(
        Translation.objects.filter(string__icontains_collate=("string", "tr-x-icu"))
    ) == {translations[n] for n in [0, 1, 4]}
    assert set(
        Translation.objects.filter(string__icontains_collate=("string", "tr-x-icu"))
    ) == {translations[n] for n in [0, 1, 4]}
    assert set(
        Translation.objects.filter(string__icontains_collate=("strİng", "tr-x-icu"))
    ) == {translations[n] for n in [0, 1, 4]}
    assert set(
        Translation.objects.filter(string__icontains_collate=("strıng", "tr-x-icu"))
    ) == {translations[n] for n in [2, 3]}
    # Check if differentiation fails without any collation(C)
    assert set(
        Translation.objects.filter(string__icontains_collate=("string", "C"))
    ) == {translations[n] for n in [0, 3, 4]}
    # Compare the icontains_collate query with regular i_contains query
    assert set(Translation.objects.filter(string__icontains="string")) == {
        translations[n] for n in [0, 2, 3, 4]
    }
