from django import forms
from django.core import validators

from pontoon.base.forms import HtmlField


class NotificationsForm(forms.Form):
    message = HtmlField()
    selected_locales = forms.CharField(
        validators=[validators.validate_comma_separated_integer_list]
    )
