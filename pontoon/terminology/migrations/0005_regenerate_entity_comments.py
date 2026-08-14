from django.db import migrations


def upper_first_letter(text):
    return text[:1].upper() + text[1:]


def entity_comment(term):
    comment = "{}. {}.".format(
        term.part_of_speech.capitalize(),
        upper_first_letter(term.definition).rstrip("."),
    )

    if term.usage:
        comment += " E.g. {}.".format(upper_first_letter(term.usage).rstrip("."))

    return comment


def recompute_entity_comments(apps, schema_editor):
    """
    Fix the capitalization of entity comments for all terms.

    Previously str.capitalize() was used to build the comment, which lowercased
    everything after the first letter.
    """
    Term = apps.get_model("terminology", "Term")
    Entity = apps.get_model("base", "Entity")

    entities = []
    for term in Term.objects.filter(entity__isnull=False).select_related("entity"):
        comment = entity_comment(term)
        if term.entity.comment != comment:
            term.entity.comment = comment
            entities.append(term.entity)

    if entities:
        Entity.objects.bulk_update(entities, ["comment"])


class Migration(migrations.Migration):
    dependencies = [
        ("terminology", "0004_remove_term_exact_match"),
    ]

    operations = [
        migrations.RunPython(
            recompute_entity_comments,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
