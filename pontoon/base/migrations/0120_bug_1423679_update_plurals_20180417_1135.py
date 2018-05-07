# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-17 11:35
from __future__ import unicode_literals

import copy

from django.db import migrations
from fluent.syntax import FluentParser, FluentSerializer, ast

# Needed for calculate_stats()
from pontoon.base.models import TranslatedResource


parser = FluentParser()
serializer = FluentSerializer()


def update_plurals(apps, schema_editor):
    Locale = apps.get_model('base', 'Locale')
    Translation = apps.get_model('base', 'Translation')
    ChangedEntityLocale = apps.get_model('base', 'ChangedEntityLocale')

    for code, data in LOCALES.items():
        locale = Locale.objects.get(code=code)

        # print ""
        # print locale.code
        # print "---------"

        # Cache for later use
        cldr_plurals_old = locale.cldr_plurals

        """
        1. Update Locale data
        """
        locale.cldr_plurals = data['cldr_plurals']
        locale.plural_rule = data['plural_rule']
        locale.save()

        translations = Translation.objects.filter(locale=locale, approved=True)

        """
        2. Update Gettext Translations
        """
        gettext_translations = translations.filter(
            entity__resource__format='po',
            plural_form__isnull=False,
        )

        # Update Translation.plural_form. It represents an index of
        # Locale.cldr_plurals_list(), which we're changing. Prefetch QuerySets
        # to prevent cycled updates.
        cldr_ids_old = map(int, cldr_plurals_old.split(','))
        cldr_ids = map(int, locale.cldr_plurals.split(','))

        translation_indexes = {}

        for index, plural_form in enumerate(cldr_ids_old):
            index_new = cldr_ids.index(plural_form)
            translation_indexes[index_new] = (
                list(gettext_translations.filter(plural_form=index).values_list('pk', flat=True))
            )

        for index_new, translation_pks in translation_indexes.items():
            Translation.objects.filter(
                pk__in=translation_pks
            ).update(
                plural_form=index_new
            )

        # Add suggestions to newly created plural forms, copied from the
        # approved plural forms with the highest index (incl. metadata).
        forms_all = range(0, len(cldr_ids))
        used_indexes = translation_indexes.keys()
        forms_new = [item for item in forms_all if item not in used_indexes]

        gettext_templates = gettext_translations.filter(
            plural_form=index_new  # Highest index
        )
        changed_entity_ids = gettext_templates.values_list(
            'entity__id',
            flat=True,
        ).distinct()

        gettext_translations_new = [
            Translation(
                entity=gettext_template.entity,
                locale=gettext_template.locale,
                plural_form=form_new,
                string=gettext_template.string,
                user=gettext_template.user,
                date=gettext_template.date,
            ) for form_new in forms_new
            for gettext_template in gettext_templates
        ]

        Translation.objects.bulk_create(gettext_translations_new)

        # Update stats
        translated_resources = TranslatedResource.objects.filter(
            locale__code=code,
            resource__in=gettext_templates.values('entity__resource'),
        )
        for tr in translated_resources:
            tr.calculate_stats()

        # Mark entities as changed, for later sync
        changed_entities = [
            ChangedEntityLocale(
                entity_id=changed_entity_id,
                locale=locale,
            ) for changed_entity_id in changed_entity_ids
        ]

        # print "Changed Gettext entities: " + str(list(changed_entity_ids))

        ChangedEntityLocale.objects.bulk_create(changed_entities)

        """
        3. Update Fluent Translations
        """
        CLDR_PLURALS = ['zero', 'one', 'two', 'few', 'many', 'other']
        locale_cldr_plurals = [CLDR_PLURALS[i] for i in cldr_ids]

        fluent_translation_candidates = translations.filter(
            entity__resource__format='ftl',
            # We need python to find pluralized FTL strings,
            # but we can narrow down the list of candidates
            # to only include selectors
            string__contains='->',
        )

        changed_fluent_entities = []

        for t in fluent_translation_candidates:
            translation_ast = parser.parse_entry(t.string)
            elements = []

            if translation_ast.value:
                elements += translation_ast.value.elements

            for attribute in translation_ast.attributes:
                if attribute.value:
                    elements += attribute.value.elements

            for element in elements:
                # Skip non-selector elements
                if not (
                    isinstance(element, ast.Placeable) and
                    hasattr(element.expression, 'variants')
                ):
                    continue

                # Keys of all variants of plural elements are either
                # CLDR plurals or numbers
                if all(
                    isinstance(variant.key, ast.NumberExpression) or
                    (
                        isinstance(variant.key, ast.VariantName) and
                        variant.key.name in CLDR_PLURALS
                    )
                    for variant in element.expression.variants
                ):
                    # Populate missing plural forms
                    existing_plural_variants = [
                        variant
                        for variant in element.expression.variants
                        if isinstance(variant.key, ast.VariantName)
                    ]

                    for cldr_plural in locale_cldr_plurals:
                        numeric_variants = [x.key.value for x in element.expression.variants if isinstance(x.key, ast.NumberExpression)]
                        # Skip 'zero' if 0 exists
                        if cldr_plural == 'zero' and '0' in numeric_variants:
                            continue

                        # Skip 'one' if 1 exists
                        if cldr_plural == 'one' and '1' in numeric_variants:
                            continue

                        # Skip 'two' if 2 exists
                        if cldr_plural == 'two' and '2' in numeric_variants:
                            continue

                        if existing_plural_variants and cldr_plural not in [variant.key.name for variant in existing_plural_variants]:
                            new_variant = copy.deepcopy(existing_plural_variants[-1])
                            new_variant.key.name = cldr_plural
                            new_variant.default = False
                            element.expression.variants.append(new_variant)

                    # Sort variants
                    element.expression.variants = sorted(
                        element.expression.variants,
                        key=lambda x: (['0'] + ['1'] + CLDR_PLURALS).index(x.key.name if hasattr(x.key, 'name') else x.key.value)
                    )

                    new_string = serializer.serialize_entry(translation_ast)

                    if t.string != new_string:
                        t.string = new_string
                        t.approved = False

                        # Does not run the custom Translation.save() method
                        t.save()

                        # Update stats
                        translatedresource, _ = TranslatedResource.objects.get_or_create(
                            resource_id=t.entity.resource.id, locale__code=code
                        )
                        translatedresource.calculate_stats()

                        # Mark entity as changed
                        ChangedEntityLocale.objects.get_or_create(entity_id=t.entity.id, locale_id=locale.id)

                        changed_fluent_entities.append(t.entity.pk)

        # print "Changed Fluent entities: " + str(changed_fluent_entities)


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0119_plural_rule_max_length_1639'),
    ]

    operations = [
        migrations.RunPython(
            update_plurals,
            migrations.RunPython.noop,
        ),
    ]


LOCALES = {
    'ka': {
        'cldr_plurals': '1,5',
        'plural_rule': '(n != 1)',
    },
    'fa': {
        'cldr_plurals': '1,5',
        'plural_rule': '(n > 1)',
    },
    'tr': {
        'cldr_plurals': '1,5',
        'plural_rule': '(n != 1)',
    },
    'cy': {
        'cldr_plurals': '0,1,2,3,4,5',
        'plural_rule': '(n == 0) ? 0 : ((n == 1) ? 1 : ((n == 2) ? 2 : ((n == 3) ? 3 : ((n == 6) ? 4 : 5))))',
    },
    'uz': {
        'cldr_plurals': '1,5',
        'plural_rule': '(n != 1)',
    },
    'br': {
        'cldr_plurals': '1,2,3,4,5',
        'plural_rule': '(n % 10 == 1 && n % 100 != 11 && n % 100 != 71 && n % 100 != 91) ? 0 : ((n % 10 == 2 && n % 100 != 12 && n % 100 != 72 && n % 100 != 92) ? 1 : ((((n % 10 == 3 || n % 10 == 4) || n % 10 == 9) && (n % 100 < 10 || n % 100 > 19) && (n % 100 < 70 || n % 100 > 79) && (n % 100 < 90 || n % 100 > 99)) ? 2 : ((n != 0 && n % 1000000 == 0) ? 3 : 4)))',
    },
}
