import math
from operator import attrgetter
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic.detail import DetailView

from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    TranslatedResource,
)
from pontoon.base.utils import require_AJAX
from pontoon.contributors.views import ContributorsMixin
from pontoon.insights.utils import get_insights
from pontoon.tags.utils import TagsTool


def localization(request, code, slug):
    """Locale-project overview."""
    locale = get_object_or_404(Locale, code=code)
    project = get_object_or_404(
        Project.objects.visible_for(request.user).available(), slug=slug
    )
    project_locale = get_object_or_404(
        ProjectLocale,
        locale=locale,
        project=project,
    )

    resource_count = len(locale.parts_stats(project)) - 1

    return render(
        request,
        "localizations/localization.html",
        {
            "locale": locale,
            "project": project,
            "project_locale": project_locale,
            "resource_count": resource_count,
            "tags_count": (
                project.tag_set.filter(resources__isnull=False).distinct().count()
                if project.tags_enabled
                else None
            ),
        },
    )


@require_AJAX
def ajax_resources(request, code, slug):
    """Resources tab."""
    locale = get_object_or_404(Locale, code=code)
    project = get_object_or_404(
        Project.objects.visible_for(request.user).available(),
        slug=slug,
    )

    # Amend the parts dict with latest activity info.
    translatedresources_qs = TranslatedResource.objects.filter(
        resource__project=project, locale=locale
    ).prefetch_related("resource", "latest_translation__user")

    if not len(translatedresources_qs):
        raise Http404

    translatedresources = {s.resource.path: s for s in translatedresources_qs}
    translatedresources = dict(list(translatedresources.items()))
    parts = locale.parts_stats(project)

    resource_priority_map = project.resource_priority_map()

    for part in parts:
        part["resource__priority"] = resource_priority_map.get(part["title"], None)

        translatedresource = translatedresources.get(part["title"], None)
        if translatedresource and translatedresource.latest_translation:
            part[
                "latest_activity"
            ] = translatedresource.latest_translation.latest_activity
        else:
            part["latest_activity"] = None

        part["chart"] = {
            "unreviewed_strings": part["unreviewed_strings"],
            "pretranslated_strings": part["pretranslated_strings"],
            "strings_with_errors": part["strings_with_errors"],
            "strings_with_warnings": part["strings_with_warnings"],
            "total_strings": part["resource__total_strings"],
            "approved_strings": part["approved_strings"],
            "approved_share": round(
                part["approved_strings"] / part["resource__total_strings"] * 100
            ),
            "unreviewed_share": round(
                part["unreviewed_strings"] / part["resource__total_strings"] * 100
            ),
            "pretranslated_share": round(
                part["pretranslated_strings"] / part["resource__total_strings"] * 100
            ),
            "errors_share": round(
                part["strings_with_errors"] / part["resource__total_strings"] * 100
            ),
            "warnings_share": round(
                part["strings_with_warnings"] / part["resource__total_strings"] * 100
            ),
            "completion_percent": int(
                math.floor(
                    (
                        part["approved_strings"]
                        + part["pretranslated_strings"]
                        + part["strings_with_warnings"]
                    )
                    / part["resource__total_strings"]
                    * 100
                )
            ),
        }

    return render(
        request,
        "localizations/includes/resources.html",
        {
            "locale": locale,
            "project": project,
            "resources": parts,
            "deadline": any(part["resource__deadline"] for part in parts),
            "priority": any(part["resource__priority"] for part in parts),
        },
    )


@require_AJAX
def ajax_tags(request, code, slug):
    """Tags tab."""
    locale = get_object_or_404(Locale, code=code)
    project = get_object_or_404(Project.objects.visible_for(request.user), slug=slug)

    if not project.tags_enabled:
        raise Http404

    tags_tool = TagsTool(
        locales=[locale],
        projects=[project],
        priority=True,
    )

    tags = sorted(tags_tool, key=attrgetter("priority"), reverse=True)

    return render(
        request,
        "localizations/includes/tags.html",
        {"locale": locale, "project": project, "tags": tags},
    )


@require_AJAX
def ajax_insights(request, code, slug):
    """Insights tab."""
    if not settings.ENABLE_INSIGHTS_TAB:
        raise ImproperlyConfigured("ENABLE_INSIGHTS_TAB variable not set in settings.")

    pl = get_object_or_404(ProjectLocale, locale__code=code, project__slug=slug)
    insights = get_insights(locale=pl.locale, project=pl.project)

    return render(request, "localizations/includes/insights.html", insights)


class LocalizationContributorsView(ContributorsMixin, DetailView):
    """
    Renders view of contributors for the localization.
    """

    template_name = "localizations/includes/contributors.html"

    def get_object(self):
        return get_object_or_404(
            ProjectLocale,
            locale__code=self.kwargs["code"],
            project__slug=self.kwargs["slug"],
        )

    def get_context_object_name(self, obj):
        return "projectlocale"

    def contributors_filter(self, **kwargs):
        return Q(
            entity__resource__project=self.object.project, locale=self.object.locale
        )
