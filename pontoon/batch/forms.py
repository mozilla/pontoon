from django import forms

from pontoon.base import utils


class BatchActionsForm(forms.Form):
    """Handles the arguments passed to the batch actions view.
    """

    locale = forms.CharField()
    action = forms.CharField()
    entities = forms.CharField(required=False)
    find = forms.CharField(required=False)
    replace = forms.CharField(required=False)

    def clean_entities(self):
        return utils.split_ints(self.cleaned_data['entities'])
