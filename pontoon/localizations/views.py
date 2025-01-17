from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic.detail import DetailView

from pontoon.base.aggregated_stats import get_chart_dict
from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    TranslatedResource,
)
from pontoon.base.utils import (
    get_locale_or_redirect,
    get_project_or_redirect,
    require_AJAX,
)
from pontoon.contributors.views import ContributorsMixin
from pontoon.insights.utils import get_insights
from pontoon.tags.utils import Tags


def localization(request, code, slug):
    """Locale-project overview."""
    locale = get_locale_or_redirect(
        code, "pontoon.localizations.localization", "code", slug=slug
    )
    if isinstance(locale, HttpResponseRedirect):
        return locale

    project = get_project_or_redirect(
        slug, "pontoon.localizations.localization", "slug", request.user, code=code
    )
    if isinstance(project, HttpResponseRedirect):
        return project

    get_object_or_404(ProjectLocale, locale=locale, project=project)

    trans_res = TranslatedResource.objects.filter(
        locale=locale, resource__project=project
    )

    return render(
        request,
        "localizations/localization.html",
        {
            "locale": locale,
            "project": project,
            "project_locale_stats": trans_res.string_stats(show_hidden=True),
            "resource_count": trans_res.filter(resource__entities__obsolete=False)
            .distinct()
            .count(),
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

    # Check if ProjectLocale exists
    get_object_or_404(ProjectLocale, locale=locale, project=project)

    # Prefetch data needed for the latest activity column
    translatedresources = (
        TranslatedResource.objects.filter(
            resource__project=project,
            locale=locale,
            resource__entities__obsolete=False,
        )
        .order_by("resource__path")
        .prefetch_related(
            "resource", "latest_translation__user", "latest_translation__approved_user"
        )
        .distinct()
    )

    if not len(translatedresources):
        raise Http404

    resource_priority_map = project.resource_priority_map()

    for tr in translatedresources:
        tr.title = tr.resource.path
        tr.deadline = tr.resource.deadline
        tr.priority = resource_priority_map.get(tr.resource.path, None)
        tr.latest_activity = (
            tr.latest_translation.latest_activity if tr.latest_translation else None
        )
        tr.chart = get_chart_dict(tr)

    return render(
        request,
        "localizations/includes/resources.html",
        {
            "locale": locale,
            "project": project,
            "resources": translatedresources,
            "deadline": any(tr.resource.deadline for tr in translatedresources),
            "priority": any(tr.priority for tr in translatedresources),
        },
    )


@require_AJAX
def ajax_tags(request, code, slug):
    """Tags tab."""
    locale = get_object_or_404(Locale, code=code)
    project = get_object_or_404(Project.objects.visible_for(request.user), slug=slug)

    # Check if ProjectLocale exists
    get_object_or_404(ProjectLocale, locale=locale, project=project)

    if not project.tags_enabled:
        raise Http404

    tags = Tags(project=project, locale=locale).get()

    return render(
        request,
        "localizations/includes/tags.html",
        {"locale": locale, "project": project, "tags": tags},
    )


@require_AJAX
def ajax_insights(request, code, slug):
    """Insights tab."""
    if not settings.ENABLE_INSIGHTS:
        raise ImproperlyConfigured("ENABLE_INSIGHTS variable not set in settings.")

    get_object_or_404(Locale, code=code)
    get_object_or_404(Project.objects.visible_for(request.user), slug=slug)
    pl = get_object_or_404(ProjectLocale, locale__code=code, project__slug=slug)

    # Cannot use cache.get_or_set(), because it always calls the slow function
    # get_insights(). The reason we use cache in first place is to avoid that.
    key = f"/{__name__}/{code}/{slug}/insights"
    insights = cache.get(key)
    if not insights:
        insights = get_insights(locale=pl.locale, project=pl.project)
        cache.set(key, insights, settings.VIEW_CACHE_TIMEOUT)

    return render(request, "localizations/includes/insights.html", insights)


class LocalizationContributorsView(ContributorsMixin, DetailView):
    """
    Renders view of contributors for the localization.
    """

    template_name = "localizations/includes/contributors.html"

    def get_object(self):
        get_object_or_404(Locale, code=self.kwargs["code"])
        get_object_or_404(
            Project.objects.visible_for(self.request.user), slug=self.kwargs["slug"]
        )
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
