import json

from django.forms import ValidationError, fields
from django.utils.translation import gettext_lazy as _

from .json import checked_loads


class InvalidJSONInput(str):
    pass


class JSONField(fields.CharField):
    default_error_messages = {
        'invalid': _('"%(value)s" value must be valid JSON.'),
    }

    def __init__(self, *args, dump_kwargs=None, load_kwargs=None, **kwargs):
        self.dump_kwargs = dump_kwargs if dump_kwargs else {}
        self.load_kwargs = load_kwargs if load_kwargs else {}

        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if self.disabled:
            return value

        if value in self.empty_values:
            return None

        try:
            return checked_loads(value, **self.load_kwargs)
        except json.JSONDecodeError:
            raise ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': value},
            )

    def bound_data(self, data, initial):
        # Note: This is a bit confusing, as there are multiple things occurring.
        #   First, the `initial` value is the *unencoded* python object provided
        #   via the form instance, while `data` is the *encoded* form input. The
        #   outgoing value needs to be uniform, so we decode `data` here.
        #
        #   Second, it may seem counterintuitive to encode data, just to decode
        #   it in `prepare_value`. Why not just decode `initial` here? This is
        #   due to `BoundField.value()`, which only calls `bound_data` when the
        #   form is bound. If unbound, the `initial` value is provided directly
        #   to `prepare_value`, and the value would still need to be encoded.
        #
        #   Lastly, we don't want to run `checked_loads` here, since we *know*
        #   that the input `data` isn't a decoded value (e.g., via `to_python`).
        if self.disabled:
            return initial
        try:
            return json.loads(data, **self.load_kwargs)
        except json.JSONDecodeError:
            return InvalidJSONInput(data)

    def prepare_value(self, value):
        if isinstance(value, InvalidJSONInput):
            return value
        return json.dumps(value, **self.dump_kwargs)
