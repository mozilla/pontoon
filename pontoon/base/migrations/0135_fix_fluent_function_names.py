import logging

from moz.l10n.formats.fluent import fluent_parse_entry
from moz.l10n.message import message_to_json

from django.db import migrations


log = logging.getLogger(__name__)

# Matches a Fluent function reference, i.e. the `{ SHORTDATE(` in `{ SHORTDATE($date) }`,
# following the Fluent grammar for a function identifier. The only other callable
# construct, a parameterized term reference like `{ -brand-name(case: "genitive") }`,
# is kept out by its leading `-`.
FLUENT_FUNCTION_REF = r"\{\s*[A-Z][A-Z0-9_-]*\("

BATCH_SIZE = 1000


def reparse(model, rows):
    batch = []
    for row in rows:
        try:
            entry = fluent_parse_entry(row.string)
        except Exception as error:
            # A value can only be rebuilt from a string that the parser accepts.
            # Skipping is better than failing the migration, as the rows left
            # behind are no worse off than before.
            log.warning(f"Skipping {model.__name__} {row.id}: {error}")
            continue
        value = message_to_json(entry.value)
        properties = {
            name: message_to_json(prop) for name, prop in entry.properties.items()
        } or None
        if value != row.value or properties != row.properties:
            row.value = value
            row.properties = properties
            batch.append(row)
            if len(batch) == BATCH_SIZE:
                model.objects.bulk_update(batch, ["value", "properties"])
                batch = []
    if batch:
        model.objects.bulk_update(batch, ["value", "properties"])


def fix_fluent_function_names(apps, schema_editor):
    """
    Re-parse Fluent messages that include a function reference.

    Until moz.l10n 0.13, the Fluent function name of an expression was recovered
    on serialization by upper-casing its data model function name. Since then it
    is retained as a `fluent-fn` attribute, and serializing an expression that
    lacks one fails. Values stored before the update have no such attribute, so
    they render as a broken placeholder and are re-imported on the next sync.

    `0122_reparse_multi_pattern_fluent` covered this for messages with selectors,
    which is all it needed to look at for its own purposes, but function
    references also appear in messages with none. Catch those here.
    """
    Entity = apps.get_model("base", "Entity")
    Translation = apps.get_model("base", "Translation")

    reparse(
        Entity,
        Entity.objects.filter(
            resource__format="fluent", string__regex=FLUENT_FUNCTION_REF
        ).iterator(chunk_size=BATCH_SIZE),
    )
    reparse(
        Translation,
        Translation.objects.filter(
            entity__resource__format="fluent", string__regex=FLUENT_FUNCTION_REF
        ).iterator(chunk_size=BATCH_SIZE),
    )


class Migration(migrations.Migration):
    dependencies = [("base", "0134_alter_locale_google_translate_code")]

    operations = [
        migrations.RunPython(
            fix_fluent_function_names, reverse_code=migrations.RunPython.noop
        ),
    ]
