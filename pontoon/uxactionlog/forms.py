from django import forms


class UXActionLogForm(forms.Form):
    """Handles the arguments passed to the log UX action view.
    """

    action_type = forms.CharField()
    experiment = forms.CharField(required=False)
    data = forms.JSONField(required=False)
