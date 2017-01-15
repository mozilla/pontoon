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

HEROKU_DEMO = os.environ.get('HEROKU_DEMO', 'False') != 'False'

DJANGO_LOGIN = os.environ.get('DJANGO_LOGIN', 'False') != 'False' or HEROKU_DEMO

ADMINS = MANAGERS = (
    (os.environ.get('ADMIN_NAME', ''),
     os.environ.get('ADMIN_EMAIL', '')),
)

# A list of project manager email addresses to send project requests to
PROJECT_MANAGERS = os.environ.get('PROJECT_MANAGERS', '').split(',')

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

APP_URL_KEY = 'APP_URL'

# For the sake of integration with Heroku, we dynamically load domain name
# From the file that's set right after the build phase.
if os.environ.get('HEROKU_DEMO') and not os.environ.get('SITE_URL'):
    def _site_url():
        from django.contrib.sites.models import Site
        from django.core.cache import cache

        app_url = cache.get(APP_URL_KEY)

        # Sometimes data from cache is flushed, We can't do anything about that.
        if not app_url:
            app_url = "https://{}".format(Site.objects.get(pk=1).domain)
            cache.set(APP_URL_KEY, app_url)

        return app_url

    SITE_URL = lazy(_site_url, str)()
else:
    SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')

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

# Raygun.io configuration
RAYGUN4PY_CONFIG = {
    'api_key': os.environ.get('RAYGUN_APIKEY', '')
}

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
    'pontoon.sync',

    # Django contrib apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    # Django sites app is required by django-allauth
    'django.contrib.sites',

    # Third-party apps, patches, fixes
    'commonware.response.cookies',
    'django_jinja',
    'django_nose',
    'pipeline',
    'session_csrf',
    'guardian',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.fxa',
)

BLOCKED_IPS = os.environ.get('BLOCKED_IPS', '').split(',')

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'sslify.middleware.SSLifyMiddleware',
    'pontoon.base.middleware.RaygunExceptionMiddleware',
    'pontoon.base.middleware.BlockedIpMiddleware',
    'pontoon.base.middleware.HerokuDemoSetupMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
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
            'match_regex': r'^(?!(admin|registration|account|socialaccount)/).*\.(html|jinja|js)$',
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
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [path('pontoon/base/templates/django')],
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': CONTEXT_PROCESSORS,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        }
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
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
    'manage_permissions': {
        'source_filenames': (
            'css/manage_permissions.css',
        ),
        'output_filename': 'css/manage_permissions.min.css',
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
            'css/jquery-ui.css',
            'css/jquery-ui-timepicker-addon.css',
            'css/translate.css',
        ),
        'output_filename': 'css/translate.min.css',
    },
    'user': {
        'source_filenames': (
            'css/user.css',
            'css/user_profile.css',
        ),
        'output_filename': 'css/user.min.css',
    },
    'user_settings': {
        'source_filenames': (
            'css/user.css',
            'css/user_settings.css',
        ),
        'output_filename': 'css/user_settings.min.css',
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
    'multiple_locale_selector': {
        'source_filenames': ('css/multiple_locale_selector.css',),
        'output_filename': 'css/multiple_locale_selector.min.css',
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
            'js/lib/jquery-1.11.1.min.js',
            'js/main.js',
            'js/lib/jquery.timeago.js',
        ),
        'output_filename': 'js/main.min.js',
    },
    'manage_permissions': {
        'source_filenames': (
            'js/manage_permissions.js',
        ),
        'output_filename': 'js/manage_permissions.min.js',
    },
    'locale': {
        'source_filenames': (
            'js/request_projects.js',
        ),
        'output_filename': 'js/locale.min.js',
    },
    'translate': {
        'source_filenames': (
            'js/lib/jquery-ui.js',
            'js/lib/jquery-ui-timepicker-addon.js',
            'js/lib/jquery.mark.js',
            'js/lib/highstock.js',
            'js/lib/diff.js',
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
            'js/lib/clipboard.min.js',
            'js/search.js',
        ),
        'output_filename': 'js/search.min.js',
    },
    'multiple_locale_selector': {
        'source_filenames': (
            'js/lib/jquery-ui.js',
            'js/multiple_locale_selector.js',
        ),
        'output_filename': 'js/multiple_locale_selector.min.js',
    }
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
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s:%(name)s] %(asctime)s %(message)s'
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
    }
}

if DEBUG:
    LOGGING['handlers']['console']['formatter'] = 'verbose'


if os.environ.get('DJANGO_SQL_LOG', False):
    LOGGING['loggers']['django.db.backends'] = {
        'level': 'DEBUG',
        'handlers': ['console']
    }

## Tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--logging-filter=-factory,-django.db,-raygun4py',
             '--logging-clear-handlers']

# Disable nose-progressive on CI due to ugly output.
if not os.environ.get('CI', False):
    NOSE_ARGS.append('--with-progressive')

# General auth settings
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = '/'

# Should robots.txt deny everything or disallow a calculated list of
# URLs we don't want to be crawled?  Default is false, disallow
# everything.
ENGAGE_ROBOTS = False

# Always generate a CSRF token for anonymous users.
ANON_ALWAYS = True

# Set X-Frame-Options to DENY by default on all responses.
X_FRAME_OPTIONS = 'DENY'

# Use correct header for detecting HTTPS on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Strict-Transport-Security: max-age=63072000
# Ensures users only visit the site over HTTPS
SECURE_HSTS_SECONDS = 63072000

# X-Content-Type-Options: nosniff
# Disables browser MIME type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# x-xss-protection: 1; mode=block
# Activates the browser's XSS filtering and helps prevent XSS attacks
SECURE_BROWSER_XSS_FILTER = True

# Content-Security-Policy headers
CSP_DEFAULT_SRC = ("'none'",)
CSP_CHILD_SRC = ("https:",)
CSP_FRAME_SRC = ("https:",)  # Older browsers
CSP_CONNECT_SRC = ("'self'",)
CSP_FONT_SRC = ("'self'",)
CSP_IMG_SRC = (
    "'self'",
    "https://*.wp.com/pontoon.mozilla.org/",
    "https://ssl.google-analytics.com",
    "https://www.gravatar.com/avatar/",
)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-eval'",
    "'sha256-x3niK4UU+vG6EGT2NK2rwi2j/etQodJd840oRpEnqd4='",
    "'sha256-fDsgbzHC0sNuBdM4W91nXVccgFLwIDkl197QEca/Cl4='",
    "https://ssl.google-analytics.com/ga.js",
)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'",)

# Needed if site not hosted on HTTPS domains (like local setup)
if not (HEROKU_DEMO or SITE_URL.startswith('https')):
    CSP_IMG_SRC = CSP_IMG_SRC + ("http://www.gravatar.com/avatar/",)
    CSP_CHILD_SRC = CSP_FRAME_SRC = CSP_FRAME_SRC + ("http:",)

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

SYNC_TASK_TIMEOUT = 60 * 60 * 1  # 1 hour

SYNC_LOG_RETENTION = 90  # days

MANUAL_SYNC = os.environ.get('MANUAL_SYNC', 'False') != 'False'

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

# Settings related to the CORS mechanisms.
# For the sake of integration with other sites,
# some of javascript files (e.g. pontoon.js)
# require Access-Control-Allow-Origin header to be set as '*'.
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/pontoon\.js$'

SOCIALACCOUNT_ENABLED = True
SOCIALACCOUNT_ADAPTER = 'pontoon.base.adapter.PontoonSocialAdapter'

def account_username(user):
    return user.name_or_email

ACCOUNT_AUTHENTICATED_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USER_DISPLAY = account_username

# Firefox Accounts
FXA_CLIENT_ID = os.environ.get('FXA_CLIENT_ID', '')
FXA_SECRET_KEY = os.environ.get('FXA_SECRET_KEY', '')
FXA_OAUTH_ENDPOINT = os.environ.get('FXA_OAUTH_ENDPOINT', '')
FXA_PROFILE_ENDPOINT = os.environ.get('FXA_PROFILE_ENDPOINT', '')
FXA_SCOPE = ['profile:uid', 'profile:display_name', 'profile:email']

# All settings related to the AllAuth
SOCIALACCOUNT_PROVIDERS = {
    'fxa': {
        'SCOPE': FXA_SCOPE,
        'OAUTH_ENDPOINT': FXA_OAUTH_ENDPOINT,
        'PROFILE_ENDPOINT': FXA_PROFILE_ENDPOINT,
    }
}

# Defined all trusted origins that will be returned in pontoon.js file.
if os.environ.get('JS_TRUSTED_ORIGINS'):
    JS_TRUSTED_ORIGINS = os.environ.get('JS_TRUSTED_ORIGINS').split(',')
else:
    JS_TRUSTED_ORIGINS = [
        SITE_URL,
    ]
