from typing import cast

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.db.models.manager import BaseManager
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic.detail import DetailView

from pontoon.base.aggregated_stats import get_top_instances
from pontoon.base.models import Locale, Project, TranslatedResource, Translation
from pontoon.base.utils import get_project_or_redirect, require_AJAX
from pontoon.contributors.views import ContributorsMixin
from pontoon.insights.utils import get_insights
from pontoon.tags.utils import Tags


def projects(request):
    """List all active projects."""
    projects = (
        Project.objects.visible()
        .visible_for(request.user)
        .prefetch_related(
            "latest_translation__entity__resource",
            "latest_translation__user",
            "latest_translation__approved_user",
        )
        .order_by("name")
    )

    if not projects:
        return render(request, "no_projects.html", {"title": "Projects"})

    project_stats = projects.stats_data_as_dict()
    return render(
        request,
        "projects/projects.html",
        {
            "projects": projects,
            "all_projects_stats": TranslatedResource.objects.current().string_stats(
                request.user
            ),
            "project_stats": project_stats,
            "top_instances": get_top_instances(projects, project_stats),
        },
    )


def project(request, slug):
    """Project dashboard."""
    project = get_project_or_redirect(
        slug, "pontoon.projects.project", "slug", request.user
    )
    if isinstance(project, HttpResponseRedirect):
        return project

    project_locales = project.project_locale
    project_tr = TranslatedResource.objects.current().filter(resource__project=project)

    # Only include filtered teams if provided
    teams = request.GET.get("teams", "").split(",")
    filtered_locales = Locale.objects.filter(code__in=teams)
    if filtered_locales.exists():
        project_locales = project_locales.filter(locale__in=filtered_locales)
        project_tr = project_tr.filter(locale__in=filtered_locales)

    return render(
        request,
        "projects/project.html",
        {
            "project_stats": project_tr.string_stats(count_system_projects=True),
            "count": project_locales.count(),
            "project": project,
            "tags_count": (
                project.tags.filter(resources__isnull=False).distinct().count()
                if project.tags_enabled
                else None
            ),
        },
    )


@require_AJAX
def ajax_teams(request, slug):
    """Project Teams tab."""
    project = get_object_or_404(
        cast(
            BaseManager[Project], Project.objects.visible_for(request.user).available()
        ),
        slug=slug,
    )

    locales = cast(BaseManager[Locale], Locale.objects.available()).order_by("name")

    # Only include filtered teams if provided
    teams = request.GET.get("teams", "").split(",")
    filtered_locales = Locale.objects.filter(code__in=teams)
    if filtered_locales.exists():
        locales = locales.filter(pk__in=filtered_locales)

    latest_trans_ids = project.project_locale.values_list(
        "latest_translation_id", flat=True
    )
    latest_activities = {
        trans.locale_id: trans.latest_activity
        for trans in Translation.objects.filter(id__in=latest_trans_ids).select_related(
            "user", "approved_user"
        )
    }

    return render(
        request,
        "projects/includes/teams.html",
        {
            "project": project,
            "locales": locales,
            "locale_stats": locales.stats_data_as_dict(project),
            "latest_activities": latest_activities,
        },
    )


@require_AJAX
def ajax_tags(request, slug):
    """Project Tags tab."""
    project = get_object_or_404(Project.objects.visible_for(request.user), slug=slug)

    if not project.tags_enabled:
        raise Http404

    tags = Tags(project=project).get()

    return render(
        request,
        "projects/includes/tags.html",
        {"project": project, "tags": tags},
    )


@require_AJAX
def ajax_insights(request, slug):
    """Project Insights tab."""
    if not settings.ENABLE_INSIGHTS:
        raise ImproperlyConfigured("ENABLE_INSIGHTS variable not set in settings.")

    project = get_object_or_404(
        Project.objects.visible_for(request.user).available(), slug=slug
    )

    # Cannot use cache.get_or_set(), because it always calls the slow function
    # get_insights(). The reason we use cache in first place is to avoid that.
    key = f"/{__name__}/{slug}/insights"
    insights = cache.get(key)
    if not insights:
        insights = get_insights(project=project)
        cache.set(key, insights, settings.VIEW_CACHE_TIMEOUT)

    return render(request, "projects/includes/insights.html", insights)


@require_AJAX
def ajax_info(request, slug):
    """Project Info tab."""
    project = get_object_or_404(
        Project.objects.visible_for(request.user).available(), slug=slug
    )

    return render(request, "projects/includes/info.html", {"project": project})


class ProjectContributorsView(ContributorsMixin, DetailView):
    """
    Renders view of contributors for the project.
    """

    template_name = "projects/includes/contributors.html"
    model = Project

    def get_queryset(self):
        return super().get_queryset().visible_for(self.request.user)

    def get_context_object_name(self, obj):
        return "project"

    def contributors_filter(self, **kwargs):
        return Q(entity__resource__project=self.object)
