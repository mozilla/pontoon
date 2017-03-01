import logging

from django.db.models import Q
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404, render

from pontoon.base.models import Project
from pontoon.base.utils import require_AJAX
from pontoon.contributors.views import ContributorsMixin


log = logging.getLogger('pontoon')


def projects(request):
    """List all active projects."""
    projects = (
        Project.objects.available()
        .prefetch_related('latest_translation__user')
        .order_by('name')
    )

    return render(request, 'projects/projects.html', {
        'projects': projects,
        'top_instances': projects.get_top_instances(),
    })


def project(request, slug):
    """Project dashboard."""
    project = get_object_or_404(Project.objects.available(), slug=slug)

    return render(request, 'projects/project.html', {
        'project': project,
    })


@require_AJAX
def ajax_teams(request, slug):
    """Teams tab."""
    project = get_object_or_404(Project.objects.available(), slug=slug)

    locales = (
        project.locales.all()
        .prefetch_latest_translation(project)
        .order_by('name')
    )

    return render(request, 'projects/includes/teams.html', {
        'project': project,
        'locales': locales,
    })


@require_AJAX
def ajax_info(request, slug):
    """Info tab."""
    project = get_object_or_404(Project.objects.available(), slug=slug)

    return render(request, 'projects/includes/info.html', {
        'project': project,
    })


class ProjectContributorsView(ContributorsMixin, DetailView):
    """
    Renders view of contributors for the project.
    """
    template_name = 'projects/includes/contributors.html'
    model = Project

    def get_context_object_name(self, obj):
        return 'project'

    def contributors_filter(self, **kwargs):
        return Q(translation__entity__resource__project=self.object)
