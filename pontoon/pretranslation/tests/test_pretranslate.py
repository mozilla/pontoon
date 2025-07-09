from textwrap import dedent
from unittest.mock import patch

import pytest

from fluent.syntax import FluentParser, FluentSerializer

from pontoon.pretranslation.pretranslate import get_pretranslation
from pontoon.test.factories import (
    EntityFactory,
    ResourceFactory,
    TranslationMemoryFactory,
)


parser = FluentParser()
serializer = FluentSerializer()


@pytest.fixture
def fluent_resource(project_a):
    return ResourceFactory(project=project_a, path="resource.ftl", format="ftl")


@pytest.mark.django_db
def test_get_pretranslations_no_match(entity_a, locale_b):
    # 100% TM match does not exist and locale.google_translate_code is None
    with pytest.raises(ValueError):
        get_pretranslation(entity_a, locale_b)


@pytest.mark.django_db
def test_get_pretranslations_empty_string(entity_a, locale_b):
    # Entity.string is an empty string
    entity_a.string = ""
    response = get_pretranslation(entity_a, locale_b)
    assert response == ("", "tm")


@pytest.mark.django_db
def test_get_pretranslations_whitespace(entity_a, locale_b):
    # Entity.string is an empty string
    entity_a.string = " "
    response = get_pretranslation(entity_a, locale_b)
    assert response == (" ", "tm")

    entity_a.string = "\t"
    response = get_pretranslation(entity_a, locale_b)
    assert response == ("\t", "tm")

    entity_a.string = "\n"
    response = get_pretranslation(entity_a, locale_b)
    assert response == ("\n", "tm")


@pytest.mark.django_db
def test_get_pretranslations_tm_match(entity_a, entity_b, locale_b):
    # 100% TM match exists
    TranslationMemoryFactory.create(
        entity=entity_b,
        source=entity_a.string,
        target="tm_translation",
        locale=locale_b,
    )

    response = get_pretranslation(entity_a, locale_b)
    assert response == ("tm_translation", "tm")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_gt_match(gt_mock, entity_a, google_translate_locale):
    # 100% TM match does not exist and locale.google_translate_code is not None
    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    response = get_pretranslation(entity_a, google_translate_locale)
    assert response == ("gt_translation", "gt")


@pytest.mark.django_db
def test_get_pretranslations_fluent_no_match(fluent_resource, locale_b):
    # 100% TM match does not exist and locale.google_translate_code is None
    fluent_string = "hello-world = Hello World!"
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    with pytest.raises(ValueError):
        get_pretranslation(fluent_entity, locale_b)


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_simple(
    gt_mock, fluent_resource, google_translate_locale
):
    # Entity.string is a simple Fluent string
    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    fluent_string = "hello-world = Hello World!"
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)
    pretranslated_string = "hello-world = gt_translation\n"

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_empty(
    gt_mock, fluent_resource, google_translate_locale
):
    # Entity.string is an empty Fluent string
    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    fluent_string = 'hello-world = { "" }\n'
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (fluent_string, "tm")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_accesskeys_no_attribute_source(
    gt_mock, fluent_resource, google_translate_locale
):
    # Pretranslate accesskeys if the message has no value or required attributes
    input_string = dedent(
        """
        title =
            .foo = Bar
            .accesskey = B
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    expected = dedent(
        """
        title =
            .foo = gt_translation
            .accesskey = B
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_accesskeys_opt_out(
    gt_mock, fluent_resource, google_translate_locale
):
    # For locales that opt-out of accesskey localization, do not pretranslate them
    google_translate_locale.accesskey_localization = False
    input_string = dedent(
        """
        title =
            .foo = Bar
            .accesskey = B
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    expected = dedent(
        """
        title =
            .foo = gt_translation
            .accesskey = B
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_accesskeys_value(
    gt_mock, fluent_resource, google_translate_locale
):
    # Generate accesskeys if the message has a value
    input_string = dedent(
        """
        title = Title
            .accesskey = B
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    expected = dedent(
        """
        title = gt_translation
            .accesskey = g
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_accesskeys_label_attribute(
    gt_mock, fluent_resource, google_translate_locale
):
    # Generate accesskeys if the message has a label attribute
    input_string = dedent(
        """
        title = Title
            .label = Label
            .aria-label = Ignore this
            .value = Ignore this
            .accesskey = B
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    expected = dedent(
        """
        title = gt_translation
            .label = gt_translation
            .aria-label = gt_translation
            .value = gt_translation
            .accesskey = g
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_accesskeys_value_attribute(
    gt_mock, fluent_resource, google_translate_locale
):
    # Generate accesskeys if the message has a value attribute
    input_string = dedent(
        """
        title = Title
            .aria-label = Ignore this
            .value = Ignore this
            .accesskey = B
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    expected = dedent(
        """
        title = gt_translation
            .aria-label = gt_translation
            .value = gt_translation
            .accesskey = g
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_accesskeys_aria_label_attribute(
    gt_mock, fluent_resource, google_translate_locale
):
    # Generate accesskeys if the message has a aria-label attribute
    input_string = dedent(
        """
        title = Title
            .aria-label = Ignore this
            .accesskey = B
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    expected = dedent(
        """
        title = gt_translation
            .aria-label = gt_translation
            .accesskey = g
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_accesskeys_prefixed_label_attribute(
    gt_mock, fluent_resource, google_translate_locale
):
    # Generate accesskeys if the message has a prefixed label attribute
    input_string = dedent(
        """
        title = Title
            .buttonlabel = Ignore this
            .buttonaccesskey = B
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    expected = dedent(
        """
        title = gt_translation
            .buttonlabel = gt_translation
            .buttonaccesskey = g
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_accesskeys_ignore_placeables(
    gt_mock, fluent_resource, google_translate_locale
):
    # Ignore placeables whene generating accesskeys
    input_string = dedent(
        """
        title = Title
            .label = { $brand } string with placeables
            .accesskey = B
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    gt_mock.return_value = {
        "status": True,
        "translation": "{ $0 } gt_translation",
    }

    expected = dedent(
        """
        title = {$0} gt_translation
            .label = { $brand } gt_translation
            .accesskey = g
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_accesskeys_select_expression_source(
    gt_mock, fluent_resource, google_translate_locale
):
    # Generate accesskeys from SelectExpression source
    input_string = dedent(
        """
        title = Title
            .label =
                { PLATFORM() ->
                    [windows] Ctrl
                   *[other] Cmd
                }
            .accesskey = B
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    expected = dedent(
        """
        title = gt_translation
            .label =
                { PLATFORM() ->
                    [windows] gt_translation
                   *[other] gt_translation
                }
            .accesskey = g
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_accesskeys_select_expression_accesskey(
    gt_mock, fluent_resource, google_translate_locale
):
    # Generate accesskeys for each SelectExpression variant
    input_string = dedent(
        """
        title =
            .label = Settings
            .accesskey =
                { PLATFORM() ->
                    [windows] S
                    *[other] n
                }
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    expected = dedent(
        """
        title =
            .label = gt_translation
            .accesskey =
                { PLATFORM() ->
                    [windows] g
                    *[other] g
                }
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@pytest.mark.django_db
def test_get_pretranslations_fluent_accesskeys_select_expression_source_and_accesskey(
    fluent_resource, entity_a, google_translate_locale
):
    # Generate accesskeys for each SelectExpression variant
    input_string = dedent(
        """
        title =
            .label =
                { PLATFORM() ->
                    [windows] Options
                    *[other] Preferences
                }
            .accesskey =
                { PLATFORM() ->
                    [windows] O
                    *[other] P
                }
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Options",
        target="Možnosti",
        locale=google_translate_locale,
    )
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Preferences",
        target="Nastavitve",
        locale=google_translate_locale,
    )

    expected = dedent(
        """
        title =
            .label =
                { PLATFORM() ->
                    [windows] Možnosti
                    *[other] Nastavitve
                }
            .accesskey =
                { PLATFORM() ->
                    [windows] M
                    *[other] N
                }
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "tm")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_accesskeys_number_literal_source(
    gt_mock, fluent_resource, google_translate_locale
):
    # Generate accesskeys from SelectExpression source with variant keys of type NumberLiteral
    input_string = dedent(
        """
        title = Title
            .label =
                { $tabCount ->
                    [1] Add Tab to New Group
                   *[other] Add Tabs to New Group
                }
            .accesskey = G
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    google_translate_locale.cldr_plurals = "1,5"

    expected = dedent(
        """
        title = gt_translation
            .label =
                { $tabCount ->
                    [1] gt_translation
                    [one] gt_translation
                   *[other] gt_translation
                }
            .accesskey = g
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@pytest.mark.django_db
def test_get_pretranslations_fluent_multiline(fluent_resource, entity_b, locale_b):
    input_string = dedent(
        """
        multiline =
            Multi
            Line
            Message
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    # 100% TM match exists
    tm = TranslationMemoryFactory.create(
        entity=entity_b,
        source="Multi\nLine\nMessage",
        target="TM: Multi\nLine\nMessage",
        locale=locale_b,
    )

    expected = f"multiline = {tm.target}"

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, locale_b)
    assert response == (pretranslated_string, "tm")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_plural(
    gt_mock, fluent_resource, google_translate_locale
):
    # Various types of whitespace should be preserved
    gt_mock.return_value = {
        "status": True,
        "translation": "GT",
    }

    google_translate_locale.cldr_plurals = "1,2,3,5"

    input_string = dedent(
        """
        plural =
            { $count ->
                [0] No matches found.
                [one] One match found.
                *[other] { $count } matches found.
            }
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=input_string)

    expected = dedent(
        """
        plural =
            { $count ->
                [0] GT
                [one] GT
                [two] GT
                [few] GT
                *[other] GT
            }
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_complex(
    gt_mock, entity_a, fluent_resource, google_translate_locale
):
    # Entity.string is a complex Fluent string.
    # - Uplift selector and repeat shared parts within variants.
    # - Only translate text nodes.
    # - Service with most translated nodes is picked as translation author.
    gt_mock.return_value = {
        "status": True,
        "translation": "GT: Open Options and select Search.",
    }

    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Open Preferences and select Search.",
        target="TM: Open Preferences and select Search.",
        locale=google_translate_locale,
    )
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Open Settings and select Search.",
        target="TM: Open Settings and select Search.",
        locale=google_translate_locale,
    )

    fluent_string = dedent(
        """
        complex-entry =
            Open { PLATFORM() ->
                [mac] Preferences
                [win] Settings
                *[other] Options
            } and select Search.
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    expected = dedent(
        """
        complex-entry =
            { PLATFORM() ->
                [mac] TM: Open Preferences and select Search.
                [win] TM: Open Settings and select Search.
                *[other] GT: Open Options and select Search.
            }
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "tm")


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_pretranslations_fluent_placeholders(
    gt_mock, fluent_resource, google_translate_locale
):
    def gt_mock_fn(**kwargs):
        return {"status": True, "translation": f"GT: {kwargs['text']}"}

    gt_mock.side_effect = gt_mock_fn

    fluent_string = dedent(
        """
        batman = The { $dark } Knight
            .weapon = Brain and { -wayne-enterprise }
            .history = Lost { 2 } parents, has { 1 } "$alfred"
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    expected = dedent(
        """
        batman = GT: The { $dark } Knight
            .weapon = GT: Brain and { -wayne-enterprise }
            .history = GT: Lost { 2 } parents, has { 1 } "$alfred"
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "gt")
    assert [call[1]["text"] for call in gt_mock.call_args_list] == [
        "The {$0} Knight",
        "Brain and {$0}",
        'Lost {$0} parents, has {$1} "$alfred"',
    ]


@pytest.mark.django_db
def test_get_pretranslations_fluent_sibling_selectors(
    entity_a, fluent_resource, google_translate_locale
):
    # Entity.string is a Fluent string with two sibling selectors.
    # - Move any text outside selectors into selector variants.
    # - Keep leading/trailing whitespace outside selector variants.
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="{ $key_count } key and { $lock_count } lock",
        target="TM: { $key_count } key and { $lock_count } lock",
        locale=google_translate_locale,
    )
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="{ $key_count } key and { $lock_count } locks",
        target="TM: { $key_count } key and { $lock_count } locks",
        locale=google_translate_locale,
    )
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="{ $key_count } keys and { $lock_count } lock",
        target="TM: { $key_count } keys and { $lock_count } lock",
        locale=google_translate_locale,
    )
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="{ $key_count } keys and { $lock_count } locks",
        target="TM: { $key_count } keys and { $lock_count } locks",
        locale=google_translate_locale,
    )

    fluent_string = dedent(
        """
        sibling-selector =
            { $key_count ->
                [one] { $key_count } key
                *[other] { $key_count } keys
            } and { $lock_count ->
                [one] { $lock_count } lock
                *[other] { $lock_count } locks
            }
    """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    expected = dedent(
        """
        sibling-selector =
            { $key_count ->
                [one]
                    { $lock_count ->
                        [one] TM: { $key_count } key and { $lock_count } lock
                        *[other] TM: { $key_count } key and { $lock_count } locks
                    }
               *[other]
                    { $lock_count ->
                        [one] TM: { $key_count } keys and { $lock_count } lock
                        *[other] TM: { $key_count } keys and { $lock_count } locks
                    }
            }
    """
    )

    # Re-serialize to match whitespace
    pretranslated_string = serializer.serialize_entry(parser.parse_entry(expected))

    google_translate_locale.cldr_plurals = "1,5"
    response = get_pretranslation(fluent_entity, google_translate_locale)
    assert response == (pretranslated_string, "tm")
