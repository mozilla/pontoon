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

    # Notification subscriptions
    new_string_notifications = models.BooleanField(default=True)
    project_deadline_notifications = models.BooleanField(default=True)
    comment_notifications = models.BooleanField(default=True)
    unreviewed_suggestion_notifications = models.BooleanField(default=True)
    review_notifications = models.BooleanField(default=True)
    new_contributor_notifications = models.BooleanField(default=True)

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

    # Used to mark users as system users.
    system_user = models.BooleanField(default=False)

    @property
    def preferred_locales(self):
        return Locale.objects.filter(pk__in=self.locales_order)

    @property
    def sorted_locales(self):
        locales = self.preferred_locales
        return sorted(locales, key=lambda locale: self.locales_order.index(locale.pk))
