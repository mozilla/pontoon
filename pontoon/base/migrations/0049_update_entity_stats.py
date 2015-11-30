# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_entity_status(apps, schema_editor):
    Entity = apps.get_model('base', 'Entity')
    Translation = apps.get_model('base', 'Translation')
    EntityLocaleStatus = apps.get_model('base', 'EntityLocaleStatus')
    for entity in Entity.objects.all():
        for locale in entity.resource.project.locales.all():
            translations = entity.translation_set.filter(locale=locale)
            entity_status, _ = EntityLocaleStatus.objects.get_or_create(entity=entity, locale=locale)

            try:
                approved_translation = translations.get(approved=True)
            except Translation.DoesNotExist:
                approved_translation = None

            entity_status.is_translated = bool(approved_translation)
            entity_status.is_fuzzy = translations.filter(fuzzy=True).exists()

            entity_status.is_changed = approved_translation is not None and entity.string != approved_translation.string
            if entity_status.is_changed == False and entity.string_plural != "":
                for plural_form in range(0, locale.nplurals or 1):
                    changed = translations.filter(approved=True, plural_form=plural_form,
                    ).exclude(string=entity.string).exists()
                    if changed:
                        entity_status.is_changed = True
                        break

            entity_status.has_suggestions = translations.filter(approved=False).exists()
            entity_status.save()

def noop(apps, schema):
    return

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0048_auto_20151204_0152'),
    ]

    operations = [
        # All data will be removed in 0048, so there's no need to backward migration
        migrations.RunPython(update_entity_status, noop)
    ]
