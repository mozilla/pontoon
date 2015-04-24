"""Django settings for Pontoon."""
import os
import socket

from django.utils.functional import lazy

import dj_database_url


_dirname = os.path.dirname
ROOT = _dirname(_dirname(_dirname(os.path.abspath(__file__))))


def path(*args):
    return os.path.join(ROOT, *args)


# Environment-dependent settings. These are loaded from environment
# variables.

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ['SECRET_KEY']

# Is this a dev instance?
DEV = os.environ.get('DJANGO_DEV', 'False') != 'False'

DEBUG = TEMPLATE_DEBUG = os.environ.get('DJANGO_DEBUG', 'False') != 'False'

ADMINS = MANAGERS = (
    (os.environ.get('ADMIN_NAME', ''),
     os.environ.get('ADMIN_EMAIL', '')),
)

DATABASES = {
    'default': dj_database_url.config(default='mysql://root@localhost/pontoon')
}

SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True') != 'False'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True') != 'False'

HMAC_KEYS = {
    'hmac-key': os.environ['HMAC_KEY'],
}

SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')

# Microsoft Translator API Key
MICROSOFT_TRANSLATOR_API_KEY = os.environ.get('MICROSOFT_TRANSLATOR_API_KEY', '')

# Google Analytics Key
GOOGLE_ANALYTICS_KEY = os.environ.get('GOOGLE_ANALYTICS_KEY', '')

# Mozillians API Key
MOZILLIANS_API_KEY = os.environ.get('MOZILLIANS_API_KEY', '')


# Environment-independent settings. These shouldn't have to change
# between server environments.
ROOT_URLCONF = 'pontoon.urls'

INSTALLED_APPS = (
    'pontoon.base',
    'pontoon.administration',
    'pontoon.intro',

    # Django contrib apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    # Third-party apps, patches, fixes
    'commonware.response.cookies',
    'django_browserid',
    'django_jinja',
    'pipeline',
    'product_details',
    'session_csrf',
    'tower',
)

MIDDLEWARE_CLASSES = (
    'multidb.middleware.PinningRouterMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'session_csrf.context_processor',
    'django.contrib.messages.context_processors.messages',
    'pontoon.base.context_processors.i18n',
    'pontoon.base.context_processors.globals',
    'django_browserid.context_processors.browserid',
)

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'APP_DIRS': True,
        'OPTIONS': {
            'match_extension': '',
            'match_regex': r'^(?!(admin|registration)/).*\.(html|jinja)$',
            'context_processors': TEMPLATE_CONTEXT_PROCESSORS,
            'extensions': [
                'jinja2.ext.do',
                'jinja2.ext.loopcontrols',
                'jinja2.ext.with_',
                'jinja2.ext.i18n',
                'jinja2.ext.autoescape',
                'django_jinja.builtins.extensions.CsrfExtension',
                'django_jinja.builtins.extensions.CacheExtension',
                'django_jinja.builtins.extensions.TimezoneExtension',
                'django_jinja.builtins.extensions.UrlsExtension',
                'django_jinja.builtins.extensions.StaticFilesExtension',
                'django_jinja.builtins.extensions.DjangoFiltersExtension',
                'pipeline.jinja2.ext.PipelineExtension',
            ],
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': TEMPLATE_CONTEXT_PROCESSORS
        }
    },
]

AUTHENTICATION_BACKENDS = [
    'django_browserid.auth.BrowserIDBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Paths containing translation files for the site.
LOCALE_PATHS = (
    os.path.join(ROOT, 'pontoon', 'locale'),
)

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        ('pontoon/**.py',
            'tower.management.commands.extract.extract_tower_python'),
        ('pontoon/**/templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
        ('templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
    ]
}

# Temporarily do not compress CSS or JS until we figure out the issue
# with Heroku failing to compress static files.
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.NoopCompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.NoopCompressor'

PIPELINE_CSS = {
    'base': {
        'source_filenames': (
            'css/style.css',
            'css/font-awesome.css',
        ),
        'output_filename': 'css/base.min.css',
    },
    'admin': {
        'source_filenames': (
            'css/admin.css',
        ),
        'output_filename': 'css/admin.min.css',
    },
    'admin_project': {
        'source_filenames': (
            'css/admin_project.css',
        ),
        'output_filename': 'css/admin_project.min.css',
    },
    'project': {
        'source_filenames': (
            'css/project.css',
        ),
        'output_filename': 'css/project.min.css',
    },
    'translate': {
        'source_filenames': (
            'css/translate.css',
        ),
        'output_filename': 'css/translate.min.css',
    },
    'user': {
        'source_filenames': (
            'css/user.css',
        ),
        'output_filename': 'css/user.min.css',
    },
    'users': {
        'source_filenames': (
            'css/users.css',
        ),
        'output_filename': 'css/users.min.css',
    },
}

PIPELINE_JS = {
    'admin': {
        'source_filenames': (
            'js/admin.js',
        ),
        'output_filename': 'js/admin.min.js',
    },
    'admin_project': {
        'source_filenames': (
            'js/admin_project.js',
        ),
        'output_filename': 'js/admin_project.min.js',
    },
    'main': {
        'source_filenames': (
            'js/main.js',
        ),
        'output_filename': 'js/main.min.js',
    },
    'locale': {
        'source_filenames': (
            'js/locale.js',
        ),
        'output_filename': 'js/locale.min.js',
    },
    'project': {
        'source_filenames': (
            'js/project.js',
        ),
        'output_filename': 'js/project.min.js',
    },
    'projects': {
        'source_filenames': (
            'js/projects.js',
        ),
        'output_filename': 'js/projects.min.js',
    },
    'translate': {
        'source_filenames': (
            'js/translate.js',
            'js/jquery.timeago.js',
        ),
        'output_filename': 'js/translate.min.js',
    },
    'user': {
        'source_filenames': (
            'js/user.js',
        ),
        'output_filename': 'js/user.min.js',
    },
}

DATABASE_ROUTERS = ('multidb.PinningMasterSlaveRouter',)

# Cache config
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'pontoon'
    }
}

# Site ID is used by Django's Sites framework.
SITE_ID = 1

## Media and templates.

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = path('static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

STATICFILES_STORAGE = 'pontoon.base.storage.GzipManifestPipelineStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)


# Set ALLOWED_HOSTS based on SITE_URL setting.
def _allowed_hosts():
    from django.conf import settings
    from urlparse import urlparse

    host = urlparse(settings.SITE_URL).netloc  # Remove protocol and path
    host = host.rsplit(':', 1)[0]  # Remove port
    return [host]
ALLOWED_HOSTS = lazy(_allowed_hosts, list)()

## Auth
# The first hasher in this list will be used for new passwords.
# Any other hasher in the list can be used for existing passwords.
# Playdoh ships with Bcrypt+HMAC by default because it's the most secure.
# To use bcrypt, fill in a secret HMAC key in your local settings.
BASE_PASSWORD_HASHERS = (
    'django_sha2.hashers.BcryptHMACCombinedPasswordVerifier',
    'django_sha2.hashers.SHA512PasswordHasher',
    'django_sha2.hashers.SHA256PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
)

from django_sha2 import get_password_hashers
PASSWORD_HASHERS = get_password_hashers(BASE_PASSWORD_HASHERS, HMAC_KEYS)

## Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
        }
    }
}

## Tests
TEST_RUNNER = 'test_utils.runner.RadicalTestSuiteRunner'

# Set X-Frame-Options to DENY by default on all responses.
X_FRAME_OPTIONS = 'DENY'

# django-browserid
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = '/'

# Should robots.txt deny everything or disallow a calculated list of
# URLs we don't want to be crawled?  Default is false, disallow
# everything.
ENGAGE_ROBOTS = False

# Always generate a CSRF token for anonymous users.
ANON_ALWAYS = True

# For absolute urls
try:
    DOMAIN = socket.gethostname()
except socket.error:
    DOMAIN = 'localhost'
PROTOCOL = "http://"
PORT = 80

# Names for slave databases from the DATABASES setting.
SLAVE_DATABASES = []

## Internationalization.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Gettext text domain
TEXT_DOMAIN = 'messages'
STANDALONE_DOMAINS = [TEXT_DOMAIN, 'javascript']
TOWER_KEYWORDS = {'_lazy': None}
TOWER_ADD_HEADERS = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

## Accepted locales

# Tells the product_details module where to find our local JSON files.
# This ultimately controls how LANGUAGES are constructed.
PROD_DETAILS_DIR = path('lib/product_details_json')

# On dev instances, the list of accepted locales defaults to the contents of
# the `locale` directory within a project module or, for older Playdoh apps,
# the root locale directory.  A localizer can add their locale in the l10n
# repository (copy of which is checked out into `locale`) in order to start
# testing the localization on the dev server.
import glob
import itertools
try:
    DEV_LANGUAGES = [
        os.path.basename(loc).replace('_', '-')
        for loc in itertools.chain(glob.iglob(ROOT + '/locale/*'),  # old style
                                   glob.iglob(ROOT + '/*/locale/*'))
        if (os.path.isdir(loc) and os.path.basename(loc) != 'templates')
    ]
except OSError:
    DEV_LANGUAGES = ('en-US',)

# On stage/prod, the list of accepted locales is manually maintained.  Only
# locales whose localizers have signed off on their work should be listed here.
PROD_LANGUAGES = (
    'en-US',
)

def lazy_lang_url_map():
    from django.conf import settings
    langs = settings.DEV_LANGUAGES if settings.DEV else settings.PROD_LANGUAGES
    return dict([(i.lower(), i) for i in langs])

LANGUAGE_URL_MAP = lazy(lazy_lang_url_map, dict)()

# Override Django's built-in with our native names
def lazy_langs():
    from django.conf import settings
    from product_details import product_details
    langs = DEV_LANGUAGES if settings.DEV else settings.PROD_LANGUAGES
    return dict([(lang.lower(), product_details.languages[lang]['native'])
                 for lang in langs if lang in product_details.languages])

LANGUAGES = lazy(lazy_langs, dict)()

# Paths that don't require a locale code in the URL.
SUPPORTED_NONLOCALES = ['media', 'static', 'admin']

# Microsoft Translator Locales
MICROSOFT_TRANSLATOR_LOCALES = [
    'ar', 'bs-Latn', 'bg', 'ca', 'zh-CHS', 'zh-CHT', 'hr', 'cs', 'da', 'nl',
    'en', 'et', 'fi', 'fr', 'de', 'el', 'ht', 'he', 'hi', 'mww', 'hu', 'id',
    'it', 'ja', 'tlh', 'tlh-Qaak', 'ko', 'lv', 'lt', 'ms', 'mt', 'yua', 'no',
    'otq', 'fa', 'pl', 'pt', 'ro', 'ru', 'sr-Cyrl', 'sr-Latn', 'sk', 'sl',
    'es', 'sv', 'th', 'tr', 'uk', 'ur', 'vi', 'cy'
]

# Microsoft Terminology Service API Locales
MICROSOFT_TERMINOLOGY_LOCALES = [
    'af-za', 'am-et', 'ar-eg', 'ar-sa', 'as-in', 'az-latn-az', 'be-by',
    'bg-bg', 'bn-bd', 'bn-in', 'bs-cyrl-ba', 'bs-latn-ba', 'ca-es',
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
    'prs-af', 'ps-af', 'pt-br', 'pt-pt', 'qut-gt', 'quz-pe', 'rm-ch', 'ro-ro',
    'ru-ru', 'rw-rw', 'sd-arab-pk', 'si-lk', 'sk-sk', 'sl-si', 'sp-xl',
    'sq-al', 'sr-cyrl-ba', 'sr-cyrl-rs', 'sr-latn-rs', 'sv-se', 'sw-ke',
    'ta-in', 'te-in', 'tg-cyrl-tj', 'th-th', 'ti-et', 'tk-tm', 'tl-ph',
    'tn-za', 'tr-tr', 'tt-ru', 'ug-cn', 'uk-ua', 'ur-pk', 'uz-latn-uz',
    'vi-vn', 'wo-sn', 'xh-za', 'yo-ng', 'zh-cn', 'zh-hk', 'zh-tw', 'zu-za',
]

# Contributors to exclude from Top Contributors list
EXCLUDE = []
