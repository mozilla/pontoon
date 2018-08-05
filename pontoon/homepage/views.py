import json
from django.shortcuts import render

# Create your views here.
def home(request):
    """Home view."""

    user = request.user

    # Redirect user to the selected home page or '/'.
    if user.is_authenticated() and user.profile.custom_homepage != '':
        # If custom homepage not set yet, set it to the most contributed locale team page
        if user.profile.custom_homepage is None:
            if user.top_contributed_locale:
                user.profile.custom_homepage = user.top_contributed_locale
                user.profile.save(update_fields=['custom_homepage'])

        if user.profile.custom_homepage:
            return redirect('pontoon.teams.team', locale=user.profile.custom_homepage)

    return render(request, 'home.html')
