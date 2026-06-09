from typing import Any, cast

from moz.l10n.message import message_from_json
from moz.l10n.model import Message

from django import forms
from django.contrib.postgres.forms import SimpleArrayField

from pontoon.base.models import Entity, Locale, Resource
from .utils import JsonMessage, serialize_for_db


class CreateTranslationForm(forms.Form):
    """
    Form for parameters to the `entities` view.
    """

    entity = forms.IntegerField()
    locale = forms.CharField()
    value = forms.JSONField(required=False)
    properties = forms.JSONField(required=False)

    ignore_warnings = forms.BooleanField(required=False)
    approve = forms.BooleanField(required=False)
    force_suggestions = forms.BooleanField(required=False)
    machinery_sources = SimpleArrayField(forms.CharField(max_length=30), required=False)
    stats = forms.ChoiceField(
        choices=[("all", "all"), ("resource", "resource")], required=False
    )

    def clean_entity(self):
        pk = self.cleaned_data["entity"]
        try:
            return Entity.objects.select_related("resource__project").get(pk=pk)
        except Entity.DoesNotExist:
            raise forms.ValidationError(f"Entity `{pk}` could not be found")

    def clean_locale(self):
        code = self.cleaned_data["locale"]
        try:
            return Locale.objects.get(code=code)
        except Locale.DoesNotExist:
            raise forms.ValidationError(f"Locale `{code}` could not be found")

    def clean_value(self) -> Message:
        value = cast(JsonMessage, self.cleaned_data["value"])
        if not value and not isinstance(value, list):
            raise forms.ValidationError("This field is required.")
        return message_from_json(value).normalize()

    def clean_properties(self) -> dict[str, Message]:
        properties = cast(dict[str, JsonMessage], self.cleaned_data["properties"])
        return (
            {k: message_from_json(v).normalize() for k, v in properties.items()}
            if properties
            else {}
        )

    def clean(self):
        cleaned_data = cast(dict[str, Any], super().clean())
        entity = cast(Entity, cleaned_data.get("entity", None))
        value = cast(Message, cleaned_data.get("value", None))
        properties = cast(dict[str, Message], cleaned_data.get("properties", None))
        if entity is None or value is None or properties is None:
            return
        format = entity.resource.format

        if properties and format != Resource.Format.FLUENT:
            raise forms.ValidationError(f"Properties are not supported for {format}")

        try:
            cleaned_data["string"] = serialize_for_db(entity, value, properties)
        except Exception as err:
            value_is = "Value is" if not properties else "Value and properties are"
            raise forms.ValidationError(
                f"{value_is} not serializable as {format}"
            ) from err
