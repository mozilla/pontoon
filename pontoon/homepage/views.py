from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings

from pontoon.base.models import Locale, Project, Entity
from pontoon.base.utils import get_project_locale_from_request


def homepage(request):
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

    # Guess user's team page or redirect to /teams
    locale = get_project_locale_from_request(request, Locale.objects.visible())
    if locale not in ('en-US', 'en', None):
        start_url = reverse('pontoon.teams.team', kwargs={
            'locale': locale,
        })
    else:
        start_url = reverse('pontoon.teams')

    homepage = get_object_or_404(Project, slug='homepage')
    strings = Entity.objects.filter(
        resource__project=homepage,
        obsolete=False,
    ).values_list('string', flat=True)

    return render(request, 'homepage.html', {
        'start_url': start_url,
        'contact': settings.PROJECT_MANAGERS[0] if settings.PROJECT_MANAGERS[0] else '',
        'strings': strings,

    })
