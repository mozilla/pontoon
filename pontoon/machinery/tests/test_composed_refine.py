import json

from textwrap import dedent
from unittest.mock import MagicMock, patch

import pytest

from django.core.cache import cache
from django.urls import reverse

from pontoon.machinery.views import MAX_COMPOSED_LEAVES
from pontoon.test.factories import (
    EntityFactory,
    LocaleFactory,
    ResourceFactory,
    TermFactory,
    TranslationMemoryFactory,
)


@pytest.fixture
def fluent_resource(project_a):
    return ResourceFactory(project=project_a, path="resource.ftl", format="fluent")


def gpt_response(leaves):
    """A mocked structured-output completion returning `{id: text}` as JSON."""
    response = MagicMock()
    response.choices[0].message.content = json.dumps(
        {"leaves": [{"id": key, "text": text} for key, text in leaves.items()]}
    )
    return response


def refine(client, entity, locale, composed, **kwargs):
    params = {
        "entity_pk": str(entity.pk),
        "locale": locale.code,
        "characteristic": "formal",
        "value": json.dumps(composed.get("value", [])),
        "properties": json.dumps(composed.get("properties", {})),
        **kwargs,
    }
    return client.post(reverse("pontoon.openai_chatgpt_composed"), params)


@pytest.mark.django_db
def test_refine_not_logged_in(client, fluent_resource, locale_a, openai_api_key):
    entity = EntityFactory(resource=fluent_resource, string="key = Hello\n")
    response = refine(client, entity, locale_a, {"value": ["Zdravo"]})
    # `login_required(login_url="/403")` redirects rather than returning 403.
    assert response.status_code == 302


@pytest.mark.django_db
def test_refine_bad_request(member, fluent_resource, locale_a, openai_api_key):
    entity = EntityFactory(resource=fluent_resource, string="key = Hello\n")
    url = reverse("pontoon.openai_chatgpt_composed")

    response = member.client.post(
        url, {"locale": locale_a.code, "characteristic": "formal", "value": "[]"}
    )
    assert response.status_code == 400

    response = member.client.post(
        url,
        {
            "entity_pk": str(entity.pk),
            "locale": locale_a.code,
            "characteristic": "formal",
            "value": "not json",
        },
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_refine_label_and_accesskey(member, fluent_resource, locale_a, openai_api_key):
    """Every text leaf is refined in one call; the accesskey follows the label."""
    cache.clear()
    fluent_string = dedent(
        """\
        button =
            .label = Save file
            .accesskey = S
            .title = Saves the current file
        """
    )
    entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    composed = {
        "value": [],
        "properties": {
            "label": ["Shrani datoteko"],
            "accesskey": ["S"],
            "title": ["Shrani trenutno datoteko"],
        },
    }

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response(
            {".label": "Shranite datoteko", ".title": "Shranite trenutno datoteko"}
        )
        response = refine(member.client, entity, locale_a, composed)

    assert response.status_code == 200
    assert create.call_count == 1

    body = json.loads(response.content)
    assert body["properties"]["label"] == ["Shranite datoteko"]
    assert body["properties"]["title"] == ["Shranite trenutno datoteko"]
    # Derived from the refined label, not carried over from the input.
    assert body["properties"]["accesskey"] == ["S"]

    # The accesskey leaf is never sent to the model.
    parts = json.loads(
        create.call_args.kwargs["messages"][1]["content"].split("PARTS (JSON):\n")[1]
    )
    assert {part["id"] for part in parts} == {".label", ".title"}


@pytest.mark.django_db
def test_refine_pairs_each_part_with_its_english(
    member, fluent_resource, locale_a, openai_api_key
):
    """Each part carries the English of that part, not of the whole entry."""
    cache.clear()
    fluent_string = dedent(
        """\
        button = Click Me
            .title = Tooltip text
        """
    )
    entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response({"value": "A", ".title": "B"})
        refine(
            member.client,
            entity,
            locale_a,
            {"value": ["Kliknite"], "properties": {"title": ["Namig"]}},
        )

    parts = json.loads(
        create.call_args.kwargs["messages"][1]["content"].split("PARTS (JSON):\n")[1]
    )
    assert parts == [
        {"id": "value", "source": "Click Me", "current": "Kliknite"},
        {"id": ".title", "source": "Tooltip text", "current": "Namig"},
    ]


@pytest.mark.django_db
def test_refine_plural_variants_pair_with_source_catchall(
    member, fluent_resource, openai_api_key
):
    """Target categories the source lacks pair with the source's catchall."""
    cache.clear()
    locale = LocaleFactory(code="sl-test", name="Plural", cldr_plurals="1,2,3,5")
    fluent_string = dedent(
        """\
        popup =
            { $count ->
               *[other] { $count } popups.
            }
        """
    )
    entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    composed = {
        "value": {
            "decl": {"count": {"$": "count", "fn": "number"}},
            "sel": ["count"],
            "alt": [
                {"keys": ["one"], "pat": [{"$": "count"}, " pojavnih oken."]},
                {"keys": ["two"], "pat": [{"$": "count"}, " pojavnih oken."]},
                {"keys": ["few"], "pat": [{"$": "count"}, " pojavnih oken."]},
                {"keys": [{"*": "other"}], "pat": [{"$": "count"}, " pojavnih oken."]},
            ],
        },
        "properties": {},
    }

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response(
            {
                "value[one]": "{ $count } pojavno okno.",
                "value[two]": "{ $count } pojavni okni.",
                "value[few]": "{ $count } pojavna okna.",
                "value[other]": "{ $count } pojavnih oken.",
            }
        )
        response = refine(member.client, entity, locale, composed)

    assert response.status_code == 200
    assert create.call_count == 1

    parts = json.loads(
        create.call_args.kwargs["messages"][1]["content"].split("PARTS (JSON):\n")[1]
    )
    # All four target categories are sent, each against the source catchall.
    assert [part["id"] for part in parts] == [
        "value[one]",
        "value[two]",
        "value[few]",
        "value[other]",
    ]
    assert {part["source"] for part in parts} == {"{ $count } popups."}

    # Placeables come back as structured elements, not as literal text.
    body = json.loads(response.content)
    assert body["value"]["alt"][0]["pat"] == [{"$": "count"}, " pojavno okno."]
    assert body["value"]["alt"][3]["pat"] == [{"$": "count"}, " pojavnih oken."]


@pytest.mark.django_db
def test_refine_omitted_leaf_stays_unrefined(
    member, fluent_resource, locale_a, openai_api_key
):
    """A partial answer refines what it can rather than failing the entry."""
    cache.clear()
    fluent_string = dedent(
        """\
        button = Click Me
            .title = Tooltip text
        """
    )
    entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        # `title` omitted, plus an id that was never requested.
        create.return_value = gpt_response({"value": "Kliknite tukaj", "bogus": "X"})
        response = refine(
            member.client,
            entity,
            locale_a,
            {"value": ["Kliknite"], "properties": {"title": ["Namig"]}},
        )

    assert response.status_code == 200
    body = json.loads(response.content)
    assert body["value"] == ["Kliknite tukaj"]
    assert body["properties"] == {"title": ["Namig"]}


@pytest.mark.django_db
def test_refine_nothing_to_refine(member, fluent_resource, locale_a, openai_api_key):
    """A suggestion with no translatable text costs no API call."""
    cache.clear()
    entity = EntityFactory(resource=fluent_resource, string="key = { $var }\n")

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        response = refine(member.client, entity, locale_a, {"value": [{"$": "var"}]})

    assert response.status_code == 200
    assert json.loads(response.content) == {}
    assert create.call_count == 0


@pytest.mark.django_db
def test_refine_cache(member, fluent_resource, locale_a, openai_api_key):
    cache.clear()
    entity = EntityFactory(
        resource=fluent_resource, string="button = Click Me\n    .title = Tooltip\n"
    )
    composed = {"value": ["Kliknite"], "properties": {"title": ["Namig"]}}

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response({"value": "A", ".title": "B"})

        first = refine(member.client, entity, locale_a, composed)
        assert create.call_count == 1

        second = refine(member.client, entity, locale_a, composed)
        assert create.call_count == 1

    assert json.loads(first.content) == json.loads(second.content)


@pytest.mark.django_db
def test_refine_auto_requires_enabled_locale(
    member, fluent_resource, locale_a, openai_api_key, settings
):
    cache.clear()
    settings.OPENAI_AUTO_SUGGESTION_LOCALES = ["other-locale"]
    entity = EntityFactory(resource=fluent_resource, string="key = Hello\n")

    response = refine(
        member.client, entity, locale_a, {"value": ["Zdravo"]}, trigger="auto"
    )
    assert response.status_code == 403

    settings.OPENAI_AUTO_SUGGESTION_LOCALES = [locale_a.code]
    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        MockOpenAI.return_value.chat.completions.create.return_value = gpt_response(
            {"value": "Pozdravljeni"}
        )
        response = refine(
            member.client, entity, locale_a, {"value": ["Zdravo"]}, trigger="auto"
        )
    assert response.status_code == 200


@pytest.mark.django_db
def test_refine_invalid_trigger(member, fluent_resource, locale_a, openai_api_key):
    entity = EntityFactory(resource=fluent_resource, string="key = Hello\n")
    response = refine(
        member.client, entity, locale_a, {"value": ["Zdravo"]}, trigger="bogus"
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_refine_consumes_machinery_composed_output(
    member, fluent_resource, entity_a, locale_a, openai_api_key
):
    """The two are separate requests joined only by the client, so their
    `(value, properties)` shapes have to agree with no massaging in between."""
    cache.clear()
    fluent_string = dedent(
        """\
        button = Click Me
            .title = Tooltip text
        """
    )
    entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    TranslationMemoryFactory.create(
        entity=entity_a, source="Click Me", target="Kliknite", locale=locale_a
    )
    TranslationMemoryFactory.create(
        entity=entity_a, source="Tooltip text", target="Namig", locale=locale_a
    )

    composed = json.loads(
        member.client.get(
            reverse("pontoon.machinery_composed"),
            {
                "entity": str(entity.pk),
                "locale": locale_a.code,
                "service": "translation-memory",
            },
        ).content
    )

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response(
            {"value": "Kliknite tukaj", ".title": "Namig za gumb"}
        )
        response = member.client.post(
            reverse("pontoon.openai_chatgpt_composed"),
            {
                "entity_pk": str(entity.pk),
                "locale": locale_a.code,
                "characteristic": "formal",
                "value": json.dumps(composed["value"]),
                "properties": json.dumps(composed["properties"]),
            },
        )

    assert response.status_code == 200
    assert json.loads(response.content) == {
        "value": ["Kliknite tukaj"],
        "properties": {"title": ["Namig za gumb"]},
    }


def sent_parts(create):
    """The PARTS block of the prompt the model was given."""
    return json.loads(
        create.call_args.kwargs["messages"][1]["content"].split("PARTS (JSON):\n")[1]
    )


@pytest.mark.django_db
def test_refine_value_and_value_attribute_do_not_collide(
    member, fluent_resource, locale_a, openai_api_key
):
    """A Fluent entry can have both a value and a `.value` attribute."""
    cache.clear()
    fluent_string = dedent(
        """\
        sync-header = Sync your data
            .value = Sync
        """
    )
    entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response(
            {"value": "Sinhronizirajte podatke", ".value": "Sinhronizacija"}
        )
        response = refine(
            member.client,
            entity,
            locale_a,
            {"value": ["Sinhroniziraj"], "properties": {"value": ["Sinh"]}},
        )

    assert [part["id"] for part in sent_parts(create)] == ["value", ".value"]
    assert json.loads(response.content) == {
        "value": ["Sinhronizirajte podatke"],
        "properties": {"value": ["Sinhronizacija"]},
    }


@pytest.mark.django_db
def test_refine_skips_a_multi_line_leaf(
    member, fluent_resource, locale_a, openai_api_key
):
    """Fluent's inline form cannot express a line break, so it is not sent."""
    cache.clear()
    entity = EntityFactory(
        resource=fluent_resource,
        string="intro = First line\n    Second line\n    .title = Intro\n",
    )

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response({".title": "Uvod v program"})
        response = refine(
            member.client,
            entity,
            locale_a,
            {"value": ["Ena\nDve"], "properties": {"title": ["Uvod"]}},
        )

    assert [part["id"] for part in sent_parts(create)] == [".title"]
    body = json.loads(response.content)
    assert body["value"] == ["Ena\nDve"]
    assert body["properties"]["title"] == ["Uvod v program"]


@pytest.mark.django_db
def test_refine_skips_a_reply_with_a_line_break(
    member, fluent_resource, locale_a, openai_api_key
):
    cache.clear()
    entity = EntityFactory(
        resource=fluent_resource, string="button = Click Me\n    .title = Tip\n"
    )

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response(
            {"value": "Kliknite\n* tukaj", ".title": "Namig"}
        )
        response = refine(
            member.client,
            entity,
            locale_a,
            {"value": ["Klikni"], "properties": {"title": ["Nasvet"]}},
        )

    body = json.loads(response.content)
    assert body["value"] == ["Klikni"]
    assert body["properties"]["title"] == ["Namig"]


@pytest.mark.django_db
def test_refine_rejects_an_implausible_number_of_parts(
    member, fluent_resource, locale_a, openai_api_key
):
    """One prompt holds every part, so a client cannot inflate it without bound.

    Variants are the lever: a target selector yields one leaf per variant even
    when the source has a single pattern.
    """
    cache.clear()
    entity = EntityFactory(resource=fluent_resource, string="key = Value\n")
    value = {
        "decl": {"n": {"$": "n", "fn": "number"}},
        "sel": ["n"],
        "alt": [
            {"keys": [f"k{i}"], "pat": [f"Vrednost {i}"]}
            for i in range(MAX_COMPOSED_LEAVES + 1)
        ],
    }

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        response = member.client.post(
            reverse("pontoon.openai_chatgpt_composed"),
            {
                "entity_pk": str(entity.pk),
                "locale": locale_a.code,
                "characteristic": "formal",
                "value": json.dumps(value),
                "properties": "{}",
            },
        )

    assert response.status_code == 400
    assert create.call_count == 0


@pytest.mark.django_db
def test_refine_matches_terminology_against_the_leaf_text(
    member, fluent_resource, locale_a, openai_api_key
):
    """Not against `entity.string`, whose serialization includes the id and keys."""
    cache.clear()
    TermFactory.create(text="header", definition="a header")
    TermFactory.create(text="Sync", definition="to synchronise")
    entity = EntityFactory(
        resource=fluent_resource,
        string="sync-header = Sync your data\n    .title = Open settings\n",
    )

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response({"value": "A", ".title": "B"})
        refine(
            member.client,
            entity,
            locale_a,
            {"value": ["Sinhroniziraj"], "properties": {"title": ["Nastavitve"]}},
        )

    prompt = create.call_args.kwargs["messages"][1]["content"]
    assert '"Sync"' in prompt
    # `header` only appears in the message id, which is not translated text.
    assert '"header"' not in prompt


@pytest.mark.django_db
def test_refine_sends_and_reads_back_real_syntax(
    member, fluent_resource, locale_a, openai_api_key
):
    """Placeables go to the model as Fluent, and the reply is parsed like a TM match."""
    cache.clear()
    entity = EntityFactory(
        resource=fluent_resource,
        string="progress = { $count } of { $total }\n    .title = Progress\n",
    )
    composed = {
        "value": [{"$": "count"}, " od ", {"$": "total"}],
        "properties": {"title": ["Napredek"]},
    }

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response({"value": "{ $count } izmed { $total }"})
        response = refine(member.client, entity, locale_a, composed)

    value_part = next(p for p in sent_parts(create) if p["id"] == "value")
    assert value_part["source"] == "{ $count } of { $total }"
    assert value_part["current"] == "{ $count } od { $total }"

    assert json.loads(response.content)["value"] == [
        {"$": "count"},
        " izmed ",
        {"$": "total"},
    ]


@pytest.mark.django_db
def test_refine_keeps_a_leaf_whose_reply_does_not_parse(
    member, fluent_resource, locale_a, openai_api_key
):
    cache.clear()
    entity = EntityFactory(
        resource=fluent_resource,
        string="greet = Hello { $name }\n    .title = Greeting\n",
    )
    composed = {
        "value": ["Zdravo ", {"$": "name"}],
        "properties": {"title": ["Pozdrav"]},
    }

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response(
            {"value": "Pozdravljeni { $name", ".title": "Pozdravi"}
        )
        response = refine(member.client, entity, locale_a, composed)

    body = json.loads(response.content)
    assert body["value"] == ["Zdravo ", {"$": "name"}]
    assert body["properties"]["title"] == ["Pozdravi"]


@pytest.mark.django_db
def test_refine_a_non_fluent_leaf_whose_english_has_placeholders(
    member, project_a, locale_a, openai_api_key
):
    """The English is only shown, so its placeholders need no round trip.

    A webext source parses `$NAME$` into a placeholder while its Translation
    Memory match is plain text, which used to skip the leaf entirely.
    """
    cache.clear()
    resource = ResourceFactory(project=project_a, path="messages.json", format="webext")
    entity = EntityFactory(
        resource=resource,
        string="Hello $NAME$",
        key=["greet"],
    )
    entity.value = ["Hello ", {"$": "NAME", "attr": {"source": "$NAME$"}}]
    entity.properties = {"title": ["Greeting"]}
    entity.save()

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response({"value": "Pozdravljeni $NAME$"})
        response = refine(
            member.client,
            entity,
            locale_a,
            {"value": ["Zdravo $NAME$"], "properties": {"title": ["Pozdrav"]}},
        )

    value_part = next(p for p in sent_parts(create) if p["id"] == "value")
    assert value_part["source"] == "Hello $NAME$"
    assert json.loads(response.content)["value"] == ["Pozdravljeni $NAME$"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "reply",
    [
        "Pozdravljeni",  # dropped
        "{ $name }, { $name }!",  # repeated
        "Pozdravljeni { $ime }",  # renamed
        "Pozdravljeni { $name } { $count }",  # invented
    ],
)
def test_refine_rejects_a_reply_that_loses_a_placeable(
    member, fluent_resource, locale_a, openai_api_key, reply
):
    """Parsing says the reply is well-formed, not that it kept the variables."""
    cache.clear()
    entity = EntityFactory(
        resource=fluent_resource,
        string="greet = Hello { $name }\n    .title = Greeting\n",
    )
    composed = {
        "value": ["Zdravo ", {"$": "name"}],
        "properties": {"title": ["Pozdrav"]},
    }

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response({"value": reply, ".title": "Pozdravilo"})
        response = refine(member.client, entity, locale_a, composed)

    body = json.loads(response.content)
    assert body["value"] == ["Zdravo ", {"$": "name"}]
    # The leaf that kept its placeables is still refined.
    assert body["properties"]["title"] == ["Pozdravilo"]


@pytest.mark.django_db
def test_refine_allows_reordered_placeables(
    member, fluent_resource, locale_a, openai_api_key
):
    """Languages reorder variables, so only the multiset has to match."""
    cache.clear()
    entity = EntityFactory(
        resource=fluent_resource,
        string="progress = { $count } of { $total }\n    .title = Progress\n",
    )
    composed = {
        "value": [{"$": "count"}, " od ", {"$": "total"}],
        "properties": {"title": ["Napredek"]},
    }

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response({"value": "{ $total } za { $count }"})
        response = refine(member.client, entity, locale_a, composed)

    assert json.loads(response.content)["value"] == [
        {"$": "total"},
        " za ",
        {"$": "count"},
    ]


def test_placeables_survived_ignores_detail_the_syntax_drops():
    """A number-annotated variable serializes to plain `{ $count }`."""
    from moz.l10n.formats import Format
    from moz.l10n.message import message_from_json

    from pontoon.machinery.composed_refine import placeables_survived

    current = message_from_json([{"$": "count", "fn": "number"}, " oken"]).pattern
    refined = message_from_json([{"$": "count"}, " okno"]).pattern
    assert placeables_survived(refined, current, Format.fluent)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "reply",
    [
        "{ $count } oken",  # NUMBER() removed
        "{ DATETIME($count) } oken",  # function changed
        "{ NUMBER($count, minimumFractionDigits: 2) } oken",  # options added
    ],
)
def test_refine_rejects_a_reply_that_changes_a_function(
    member, fluent_resource, locale_a, openai_api_key, reply
):
    """`{ NUMBER($count) }` and `{ $count }` are not the same placeable."""
    cache.clear()
    entity = EntityFactory(
        resource=fluent_resource,
        string="popups = { NUMBER($count) } popups\n    .title = Popups\n",
    )
    composed = {
        "value": [
            {"$": "count", "fn": "number", "attr": {"fluent-fn": "NUMBER"}},
            " oken",
        ],
        "properties": {"title": ["Pojavna okna"]},
    }

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response({"value": reply, ".title": "Okna"})
        response = refine(member.client, entity, locale_a, composed)

    body = json.loads(response.content)
    assert body["value"] == [
        {"$": "count", "fn": "number", "attr": {"fluent-fn": "NUMBER"}},
        " oken",
    ]
    assert body["properties"]["title"] == ["Okna"]


@pytest.mark.django_db
def test_refine_rejects_a_reply_that_changes_a_term_option(
    member, fluent_resource, locale_a, openai_api_key
):
    cache.clear()
    entity = EntityFactory(
        resource=fluent_resource,
        string='install = Install { -brand(case: "acc") }\n    .title = Install\n',
    )
    term = {"_": "-brand", "fn": "message", "opt": {"case": "acc"}}
    composed = {
        "value": ["Namesti ", term],
        "properties": {"title": ["Namesti"]},
    }

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        create = MockOpenAI.return_value.chat.completions.create
        create.return_value = gpt_response(
            {"value": 'Namestite { -brand(case: "nom") }'}
        )
        response = refine(member.client, entity, locale_a, composed)

    assert json.loads(response.content)["value"] == ["Namesti ", term]
