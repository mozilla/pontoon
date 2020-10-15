# The classes here provide similar functionality to
# TranslatedResource.stats in mangling stats data,
# although they use queryset `values` rather than objects

from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce

from .base import TagsTRTool


class TagsStatsTool(TagsTRTool):
    """Creates aggregated stat data for tags according to
    filters
    """

    coalesce = list

    filter_methods = ("tag", "projects", "locales", "path")

    # from the perspective of translated resources
    _default_annotations = (
        ("total_strings", Coalesce(Sum("resource__total_strings"), Value(0))),
        ("fuzzy_strings", Coalesce(Sum("fuzzy_strings"), Value(0))),
        ("strings_with_warnings", Coalesce(Sum("strings_with_warnings"), Value(0))),
        ("strings_with_errors", Coalesce(Sum("strings_with_errors"), Value(0))),
        ("approved_strings", Coalesce(Sum("approved_strings"), Value(0))),
        ("unreviewed_strings", Coalesce(Sum("unreviewed_strings"), Value(0))),
    )

    def get_data(self):
        """Stats can be generated either grouping by tag or by locale

        Once the tags/locales are found a second query is made to get
        their data

        """
        if self.get_groupby()[0] == "resource__tag":
            stats = {
                stat["resource__tag"]: stat
                for stat in super(TagsStatsTool, self).get_data()
            }

            # get the found tags as values
            tags = self.tag_manager.filter(pk__in=stats.keys())
            tags = tags.values("pk", "slug", "name", "priority", "project")
            tags = tags.annotate(resource__tag=F("pk"))
            for tag in tags:
                # update the stats with tag data
                tag.update(stats[tag["pk"]])
            return tags
        elif self.get_groupby()[0] == "locale":
            result = list(super(TagsStatsTool, self).get_data())
            # get the found locales as values
            locales = {
                loc["pk"]: loc
                for loc in self.locale_manager.filter(
                    pk__in=(r["locale"] for r in result)
                ).values("pk", "name", "code", "population")
            }
            for r in result:
                # update the stats with locale data
                r.update(locales[r["locale"]])
            return sorted(result, key=lambda r: r["name"])
