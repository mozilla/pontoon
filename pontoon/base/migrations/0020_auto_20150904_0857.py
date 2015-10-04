# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def complete_plurals(apps, schema_editor):
    Locale = apps.get_model('base', 'Locale')

    for locale in LOCALES:
        l = Locale.objects.get(code=locale['code'])
        l.plural_rule = locale['plural_rule']
        l.nplurals = locale['nplurals']
        l.cldr_plurals = locale['cldr_plurals']
        l.save()

    # Also rename Panjabi to Punjabi
    for pa in Locale.objects.filter(code__startswith='pa'):
        pa.name = 'Punjabi'
        pa.save()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_auto_20150820_1345'),
    ]

    operations = [
        migrations.RunPython(complete_plurals)
    ]


LOCALES = [
    {
        'code': 'hy-AM',
        'plural_rule': '(n != 1)',
        'nplurals': 2,
        'cldr_plurals': '1,5'
    },
    {
        'code': 'as',
        'plural_rule': '(n != 1)',
        'nplurals': 2,
        'cldr_plurals': '1,5'
    },
    {
        'code': 'ilo',
        'plural_rule': '(n != 1)',
        'nplurals': 2,
        'cldr_plurals': '1,5'
    },
    {
        'code': 'ga-IE',
        'plural_rule': 'n==1 ? 0 : n==2 ? 1 : n<7 ? 2 : n<11 ? 3 : 4',
        'nplurals': 5,
        'cldr_plurals': '1,2,3,4,5'
    },
    {
        'code': 'ne-NP',
        'plural_rule': '(n != 1)',
        'nplurals': 2,
        'cldr_plurals': '1,5'
    },
    {
        'code': 'nb-NO',
        'plural_rule': '(n != 1)',
        'nplurals': 2,
        'cldr_plurals': '1,5'
    },
    {
        'code': 'nn-NO',
        'plural_rule': '(n != 1)',
        'nplurals': 2,
        'cldr_plurals': '1,5'
    },
    {
        'code': 'pa-IN',
        'plural_rule': '(n != 1)',
        'nplurals': 2,
        'cldr_plurals': '1,5'
    },
    {
        'code': 'pt-PT',
        'plural_rule': '(n != 1)',
        'nplurals': 2,
        'cldr_plurals': '1,5'
    },
    {
        'code': 'es-ES',
        'plural_rule': '(n != 1)',
        'nplurals': 2,
        'cldr_plurals': '1,5'
    },
    {
        'code': 'ta-LK',
        'plural_rule': '(n != 1)',
        'nplurals': 2,
        'cldr_plurals': '1,5'
    },
    {
        'code': 'fy-NL',
        'plural_rule': '(n != 1)',
        'nplurals': 2,
        'cldr_plurals': '1,5'
    },
    {
        'code': 'zu',
        'plural_rule': '(n != 1)',
        'nplurals': 2,
        'cldr_plurals': '1,5'
    },
]
