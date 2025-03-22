from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.migrations import swappable_dependency

_prefixes = {}


def swappable_setting(app_label, model):
    """Returns the setting name to use for the given model

    Returns the setting name to use for the given model (i.e.
    AUTH_USER_MODEL)
    """
    prefix = _prefixes.get(app_label, app_label)
    setting = "{prefix}_{model}_MODEL".format(
        prefix=prefix.upper(), model=model.upper()
    )

    # Ensure this attribute exists to avoid migration issues in Django 1.7
    if not hasattr(settings, setting):
        setattr(settings, setting, join(app_label, model))

    return setting


def is_swapped(app_label, model):
    """Returns the value of the swapped setting.

    Returns the value of the swapped setting, or False if the model hasn't
    been swapped.
    """
    default_model = join(app_label, model)
    setting = swappable_setting(app_label, model)
    value = getattr(settings, setting, default_model)
    if value != default_model:
        return value
    else:
        return False


def get_model_name(app_label, model):
    """Returns [app_label.model].

    Returns [app_label.model] unless the model has been swapped, in which
    case returns the swappable setting value.
    """
    return is_swapped(app_label, model) or join(app_label, model)


def dependency(app_label, model, version=None):
    """Returns a Django 1.7+ style dependency tuple

    Returns a Django 1.7+ style dependency tuple for inclusion in
    migration.dependencies[]
    """
    dependencies = swappable_dependency(get_model_name(app_label, model))
    if not version:
        return dependencies
    return dependencies[0], version


def get_model_names(app_label, models):
    """Map model names to their swapped equivalents for the given app"""
    return dict((model, get_model_name(app_label, model)) for model in models)


def load_model(app_label, model, required=True, require_ready=True):
    """Load the specified model class, or the class it was swapped out for."""
    swapped = is_swapped(app_label, model)
    if swapped:
        app_label, model = split(swapped)

    try:
        cls = apps.get_model(app_label, model, require_ready=require_ready)
    except LookupError:
        cls = None

    if cls is None and required:
        raise ImproperlyConfigured(
            "Could not find {name}!".format(name=join(app_label, model))
        )
    return cls


def set_app_prefix(app_label, prefix):
    """Set a custom prefix to use for the given app (e.g. WQ)"""
    _prefixes[app_label] = prefix


def join(app_label, model):
    return "{app_label}.{model}".format(
        app_label=app_label,
        model=model,
    )


def split(model):
    app_label, _, model = model.rpartition(".")
    return app_label, model
