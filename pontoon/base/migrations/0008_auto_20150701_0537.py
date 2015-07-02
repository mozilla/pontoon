# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_cldr_plurals_to_locales(apps, schema_editor):
    CLDR_Plurals = apps.get_model('base', 'CLDR_Plurals')
    Locale = apps.get_model('base', 'Locale')

    for locale in LOCALE_CLDR:
        l = Locale.objects.get(code=locale["code"])

        for cldr_plural in locale["cldr_plurals"]:
            plural = CLDR_Plurals.objects.get(name=cldr_plural)
            l.cldr_plurals.add(plural)

        l.save()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20150627_1220'),
    ]

    operations = [
        migrations.RunPython(add_cldr_plurals_to_locales),
    ]


LOCALE_CLDR = [{
    "code": "af",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ak",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "sq",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "am",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ar",
    "cldr_plurals": ["zero", "one", "two", "few", "many", "other"]
}, {
    "code": "an",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "hy",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ast",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "az",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "eu",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "be",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "bn",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "bn-BD",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "bn-IN",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "bs",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "br",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "bg",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "my",
    "cldr_plurals": ["other"]
}, {
    "code": "ca",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "hne",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "zh",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "zh-CN",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "zh-HK",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "zh-TW",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "kw",
    "cldr_plurals": ["one", "two", "few", "other"]
}, {
    "code": "hr",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "cs",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "da",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "nl",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "dz",
    "cldr_plurals": ["other"]
}, {
    "code": "en",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "en-AU",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "en-CA",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "en-IE",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "en-ZA",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "en-GB",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "en-US",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "eo",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "et",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "fo",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "fil",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "fi",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "fr",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "fur",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ff",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "gd",
    "cldr_plurals": ["one", "two", "few", "other"]
}, {
    "code": "gl",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ka",
    "cldr_plurals": ["other"]
}, {
    "code": "de",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "el",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "gu",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "gu-IN",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "gun",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ht",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ha",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "he",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "hi",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "hi-IN",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "hu",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "is",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "id",
    "cldr_plurals": ["other"]
}, {
    "code": "ia",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ga",
    "cldr_plurals": ["one", "two", "few", "many", "other"]
}, {
    "code": "it",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ja",
    "cldr_plurals": ["other"]
}, {
    "code": "jv",
    "cldr_plurals": ["zero", "other"]
}, {
    "code": "kn",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "csb",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "kk",
    "cldr_plurals": ["other"]
}, {
    "code": "km",
    "cldr_plurals": ["other"]
}, {
    "code": "rw",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ky",
    "cldr_plurals": ["other"]
}, {
    "code": "ko",
    "cldr_plurals": ["other"]
}, {
    "code": "ku",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "lo",
    "cldr_plurals": ["other"]
}, {
    "code": "lv",
    "cldr_plurals": ["zero", "one", "other"]
}, {
    "code": "lij",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ln",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "lt",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "lb",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "mk",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "mai",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "mg",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ms",
    "cldr_plurals": ["other"]
}, {
    "code": "ml",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "mt",
    "cldr_plurals": ["one", "few", "many", "other"]
}, {
    "code": "mi",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "arn",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "mr",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "mn",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "nah",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "nap",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ne",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "se",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "nso",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "no",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "nb",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "nn",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "oc",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "or",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "pa",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "pap",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "fa",
    "cldr_plurals": ["other"]
}, {
    "code": "pms",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "pl",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "pt",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "pt-BR",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ps",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ro",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "rm",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ru",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "sco",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "sr",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "sr@latin",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "si",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "sk",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "sl",
    "cldr_plurals": ["one", "two", "few", "other"]
}, {
    "code": "sl-SI",
    "cldr_plurals": ["one", "two", "few", "other"]
}, {
    "code": "so",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "son",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "st",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "es-AR",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "es",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "es-CL",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "es-MX",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "su",
    "cldr_plurals": ["other"]
}, {
    "code": "sw",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "sv",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "sv-SE",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "tg",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ta",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ta-IN",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "tt",
    "cldr_plurals": ["other"]
}, {
    "code": "te",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "th",
    "cldr_plurals": ["other"]
}, {
    "code": "bo",
    "cldr_plurals": ["other"]
}, {
    "code": "ti",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "tr",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "tk",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "ug",
    "cldr_plurals": ["other"]
}, {
    "code": "uk",
    "cldr_plurals": ["one", "few", "other"]
}, {
    "code": "hsb",
    "cldr_plurals": ["one", "two", "few", "other"]
}, {
    "code": "ur",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "uz",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "vi",
    "cldr_plurals": ["other"]
}, {
    "code": "wa",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "cy",
    "cldr_plurals": ["one", "two", "few", "other"]
}, {
    "code": "fy",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "wo",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "xh",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "yo",
    "cldr_plurals": ["one", "other"]
}, {
    "code": "dsb",
    "cldr_plurals": ["one", "two", "few", "other"]
}]
