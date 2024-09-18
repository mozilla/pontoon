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

    translation_minimum = forms.IntegerField(required=False, min_value=0)
    translation_maximum = forms.IntegerField(required=False, min_value=0)
    translation_from = forms.DateField(required=False)
    translation_to = forms.DateField(required=False)

    review_minimum = forms.IntegerField(required=False, min_value=0)
    review_maximum = forms.IntegerField(required=False, min_value=0)
    review_from = forms.DateField(required=False)
    review_to = forms.DateField(required=False)

    login_from = forms.DateField(required=False)
    login_to = forms.DateField(required=False)

    send_to_myself = forms.BooleanField(required=False)
