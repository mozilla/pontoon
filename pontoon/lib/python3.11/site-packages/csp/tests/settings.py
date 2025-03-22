import django

CSP_REPORT_ONLY = False

CSP_INCLUDE_NONCE_IN = ["default-src"]

DATABASES = {
    "default": {
        "NAME": "test.db",
        "ENGINE": "django.db.backends.sqlite3",
    }
}

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "csp",
)

SECRET_KEY = "csp-test-key"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "csp.tests.environment.environment",
            "extensions": ["csp.extensions.NoncedScript"],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]


# Django >1.6 requires `setup` call to initialise apps framework
if hasattr(django, "setup"):
    django.setup()
