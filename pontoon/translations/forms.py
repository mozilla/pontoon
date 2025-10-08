from django import forms
from django.contrib.postgres.forms import SimpleArrayField

from pontoon.base.models import (
    Entity,
    Locale,
)


class CreateTranslationForm(forms.Form):
    """
    Form for parameters to the `entities` view.
    """

    entity = forms.IntegerField()
    locale = forms.CharField()

    # Some file formats allow empty translations.
    translation = forms.CharField(required=False)

    ignore_warnings = forms.BooleanField(required=False)
    approve = forms.BooleanField(required=False)
    force_suggestions = forms.BooleanField(required=False)
    paths = forms.MultipleChoiceField(required=False)
    machinery_sources = SimpleArrayField(forms.CharField(max_length=30), required=False)

    def clean_paths(self):
        try:
            return self.data.getlist("paths[]")
        except AttributeError:
            # If the data source is not a QueryDict, it won't have a `getlist` method.
            return self.data.get("paths[]") or []

    def clean_entity(self):
        pk = self.cleaned_data["entity"]
        try:
            return Entity.objects.get(pk=pk)
        except Entity.DoesNotExist:
            raise forms.ValidationError(f"Entity `{pk}` could not be found")

    def clean_locale(self):
        code = self.cleaned_data["locale"]
        try:
            return Locale.objects.get(code=code)
        except Locale.DoesNotExist:
            raise forms.ValidationError(f"Locale `{code}` could not be found")

    def clean_translation(self):
        return self.data.get("translation", "")
