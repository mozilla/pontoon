from django.conf.urls import url

import views

urlpatterns = [
    url(
        r'^update-tour-status/',
        views.update_tour_status,
        name='pontoon.update_tour_status',
    ),
]
