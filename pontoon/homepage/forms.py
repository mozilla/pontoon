from django import forms
from django_ace import AceWidget

from pontoon.homepage import models


class HomepageForm(forms.ModelForm):
    class Meta:
        model = models.Homepage
        fields = '__all__'
        widgets = {
            'text': AceWidget(mode='html', theme='tomorrow_night', width="900px", height="400px"),
        }
