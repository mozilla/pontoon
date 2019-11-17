from __future__ import absolute_import

from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'^approve/$',
        views.approve_translation,
        name='pontoon.review.approve',
    ),
    url(
        r'^unapprove/$',
        views.unapprove_translation,
        name='pontoon.review.unapprove',
    ),
    url(
        r'^reject/$',
        views.reject_translation,
        name='pontoon.review.reject',
    ),
    url(
        r'^unreject/$',
        views.unreject_translation,
        name='pontoon.review.unreject',
    ),
]
