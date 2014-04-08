# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

from funfactory.settings_base import *

# Name of the top-level module where you put all your apps.
# If you did not install Playdoh with the funfactory installer script
# you may need to edit this value. See the docs about installing from a
# clone.
PROJECT_MODULE = 'pontoon'

# Defines the views served for root URLs.
ROOT_URLCONF = '%s.urls' % PROJECT_MODULE

INSTALLED_APPS = list(INSTALLED_APPS) + [
    # Application base, containing global templates.
    '%s.base' % PROJECT_MODULE,
    '%s.administration' % PROJECT_MODULE,
    'django.contrib.admin', 
    'south',
]

LOCALE_PATHS = (
    os.path.join(ROOT, PROJECT_MODULE, 'locale'),
)

# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
    'registration',
]

# BrowserID configuration
AUTHENTICATION_BACKENDS = [
    'django_browserid.auth.BrowserIDBackend',
    'django.contrib.auth.backends.ModelBackend',
]

SITE_URL = 'http://127.0.0.1:8000'
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = '/'

TEMPLATE_CONTEXT_PROCESSORS = list(TEMPLATE_CONTEXT_PROCESSORS) + [
    'django_browserid.context_processors.browserid',
]

# Should robots.txt deny everything or disallow a calculated list of URLs we
# don't want to be crawled?  Default is false, disallow everything.
# Also see http://www.google.com/support/webmasters/bin/answer.py?answer=93710
ENGAGE_ROBOTS = False

# Always generate a CSRF token for anonymous users.
ANON_ALWAYS = True

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS['messages'] = [
    ('%s/**.py' % PROJECT_MODULE,
        'tower.management.commands.extract.extract_tower_python'),
    ('%s/**/templates/**.html' % PROJECT_MODULE,
        'tower.management.commands.extract.extract_tower_template'),
    ('templates/**.html',
        'tower.management.commands.extract.extract_tower_template'),
]

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['lhtml'] = [
#    ('**/templates/**.lhtml',
#        'tower.management.commands.extract.extract_tower_template'),
# ]

# # Use this if you have localizable JS files:
# DOMAIN_METHODS['javascript'] = [
#    # Make sure that this won't pull in strings from external libraries you
#    # may use.
#    ('media/js/**.js', 'javascript'),
# ]

LOGGING = dict(loggers=dict(pontoon = {'level': logging.DEBUG}))

# Required for storing additional information about users
AUTH_PROFILE_MODULE = 'base.UserProfile'

# Microsoft Translator Locales
MICROSOFT_TRANSLATOR_LOCALES = [
    'ar', 'bg', 'ca', 'zh-CHS', 'zh-CHT', 'cs', 'da', 'nl', 'en', 'et', 'fi',
    'fr', 'de', 'el', 'ht', 'he', 'hi', 'mww', 'hu', 'id', 'it', 'ja', 'tlh',
    'tlh-Qaak', 'ko', 'lv', 'lt', 'ms', 'mt', 'no', 'fa', 'pl', 'pt', 'ro',
    'ru', 'sk', 'sl', 'es', 'sv', 'th', 'tr', 'uk', 'ur', 'vi', 'cy'
]

# Microsoft Terminology Service API Locales
MICROSOFT_TERMINOLOGY_LOCALES = [
    'af-za', 'am-et', 'ar-cl', 'ar-eg', 'ar-sa', 'as-in', 'az-latn-az',
    'be-by', 'bg-bg', 'bn-bd', 'bn-in', 'bs-cyrl-ba', 'bs-latn-ba', 'ca-es',
    'ca-es-valencia', 'chr-cher-us', 'cs-cz', 'cy-gb', 'da-dk', 'de-at',
    'de-ch', 'de-de', 'el-gr', 'en-au', 'en-ca', 'en-gb', 'en-ie', 'en-my',
    'en-nz', 'en-ph', 'en-sg', 'en-us', 'en-za', 'es-es', 'es-mx', 'es-us',
    'et-ee', 'eu-es', 'fa-ir', 'fi-fi', 'fil-ph', 'fr-be', 'fr-ca', 'fr-ch',
    'fr-fr', 'fr-lu', 'fuc-latn-sn', 'ga-ie', 'gd-gb', 'gl-es', 'gu-in',
    'guc-ve', 'ha-latn-ng', 'he-il', 'hi-in', 'hr-hr', 'hu-hu', 'hy-am',
    'id-id', 'ig-ng', 'is-is', 'it-ch', 'it-it', 'iu-latn-ca', 'ja-jp',
    'ka-ge', 'kk-kz', 'km-kh', 'kn-in', 'ko-kr', 'kok-in', 'ku-arab-iq',
    'ky-kg', 'lb-lu', 'lo-la', 'lt-lt', 'lv-lv', 'mi-nz', 'mk-mk', 'ml-in',
    'mn-mn', 'mr-in', 'ms-bn', 'ms-my', 'mt-mt', 'nb-no', 'ne-np', 'nl-be',
    'nl-nl', 'nn-no', 'nso-za', 'or-in', 'pa-arab-pk', 'pa-in', 'pl-pl',
    'prs-af', 'ps-af', 'pt-br', 'pt-pt', 'qut-gt', 'quz-pe', 'rm-ch',
    'ro-ro', 'ru-ru', 'rw-rw', 'sd-arab-pk', 'si-lk', 'sk-sk', 'sl-si',
    'sp-xl', 'sq-al', 'sr-cyrl-ba', 'sr-cyrl-rs', 'sr-latn-rs', 'sv-se',
    'sw-ke', 'ta-in', 'te-in', 'tg-cyrl-tj', 'th-th', 'ti-et', 'tk-tm',
    'tl-ph', 'tn-za', 'tr-tr', 'tt-ru', 'ug-cn', 'uk-ua', 'ur-pk',
    'uz-latn-uz', 'vi-vn', 'wo-sn', 'xh-za', 'yo-ng', 'zh-cn', 'zh-hk',
    'zh-tw', 'zu-za'
]
