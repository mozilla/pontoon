import math

from functools import cached_property


class AggregatedStats:
    trans_res_query: object

    @cached_property
    def _stats(self) -> dict[str, int]:
        return self.trans_res_query.string_stats()

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
    def missing_strings(self):
        return (
            self.total_strings
            - self.approved_strings
            - self.pretranslated_strings
            - self.strings_with_errors
            - self.strings_with_warnings
        )


def get_completed_percent(obj):
    if not obj.total_strings:
        return 0
    completed_strings = (
        obj.approved_strings + obj.pretranslated_strings + obj.strings_with_warnings
    )
    return completed_strings / obj.total_strings * 100


def get_chart_dict(obj: "AggregatedStats"):
    """Get chart data dictionary"""
    if ts := obj.total_strings:
        return {
            "total": ts,
            "approved": obj.approved_strings,
            "pretranslated": obj.pretranslated_strings,
            "errors": obj.strings_with_errors,
            "warnings": obj.strings_with_warnings,
            "unreviewed": obj.unreviewed_strings,
            "approved_share": round(obj.approved_strings / ts * 100),
            "pretranslated_share": round(obj.pretranslated_strings / ts * 100),
            "errors_share": round(obj.strings_with_errors / ts * 100),
            "warnings_share": round(obj.strings_with_warnings / ts * 100),
            "unreviewed_share": round(obj.unreviewed_strings / ts * 100),
            "completion_percent": int(math.floor(get_completed_percent(obj))),
        }


def get_top_instances(qs):
    """
    Get top instances in the queryset.
    """
    return {
        "most_strings": sorted(qs, key=lambda x: x.total_strings)[-1],
        "most_translations": sorted(qs, key=lambda x: x.approved_strings)[-1],
        "most_suggestions": sorted(qs, key=lambda x: x.unreviewed_strings)[-1],
        "most_missing": sorted(qs, key=lambda x: x.missing_strings)[-1],
    }
