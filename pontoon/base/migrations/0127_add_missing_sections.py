from collections import defaultdict
from itertools import groupby

from django.db import migrations
from django.db.models import F


section_key_formats = {"ini", "xcode", "xliff"}


def add_missing_sections(apps, schema_editor):
    Entity = apps.get_model("base", "Entity")
    Section = apps.get_model("base", "Section")

    entities = list(
        Entity.objects.filter(section_id=None, obsolete=False)
        .only("id", "key", "resource_id")
        .annotate(format=F("resource__format"))
    )
    prev_sections = defaultdict(
        list,
        (
            (res_id, list(res_sections))
            for res_id, res_sections in groupby(
                Section.objects.filter(
                    resource_id__in={e.resource_id for e in entities}
                ).order_by("resource_id"),
                key=lambda s: s.resource_id,
            )
        ),
    )
    new_sections = []
    for e in entities:
        section_key = e.key[:1] if e.format in section_key_formats else []
        res_sections = prev_sections[e.resource_id]
        section = next((s for s in res_sections if s.key == section_key), None)
        if section is None:
            section = Section(resource_id=e.resource_id, key=section_key)
            new_sections.append(section)
            res_sections.append(section)
        e.section = section

    print(
        f"\n    Adding {len(new_sections)} sections, updating {len(entities)} entities...\n   ",
        end="",
        flush=True,
    )
    Section.objects.bulk_create(new_sections)
    Entity.objects.bulk_update(entities, ["section"], batch_size=10_000)


class Migration(migrations.Migration):
    dependencies = [("base", "0126_set_system_user_roles")]

    operations = [
        migrations.RunPython(
            add_missing_sections,
            reverse_code=migrations.RunPython.noop,
        )
    ]
