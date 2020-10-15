import urllib.parse

from django import forms

from pontoon.base import utils
from pontoon.batch.actions import ACTIONS_FN_MAP


class BatchActionsForm(forms.Form):
    """Handles the arguments passed to the batch actions view.
    """

    locale = forms.CharField()
    action = forms.ChoiceField(choices=[(x, x) for x in ACTIONS_FN_MAP.keys()])
    entities = forms.CharField(required=False)
    find = forms.CharField(required=False)
    replace = forms.CharField(required=False)

    def clean_entities(self):
        return utils.split_ints(self.cleaned_data["entities"])

    def decode_field(self, param_name):
        """
        The frontend sends quoted form fields to avoid issues with e.g. non breakable spaces.

        Related bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1438575
        """
        field_val = self.cleaned_data.get(param_name, "")
        return urllib.parse.unquote(field_val)

    def clean_find(self):
        return self.decode_field("find")

    def clean_replace(self):
        return self.decode_field("replace")
