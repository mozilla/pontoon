from django.conf.urls import url

import views

urlpatterns = [
    # Homepage
    url(r'^$', views.homepage, name='pontoon.homepage'),
]
