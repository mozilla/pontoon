from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic.detail import DetailView

from pontoon.base.aggregated_stats import get_top_instances
from pontoon.base.models import Locale, Project, TranslatedResource
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
            "latest_translation__user", "latest_translation__approved_user"
        )
        .order_by("name")
    )

    if not projects:
        return render(request, "no_projects.html", {"title": "Projects"})

    return render(
        request,
        "projects/projects.html",
        {
            "projects": projects,
            "project_stats": TranslatedResource.objects.all().string_stats(
                request.user
            ),
            "top_instances": get_top_instances(projects),
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
    project_tr = TranslatedResource.objects.filter(resource__project=project)

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
            "project_stats": project_tr.string_stats(show_hidden=True),
            "count": project_locales.count(),
            "project": project,
            "tags_count": (
                project.tag_set.filter(resources__isnull=False).distinct().count()
                if project.tags_enabled
                else None
            ),
        },
    )


@require_AJAX
def ajax_teams(request, slug):
    """Teams tab."""
    project = get_object_or_404(
        Project.objects.visible_for(request.user).available(), slug=slug
    )

    locales = Locale.objects.available()

    # Only include filtered teams if provided
    teams = request.GET.get("teams", "").split(",")
    filtered_locales = Locale.objects.filter(code__in=teams)
    if filtered_locales.exists():
        locales = locales.filter(pk__in=filtered_locales)

    locales = locales.prefetch_project_locale(project).order_by("name")

    return render(
        request,
        "projects/includes/teams.html",
        {"project": project, "locales": locales},
    )


@require_AJAX
def ajax_tags(request, slug):
    """Tags tab."""
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
    """Insights tab."""
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
    """Info tab."""
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
