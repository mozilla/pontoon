from django import forms

from pontoon.base.models import UserProfile


class UserTourStatusForm(forms.ModelForm):
    """
    Form is responsible for saving tour status of the user.
    """

    class Meta:
        model = UserProfile
        fields = ("tour_status",)
