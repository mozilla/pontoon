from datetime import timedelta
from django.db import models
from django.utils import timezone

from pontoon.base.models import AggregatedStats


def active_users_default():
    return {
        "managers": 0,
        "reviewers": 0,
        "contributors": 0,
    }


class InsightsSnapshot(AggregatedStats, models.Model):
    created_at = models.DateField(default=timezone.now)

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

    class Meta:
        abstract = True


class LocaleInsightsSnapshot(InsightsSnapshot):
    locale = models.ForeignKey("base.Locale", models.CASCADE)


class ProjectInsightsSnapshot(InsightsSnapshot):
    project = models.ForeignKey("base.Project", models.CASCADE)


class ProjectLocaleInsightsSnapshot(AggregatedStats):
    project_locale = models.ForeignKey("base.ProjectLocale", models.CASCADE)
    created_at = models.DateField(default=timezone.now)
    completion = models.FloatField()
