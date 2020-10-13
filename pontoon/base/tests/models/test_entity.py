import pytest

from pontoon.base.models import Entity, Project
from pontoon.test.factories import (
    EntityFactory,
    ResourceFactory,
    SubpageFactory,
    TermFactory,
    TranslationFactory,
)
from pontoon.sync import KEY_SEPARATOR


@pytest.fixture
def entity_test_models(translation_a, locale_b):
    """This fixture provides:

    - 2 translations of a plural entity
    - 1 translation of a non-plural entity
    - A subpage that contains the plural entity
    """

    entity_a = translation_a.entity
    locale_a = translation_a.locale
    project_a = entity_a.resource.project

    locale_a.cldr_plurals = "0,1"
    locale_a.save()
    translation_a.plural_form = 0
    translation_a.active = True
    translation_a.save()
    resourceX = ResourceFactory(project=project_a, path="resourceX.po",)
    entity_a.string = "Entity zero"
    entity_a.key = entity_a.string
    entity_a.string_plural = "Plural %s" % entity_a.string
    entity_a.order = 0
    entity_a.save()
    entity_b = EntityFactory(
        resource=resourceX,
        string="entity_b",
        key="Key%sentity_b" % KEY_SEPARATOR,
        order=0,
    )
    translation_a_pl = TranslationFactory(
        entity=entity_a,
        locale=locale_a,
        plural_form=1,
        active=True,
        string="Plural %s" % translation_a.string,
    )
    translationX = TranslationFactory(
        entity=entity_b,
        locale=locale_a,
        active=True,
        string="Translation %s" % entity_b.string,
    )
    subpageX = SubpageFactory(project=project_a, name="Subpage",)
    subpageX.resources.add(entity_a.resource)
    return translation_a, translation_a_pl, translationX, subpageX


@pytest.fixture
def translation_b(translation_a):
    """
    This fixture provides a secondary translation
    for translation_a's entity.
    """
    translation_b = TranslationFactory(
        entity=translation_a.entity,
        locale=translation_a.locale,
        string="Translation B for entity_a",
    )
    translation_b.locale.refresh_from_db()
    translation_b.entity.resource.project.refresh_from_db()
    return translation_b


@pytest.mark.django_db
def test_reset_active_translation_single_unreviewed(translation_a):
    """
    Test if active translations gets set properly for an entity
    with a single unreviewed translation.
    """
    entity = translation_a.entity
    locale = translation_a.locale

    assert entity.reset_active_translation(locale) == translation_a


@pytest.mark.django_db
def test_reset_active_translation_single_approved(translation_a):
    """
    Test if active translations gets set properly for an entity
    with a single approved translation.
    """
    entity = translation_a.entity
    locale = translation_a.locale

    translation_a.approved = True
    translation_a.save()

    assert entity.reset_active_translation(locale) == translation_a


@pytest.mark.django_db
def test_reset_active_translation_single_fuzzy(translation_a):
    """
    Test if active translations gets set properly for an entity
    with a single fuzzy translation.
    """
    entity = translation_a.entity
    locale = translation_a.locale

    translation_a.fuzzy = True
    translation_a.save()

    assert entity.reset_active_translation(locale) == translation_a


@pytest.mark.django_db
def test_reset_active_translation_single_rejected(translation_a):
    """
    Test if active translations gets set properly for an entity
    with a single rejected translation.
    """
    entity = translation_a.entity
    locale = translation_a.locale

    translation_a.rejected = True
    translation_a.save()

    assert entity.reset_active_translation(locale).pk is None


@pytest.mark.django_db
def test_reset_active_translation_two_unreviewed(
    translation_a, translation_b,
):
    """
    Test if active translations gets set properly for an entity
    with two unreviewed translations.
    """
    entity = translation_a.entity
    locale = translation_a.locale

    assert entity.reset_active_translation(locale) == translation_b


@pytest.mark.django_db
def test_reset_active_translation_unreviewed_and_approved(
    translation_a, translation_b,
):
    """
    Test if active translations gets set properly for an entity
    with an unreviewed and approved translation.
    """
    entity = translation_a.entity
    locale = translation_a.locale

    translation_b.approved = True
    translation_b.save()

    assert entity.reset_active_translation(locale) == translation_b


@pytest.mark.django_db
def test_reset_active_translation_fuzzy_and_unreviewed(
    translation_a, translation_b,
):
    """
    Test if active translations gets set properly for an entity
    with a fuzzy and unreviewed translation.
    """
    entity = translation_a.entity
    locale = translation_a.locale

    translation_a.fuzzy = True
    translation_a.save()

    assert entity.reset_active_translation(locale) == translation_a


@pytest.mark.django_db
def test_reset_term_translation(locale_a):
    """
    Test if TermTranslation gets properly updated when translation
    in the "Terminology" project changes.
    """
    project, _ = Project.objects.get_or_create(slug="terminology")
    entity = EntityFactory.create(resource=project.resources.first())

    term = TermFactory.create()
    entity.term = term

    # No approved Translations of an Entity: no TermTranslation
    TranslationFactory.create(locale=locale_a, entity=entity)
    entity.reset_term_translation(locale_a)
    assert entity.term.translations.filter(locale=locale_a).count() == 0

    # First approved Translation of an Entity added: create TermTranslation to match the Translation
    translation_approved = TranslationFactory.create(
        locale=locale_a, entity=entity, approved=True
    )
    entity.reset_term_translation(locale_a)
    assert entity.term.translations.filter(locale=locale_a).count() == 1
    assert (
        entity.term.translations.get(locale=locale_a).text
        == translation_approved.string
    )

    # Another approved Translation of an Entity added: update TermTranslation to match the Translation
    translation_approved_2 = TranslationFactory.create(
        locale=locale_a, entity=entity, approved=True
    )
    entity.reset_term_translation(locale_a)
    assert entity.term.translations.filter(locale=locale_a).count() == 1
    assert (
        entity.term.translations.get(locale=locale_a).text
        == translation_approved_2.string
    )


@pytest.mark.django_db
def test_entity_project_locale_filter(admin, entity_test_models, locale_b, project_b):
    """
    Evaluate entities filtering by locale, project, obsolete.
    """
    tr0, tr0pl, trX, subpageX = entity_test_models
    locale_a = tr0.locale
    resource0 = tr0.entity.resource
    project_a = tr0.entity.resource.project
    EntityFactory.create(
        obsolete=True, resource=resource0, string="Obsolete String",
    )
    assert len(Entity.for_project_locale(admin, project_a, locale_b)) == 0
    assert len(Entity.for_project_locale(admin, project_b, locale_a)) == 0
    assert len(Entity.for_project_locale(admin, project_a, locale_a)) == 2


@pytest.mark.django_db
def test_entity_project_locale_no_paths(
    admin, entity_test_models, locale_b, project_b,
):
    """
    If paths not specified, return all project entities along with their
    translations for locale.
    """
    tr0, tr0pl, trX, subpageX = entity_test_models
    locale_a = tr0.locale
    preferred_source_locale = ""
    entity_a = tr0.entity
    resource0 = tr0.entity.resource
    project_a = tr0.entity.resource.project
    entities = Entity.map_entities(
        locale_a,
        preferred_source_locale,
        Entity.for_project_locale(admin, project_a, locale_a),
    )
    assert len(entities) == 2
    assert entities[0]["path"] == resource0.path
    assert entities[0]["original"] == entity_a.string
    assert entities[0]["translation"][0]["string"] == tr0.string
    assert entities[1]["path"] == trX.entity.resource.path
    assert entities[1]["original"] == trX.entity.string
    assert entities[1]["translation"][0]["string"] == trX.string

    # Ensure all attributes are assigned correctly
    expected = {
        "comment": "",
        "group_comment": "",
        "resource_comment": "",
        "format": "po",
        "obsolete": False,
        "key": "",
        "path": str(resource0.path),
        "project": project_a.serialize(),
        "translation": [
            {
                "pk": tr0.pk,
                "fuzzy": False,
                "string": str(tr0.string),
                "approved": False,
                "rejected": False,
                "warnings": [],
                "errors": [],
            },
            {
                "pk": tr0pl.pk,
                "fuzzy": False,
                "string": str(tr0pl.string),
                "approved": False,
                "rejected": False,
                "warnings": [],
                "errors": [],
            },
        ],
        "order": 0,
        "source": [],
        "original_plural": str(entity_a.string_plural),
        "pk": entity_a.pk,
        "original": str(entity_a.string),
        "machinery_original": str(entity_a.string),
        "readonly": False,
        "visible": False,
    }
    assert entities[0] == expected


@pytest.mark.django_db
def test_entity_project_locale_paths(admin, entity_test_models):
    """
    If paths specified, return project entities from these paths only along
    with their translations for locale.
    """
    tr0, tr0pl, trX, subpageX = entity_test_models
    locale_a = tr0.locale
    preferred_source_locale = ""
    project_a = tr0.entity.resource.project
    paths = ["resourceX.po"]
    entities = Entity.map_entities(
        locale_a,
        preferred_source_locale,
        Entity.for_project_locale(admin, project_a, locale_a, paths,),
    )
    assert len(entities) == 1
    assert entities[0]["path"] == trX.entity.resource.path
    assert entities[0]["original"] == trX.entity.string
    assert entities[0]["translation"][0]["string"] == trX.string


@pytest.mark.django_db
def test_entity_project_locale_subpages(admin, entity_test_models):
    """
    If paths specified as subpages, return project entities from paths
    assigned to these subpages only along with their translations for
    locale.
    """
    tr0 = entity_test_models[0]
    subpageX = entity_test_models[3]
    locale_a = tr0.locale
    preferred_source_locale = ""
    entity_a = tr0.entity
    resource0 = tr0.entity.resource
    project_a = tr0.entity.resource.project
    subpages = [subpageX.name]
    entities = Entity.map_entities(
        locale_a,
        preferred_source_locale,
        Entity.for_project_locale(admin, project_a, locale_a, subpages,),
    )
    assert len(entities) == 1
    assert entities[0]["path"] == resource0.path
    assert entities[0]["original"] == entity_a.string
    assert entities[0]["translation"][0]["string"] == tr0.string


@pytest.mark.django_db
def test_entity_project_locale_plurals(
    admin, entity_test_models, locale_b, project_b,
):
    """
    For pluralized strings, return all available plural forms.
    """
    tr0, tr0pl, trX, subpageX = entity_test_models
    locale_a = tr0.locale
    preferred_source_locale = ""
    entity_a = tr0.entity
    project_a = tr0.entity.resource.project
    entities = Entity.map_entities(
        locale_a,
        preferred_source_locale,
        Entity.for_project_locale(admin, project_a, locale_a,),
    )
    assert entities[0]["original"] == entity_a.string
    assert entities[0]["original_plural"] == entity_a.string_plural
    assert entities[0]["translation"][0]["string"] == tr0.string
    assert entities[0]["translation"][1]["string"] == tr0pl.string


@pytest.mark.django_db
def test_entity_project_locale_order(admin, entity_test_models):
    """
    Return entities in correct order.
    """
    resource0 = entity_test_models[0].entity.resource
    locale_a = entity_test_models[0].locale
    preferred_source_locale = ""
    project_a = resource0.project
    EntityFactory.create(
        order=2, resource=resource0, string="Second String",
    )
    EntityFactory.create(
        order=1, resource=resource0, string="First String",
    )
    entities = Entity.map_entities(
        locale_a,
        preferred_source_locale,
        Entity.for_project_locale(admin, project_a, locale_a,),
    )
    assert entities[1]["original"] == "First String"
    assert entities[2]["original"] == "Second String"


@pytest.mark.django_db
def test_entity_project_locale_cleaned_key(admin, entity_test_models):
    """
    If key contanis source string and Translate Toolkit separator,
    remove them.
    """
    resource0 = entity_test_models[0].entity.resource
    locale_a = entity_test_models[0].locale
    preferred_source_locale = ""
    project_a = resource0.project
    entities = Entity.map_entities(
        locale_a,
        preferred_source_locale,
        Entity.for_project_locale(admin, project_a, locale_a,),
    )
    assert entities[0]["key"] == ""
    assert entities[1]["key"] == "Key"


@pytest.mark.django_db
def test_entity_project_locale_tags(admin, entity_a, locale_a, tag_a):
    """ Test filtering of tags in for_project_locale
    """
    resource = entity_a.resource
    project = resource.project
    entities = Entity.for_project_locale(admin, project, locale_a, tag=tag_a.slug,)
    assert entity_a in entities

    # remove the resource <> tag association
    resource.tag_set.remove(tag_a)

    entities = Entity.for_project_locale(admin, project, locale_a, tag=tag_a.slug,)
    assert entity_a not in entities
