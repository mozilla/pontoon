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

DEBUG = os.environ.get('DJANGO_DEBUG', 'False') != 'False'

ADMINS = MANAGERS = (
    (os.environ.get('ADMIN_NAME', ''),
     os.environ.get('ADMIN_EMAIL', '')),
)

DATABASES = {
    'default': dj_database_url.config(default='mysql://root@localhost/pontoon')
}

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.environ.get('STATIC_ROOT', path('static'))

# Optional CDN hostname for static files, e.g. '//asdf.cloudfront.net'
STATIC_HOST = os.environ.get('STATIC_HOST', '')

SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True') != 'False'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True') != 'False'

SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')
BROWSERID_AUDIENCES = [SITE_URL]

# Custom LD_LIBRARY_PATH environment variable for SVN
SVN_LD_LIBRARY_PATH = os.environ.get('SVN_LD_LIBRARY_PATH', '')

# Disable forced SSL if debug mode is enabled or if CI is running the
# tests.
SSLIFY_DISABLE = DEBUG or os.environ.get('CI', False)

# URL to the RabbitMQ server
BROKER_URL = os.environ.get('RABBITMQ_URL', None)

# Microsoft Translator API Key
MICROSOFT_TRANSLATOR_API_KEY = os.environ.get('MICROSOFT_TRANSLATOR_API_KEY', '')

# Google Analytics Key
GOOGLE_ANALYTICS_KEY = os.environ.get('GOOGLE_ANALYTICS_KEY', '')

# Raygun.io API Key
RAYGUN4PY_API_KEY = os.environ.get('RAYGUN_APIKEY', '')

# Email settings
EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME', '')
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD', '')

# Log emails to console if the SendGrid credentials are missing.
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Environment-independent settings. These shouldn't have to change
# between server environments.
ROOT_URLCONF = 'pontoon.urls'

INSTALLED_APPS = (
    'pontoon.base',
    'pontoon.administration',
    'pontoon.intro',
    'pontoon.sites',
    'pontoon.sync',

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
    'django_nose',
    'pipeline',
    'session_csrf',
    'guardian',
)

BLOCKED_IPS = os.environ.get('BLOCKED_IPS', '').split(',')

MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',
    'pontoon.base.middleware.RaygunExceptionMiddleware',
    'pontoon.base.middleware.BlockedIpMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.debug',
    'django.template.context_processors.media',
    'django.template.context_processors.request',
    'session_csrf.context_processor',
    'django.contrib.messages.context_processors.messages',
    'pontoon.base.context_processors.globals',
)

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'APP_DIRS': True,
        'OPTIONS': {
            'match_extension': '',
            'match_regex': r'^(?!(admin|registration)/).*\.(html|jinja)$',
            'context_processors': CONTEXT_PROCESSORS,
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
                'pipeline.templatetags.ext.PipelineExtension',
            ],
            'globals': {
                'browserid_info': 'django_browserid.helpers.browserid_info',
            }
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': CONTEXT_PROCESSORS
        }
    },
]

AUTHENTICATION_BACKENDS = [
    'django_browserid.auth.BrowserIDBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
]

# This variable is required by django-guardian.
# App supports giving permissions for anonymous users.
ANONYMOUS_USER_ID = -1
GUARDIAN_RAISE_403 = True

PIPELINE_COMPILERS = (
    'pipeline.compilers.es6.ES6Compiler',
)

PIPELINE_YUGLIFY_BINARY = path('node_modules/.bin/yuglify')
PIPELINE_BABEL_BINARY = path('node_modules/.bin/babel')
PIPELINE_BABEL_ARGUMENTS = '--modules ignore'

PIPELINE_DISABLE_WRAPPER = True
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
    'locale_manage': {
        'source_filenames': (
            'css/locale_manage.css',
        ),
        'output_filename': 'css/locale_manage.min.css',
    },
    'locale_project': {
        'source_filenames': (
            'css/locale_project.css',
        ),
        'output_filename': 'css/locale_project.min.css',
    },
    'locales': {
        'source_filenames': (
            'css/locales.css',
        ),
        'output_filename': 'css/locales.min.css',
    },
    'locale': {
        'source_filenames': (
            'css/locale.css',
        ),
        'output_filename': 'css/locale.min.css',
    },
    'sync_logs': {
        'source_filenames': (
            'css/sync_logs.css',
        ),
        'output_filename': 'css/sync_logs.min.css',
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
    'intro': {
        'source_filenames': (
            'css/bootstrap.min.css',
            'css/agency.css',
        ),
        'output_filename': 'css/intro.min.css',
    },
}

PIPELINE_JS = {
    'admin_project': {
        'source_filenames': (
            'js/admin_project.js',
        ),
        'output_filename': 'js/admin_project.min.js',
    },
    'main': {
        'source_filenames': (
            'js/jquery-1.11.1.min.js',
            'js/main.js',
            'js/jquery.timeago.js',
        ),
        'output_filename': 'js/main.min.js',
    },
    'locale_manage': {
        'source_filenames': (
            'js/locale_manage.js',
        ),
        'output_filename': 'js/locale_manage.min.js',
    },
    'locale': {
        'source_filenames': (
            'js/request_projects.js',
        ),
        'output_filename': 'js/locale.min.js',
    },
    'translate': {
        'source_filenames': (
            'js/translate.js',
            'js/request_projects.js',
        ),
        'output_filename': 'js/translate.min.js',
    },
    'user': {
        'source_filenames': (
            'js/user.js',
        ),
        'output_filename': 'js/user.min.js',
    },
    'search': {
        'source_filenames': (
            'js/search.js',
        ),
        'output_filename': 'js/search.min.js',
    },
}

# Cache config
# If the environment contains configuration data for Memcached, use
# PyLibMC for the cache backend. Otherwise, default to an in-memory
# cache.
if os.environ.get('MEMCACHE_SERVERS') is not None:
    CACHES = {
        'default': {
            'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
            'TIMEOUT': 500,
            'BINARY': True,
            'OPTIONS': {}
        }
    }
else:
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

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = STATIC_HOST + '/static/'

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
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
)

## Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
        },
        'pontoon': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'django_browserid': {
            'handlers': ['console'],
        },
    }
}

## Tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--logging-filter=-django_browserid,-factory,-django.db,-raygun4py',
             '--logging-clear-handlers']

# Disable nose-progressive on CI due to ugly output.
if not os.environ.get('CI', False):
    NOSE_ARGS.append('--with-progressive')

# Set X-Frame-Options to DENY by default on all responses.
X_FRAME_OPTIONS = 'DENY'

# django-browserid
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = '/'
BROWSERID_REQUEST_ARGS = {'siteName': 'Pontoon'}

# Should robots.txt deny everything or disallow a calculated list of
# URLs we don't want to be crawled?  Default is false, disallow
# everything.
ENGAGE_ROBOTS = False

# Always generate a CSRF token for anonymous users.
ANON_ALWAYS = True

# Use correct header for detecting HTTPS on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

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

# Enable timezone-aware datetimes.
USE_TZ = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = os.environ.get('TZ', 'UTC')

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

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
EXCLUDE = os.environ.get('EXCLUDE', '').split(',')

SYNC_TASK_TIMEOUT = 60 * 60 * 4  # 4 hours

SYNC_LOG_RETENTION = 90  # days

# Celery

# Execute celery tasks locally instead of in a worker unless the
# environment is configured.
CELERY_ALWAYS_EAGER = os.environ.get('CELERY_ALWAYS_EAGER', 'True') != 'False'

# Limit the number of tasks a celery worker can handle before being replaced.
try:
    CELERYD_MAX_TASKS_PER_CHILD = int(os.environ.get('CELERYD_MAX_TASKS_PER_CHILD', ''))
except ValueError:
    CELERYD_MAX_TASKS_PER_CHILD = 20

BROKER_POOL_LIMIT = 1  # Limit to one connection per worker
BROKER_CONNECTION_TIMEOUT = 30  # Give up connecting faster
CELERY_RESULT_BACKEND = None  # We don't store results
CELERY_SEND_EVENTS = False  # We aren't yet monitoring events
