from datetime import timedelta

from django.db import models
from django.utils import timezone


def active_users_default():
    return {
        "managers": 0,
        "reviewers": 0,
        "contributors": 0,
    }


class InsightsSnapshot(models.Model):
    created_at = models.DateField(default=timezone.now)

    # Aggregated stats
    total_strings = models.PositiveIntegerField(default=0)
    approved_strings = models.PositiveIntegerField(default=0)
    pretranslated_strings = models.PositiveIntegerField(default=0)
    strings_with_errors = models.PositiveIntegerField(default=0)
    strings_with_warnings = models.PositiveIntegerField(default=0)
    unreviewed_strings = models.PositiveIntegerField(default=0)

    @property
    def missing_strings(self):
        return (
            self.total_strings
            - self.approved_strings
            - self.pretranslated_strings
            - self.strings_with_errors
            - self.strings_with_warnings
        )

    # Active users
    total_managers = models.PositiveIntegerField(default=0)
    total_reviewers = models.PositiveIntegerField(default=0)
    total_contributors = models.PositiveIntegerField(default=0)
    active_users_last_12_months = models.JSONField(default=active_users_default)
    active_users_last_6_months = models.JSONField(default=active_users_default)
    active_users_last_3_months = models.JSONField(default=active_users_default)
    active_users_last_month = models.JSONField(default=active_users_default)

    # Unreviewed lifespan
    unreviewed_suggestions_lifespan = models.DurationField(default=timedelta)

    # Time to review suggestions
    time_to_review_suggestions = models.DurationField(
        default=None, null=True, blank=True
    )

    # Time to review pretranslations
    time_to_review_pretranslations = models.DurationField(
        default=None, null=True, blank=True
    )

    # Translation activity
    completion = models.FloatField()
    human_translations = models.PositiveIntegerField(default=0)
    machinery_translations = models.PositiveIntegerField(default=0)
    new_source_strings = models.PositiveIntegerField(default=0)

    # Review activity
    peer_approved = models.PositiveIntegerField(default=0)
    self_approved = models.PositiveIntegerField(default=0)
    rejected = models.PositiveIntegerField(default=0)
    new_suggestions = models.PositiveIntegerField(default=0)

    # Pretranslation quality
    pretranslations_chrf_score = models.FloatField(default=None, null=True, blank=True)
    pretranslations_approved = models.PositiveIntegerField(default=0)
    pretranslations_rejected = models.PositiveIntegerField(default=0)
    pretranslations_new = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True


class LocaleInsightsSnapshot(InsightsSnapshot):
    locale = models.ForeignKey("base.Locale", models.CASCADE)


class ProjectLocaleInsightsSnapshot(InsightsSnapshot):
    project_locale = models.ForeignKey("base.ProjectLocale", models.CASCADE)
