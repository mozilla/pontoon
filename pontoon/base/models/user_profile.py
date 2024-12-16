import uuid

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models

from pontoon.base.models.locale import Locale


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(
        User, models.CASCADE, related_name="profile", primary_key=True
    )

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)

    # Personal information
    username = models.SlugField(unique=True, blank=True, null=True)
    bio = models.TextField(max_length=160, blank=True, null=True)

    # Email communications
    contact_email = models.EmailField("Contact email address", blank=True, null=True)
    contact_email_verified = models.BooleanField(default=False)
    email_communications_enabled = models.BooleanField(default=False)
    email_consent_dismissed_at = models.DateTimeField(null=True, blank=True)
    monthly_activity_summary = models.BooleanField(default=False)

    # Theme
    class Themes(models.TextChoices):
        DARK = "dark", "Dark"
        LIGHT = "light", "Light"
        SYSTEM = "system", "System"

    theme = models.CharField(
        choices=Themes.choices,
        max_length=20,
        default=Themes.DARK,
    )

    # External accounts
    chat = models.CharField("Chat username", max_length=255, blank=True, null=True)
    github = models.CharField("GitHub username", max_length=255, blank=True, null=True)
    bugzilla = models.EmailField("Bugzilla email address", blank=True, null=True)

    # Visibility
    class Visibility(models.TextChoices):
        ALL = "Public", "Public"
        TRANSLATORS = "Translators", "Users with translator rights"

    class VisibilityLoggedIn(models.TextChoices):
        LOGGED_IN = "Logged-in users", "Logged-in users"
        TRANSLATORS = "Translators", "Users with translator rights"

    visibility_email = models.CharField(
        "Email address",
        max_length=20,
        default=VisibilityLoggedIn.TRANSLATORS,
        choices=VisibilityLoggedIn.choices,
    )

    visibility_external_accounts = models.CharField(
        "External accounts",
        max_length=20,
        default=Visibility.TRANSLATORS,
        choices=Visibility.choices,
    )

    visibility_self_approval = models.CharField(
        "Self-approval rate",
        max_length=20,
        default=Visibility.ALL,
        choices=Visibility.choices,
    )

    visibility_approval = models.CharField(
        "Approval rate",
        max_length=20,
        default=Visibility.ALL,
        choices=Visibility.choices,
    )

    # In-app Notification subscriptions
    new_string_notifications = models.BooleanField(default=True)
    project_deadline_notifications = models.BooleanField(default=True)
    comment_notifications = models.BooleanField(default=True)
    unreviewed_suggestion_notifications = models.BooleanField(default=True)
    review_notifications = models.BooleanField(default=True)
    new_contributor_notifications = models.BooleanField(default=True)

    # Email Notification subscriptions
    new_string_notifications_email = models.BooleanField(default=False)
    project_deadline_notifications_email = models.BooleanField(default=False)
    comment_notifications_email = models.BooleanField(default=False)
    unreviewed_suggestion_notifications_email = models.BooleanField(default=False)
    review_notifications_email = models.BooleanField(default=False)
    new_contributor_notifications_email = models.BooleanField(default=False)

    # Email Notification frequencies
    class EmailFrequencies(models.TextChoices):
        DAILY = "Daily", "Daily"
        WEEKLY = "Weekly", "Weekly"

    notification_email_frequency = models.CharField(
        max_length=10,
        choices=EmailFrequencies.choices,
        default=EmailFrequencies.WEEKLY,
    )

    # Translation settings
    quality_checks = models.BooleanField(default=True)
    force_suggestions = models.BooleanField(default=False)

    # Used to redirect a user to a custom team page.
    custom_homepage = models.CharField(max_length=20, blank=True, null=True)

    # Used to display strings from preferred source locale.
    preferred_source_locale = models.CharField(max_length=20, blank=True, null=True)

    # Defines the order of locales displayed in locale tab.
    locales_order = ArrayField(
        models.PositiveIntegerField(),
        default=list,
        blank=True,
    )

    # Used to dismiss promotional banner for the Pontoon Add-On.
    has_dismissed_addon_promotion = models.BooleanField(default=False)

    # Used to keep track of start/step no. of user tour.
    # Not started:0, Completed: -1, Finished Step No. otherwise
    tour_status = models.IntegerField(default=0)

    # Used to keep track of the latest onboarding email sent.
    onboarding_email_status = models.IntegerField(default=0)

    # Used to keep track of the latest inactive reminder email sent.
    last_inactive_reminder_sent = models.DateTimeField(null=True, blank=True)

    # Used to mark users as system users.
    system_user = models.BooleanField(default=False)

    @property
    def preferred_locales(self):
        return Locale.objects.filter(pk__in=self.locales_order)

    @property
    def sorted_locales(self):
        locales = self.preferred_locales
        return sorted(locales, key=lambda locale: self.locales_order.index(locale.pk))

    def save(self, *args, **kwargs):
        notification_fields = [
            (
                "new_string_notifications",
                "new_string_notifications_email",
            ),
            (
                "project_deadline_notifications",
                "project_deadline_notifications_email",
            ),
            (
                "comment_notifications",
                "comment_notifications_email",
            ),
            (
                "unreviewed_suggestion_notifications",
                "unreviewed_suggestion_notifications_email",
            ),
            (
                "review_notifications",
                "review_notifications_email",
            ),
            (
                "new_contributor_notifications",
                "new_contributor_notifications_email",
            ),
        ]

        # Ensure notification email fields are False if the corresponding non-email notification field is False
        for non_email_field, email_field in notification_fields:
            if not getattr(self, non_email_field):
                setattr(self, email_field, False)

        super().save(*args, **kwargs)
