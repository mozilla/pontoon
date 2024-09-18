from django import forms
from django.core import validators

from pontoon.base.forms import HtmlField

from .models import Message


class MessageForm(forms.ModelForm):
    body = HtmlField()

    locales = forms.CharField(
        widget=forms.Textarea(),
        validators=[validators.validate_comma_separated_integer_list],
    )
    projects = forms.CharField(
        widget=forms.Textarea(),
        validators=[validators.validate_comma_separated_integer_list],
    )

    send_to_myself = forms.BooleanField(required=False)

    class Meta:
        model = Message
        fields = [
            "notification",
            "email",
            "transactional",
            "subject",
            "body",
            "managers",
            "translators",
            "contributors",
            "locales",
            "projects",
            "translation_minimum",
            "translation_maximum",
            "translation_from",
            "translation_to",
            "review_minimum",
            "review_maximum",
            "review_from",
            "review_to",
            "login_from",
            "login_to",
            "send_to_myself",
        ]
