from django.db.models import Max, Q, Sum

from pontoon.base.aggregated_stats import get_chart_dict
from pontoon.base.models import TranslatedResource, Translation
from pontoon.tags.models import Tag


class Tags:
    """This provides an API for retrieving related ``Tags`` for given filters,
    providing statistical information and latest activity data.
    """

    def __init__(self, **kwargs):
        self.project = kwargs.get("project")
        self.locale = kwargs.get("locale")
        self.slug = kwargs.get("slug")
        self.tag = Tag.objects.filter(
            project=self.project, slug=self.slug, resources__isnull=False
        ).first()

    def get(self):
        tags = (
            Tag.objects.filter(project=self.project, resources__isnull=False)
            .distinct()
            .order_by("-priority", "name")
        )

        chart = self.chart(Q(), "resource__tag")
        latest_activity = self.latest_activity(Q(), "resource__tag")
        for tag in tags:
            tag.chart = chart.get(tag.pk)
            tag.latest_activity = latest_activity.get(tag.pk)

        return tags

    def get_tag_locales(self):
        tag = self.tag

        if tag is None:
            return None

        chart = self.chart(Q(resource__tag=self.tag), "resource__tag")
        tag.chart = chart.get(tag.pk)
        tag.locales = self.project.locales.all()

        locale_chart = self.chart(Q(resource__tag=self.tag), "locale")
        locale_latest_activity = self.latest_activity(
            Q(resource__tag=self.tag), "locale"
        )
        for locale in tag.locales:
            locale.chart = locale_chart.get(locale.pk)
            locale.latest_activity = locale_latest_activity.get(locale.pk)

        return tag

    def chart(self, query, group_by):
        trs = (
            self.translated_resources.filter(query)
            .values(group_by)
            .annotate(
                # should be Sum("total_strings"), but tests fail with it
                total=Sum("resource__total_strings"),
                approved=Sum("approved_strings"),
                pretranslated=Sum("pretranslated_strings"),
                errors=Sum("strings_with_errors"),
                warnings=Sum("strings_with_warnings"),
                unreviewed=Sum("unreviewed_strings"),
            )
        )

        print(list(k for k in trs[0].keys()))
        return {
            tr[group_by]: get_chart_dict(
                TranslatedResource(
                    total_strings=tr["total"],
                    approved_strings=tr["approved"],
                    pretranslated_strings=tr["pretranslated"],
                    strings_with_errors=tr["errors"],
                    strings_with_warnings=tr["warnings"],
                    unreviewed_strings=tr["unreviewed"],
                )
            )
            for tr in trs
        }

    def latest_activity(self, query, group_by):
        latest_activity = {}
        dates = {}
        translations = Translation.objects.none()

        trs = (
            self.translated_resources.exclude(latest_translation__isnull=True)
            .filter(query)
            .values(group_by)
            .annotate(
                date=Max("latest_translation__date"),
                approved_date=Max("latest_translation__approved_date"),
            )
        )

        for tr in trs:
            date = max(tr["date"], tr["approved_date"] or tr["date"])
            dates[date] = tr[group_by]
            prefix = "entity__" if group_by == "resource__tag" else ""

            # Find translations with matching date and tag/locale
            translations |= Translation.objects.filter(
                Q(**{"date": date, f"{prefix}{group_by}": tr[group_by]})
            ).prefetch_related("user", "approved_user")

        for t in translations:
            key = dates[t.latest_activity["date"]]
            latest_activity[key] = t.latest_activity

        return latest_activity

    @property
    def translated_resources(self):
        trs = TranslatedResource.objects

        if self.project is not None:
            trs = trs.filter(resource__project=self.project)

        if self.locale is not None:
            trs = trs.filter(locale=self.locale)

        return trs
