from django.conf.urls import url
from django.views.generic import RedirectView

from pontoon.teams.views import teams

import views

urlpatterns = [
    # Home
    url(r'^$', views.home, name='pontoon.home'),

    # #Primary Button -- Localization teams
    url(r'^teams/$',teams),

    # #Secondary Button
    # url(r'^tour/$',)
    #
    # #In-context Localization
    # url(r'^in-context/$',)
]
