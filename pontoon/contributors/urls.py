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
        "contributors/",
        views.ContributorsView.as_view(),
        name="pontoon.contributors",
    ),
    # Contributor profile by username
    path(
        "contributors/<username:username>/",
        views.contributor_username,
        name="pontoon.contributors.contributor.username",
    ),
    # Verify email address
    path(
        "verify-email-address/<str:token>/",
        views.verify_email_address,
        name="pontoon.contributors.verify.email",
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
    # Current user's remaining notifications
    path(
        "ajax/notifications/",
        views.ajax_notifications,
        name="pontoon.contributors.ajax.notifications",
    ),
    # Mark current user's notifications as read
    path(
        "notifications/mark-all-as-read/",
        views.mark_all_notifications_as_read,
        name="pontoon.contributors.notifications.mark.all.as.read",
    ),
    path(
        "user/theme/",
        views.toggle_theme,
        name="pontoon.contributors.toggle_theme",
    ),
    path(
        "user/attributes/field/",
        views.edit_user_profile_fields,
        name="pontoon.contributors.edit_field",
    ),
    path(
        "user/attributes/toggle/",
        views.toggle_user_profile_attribute,
        name="pontoon.contributors.toggle_user_profile_attribute",
    ),
    # Edit user profile locale selector
    path(
        "user/attributes/selector/",
        views.edit_user_profile_locale_selector,
        name="pontoon.contributors.edit_locale_selector",
    ),
    path(
        "save-custom-homepage/",
        views.save_custom_homepage,
        name="pontoon.contributors.save_custom_homepage",
    ),
    path(
        "save-preferred-source-locale/",
        views.save_preferred_source_locale,
        name="pontoon.contributors.save_preferred_source_locale",
    ),
    path(
        "dismiss-addon-promotion/",
        views.dismiss_addon_promotion,
        name="pontoon.contributors.dismiss_addon_promotion",
    ),
    path(
        "update-contribution-graph/",
        views.update_contribution_graph,
        name="pontoon.contributors.update_contribution_graph",
    ),
    path(
        "update-contribution-timeline/",
        views.update_contribution_timeline,
        name="pontoon.contributors.update_contribution_timeline",
    ),
    # Toggle user account status (i.e. `is_active`)
    path(
        "toggle-active-user-status/<username:username>/",
        views.toggle_active_user_status,
        name="pontoon.contributors.toggle_active_user_status",
    ),
    # Generate a new personal access token
    path(
        "generate-token/",
        views.generate_token,
        name="pontoon.contributors.generate_token",
    ),
    # Delete a personal access token
    path(
        "delete-token/<int:token_id>/",
        views.delete_token,
        name="pontoon.contributors.delete_token",
    ),
]
