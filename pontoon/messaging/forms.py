from django_ace import AceWidget

from django import forms
from django.core import validators

from pontoon.base.forms import HtmlField
from pontoon.base.models import Project

from .models import EmailContent, Message


class MessageForm(forms.ModelForm):
    body = HtmlField()
    send_to_myself = forms.BooleanField(required=False)

    recipient_ids = forms.CharField(
        required=False,
        widget=forms.Textarea(),
        validators=[validators.validate_comma_separated_integer_list],
    )

    locales = forms.CharField(
        widget=forms.Textarea(),
        validators=[validators.validate_comma_separated_integer_list],
        required=False,
    )

    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(), required=False
    )

    class Meta:
        model = Message
        fields = [
            "recipient_ids",
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
        widgets = {
            "translation_from": forms.DateInput(attrs={"type": "date"}),
            "translation_to": forms.DateInput(attrs={"type": "date"}),
            "review_from": forms.DateInput(attrs={"type": "date"}),
            "review_to": forms.DateInput(attrs={"type": "date"}),
            "login_from": forms.DateInput(attrs={"type": "date"}),
            "login_to": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "translation_minimum": "Minimum",
            "translation_maximum": "Maximum",
            "translation_from": "From",
            "translation_to": "To",
            "review_minimum": "Minimum",
            "review_maximum": "Maximum",
            "review_from": "From",
            "review_to": "To",
            "login_from": "From",
            "login_to": "To",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove the colon from all field labels
        for field in self.fields.values():
            field.label_suffix = ""


class EmailContentForm(forms.ModelForm):
    class Meta:
        model = EmailContent
        fields = "__all__"
        widgets = {
            "body": AceWidget(mode="html", width="100%"),
        }
