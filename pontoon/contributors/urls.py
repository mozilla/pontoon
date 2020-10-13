from django.conf.urls import url
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # Legacy: Redirect to /contributors/email
    url(
        r"^contributor/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$",
        RedirectView.as_view(url="/contributors/%(email)s/", permanent=True),
    ),
    # List contributors
    url(
        r"^contributors/$",
        views.ContributorsView.as_view(),
        name="pontoon.contributors",
    ),
    # Contributor profile by email
    url(
        r"^contributors/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$",
        views.contributor_email,
        name="pontoon.contributors.contributor.email",
    ),
    # Contributor timeline
    url(
        r"^contributors/(?P<username>[\w.@+-]+)/timeline/$",
        views.contributor_timeline,
        name="pontoon.contributors.contributor.timeline",
    ),
    # Contributor profile by username
    url(
        r"^contributors/(?P<username>[\w.@+-]+)/$",
        views.contributor_username,
        name="pontoon.contributors.contributor.username",
    ),
    # Current user's profile
    url(r"^profile/$", views.profile, name="pontoon.contributors.profile"),
    # Current user's settings
    url(r"^settings/$", views.settings, name="pontoon.contributors.settings"),
    # Current user's notifications
    url(
        r"^notifications/$",
        views.notifications,
        name="pontoon.contributors.notifications",
    ),
    # Mark current user's notifications as read
    url(
        r"^notifications/mark-all-as-read/$",
        views.mark_all_notifications_as_read,
        name="pontoon.contributors.notifications.mark.all.as.read",
    ),
    # API: Toogle user profile attribute
    url(
        r"^api/v1/user/(?P<username>[\w.@+-]+)/$",
        views.toggle_user_profile_attribute,
        name="pontoon.contributors.toggle_user_profile_attribute",
    ),
    # AJAX
    url(
        r"^save-custom-homepage/$",
        views.save_custom_homepage,
        name="pontoon.contributors.save_custom_homepage",
    ),
    # AJAX: Save preferred source locale
    url(
        r"^save-preferred-source-locale/$",
        views.save_preferred_source_locale,
        name="pontoon.contributors.save_preferred_source_locale",
    ),
]
