from django import forms

from pontoon.base.models.user_profile import UserProfile


class CommunityHealthLocalesForm(forms.ModelForm):
    """
    Form is responsible for saving custom configurations of the Insights Dashboard.
    """

    class Meta:
        model = UserProfile
        fields = ("community_health_locales",)
