from django import forms

from pontoon.base.forms import HtmlField


class MessageForm(forms.Form):
    notification = forms.BooleanField(required=False)
    email = forms.BooleanField(required=False)
    transactional = forms.BooleanField(required=False)
    subject = forms.CharField()
    body = HtmlField()
