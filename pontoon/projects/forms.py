from django import forms
from django.core import validators


class NotificationsForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
    selected_locales = forms.CharField(
        validators=[validators.validate_comma_separated_integer_list]
    )
