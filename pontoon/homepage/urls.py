from django.conf.urls import url

from pontoon.teams.views import teams

import views

urlpatterns = [
    # Homepage
    url(r'^$', views.homepage, name='pontoon.homepage'),
]
