from django.conf.urls import url
from django.views.generic import RedirectView

import views

urlpatterns = [
    # Legacy: Redirect to /contributors/email
    url(r'^contributor/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        RedirectView.as_view(url="/contributors/%(email)s/", permanent=True)),

    # List contributors
    url(r'^contributors/$',
        views.ContributorsView.as_view(),
        name='pontoon.contributors'),

    # Contributor profile by email
    url(r'^contributors/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        views.contributor_email,
        name='pontoon.contributors.contributor.email'),

    # Contributor timeline
    url(r'^contributors/(?P<username>[\w-]+)/timeline/$',
        views.contributor_timeline,
        name='pontoon.contributors.contributor.timeline'),

    # Contributor profile by username
    url(r'^contributors/(?P<username>[\w-]+)/$',
        views.contributor_username,
        name='pontoon.contributors.contributor.username'),

    # Current user's profile
    url(r'^profile/$',
        views.profile,
        name='pontoon.contributors.profile'),

    # Current user's settings
    url(r'^settings/', views.settings,
        name='pontoon.contributors.settings'),

    # API: Toogle user profile attribute
    url(r'^api/v1/user/(?P<username>[\w-]+)/$',
        views.toggle_user_profile_attribute,
        name='pontoon.contributors.toggle_user_profile_attribute'),

    # AJAX
    url(r'^save-user-name/', views.save_user_name,
        name='pontoon.contributors.save_user_name'),
]
