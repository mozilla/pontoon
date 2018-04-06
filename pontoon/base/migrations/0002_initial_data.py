# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


def load_initial_data(apps, schema_editor):
    Locale = apps.get_model('base', 'Locale')
    for locale_kwargs in LOCALES:
        Locale.objects.create(**locale_kwargs)

    Project = apps.get_model('base', 'Project')
    project = Project.objects.create(
        name='Pontoon Intro',
        slug='pontoon-intro',
        url=settings.SITE_URL + '/intro/',
        links=True,
        repository_type='git',
        repository_url='https://github.com/mozilla/pontoon-intro.git',
        info_brief=('This is a demo website, used for demonstration purposes '
                    'only. You can translate on the website itself by double '
                    'clicking on page elements. Access to advanced features '
                    'like translation memory and machine translation is '
                    'available by clicking on the menu icon in the top-left '
                    'corner.')
    )

    # The "historical" version of the Project model that this migration
    # uses has trouble working with the ManyToManyField on the Project
    # model. Our workaround is to use the auto-generated intermediate
    # model directly to create the relation between project and locales.
    locale = Locale.objects.get(code='en-GB')
    Project.locales.through.objects.create(project_id=project.id, locale_id=locale.id)


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]


LOCALES = [
    {
        u'code': u'af',
        u'name': u'Afrikaans',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'af-ZA', u'name': u'Afrikaans'
    },
    {
        u'code': u'ak',
        u'name': u'Akan',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'sq',
        u'name': u'Albanian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'sq-AL', u'name': u'Albanian'
    },
    {
        u'code': u'aln', u'name': u'Albanian Gheg'
    },
    {
        u'code': u'am',
        u'name': u'Amharic',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'am-ET', u'name': u'Amharic'
    },
    {
        u'code': u'ar',
        u'name': u'Arabic',
        u'nplurals': u'6',
        u'plural_rule': u'(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5)'
    },
    {
        u'code': u'ar-SA', u'name': u'Arabic'
    },
    {
        u'code': u'an',
        u'name': u'Aragonese',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'hy',
        u'name': u'Armenian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'hy-AM', u'name': u'Armenian'
    },
    {
        u'code': u'as', u'name': u'Assamese'
    },
    {
        u'code': u'as-IN', u'name': u'Assamese'
    },
    {
        u'code': u'ast',
        u'name': u'Asturian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'az',
        u'name': u'Azerbaijani',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'az-AZ', u'name': u'Azerbaijani'
    },
    {
        u'code': u'bal', u'name': u'Balochi'
    },
    {
        u'code': u'eu',
        u'name': u'Basque',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'eu-ES', u'name': u'Basque'
    },
    {
        u'code': u'be',
        u'name': u'Belarusian',
        u'nplurals': u'3',
        u'plural_rule': u'(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    },
    {
        u'code': u'be-BY', u'name': u'Belarusian'
    },
    {
        u'code': u'be@tarask', u'name': u'Belarusian'
    },
    {
        u'code': u'bn',
        u'name': u'Bengali',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'bn-BD',
        u'name': u'Bengali',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'bn-IN',
        u'name': u'Bengali',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'bs',
        u'name': u'Bosnian',
        u'nplurals': u'3',
        u'plural_rule': u'(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    },
    {
        u'code': u'bs-BA', u'name': u'Bosnian'
    },
    {
        u'code': u'br',
        u'name': u'Breton',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'bg',
        u'name': u'Bulgarian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'bg-BG', u'name': u'Bulgarian'
    },
    {
        u'code': u'my',
        u'name': u'Burmese',
        u'nplurals': u'1',
        u'plural_rule': u'0'
    },
    {
        u'code': u'my-MM', u'name': u'Burmese'
    },
    {
        u'code': u'ca',
        u'name': u'Catalan',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ca-ES', u'name': u'Catalan'
    },
    {
        u'code': u'ca@valencia', u'name': u'Catalan'
    },
    {
        u'code': u'hne',
        u'name': u'Chhattisgarhi',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'zh',
        u'name': u'Chinese',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'zh-CN',
        u'name': u'Chinese',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'zh-CN.GB2312', u'name': u'Chinese'
    },
    {
        u'code': u'zh-HK',
        u'name': u'Chinese',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'zh-TW',
        u'name': u'Chinese',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'zh-TW.Big5', u'name': u'Chinese'
    },
    {
        u'code': u'kw',
        u'name': u'Cornish',
        u'nplurals': u'4',
        u'plural_rule': u'(n==1) ? 0 : (n==2) ? 1 : (n == 3) ? 2 : 3'
    },
    {
        u'code': u'crh', u'name': u'Crimean Turkish'
    },
    {
        u'code': u'hr',
        u'name': u'Croatian',
        u'nplurals': u'3',
        u'plural_rule': u'(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    },
    {
        u'code': u'hr-HR', u'name': u'Croatian'
    },
    {
        u'code': u'cs',
        u'name': u'Czech',
        u'nplurals': u'3',
        u'plural_rule': u'(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2'
    },
    {
        u'code': u'cs-CZ', u'name': u'Czech'
    },
    {
        u'code': u'da',
        u'name': u'Danish',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'da-DK', u'name': u'Danish'
    },
    {
        u'code': u'nl',
        u'name': u'Dutch',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'nl-BE', u'name': u'Dutch'
    },
    {
        u'code': u'nl-NL', u'name': u'Dutch'
    },
    {
        u'code': u'dz',
        u'name': u'Dzongkha',
        u'nplurals': u'1',
        u'plural_rule': u'0'
    },
    {
        u'code': u'dz-BT', u'name': u'Dzongkha'
    },
    {
        u'code': u'en',
        u'name': u'English',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'en-AU',
        u'name': u'English',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'en-CA',
        u'name': u'English',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'en-IE',
        u'name': u'English',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'en-ZA',
        u'name': u'English',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'en-GB',
        u'name': u'English',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'en-US',
        u'name': u'English',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'eo',
        u'name': u'Esperanto',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'et',
        u'name': u'Estonian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'et-EE', u'name': u'Estonian'
    },
    {
        u'code': u'fo',
        u'name': u'Faroese',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'fo-FO', u'name': u'Faroese'
    },
    {
        u'code': u'fil',
        u'name': u'Filipino',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'fi',
        u'name': u'Finnish',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'fi-FI', u'name': u'Finnish'
    },
    {
        u'code': u'frp', u'name': u'Franco-Proven\xe7al'
    },
    {
        u'code': u'fr',
        u'name': u'French',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'fr-CA', u'name': u'French'
    },
    {
        u'code': u'fr-FR', u'name': u'French'
    },
    {
        u'code': u'fr-CH', u'name': u'French'
    },
    {
        u'code': u'fur',
        u'name': u'Friulian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ff',
        u'name': u'Fulah',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'gd',
        u'name': u'Gaelic, Scottish',
        u'nplurals': u'4',
        u'plural_rule': u'(n==1 || n==11) ? 0 : (n==2 || n==12) ? 1 : (n > 2 && n < 20) ? 2 : 3'
    },
    {
        u'code': u'gl',
        u'name': u'Galician',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'gl-ES', u'name': u'Galician'
    },
    {
        u'code': u'ka',
        u'name': u'Georgian',
        u'nplurals': u'1',
        u'plural_rule': u'0'
    },
    {
        u'code': u'ka-GE', u'name': u'Georgian'
    },
    {
        u'code': u'de',
        u'name': u'German',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'de-DE', u'name': u'German'
    },
    {
        u'code': u'de-CH', u'name': u'German'
    },
    {
        u'code': u'el',
        u'name': u'Greek',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'el-GR', u'name': u'Greek'
    },
    {
        u'code': u'gu',
        u'name': u'Gujarati',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'gu-IN',
        u'name': u'Gujarati',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'gun',
        u'name': u'Gun',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'ht',
        u'name': u'Haitian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ht-HT', u'name': u'Haitian'
    },
    {
        u'code': u'ha',
        u'name': u'Hausa',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'he',
        u'name': u'Hebrew',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'he-IL', u'name': u'Hebrew'
    },
    {
        u'code': u'hi',
        u'name': u'Hindi',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'hi-IN',
        u'name': u'Hindi',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'hu',
        u'name': u'Hungarian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'hu-HU', u'name': u'Hungarian'
    },
    {
        u'code': u'is',
        u'name': u'Icelandic',
        u'nplurals': u'2',
        u'plural_rule': u'(n%10!=1 || n%100==11)'
    },
    {
        u'code': u'is-IS', u'name': u'Icelandic'
    },
    {
        u'code': u'ig', u'name': u'Igbo'
    },
    {
        u'code': u'ilo', u'name': u'Iloko'
    },
    {
        u'code': u'id',
        u'name': u'Indonesian',
        u'nplurals': u'1',
        u'plural_rule': u'0'
    },
    {
        u'code': u'id-ID', u'name': u'Indonesian'
    },
    {
        u'code': u'ia',
        u'name': u'Interlingua',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ga',
        u'name': u'Irish',
        u'nplurals': u'5',
        u'plural_rule': u'n==1 ? 0 : n==2 ? 1 : n<7 ? 2 : n<11 ? 3 : 4'
    },
    {
        u'code': u'ga-IE', u'name': u'Irish'
    },
    {
        u'code': u'it',
        u'name': u'Italian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'it-IT', u'name': u'Italian'
    },
    {
        u'code': u'ja',
        u'name': u'Japanese',
        u'nplurals': u'1',
        u'plural_rule': u'0'
    },
    {
        u'code': u'ja-JP', u'name': u'Japanese'
    },
    {
        u'code': u'jv',
        u'name': u'Javanese',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 0)'
    },
    {
        u'code': u'kn',
        u'name': u'Kannada',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'kn-IN', u'name': u'Kannada'
    },
    {
        u'code': u'ks', u'name': u'Kashmiri'
    },
    {
        u'code': u'ks-IN', u'name': u'Kashmiri'
    },
    {
        u'code': u'csb',
        u'name': u'Kashubian',
        u'nplurals': u'3',
        u'plural_rule': u'(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    },
    {
        u'code': u'kk', u'name': u'Kazakh', u'nplurals': u'1', u'plural_rule': u'0'
    },
    {
        u'code': u'kk-KZ', u'name': u'Kazakh'
    },
    {
        u'code': u'km', u'name': u'Khmer', u'nplurals': u'1', u'plural_rule': u'0'
    },
    {
        u'code': u'km-KH', u'name': u'Khmer'
    },
    {
        u'code': u'rw',
        u'name': u'Kinyarwanda',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ky', u'name': u'Kirgyz', u'nplurals': u'1', u'plural_rule': u'0'
    },
    {
        u'code': u'tlh', u'name': u'Klingon'
    },
    {
        u'code': u'ko', u'name': u'Korean', u'nplurals': u'1', u'plural_rule': u'0'
    },
    {
        u'code': u'ko-KR', u'name': u'Korean'
    },
    {
        u'code': u'ku',
        u'name': u'Kurdish',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ku-IQ', u'name': u'Kurdish'
    },
    {
        u'code': u'lo', u'name': u'Lao', u'nplurals': u'1', u'plural_rule': u'0'
    },
    {
        u'code': u'lo-LA', u'name': u'Lao'
    },
    {
        u'code': u'la', u'name': u'Latin'
    },
    {
        u'code': u'lv',
        u'name': u'Latvian',
        u'nplurals': u'3',
        u'plural_rule': u'(n%10==1 && n%100!=11 ? 0 : n != 0 ? 1 : 2)'
    },
    {
        u'code': u'lv-LV', u'name': u'Latvian'
    },
    {
        u'code': u'lij',
        u'name': u'Ligurian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'li', u'name': u'Limburgian'
    },
    {
        u'code': u'ln',
        u'name': u'Lingala',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'lt',
        u'name': u'Lithuanian',
        u'nplurals': u'3',
        u'plural_rule': u'(n%10==1 && n%100!=11 ? 0 : n%10>=2 && (n%100<10 or n%100>=20) ? 1 : 2)'
    },
    {
        u'code': u'lt-LT', u'name': u'Lithuanian'
    },
    {
        u'code': u'nds', u'name': u'Low German'
    },
    {
        u'code': u'lb',
        u'name': u'Luxembourgish',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'mk',
        u'name': u'Macedonian',
        u'nplurals': u'2',
        u'plural_rule': u'(n==1 || n%10==1 ? 0 : 1)'
    },
    {
        u'code': u'mk-MK', u'name': u'Macedonian'
    },
    {
        u'code': u'mai',
        u'name': u'Maithili',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'mg',
        u'name': u'Malagasy',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'ms', u'name': u'Malay', u'nplurals': u'1', u'plural_rule': u'0'
    },
    {
        u'code': u'ml',
        u'name': u'Malayalam',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ml-IN', u'name': u'Malayalam'
    },
    {
        u'code': u'ms-MY', u'name': u'Malay'
    },
    {
        u'code': u'mt',
        u'name': u'Maltese',
        u'nplurals': u'4',
        u'plural_rule': u'(n==1 ? 0 : n==0 || ( n%100>1 && n%100<11) ? 1 : (n%100>10 && n%100<20 ) ? 2 : 3)'
    },
    {
        u'code': u'mt-MT', u'name': u'Maltese'
    },
    {
        u'code': u'mi',
        u'name': u'Māori',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'arn',
        u'name': u'Mapudungun',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'mr',
        u'name': u'Marathi',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'mr-IN', u'name': u'Marathi'
    },
    {
        u'code': u'mn',
        u'name': u'Mongolian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'mn-MN', u'name': u'Mongolian'
    },
    {
        u'code': u'nah',
        u'name': u'Nahuatl',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'nr', u'name': u'Ndebele, South'
    },
    {
        u'code': u'nap',
        u'name': u'Neapolitan',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ne',
        u'name': u'Nepali',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ne-NP', u'name': u'Nepali'
    },
    {
        u'code': u'se',
        u'name': u'Northern Sami',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'nso',
        u'name': u'Northern Sotho',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'no',
        u'name': u'Norwegian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'nb',
        u'name': u'Norwegian Bokm\xe5l',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'nb-NO', u'name': u'Norwegian Bokm\xe5l'
    },
    {
        u'code': u'no-NO', u'name': u'Norwegian'
    },
    {
        u'code': u'nn',
        u'name': u'Norwegian Nynorsk',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'nn-NO', u'name': u'Norwegian Nynorsk'
    },
    {
        u'code': u'oc',
        u'name': u'Occitan',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'or',
        u'name': u'Oriya',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'or-IN', u'name': u'Oriya'
    },
    {
        u'code': u'pa',
        u'name': u'Panjabi',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'pa-IN', u'name': u'Panjabi'
    },
    {
        u'code': u'pap',
        u'name': u'Papiamento',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'fa',
        u'name': u'Persian',
        u'nplurals': u'1',
        u'plural_rule': u'0'
    },
    {
        u'code': u'fa-IR', u'name': u'Persian'
    },
    {
        u'code': u'pms',
        u'name': u'Piemontese',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'pl',
        u'name': u'Polish',
        u'nplurals': u'3',
        u'plural_rule': u'(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    },
    {
        u'code': u'pl-PL', u'name': u'Polish'
    },
    {
        u'code': u'pt',
        u'name': u'Portuguese',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'pt-BR',
        u'name': u'Portuguese',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'pt-PT', u'name': u'Portuguese'
    },
    {
        u'code': u'ps',
        u'name': u'Pushto',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ro',
        u'name': u'Romanian',
        u'nplurals': u'3',
        u'plural_rule': u'(n==1 ? 0 : (n==0 || (n%100 > 0 && n%100 < 20)) ? 1 : 2)'
    },
    {
        u'code': u'ro-RO', u'name': u'Romanian'
    },
    {
        u'code': u'rm',
        u'name': u'Romansh',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ru',
        u'name': u'Russian',
        u'nplurals': u'3',
        u'plural_rule': u'(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    },
    {
        u'code': u'ru-RU', u'name': u'Russian'
    },
    {
        u'code': u'sm', u'name': u'Samoan'
    },
    {
        u'code': u'sc', u'name': u'Sardinian'
    },
    {
        u'code': u'sco',
        u'name': u'Scots',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'sr',
        u'name': u'Serbian',
        u'nplurals': u'3',
        u'plural_rule': u'(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    },
    {
        u'code': u'sr@latin',
        u'name': u'Serbian',
        u'nplurals': u'3',
        u'plural_rule': u'(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    },
    {
        u'code': u'sr-RS@latin', u'name': u'Serbian'
    },
    {
        u'code': u'sr-RS', u'name': u'Serbian'
    },
    {
        u'code': u'sn', u'name': u'Shona'
    },
    {
        u'code': u'si',
        u'name': u'Sinhala',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'si-LK', u'name': u'Sinhala'
    },
    {
        u'code': u'sk',
        u'name': u'Slovak',
        u'nplurals': u'3',
        u'plural_rule': u'(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2'
    },
    {
        u'code': u'sk-SK', u'name': u'Slovak'
    },
    {
        u'code': u'sl',
        u'name': u'Slovenian',
        u'nplurals': u'4',
        u'plural_rule': u'(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3)'
    },
    {
        u'code': u'sl-SI',
        u'name': u'Slovenian',
        u'nplurals': u'4',
        u'plural_rule': u'(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3)'
    },
    {
        u'code': u'so',
        u'name': u'Somali',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'son',
        u'name': u'Songhay',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'st',
        u'name': u'Sotho, Southern',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'st-ZA', u'name': u'Sotho, Southern'
    },
    {
        u'code': u'es-AR',
        u'name': u'Spanish',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'es-BO', u'name': u'Spanish'
    },
    {
        u'code': u'es',
        u'name': u'Spanish',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'es-CL',
        u'name': u'Spanish',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'es-CO', u'name': u'Spanish'
    },
    {
        u'code': u'es-CR', u'name': u'Spanish'
    },
    {
        u'code': u'es-DO', u'name': u'Spanish'
    },
    {
        u'code': u'es-EC', u'name': u'Spanish'
    },
    {
        u'code': u'es-SV', u'name': u'Spanish'
    },
    {
        u'code': u'es-MX',
        u'name': u'Spanish',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'es-NI', u'name': u'Spanish'
    },
    {
        u'code': u'es-PA', u'name': u'Spanish'
    },
    {
        u'code': u'es-PY', u'name': u'Spanish'
    },
    {
        u'code': u'es-PE', u'name': u'Spanish'
    },
    {
        u'code': u'es-PR', u'name': u'Spanish'
    },
    {
        u'code': u'es-ES', u'name': u'Spanish'
    },
    {
        u'code': u'es-UY', u'name': u'Spanish'
    },
    {
        u'code': u'es-VE', u'name': u'Spanish'
    },
    {
        u'code': u'su',
        u'name': u'Sundanese',
        u'nplurals': u'1',
        u'plural_rule': u'0'
    },
    {
        u'code': u'sw',
        u'name': u'Swahili',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'sw-KE', u'name': u'Swahili'
    },
    {
        u'code': u'sv',
        u'name': u'Swedish',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'sv-FI', u'name': u'Swedish'
    },
    {
        u'code': u'sv-SE',
        u'name': u'Swedish',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'tl', u'name': u'Tagalog'
    },
    {
        u'code': u'tl-PH', u'name': u'Tagalog'
    },
    {
        u'code': u'tg',
        u'name': u'Tajik',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'tg-TJ', u'name': u'Tajik'
    },
    {
        u'code': u'ta',
        u'name': u'Tamil',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ta-IN',
        u'name': u'Tamil',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ta-LK', u'name': u'Tamil'
    },
    {
        u'code': u'tt', u'name': u'Tatar', u'nplurals': u'1', u'plural_rule': u'0'
    },
    {
        u'code': u'te',
        u'name': u'Telugu',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'te-IN', u'name': u'Telugu'
    },
    {
        u'code': u'th', u'name': u'Thai', u'nplurals': u'1', u'plural_rule': u'0'
    },
    {
        u'code': u'th-TH', u'name': u'Thai'
    },
    {
        u'code': u'bo',
        u'name': u'Tibetan',
        u'nplurals': u'1',
        u'plural_rule': u'0'
    },
    {
        u'code': u'bo-CN', u'name': u'Tibetan'
    },
    {
        u'code': u'ti',
        u'name': u'Tigrinya',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'to', u'name': u'Tongan'
    },
    {
        u'code': u'tr',
        u'name': u'Turkish',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'tr-TR', u'name': u'Turkish'
    },
    {
        u'code': u'tk',
        u'name': u'Turkmen',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ug', u'name': u'Uighur', u'nplurals': u'1', u'plural_rule': u'0'
    },
    {
        u'code': u'uk',
        u'name': u'Ukrainian',
        u'nplurals': u'3',
        u'plural_rule': u'(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    },
    {
        u'code': u'uk-UA', u'name': u'Ukrainian'
    },
    {
        u'code': u'hsb',
        u'name': u'Upper Sorbian',
        u'nplurals': u'4',
        u'plural_rule': u'(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3)'
    },
    {
        u'code': u'ur',
        u'name': u'Urdu',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'ur-PK', u'name': u'Urdu'
    },
    {
        u'code': u'uz',
        u'name': u'Uzbek',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u've', u'name': u'Venda'
    },
    {
        u'code': u'vi',
        u'name': u'Vietnamese',
        u'nplurals': u'1',
        u'plural_rule': u'0'
    },
    {
        u'code': u'vi-VN', u'name': u'Vietnamese'
    },
    {
        u'code': u'vls', u'name': u'Vlaams'
    },
    {
        u'code': u'wa',
        u'name': u'Walloon',
        u'nplurals': u'2',
        u'plural_rule': u'(n > 1)'
    },
    {
        u'code': u'cy',
        u'name': u'Welsh',
        u'nplurals': u'4',
        u'plural_rule': u'(n==1) ? 0 : (n==2) ? 1 : (n != 8 && n != 11) ? 2 : 3'
    },
    {
        u'code': u'cy-GB', u'name': u'Welsh'
    },
    {
        u'code': u'fy',
        u'name': u'Western Frisian',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'fy-NL', u'name': u'Western Frisian'
    },
    {
        u'code': u'wo',
        u'name': u'Wolof',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'wo-SN', u'name': u'Wolof'
    },
    {
        u'code': u'xh',
        u'name': u'Xhosa',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'yi', u'name': u'Yiddish'
    },
    {
        u'code': u'yo',
        u'name': u'Yoruba',
        u'nplurals': u'2',
        u'plural_rule': u'(n != 1)'
    },
    {
        u'code': u'zu', u'name': u'Zulu'
    },
    {
        u'code': u'zu-ZA', u'name': u'Zulu'
    },
    {
        u'code': u'dsb',
        u'name': u'Lower Sorbian',
        u'nplurals': u'4',
        u'plural_rule': u'(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3)'
    }]
