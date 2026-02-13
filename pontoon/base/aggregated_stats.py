from functools import cached_property


class AggregatedStats:
    aggregated_stats_query: object
    """
    Must be set by the child class as a QuerySet of TranslatedResource objects.

    Should include any filters leaving out disabled or system projects.
    """

    @cached_property
    def _stats(self) -> dict[str, int]:
        return self.aggregated_stats_query.string_stats(
            count_disabled=True, count_system_projects=True
        )

    @property
    def total_strings(self) -> int:
        return self._stats["total"]

    @property
    def approved_strings(self) -> int:
        return self._stats["approved"]

    @property
    def pretranslated_strings(self) -> int:
        return self._stats["pretranslated"]

    @property
    def strings_with_errors(self) -> int:
        return self._stats["errors"]

    @property
    def strings_with_warnings(self) -> int:
        return self._stats["warnings"]

    @property
    def unreviewed_strings(self) -> int:
        return self._stats["unreviewed"]

    @property
    def missing_strings(self) -> int:
        return (
            self.total_strings
            - self.approved_strings
            - self.pretranslated_strings
            - self.strings_with_errors
            - self.strings_with_warnings
        )

    @property
    def complete(self) -> bool:
        return self.total_strings == self.approved_strings + self.strings_with_warnings


def get_top_instances(qs, stats: dict[int, dict[str, int]]) -> dict[str, object] | None:
    """
    Get top instances in the queryset.
    """

    if not stats:
        return None

    def _missing(x: tuple[int, dict[str, int]]) -> int:
        _, d = x
        return (
            d["total"]
            - d["approved"]
            - d["pretranslated"]
            - d["errors"]
            - d["warnings"]
        )

    max_total_id = max(stats.items(), key=lambda x: x[1]["total"])[0]
    max_approved_id = max(stats.items(), key=lambda x: x[1]["approved"])[0]
    max_suggestions_id = max(stats.items(), key=lambda x: x[1]["unreviewed"])[0]
    max_missing_id = max(stats.items(), key=_missing)[0]

    return {
        "most_strings": next(row for row in qs if row.id == max_total_id),
        "most_translations": next(row for row in qs if row.id == max_approved_id),
        "most_suggestions": next(row for row in qs if row.id == max_suggestions_id),
        "most_missing": next(row for row in qs if row.id == max_missing_id),
    }
