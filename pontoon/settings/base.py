"""Django settings for Pontoon."""
import re
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
SECRET_KEY = os.environ["SECRET_KEY"]

# Is this a dev instance?
DEV = os.environ.get("DJANGO_DEV", "False") != "False"

DEBUG = os.environ.get("DJANGO_DEBUG", "False") != "False"

HEROKU_DEMO = os.environ.get("HEROKU_DEMO", "False") != "False"

LOGOUT_REDIRECT_URL = "/"

ADMINS = MANAGERS = (
    (os.environ.get("ADMIN_NAME", ""), os.environ.get("ADMIN_EMAIL", "")),
)

# A list of project manager email addresses to send project requests to
PROJECT_MANAGERS = os.environ.get("PROJECT_MANAGERS", "").split(",")

# VCS identity to be used when committing translations.
VCS_SYNC_NAME = os.environ.get("VCS_SYNC_NAME", "Pontoon")
VCS_SYNC_EMAIL = os.environ.get("VCS_SYNC_EMAIL", "pontoon@example.com")

DATABASES = {
    "default": dj_database_url.config(default="mysql://root@localhost/pontoon")
}

# Ensure that psycopg2 uses a secure SSL connection.
if not DEV and not DEBUG:
    if "OPTIONS" not in DATABASES["default"]:
        DATABASES["default"]["OPTIONS"] = {}
    DATABASES["default"]["OPTIONS"]["sslmode"] = "require"

TAGADMIN_DIR = os.path.join(ROOT, "tag-admin")
TRANSLATE_DIR = os.path.join(ROOT, "translate")

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.environ.get("STATIC_ROOT", path("static"))

# Optional CDN hostname for static files, e.g. '//asdf.cloudfront.net'
STATIC_HOST = os.environ.get("STATIC_HOST", "")

SESSION_COOKIE_HTTPONLY = os.environ.get("SESSION_COOKIE_HTTPONLY", "True") != "False"
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "True") != "False"

APP_URL_KEY = "APP_URL"

SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000")

# Custom LD_LIBRARY_PATH environment variable for SVN
SVN_LD_LIBRARY_PATH = os.environ.get("SVN_LD_LIBRARY_PATH", "")

# URL to the RabbitMQ server
BROKER_URL = os.environ.get("RABBITMQ_URL", None)

# Google Cloud Translation API key
GOOGLE_TRANSLATE_API_KEY = os.environ.get("GOOGLE_TRANSLATE_API_KEY", "")

# Pontoon locale codes supported by Google Cloud AutoML Translation Project ID
#
# Source:
# https://cloud.google.com/translate/automl/docs/languages#supported_codes_for_language_variants
GOOGLE_AUTOML_SUPPORTED_LOCALES = [
    "af",
    "ar",
    "az",
    "bg",
    "bn",
    "ca",
    "cs",
    "cy",
    "da",
    "de",
    "el",
    "es",
    "es-AR",
    "es-CL",
    "es-ES",
    "es-MX",
    "et",
    "fa",
    "fi",
    "fil",
    "fr",
    "gl",
    "gu-IN",
    "he",
    "hi",
    "hi-IN",
    "hr",
    "ht",
    "hu",
    "id",
    "is",
    "it",
    "ja",
    "jv",
    "ka",
    "km",
    "ko",
    "lt",
    "lv",
    "mr",
    "ms",
    "my",
    "nb-NO",
    "ne-NP",
    "nl",
    "pa-IN",
    "pa-PK",
    "pl",
    "ps",
    "pt",
    "pt-BR",
    "pt-PT",
    "ro",
    "ru",
    "sk",
    "sl",
    "sq",
    "sr",
    "sv-SE",
    "sw",
    "ta",
    "te",
    "th",
    "tr",
    "uk",
    "ur",
    "uz",
    "vi",
    "zh-CN",
    "zh-HK",
    "zh-TW",
    "zu",
]

# Google Cloud AutoML Translation Project ID
GOOGLE_AUTOML_PROJECT_ID = os.environ.get("GOOGLE_AUTOML_PROJECT_ID", "")

# It is recommended to make Google Cloud AutoML Translation warmup requests every minute,
# although in our experience every 5 minutes (300 seconds) is sufficient.
GOOGLE_AUTOML_WARMUP_INTERVAL = float(
    os.environ.get("GOOGLE_AUTOML_WARMUP_INTERVAL", "300")
)

# Microsoft Translator API Key
MICROSOFT_TRANSLATOR_API_KEY = os.environ.get("MICROSOFT_TRANSLATOR_API_KEY", "")

# SYSTRAN Translate Settings
SYSTRAN_TRANSLATE_API_KEY = os.environ.get("SYSTRAN_TRANSLATE_API_KEY", "")
SYSTRAN_TRANSLATE_SERVER = os.environ.get("SYSTRAN_TRANSLATE_SERVER", "")
SYSTRAN_TRANSLATE_PROFILE_OWNER = os.environ.get("SYSTRAN_TRANSLATE_PROFILE_OWNER", "")

# Microsoft Translator API Key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Google Analytics Key
GOOGLE_ANALYTICS_KEY = os.environ.get("GOOGLE_ANALYTICS_KEY", "")

# Raygun.io configuration
RAYGUN4PY_CONFIG = {"api_key": os.environ.get("RAYGUN_APIKEY", "")}


def _get_site_url_netloc():
    from urllib.parse import urlparse
    from django.conf import settings

    return urlparse(settings.SITE_URL).netloc


def _default_from_email():
    return os.environ.get(
        "DEFAULT_FROM_EMAIL", f"Pontoon <pontoon@{_get_site_url_netloc()}>"
    )


# Email settings
DEFAULT_FROM_EMAIL = lazy(_default_from_email, str)()
EMAIL_HOST_USER = os.environ.get(
    "EMAIL_HOST_USER", os.environ.get("SENDGRID_USERNAME", "apikey")
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.sendgrid.net")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") != "False"
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "False") != "False"
EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD", os.environ.get("SENDGRID_PASSWORD", "")
)
EMAIL_COMMUNICATION_HELP_TEXT = os.environ.get("EMAIL_COMMUNICATION_HELP_TEXT", "")

# Log emails to console if the SendGrid credentials are missing.
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Environment-independent settings. These shouldn't have to change
# between server environments.
ROOT_URLCONF = "pontoon.urls"

INSTALLED_APPS = (
    "pontoon.actionlog",
    "pontoon.administration",
    "pontoon.base",
    "pontoon.contributors",
    "pontoon.checks",
    "pontoon.insights",
    "pontoon.localizations",
    "pontoon.machinery",
    "pontoon.projects",
    "pontoon.sync",
    "pontoon.tags",
    "pontoon.teams",
    "pontoon.terminology",
    "pontoon.tour",
    "pontoon.translate",
    "pontoon.translations",
    "pontoon.uxactionlog",
    "pontoon.homepage",
    # Django contrib apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    # Django sites app is required by django-allauth
    "django.contrib.sites",
    # Third-party apps, patches, fixes
    "django_jinja",
    "pipeline",
    "guardian",
    "corsheaders",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.fxa",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.gitlab",
    "allauth.socialaccount.providers.keycloak",
    "notifications",
    "graphene_django",
    "django_ace",
)

# A list of IP addresses to be blocked from accessing the app, because they are DDoS'ing the server
BLOCKED_IPS = os.environ.get("BLOCKED_IPS", "").split(",")

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "pontoon.base.middleware.RaygunExceptionMiddleware",
    "pontoon.base.middleware.BlockedIpMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
)

CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.template.context_processors.debug",
    "django.template.context_processors.media",
    "django.template.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "pontoon.base.context_processors.globals",
)

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "NAME": "jinja2",
        "APP_DIRS": True,
        "DIRS": [os.path.join(TRANSLATE_DIR, "public")],
        "OPTIONS": {
            "match_extension": "",
            "match_regex": re.compile(
                r"""
                ^(?!(
                    admin|
                    registration|
                    account|
                    socialaccount|
                    graphene|
                )/).*\.(
                    html|
                    jinja|
                    js|
                )$
            """,
                re.VERBOSE,
            ),
            "context_processors": CONTEXT_PROCESSORS,
            "extensions": [
                "jinja2.ext.do",
                "jinja2.ext.loopcontrols",
                "jinja2.ext.i18n",
                "django_jinja.builtins.extensions.CsrfExtension",
                "django_jinja.builtins.extensions.CacheExtension",
                "django_jinja.builtins.extensions.TimezoneExtension",
                "django_jinja.builtins.extensions.UrlsExtension",
                "django_jinja.builtins.extensions.StaticFilesExtension",
                "django_jinja.builtins.extensions.DjangoFiltersExtension",
                "pipeline.jinja2.PipelineExtension",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [path("pontoon/base/templates/django")],
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": CONTEXT_PROCESSORS,
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        },
    },
]

SESSION_COOKIE_SAMESITE = "lax"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "guardian.backends.ObjectPermissionBackend",
]

GUARDIAN_RAISE_403 = True

PIPELINE_CSS = {
    "base": {
        "source_filenames": (
            "css/dark-theme.css",
            "css/light-theme.css",
            "css/fontawesome-all.css",
            "css/nprogress.css",
            "css/boilerplate.css",
            "css/fonts.css",
            "css/style.css",
        ),
        "output_filename": "css/base.min.css",
    },
    "translate": {
        "source_filenames": (
            "translate.css",
            "css/dark-theme.css",
            "css/light-theme.css",
        ),
        "output_filename": "css/translate.min.css",
    },
    "admin": {
        "source_filenames": (
            "css/table.css",
            "css/admin.css",
        ),
        "output_filename": "css/admin.min.css",
    },
    "admin_project": {
        "source_filenames": (
            "css/double_list_selector.css",
            "css/multiple_team_selector.css",
            "css/admin_project.css",
            "tag_admin.css",
        ),
        "output_filename": "css/admin_project.min.css",
    },
    "project": {
        "source_filenames": (
            "css/table.css",
            "css/request.css",
            "css/contributors.css",
            "css/heading_info.css",
            "css/sidebar_menu.css",
            "css/multiple_team_selector.css",
            "css/manual_notifications.css",
            "css/insights_charts.css",
            "css/insights_tab.css",
        ),
        "output_filename": "css/project.min.css",
    },
    "insights": {
        "source_filenames": (
            "css/insights_charts.css",
            "css/insights.css",
        ),
        "output_filename": "css/insights.min.css",
    },
    "localization": {
        "source_filenames": (
            "css/table.css",
            "css/contributors.css",
            "css/heading_info.css",
            "css/info.css",
            "css/download_selector.css",
            "css/insights_charts.css",
            "css/insights_tab.css",
        ),
        "output_filename": "css/localization.min.css",
    },
    "projects": {
        "source_filenames": (
            "css/heading_info.css",
            "css/table.css",
        ),
        "output_filename": "css/projects.min.css",
    },
    "team": {
        "source_filenames": (
            "css/table.css",
            "css/double_list_selector.css",
            "css/download_selector.css",
            "css/contributors.css",
            "css/heading_info.css",
            "css/team.css",
            "css/request.css",
            "css/insights_charts.css",
            "css/insights_tab.css",
            "css/info.css",
        ),
        "output_filename": "css/team.min.css",
    },
    "teams": {
        "source_filenames": (
            "css/heading_info.css",
            "css/table.css",
            "css/request.css",
        ),
        "output_filename": "css/teams.min.css",
    },
    "sync_logs": {
        "source_filenames": ("css/sync_logs.css",),
        "output_filename": "css/sync_logs.min.css",
    },
    "profile": {
        "source_filenames": (
            "css/contributor.css",
            "css/insights_charts.css",
            "css/profile.css",
        ),
        "output_filename": "css/profile.min.css",
    },
    "settings": {
        "source_filenames": (
            "css/multiple_team_selector.css",
            "css/contributor.css",
            "css/team_selector.css",
            "css/settings.css",
        ),
        "output_filename": "css/settings.min.css",
    },
    "notifications": {
        "source_filenames": (
            "css/sidebar_menu.css",
            "css/notifications.css",
        ),
        "output_filename": "css/notifications.min.css",
    },
    "machinery": {
        "source_filenames": (
            "css/team_selector.css",
            "css/machinery.css",
        ),
        "output_filename": "css/machinery.min.css",
    },
    "contributors": {
        "source_filenames": (
            "css/heading_info.css",
            "css/contributors.css",
        ),
        "output_filename": "css/contributors.min.css",
    },
    "terms": {
        "source_filenames": ("css/terms.css",),
        "output_filename": "css/terms.min.css",
    },
    "homepage": {
        "source_filenames": ("css/homepage.css",),
        "output_filename": "css/homepage.min.css",
    },
}

PIPELINE_JS = {
    "base": {
        "source_filenames": (
            "js/lib/jquery-3.6.1.js",
            "js/lib/jquery.timeago.js",
            "js/lib/jquery.color-2.1.2.js",
            "js/lib/nprogress.js",
            "js/main.js",
            "js/theme-switcher.js",
        ),
        "output_filename": "js/base.min.js",
    },
    "translate": {
        "source_filenames": ("translate.js",),
        "output_filename": "js/translate.min.js",
    },
    "admin": {
        "source_filenames": ("js/table.js",),
        "output_filename": "js/admin.min.js",
    },
    "admin_project": {
        "source_filenames": (
            "js/double_list_selector.js",
            "js/multiple_team_selector.js",
            "js/admin_project.js",
            "tag_admin.js",
        ),
        "output_filename": "js/admin_project.min.js",
    },
    "insights": {
        "source_filenames": (
            "js/lib/Chart.bundle.js",
            "js/insights_charts.js",
            "js/insights.js",
        ),
        "output_filename": "js/insights.min.js",
    },
    "localization": {
        "source_filenames": (
            "js/lib/Chart.bundle.js",
            "js/table.js",
            "js/progress-chart.js",
            "js/tabs.js",
            "js/insights_charts.js",
            "js/insights_tab.js",
            "js/info.js",
        ),
        "output_filename": "js/localization.min.js",
    },
    "project": {
        "source_filenames": (
            "js/lib/Chart.bundle.js",
            "js/table.js",
            "js/request.js",
            "js/progress-chart.js",
            "js/tabs.js",
            "js/sidebar_menu.js",
            "js/multiple_team_selector.js",
            "js/manual_notifications.js",
            "js/insights_charts.js",
            "js/insights_tab.js",
        ),
        "output_filename": "js/project.min.js",
    },
    "projects": {
        "source_filenames": (
            "js/table.js",
            "js/progress-chart.js",
        ),
        "output_filename": "js/projects.min.js",
    },
    "team": {
        "source_filenames": (
            "js/lib/Chart.bundle.js",
            "js/table.js",
            "js/progress-chart.js",
            "js/double_list_selector.js",
            "js/bugzilla.js",
            "js/tabs.js",
            "js/request.js",
            "js/permissions.js",
            "js/insights_charts.js",
            "js/insights_tab.js",
            "js/info.js",
        ),
        "output_filename": "js/team.min.js",
    },
    "teams": {
        "source_filenames": (
            "js/table.js",
            "js/progress-chart.js",
            "js/request.js",
        ),
        "output_filename": "js/teams.min.js",
    },
    "profile": {
        "source_filenames": (
            "js/lib/Chart.bundle.js",
            "js/insights_charts.js",
            "js/profile.js",
        ),
        "output_filename": "js/profile.min.js",
    },
    "settings": {
        "source_filenames": (
            "js/lib/jquery-ui-1.13.2.js",
            "js/multiple_team_selector.js",
            "js/team_selector.js",
            "js/settings.js",
        ),
        "output_filename": "js/settings.min.js",
    },
    "notifications": {
        "source_filenames": (
            "js/sidebar_menu.js",
            "js/notifications.js",
        ),
        "output_filename": "js/notifications.min.js",
    },
    "machinery": {
        "source_filenames": (
            "js/lib/diff.js",
            "js/lib/clipboard.min.js",
            "js/team_selector.js",
            "js/machinery.js",
        ),
        "output_filename": "js/machinery.min.js",
    },
    "homepage": {
        "source_filenames": ("js/homepage.js",),
        "output_filename": "js/homepage.min.js",
    },
}

PIPELINE = {
    "STYLESHEETS": PIPELINE_CSS,
    "JAVASCRIPT": PIPELINE_JS,
    "JS_COMPRESSOR": "pipeline.compressors.terser.TerserCompressor",
    "CSS_COMPRESSOR": "pipeline.compressors.NoopCompressor",
    "YUGLIFY_BINARY": path(
        os.environ.get("YUGLIFY_BINARY", "node_modules/.bin/yuglify")
    ),
    "TERSER_BINARY": path(os.environ.get("TERSER_BINARY", "node_modules/.bin/terser")),
    "DISABLE_WRAPPER": True,
}

# Cache config
# If the environment contains configuration data for Memcached, use
# BMemcached for the cache backend. Otherwise, default to an in-memory
# cache.
if os.environ.get("MEMCACHE_SERVERS") is not None:
    CACHES = {
        "default": {"BACKEND": "django_bmemcached.memcached.BMemcached", "OPTIONS": {}}
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "pontoon",
        }
    }

# Default timeout for the per-view cache, in seconds.
VIEW_CACHE_TIMEOUT = 60 * 60 * 24  # 1 day

# Site ID is used by Django's Sites framework.
SITE_ID = 1

# Media and templates.

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", path("media"))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/media/"

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = STATIC_HOST + "/static/"

STORAGES = {
    "staticfiles": {
        "BACKEND": "pontoon.base.storage.CompressedManifestPipelineStorage",
    },
}

STATICFILES_FINDERS = (
    "pipeline.finders.PipelineFinder",
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
STATICFILES_DIRS = [
    os.path.join(TRANSLATE_DIR, "dist"),
    os.path.join(TRANSLATE_DIR, "public"),
    os.path.join(TAGADMIN_DIR, "dist"),
]

allowed_hosts = os.environ.get("ALLOWED_HOSTS")
ALLOWED_HOSTS = allowed_hosts.split(",") if allowed_hosts else []

# Auth
# The first hasher in this list will be used for new passwords.
# Any other hasher in the list can be used for existing passwords.
PASSWORD_HASHERS = (
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.MD5PasswordHasher",
)

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "formatters": {
        "verbose": {"format": "[%(levelname)s:%(name)s] %(asctime)s %(message)s"},
    },
    "loggers": {
        "django": {"handlers": ["console"]},
        "pontoon": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "DEBUG" if DEBUG else "INFO"),
        },
    },
}

if DEBUG:
    LOGGING["handlers"]["console"]["formatter"] = "verbose"

if os.environ.get("DJANGO_SQL_LOG", False):
    LOGGING["loggers"]["django.db.backends"] = {
        "level": "DEBUG",
        "handlers": ["console"],
    }

# General auth settings
LOGIN_URL = "/"
LOGIN_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL_FAILURE = "/"

# Should robots.txt deny everything or disallow a calculated list of
# URLs we don't want to be crawled?  Default is false, disallow
# everything.
ENGAGE_ROBOTS = False

# Store the CSRF token in the user's session instead of in a cookie.
CSRF_USE_SESSIONS = True

# Set X-Frame-Options to DENY by default on all responses.
X_FRAME_OPTIONS = "DENY"

# Use correct header for detecting HTTPS on Heroku.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Do not set SECURE_HSTS_SECONDS.
# HSTS is being taken care of in pontoon/wsgi.py.
# SECURE_HSTS_SECONDS = 63072000

# X-Content-Type-Options: nosniff
# Disables browser MIME type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# x-xss-protection: 1; mode=block
# Activates the browser's XSS filtering and helps prevent XSS attacks
SECURE_BROWSER_XSS_FILTER = True

# Redirect non-HTTPS requests to HTTPS
SECURE_SSL_REDIRECT = not (DEBUG or os.environ.get("CI", False))

# Content-Security-Policy headers
CSP_DEFAULT_SRC = ("'none'",)
CSP_FRAME_SRC = ("https:",)
CSP_WORKER_SRC = ("https:",)
CSP_CONNECT_SRC = (
    "'self'",
    "https://bugzilla.mozilla.org/rest/bug",
    "https://region1.google-analytics.com/g/collect",
)
CSP_FONT_SRC = ("'self'",)
CSP_IMG_SRC = (
    "'self'",
    "https:",
    # Needed for ACE editor images
    "data:",
    "https://*.wp.com/pontoon.mozilla.org/",
    "https://www.google-analytics.com",
    "https://www.gravatar.com/avatar/",
)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-eval'",
    "'sha256-fDsgbzHC0sNuBdM4W91nXVccgFLwIDkl197QEca/Cl4='",
    # Rules related to Google Analytics
    "'sha256-MAn2iEyXLmB7sfv/20ImVRdQs8NCZ0A5SShdZsZdv20='",
    "https://www.googletagmanager.com/gtag/js",
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
)

# Needed if site not hosted on HTTPS domains (like local setup)
if not (HEROKU_DEMO or SITE_URL.startswith("https")):
    CSP_IMG_SRC = CSP_IMG_SRC + ("http://www.gravatar.com/avatar/",)
    CSP_WORKER_SRC = CSP_FRAME_SRC = CSP_FRAME_SRC + ("http:",)

# For absolute urls
try:
    DOMAIN = socket.gethostname()
except OSError:
    DOMAIN = "localhost"
PROTOCOL = "http://"
PORT = 80

# Names for slave databases from the DATABASES setting.
SLAVE_DATABASES = []

# Internationalization.

# Enable timezone-aware datetimes.
USE_TZ = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = os.environ.get("TZ", "UTC")

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Enable Bugs tab on the team pages, pulling data from bugzilla.mozilla.org.
# See bug 1567402 for details. A Mozilla-specific variable.
ENABLE_BUGS_TAB = os.environ.get("ENABLE_BUGS_TAB", "False") != "False"

# Enable Insights dashboards,
# presenting data that needs to be collected by a scheduled job.
# See docs/admin/deployment.rst for more information.
ENABLE_INSIGHTS = os.environ.get("ENABLE_INSIGHTS", "False") != "False"

# Bleach tags and attributes
ALLOWED_TAGS = [
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "br",
    "code",
    "em",
    "i",
    "li",
    "ol",
    "p",
    "strong",
    "ul",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target"],
    "abbr": ["title"],
    "acronym": ["title"],
}

# Multiple sync tasks for the same project cannot run concurrently to prevent
# potential DB and VCS inconsistencies. We store the information about the
# running task in cache and clear it after the task completes. In case of an
# error, we might never clear the cache, so we use SYNC_TASK_TIMEOUT as the
# longest possible period (in seconds) after which the cache is cleared and
# the subsequent task can run. The value should exceed the longest sync task
# of the instance.
try:
    SYNC_TASK_TIMEOUT = int(os.environ.get("SYNC_TASK_TIMEOUT", ""))
except ValueError:
    SYNC_TASK_TIMEOUT = 60 * 60 * 1  # 1 hour

SYNC_LOG_RETENTION = 90  # days

MANUAL_SYNC = os.environ.get("MANUAL_SYNC", "True") != "False"

# Celery

# Execute celery tasks locally instead of in a worker unless the
# environment is configured.
CELERY_ALWAYS_EAGER = os.environ.get("CELERY_ALWAYS_EAGER", "True") != "False"

# Limit the number of tasks a celery worker can handle before being replaced.
try:
    CELERYD_MAX_TASKS_PER_CHILD = int(os.environ.get("CELERYD_MAX_TASKS_PER_CHILD", ""))
except ValueError:
    CELERYD_MAX_TASKS_PER_CHILD = 20

BROKER_POOL_LIMIT = 1  # Limit to one connection per worker
BROKER_CONNECTION_TIMEOUT = 30  # Give up connecting faster
CELERY_RESULT_BACKEND = None  # We don't store results
CELERY_SEND_EVENTS = False  # We aren't yet monitoring events

# The default serializer since Celery 4 is 'json'
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_ACCEPT_CONTENT = ["pickle"]

# Settings related to the CORS mechanisms.
# For the sake of integration with other sites,
# all origins are allowed for the GraphQL endpoint.
CORS_ALLOW_ALL_ORIGINS = True
CORS_URLS_REGEX = r"^/graphql/?$"

SOCIALACCOUNT_ENABLED = True
SOCIALACCOUNT_ADAPTER = "pontoon.base.adapter.PontoonSocialAdapter"

# Supported values: 'django', 'fxa', 'github', 'gitlab', 'google'
AUTHENTICATION_METHOD = os.environ.get("AUTHENTICATION_METHOD", "django")


def account_username(user):
    return user.name_or_email


# django-allauth settings
ACCOUNT_AUTHENTICATED_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_USER_DISPLAY = account_username

# Mozilla Accounts (formerly Firefox Accounts)
FXA_CLIENT_ID = os.environ.get("FXA_CLIENT_ID")
FXA_SECRET_KEY = os.environ.get("FXA_SECRET_KEY")
FXA_OAUTH_ENDPOINT = os.environ.get("FXA_OAUTH_ENDPOINT", "")
FXA_PROFILE_ENDPOINT = os.environ.get("FXA_PROFILE_ENDPOINT", "")
FXA_SCOPE = ["profile:uid", "profile:display_name", "profile:email"]

# Github
GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_SECRET_KEY = os.environ.get("GITHUB_SECRET_KEY")

# GitLab
GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.com")
GITLAB_CLIENT_ID = os.environ.get("GITLAB_CLIENT_ID")
GITLAB_SECRET_KEY = os.environ.get("GITLAB_SECRET_KEY")

# Google Accounts
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_SECRET_KEY = os.environ.get("GOOGLE_SECRET_KEY")

# Keycloak Accounts
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.environ.get("KEYCLOAK_CLIENT_SECRET")

# All settings related to the AllAuth
SOCIALACCOUNT_PROVIDERS = {
    "fxa": {
        "SCOPE": FXA_SCOPE,
        "OAUTH_ENDPOINT": FXA_OAUTH_ENDPOINT,
        "PROFILE_ENDPOINT": FXA_PROFILE_ENDPOINT,
    },
    "gitlab": {"GITLAB_URL": GITLAB_URL, "SCOPE": ["read_user"]},
    "keycloak": {
        "KEYCLOAK_URL": os.environ.get("KEYCLOAK_URL"),
        "KEYCLOAK_REALM": os.environ.get("KEYCLOAK_REALM"),
    },
}

# Configuration of `django-notifications-hq` app
DJANGO_NOTIFICATIONS_CONFIG = {
    # Attach extra arguments passed to notify.send(...) to the .data attribute
    # of the Notification object.
    "USE_JSONFIELD": True,
}

# Maximum number of read notifications to display in the notifications menu
NOTIFICATIONS_MAX_COUNT = 7

# Integer representing a day of the week on which the `send_suggestion_notifications`
# management command will run.
SUGGESTION_NOTIFICATIONS_DAY = os.environ.get("SUGGESTION_NOTIFICATIONS_DAY", 4)

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
