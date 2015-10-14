# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def remove_unused_locales(apps, schema_editor):
    Locale = apps.get_model('base', 'Locale')
    Locale.objects.filter(code__in=UNUSED_LOCALES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_auto_20150803_1524'),
    ]

    operations = [
        migrations.RunPython(remove_unused_locales),
    ]

UNUSED_LOCALES = [u'af-ZA', u'aln', u'am', u'am-ET', u'ar-SA', u'arn', u'as-IN',
    u'az-AZ', u'bal', u'be-BY', u'be@tarask', u'bg-BG', u'bn', u'bo', u'bo-CN',
    u'bs-BA', u'ca-ES', u'ca@valencia', u'crh', u'cs-CZ', u'cy-GB', u'da-DK',
    u'de-CH', u'de-DE', u'dz', u'dz-BT', u'el-GR', u'en', u'en-AU', u'en-CA',
    u'en-IE', u'en-US', u'es-BO', u'es-CO', u'es-CR', u'es-DO', u'es-EC',
    u'es-NI', u'es-PA', u'es-PE', u'es-PR', u'es-PY', u'es-SV', u'es-UY',
    u'es-VE', u'et-EE', u'eu-ES', u'fa-IR', u'fi-FI', u'fil', u'fo', u'fo-FO',
    u'fr-CA', u'fr-CH', u'fr-FR', u'frp', u'gl-ES', u'gu', u'gun', u'ha',
    u'he-IL', u'hi', u'hne', u'hr-HR', u'ht-HT', u'hu-HU', u'hy', u'ia',
    u'id-ID', u'ig', u'is-IS', u'it-IT', u'ja-JP', u'jv', u'ka-GE', u'kk-KZ',
    u'km-KH', u'kn-IN', u'ko-KR', u'ks', u'ks-IN', u'ku-IQ', u'kw', u'ky',
    u'la', u'lb', u'li', u'ln', u'lo', u'lo-LA', u'lt-LT', u'lv-LV', u'mg',
    u'mi', u'mk-MK', u'ml-IN', u'mn-MN', u'mr-IN', u'ms-MY', u'mt', u'mt-MT',
    u'my-MM', u'nah', u'nap', u'nb', u'nds', u'ne', u'nl-BE', u'nl-NL', u'nn',
    u'no', u'no-NO', u'nr', u'or-IN', u'pap', u'pl-PL', u'pms', u'ps',
    u'ro-RO', u'ru-RU', u'rw', u'sc', u'sco', u'se', u'si-LK', u'sk-SK',
    u'sl-SI', u'sm', u'sn', u'so', u'sq-AL', u'sr-RS', u'sr-RS@latin',
    u'sr@latin', u'st', u'st-ZA', u'su', u'sv', u'sv-FI', u'sw-KE', u'ta-IN',
    u'te-IN', u'tg', u'tg-TJ', u'th-TH', u'ti', u'tk', u'tl', u'tl-PH', u'tlh',
    u'to', u'tr-TR', u'tt', u'ug', u'uk-UA', u'ur-PK', u've', u'vi-VN', u'vls',
    u'wa', u'wo-SN', u'yi', u'yo', u'zh', u'zh-CN.GB2312', u'zh-HK',
    u'zh-TW.Big5', u'zu-ZA'
]
