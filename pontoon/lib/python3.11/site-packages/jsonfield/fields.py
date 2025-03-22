import copy
import json
import warnings

from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from . import forms
from .encoder import JSONEncoder
from .json import JSONString, checked_loads

DEFAULT_DUMP_KWARGS = {
    'cls': JSONEncoder,
}

DEFAULT_LOAD_KWARGS = {}

INVALID_JSON_WARNING = (
    '{0!s} failed to load invalid json ({1}) from the database. The value has '
    'been returned as a string instead.'
)


class JSONFieldMixin(models.Field):
    form_class = forms.JSONField

    def __init__(self, *args, dump_kwargs=None, load_kwargs=None, **kwargs):
        self.dump_kwargs = DEFAULT_DUMP_KWARGS if dump_kwargs is None else dump_kwargs
        self.load_kwargs = DEFAULT_LOAD_KWARGS if load_kwargs is None else load_kwargs

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        if self.dump_kwargs != DEFAULT_DUMP_KWARGS:
            kwargs['dump_kwargs'] = self.dump_kwargs
        if self.load_kwargs != DEFAULT_LOAD_KWARGS:
            kwargs['load_kwargs'] = self.load_kwargs

        return name, path, args, kwargs

    def to_python(self, value):
        try:
            return checked_loads(value, **self.load_kwargs)
        except ValueError:
            raise ValidationError(_("Enter valid JSON."))

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None

        try:
            return checked_loads(value, **self.load_kwargs)
        except json.JSONDecodeError:
            warnings.warn(INVALID_JSON_WARNING.format(self, value), RuntimeWarning)
            return JSONString(value)

    def get_prep_value(self, value):
        """Convert JSON object to a string"""
        if self.null and value is None:
            return None
        return json.dumps(value, **self.dump_kwargs)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return json.dumps(value, **self.dump_kwargs)

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', self.form_class)
        if issubclass(kwargs['form_class'], forms.JSONField):
            kwargs.setdefault('dump_kwargs', self.dump_kwargs)
            kwargs.setdefault('load_kwargs', self.load_kwargs)

        return super().formfield(**kwargs)

    def get_default(self):
        """
        Returns the default value for this field.

        The default implementation on models.Field calls force_unicode
        on the default, which means you can't set arbitrary Python
        objects as the default. To fix this, we just return the value
        without calling force_unicode on it. Note that if you set a
        callable as a default, the field will still call it. It will
        *not* try to pickle and encode it.
        """
        if self.has_default():
            if callable(self.default):
                return self.default()
            return copy.deepcopy(self.default)
        # If the field doesn't have a default, then we punt to models.Field.
        return super().get_default()


class JSONField(JSONFieldMixin, models.TextField):
    """JSONField is a generic textfield that serializes/deserializes JSON objects"""

    def formfield(self, **kwargs):
        field = super().formfield(**kwargs)
        if isinstance(field, forms.JSONField):
            # Note: TextField sets the Textarea widget
            field.dump_kwargs.setdefault('indent', 4)
            field.dump_kwargs.setdefault('ensure_ascii', False)
        return field


class JSONCharField(JSONFieldMixin, models.CharField):
    """JSONCharField is a generic textfield that serializes/deserializes JSON objects"""
