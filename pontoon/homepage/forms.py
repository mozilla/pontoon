from django import forms
from django_ace import AceWidget

from pontoon.homepage import models


class HomepageForm(forms.ModelForm):
    class Meta:
        model = models.Homepage
        fields = "__all__"
        widgets = {
            "text": AceWidget(
                mode="django", theme="tomorrow_night", width="900px", height="400px"
            ),
        }
        help_texts = {
            "text": """To keep the content compatible with the current slide structure of the
                home page, the content is expected to be separated into sections with class
                "section"."""
        }
