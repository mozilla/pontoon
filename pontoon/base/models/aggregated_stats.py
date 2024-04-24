import math

from django.db import models
from django.db.models import F


class AggregatedStats(models.Model):
    total_strings = models.PositiveIntegerField(default=0)
    approved_strings = models.PositiveIntegerField(default=0)
    pretranslated_strings = models.PositiveIntegerField(default=0)
    strings_with_errors = models.PositiveIntegerField(default=0)
    strings_with_warnings = models.PositiveIntegerField(default=0)
    unreviewed_strings = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    @classmethod
    def get_chart_dict(cls, obj):
        """Get chart data dictionary"""
        if obj.total_strings:
            return {
                "total_strings": obj.total_strings,
                "approved_strings": obj.approved_strings,
                "pretranslated_strings": obj.pretranslated_strings,
                "strings_with_errors": obj.strings_with_errors,
                "strings_with_warnings": obj.strings_with_warnings,
                "unreviewed_strings": obj.unreviewed_strings,
                "approved_share": round(obj.approved_percent),
                "pretranslated_share": round(obj.pretranslated_percent),
                "errors_share": round(obj.errors_percent),
                "warnings_share": round(obj.warnings_percent),
                "unreviewed_share": round(obj.unreviewed_percent),
                "completion_percent": int(math.floor(obj.completed_percent)),
            }

    @classmethod
    def get_stats_sum(cls, qs):
        """
        Get sum of stats for all items in the queryset.
        """
        return {
            "total_strings": sum(x.total_strings for x in qs),
            "approved_strings": sum(x.approved_strings for x in qs),
            "pretranslated_strings": sum(x.pretranslated_strings for x in qs),
            "strings_with_errors": sum(x.strings_with_errors for x in qs),
            "strings_with_warnings": sum(x.strings_with_warnings for x in qs),
            "unreviewed_strings": sum(x.unreviewed_strings for x in qs),
        }

    @classmethod
    def get_top_instances(cls, qs):
        """
        Get top instances in the queryset.
        """
        return {
            "most_strings": sorted(qs, key=lambda x: x.total_strings)[-1],
            "most_translations": sorted(qs, key=lambda x: x.approved_strings)[-1],
            "most_suggestions": sorted(qs, key=lambda x: x.unreviewed_strings)[-1],
            "most_missing": sorted(qs, key=lambda x: x.missing_strings)[-1],
        }

    def adjust_stats(
        self,
        total_strings_diff,
        approved_strings_diff,
        pretranslated_strings_diff,
        strings_with_errors_diff,
        strings_with_warnings_diff,
        unreviewed_strings_diff,
    ):
        self.total_strings = F("total_strings") + total_strings_diff
        self.approved_strings = F("approved_strings") + approved_strings_diff
        self.pretranslated_strings = (
            F("pretranslated_strings") + pretranslated_strings_diff
        )
        self.strings_with_errors = F("strings_with_errors") + strings_with_errors_diff
        self.strings_with_warnings = (
            F("strings_with_warnings") + strings_with_warnings_diff
        )
        self.unreviewed_strings = F("unreviewed_strings") + unreviewed_strings_diff

        self.save(
            update_fields=[
                "total_strings",
                "approved_strings",
                "pretranslated_strings",
                "strings_with_errors",
                "strings_with_warnings",
                "unreviewed_strings",
            ]
        )

    @property
    def missing_strings(self):
        return (
            self.total_strings
            - self.approved_strings
            - self.pretranslated_strings
            - self.strings_with_errors
            - self.strings_with_warnings
        )

    @property
    def completed_strings(self):
        return (
            self.approved_strings
            + self.pretranslated_strings
            + self.strings_with_warnings
        )

    @property
    def complete(self):
        return self.total_strings == self.completed_strings

    @property
    def completed_percent(self):
        return self.percent_of_total(self.completed_strings)

    @property
    def approved_percent(self):
        return self.percent_of_total(self.approved_strings)

    @property
    def pretranslated_percent(self):
        return self.percent_of_total(self.pretranslated_strings)

    @property
    def errors_percent(self):
        return self.percent_of_total(self.strings_with_errors)

    @property
    def warnings_percent(self):
        return self.percent_of_total(self.strings_with_warnings)

    @property
    def unreviewed_percent(self):
        return self.percent_of_total(self.unreviewed_strings)

    def percent_of_total(self, n):
        return n / self.total_strings * 100 if self.total_strings else 0
