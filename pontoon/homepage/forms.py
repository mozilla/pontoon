from django_ace import AceWidget

from django import forms

from pontoon.homepage import models


class HomepageForm(forms.ModelForm):
    class Meta:
        model = models.Homepage
        fields = "__all__"
        widgets = {
            "text": AceWidget(mode="django", width="100%"),
        }
        help_texts = {
            "text": """To keep the content compatible with the current slide structure of the
                home page, the content is expected to be separated into sections with class
                "section"."""
        }
