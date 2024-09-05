from django import forms
from django.core import validators

from pontoon.base.forms import HtmlField


class MessageForm(forms.Form):
    notification = forms.BooleanField(required=False)
    email = forms.BooleanField(required=False)
    transactional = forms.BooleanField(required=False)

    subject = forms.CharField()
    body = HtmlField()

    managers = forms.BooleanField(required=False)
    translators = forms.BooleanField(required=False)
    contributors = forms.BooleanField(required=False)

    locales = forms.CharField(
        validators=[validators.validate_comma_separated_integer_list]
    )
    projects = forms.CharField(
        validators=[validators.validate_comma_separated_integer_list]
    )
