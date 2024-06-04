from django import forms

from pontoon.base.models import Locale


class LocaleRequestForm(forms.ModelForm):
    """
    Form is for validating response of user in locale request form.
    """

    class Meta:
        model = Locale
        fields = ("name", "code")
        labels = {"name": "Language Name", "code": "Locale Code"}
