from django.urls import path, register_converter
from django.urls.converters import StringConverter
from django.views.generic import RedirectView

from . import views


class EmailConverter(StringConverter):
    regex = r"[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}"


class UsernameConverter(StringConverter):
    regex = r"[\w.@+-]+"


register_converter(EmailConverter, "email")
register_converter(UsernameConverter, "username")

urlpatterns = [
    # Legacy: Redirect to /contributors/email
    path(
        "contributor/<email:email>/",
        RedirectView.as_view(url="/contributors/%(email)s/", permanent=True),
    ),
    # List contributors
    path(
        "contributors/", views.ContributorsView.as_view(), name="pontoon.contributors",
    ),
    # Contributor profile by email
    path(
        "contributors/<email:email>/",
        views.contributor_email,
        name="pontoon.contributors.contributor.email",
    ),
    # Contributor timeline
    path(
        "contributors/<username:username>/timeline/",
        views.contributor_timeline,
        name="pontoon.contributors.contributor.timeline",
    ),
    # Contributor profile by username
    path(
        "contributors/<username:username>/",
        views.contributor_username,
        name="pontoon.contributors.contributor.username",
    ),
    # Current user's profile
    path("profile/", views.profile, name="pontoon.contributors.profile"),
    # Current user's settings
    path("settings/", views.settings, name="pontoon.contributors.settings"),
    # Current user's notifications
    path(
        "notifications/",
        views.notifications,
        name="pontoon.contributors.notifications",
    ),
    # Mark current user's notifications as read
    path(
        "notifications/mark-all-as-read/",
        views.mark_all_notifications_as_read,
        name="pontoon.contributors.notifications.mark.all.as.read",
    ),
    # API: Toggle user profile attribute
    path(
        "api/v1/user/<username:username>/",
        views.toggle_user_profile_attribute,
        name="pontoon.contributors.toggle_user_profile_attribute",
    ),
    # AJAX: Save custom homepage
    path(
        "save-custom-homepage/",
        views.save_custom_homepage,
        name="pontoon.contributors.save_custom_homepage",
    ),
    # AJAX: Save preferred source locale
    path(
        "save-preferred-source-locale/",
        views.save_preferred_source_locale,
        name="pontoon.contributors.save_preferred_source_locale",
    ),
    # AJAX: Dismiss Add-On Promotion
    path(
        "dismiss-addon-promotion/",
        views.dismiss_addon_promotion,
        name="pontoon.contributors.dismiss_addon_promotion",
    ),
]
