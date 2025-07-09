from datetime import timedelta
from typing import Any

from moz.l10n.formats.mf2 import mf2_parse_message, mf2_serialize_message
from moz.l10n.model import (
    CatchallKey,
    Expression,
    Pattern,
    PatternMessage,
    SelectMessage,
    VariableRef,
)

from django.db import migrations
from django.db.models import Q
from django.utils import timezone


def escape(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    entities = Entity.objects.filter(resource__format="po", string_plural="").filter(
        Q(string__startswith=".")
        | Q(string__contains="\\")
        | Q(string__contains="{")
        | Q(string__contains="}")
    )
    for entity in entities:
        entity.string = mf2_serialize_message(PatternMessage([entity.string]))
    Entity.objects.bulk_update(entities, ["string"], batch_size=10_000)

    Translation = apps.get_model("base", "Translation")
    translations = Translation.objects.filter(entity__resource__format="po").filter(
        Q(string__startswith=".")
        | Q(string__contains="\\")
        | Q(string__contains="{")
        | Q(string__contains="}")
    )
    for trans in translations:
        trans.string = mf2_serialize_message(PatternMessage([trans.string]))
    Translation.objects.bulk_update(translations, ["string"], batch_size=10_000)


def plural_translations(apps: Any, schema_editor):
    ActionLog = apps.get_model("actionlog", "ActionLog")
    User = apps.get_model("auth", "User")
    Locale = apps.get_model("base", "Locale")
    Translation = apps.get_model("base", "Translation")

    plural_names = ["zero", "one", "two", "few", "many", "other"]
    plural_categories: dict[int, list[str]] = {
        id: [plural_names[int(pi)] for pi in plurals.split(",")]
        for id, plurals in Locale.objects.exclude(cldr_plurals="")
        .values_list("id", "cldr_plurals")
        .iterator()
    }

    # constants
    now = timezone.now()
    sync_user = User.objects.get(username="pontoon-sync")

    # internal vars
    prev_key = None
    plural_count = 0
    approved: list[Pattern] = []
    approved_tx: Any = None
    suggested: list[Pattern] = []
    suggested_tx: Any = None

    old_translations = (
        Translation.objects.filter(entity__resource__format="po", active=True)
        .exclude(entity__string_plural="")
        .order_by("entity_id", "locale_id", "plural_form")
    )

    # outputs
    new_translations: list[Any] = []
    actions: list[Any] = []

    def add_translation(tx: Any, patterns: list[Pattern]):
        try:
            plurals = plural_categories[tx.locale_id]
            msg = (
                SelectMessage(
                    declarations={"n": Expression(VariableRef("n"), "number")},
                    selectors=(VariableRef("n"),),
                    variants={
                        (
                            plurals[idx]
                            if idx < len(plurals) - 1
                            else CatchallKey(plurals[-1]),
                        ): pattern
                        for idx, pattern in enumerate(patterns)
                    },
                )
                if len(plurals) > 1
                else PatternMessage(patterns[0])
            )
            tx.string = mf2_serialize_message(msg)
        except Exception as err:
            raise ValueError(
                f"Serialization failed for {'approved' if tx.approved else 'suggested'} {tx.locale.code} translation of entity {tx.entity_id}"
            ) from err
        new_translations.append(tx)
        actions.append(
            ActionLog(
                action_type="translation:created",
                created_at=now,
                performed_by=sync_user,
                translation=tx,
            )
        )

    for t in old_translations:
        t_key = (t.entity_id, t.locale_id)
        t_date = t.date + timedelta(seconds=1)
        if t_key != prev_key:
            if prev_key is not None:
                if any(approved):
                    add_translation(approved_tx, approved)
                    if not all(approved):
                        suggested_tx.active = False
                        add_translation(suggested_tx, suggested)
                else:
                    suggested_tx.active = True
                    add_translation(suggested_tx, suggested)
            prev_key = t_key

            plural_count = (
                len(plural_categories[t.locale_id])
                if t.locale_id in plural_categories
                else 1
            )
            approved = [[] for _ in range(plural_count)]
            approved_tx = Translation(
                entity_id=t.entity_id,
                locale_id=t.locale_id,
                user_id=t.user_id,
                date=t_date,
                active=True,
                approved=True,
                approved_date=now,
            )
            suggested = [[] for _ in range(plural_count)]
            suggested_tx = Translation(
                entity_id=t.entity_id,
                locale_id=t.locale_id,
                user_id=t.user_id,
                date=t_date,
            )

        t_plural: int = t.plural_form or 0
        t_msg = mf2_parse_message(t.string)
        assert isinstance(t_msg, PatternMessage)
        if t.approved:
            if t_plural < plural_count:
                approved[t_plural] = t_msg.pattern
                if t_date > approved_tx.date:
                    approved_tx.date = t_date
                    approved_tx.user_id = t.user_id
            t.approved = False
            t.rejected = True
            t.rejected_date = now
            t.rejected_user = None
            actions.append(
                ActionLog(
                    action_type="translation:rejected",
                    created_at=now,
                    performed_by=sync_user,
                    translation=t,
                    is_implicit_action=True,
                )
            )
        if t_plural < plural_count:
            suggested[t_plural] = t_msg.pattern
            if t_date > suggested_tx.date:
                suggested_tx.date = t_date
                suggested_tx.user_id = t.user_id
            if t.fuzzy:
                suggested_tx.fuzzy = True
        t.active = False

    if any(approved):
        add_translation(approved_tx, approved)
        if not all(approved):
            suggested_tx.active = False
            add_translation(suggested_tx, suggested)
    elif suggested_tx is not None:
        suggested_tx.active = True
        add_translation(suggested_tx, suggested)

    Translation.objects.bulk_update(
        old_translations,
        ["active", "approved", "rejected", "rejected_date", "rejected_user"],
        batch_size=10_000,
    )
    Translation.objects.bulk_create(new_translations, batch_size=10_000)
    ActionLog.objects.bulk_create(actions)


def plural_entities(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    entities = Entity.objects.filter(resource__format="po").exclude(string_plural="")
    for e in entities:
        e.string = "".join(
            mf2_serialize_message(
                SelectMessage(
                    declarations={"n": Expression(VariableRef("n"), "number")},
                    selectors=(VariableRef("n"),),
                    variants={
                        ("one",): [e.string],
                        (CatchallKey(),): [e.string_plural],
                    },
                )
            )
        )
        e.string_plural = ""
    Entity.objects.bulk_update(entities, ["string", "string_plural"], batch_size=10_000)


def fix_nonplural_plural_form(apps, schema_editor):
    """
    De-activate and reject translations for gettext entities that
    were plural but have become non-plural since then.
    """
    Translation = apps.get_model("base", "Translation")
    translations = Translation.objects.filter(
        active=True, plural_form__isnull=False, entity__string_plural=""
    )
    for trans in translations:
        trans.active = False
        trans.fuzzy = False
        if trans.approved:
            trans.approved = False
            trans.rejected = True
            trans.rejected_date = timezone.now()
    Translation.objects.bulk_update(
        translations, ["active", "fuzzy", "approved", "rejected", "rejected_date"]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0081_fix_android_spaces"),
        ("sync", "0002_change_pontoon_sync_email"),
    ]
    operations = [
        migrations.RunPython(escape),
        migrations.RunPython(plural_translations),
        migrations.RunPython(plural_entities),
        migrations.RunPython(fix_nonplural_plural_form),
    ]
