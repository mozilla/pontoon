import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.detail import DetailView

from guardian.decorators import permission_required_or_403
from notifications.models import Notification
from notifications.signals import notify

from pontoon.base.models import Project, Locale
from pontoon.base.utils import require_AJAX, split_ints
from pontoon.contributors.views import ContributorsMixin
from pontoon.insights.utils import get_project_insights
from pontoon.projects import forms
from pontoon.tags.utils import TagsTool


def projects(request):
    """List all active projects."""
    projects = (
        Project.objects.visible()
        .visible_for(request.user)
        .prefetch_related("latest_translation__user")
        .order_by("name")
    )

    if not projects:
        return render(request, "no_projects.html", {"title": "Projects"})

    return render(
        request,
        "projects/projects.html",
        {"projects": projects, "top_instances": projects.get_top_instances()},
    )


def project(request, slug):
    """Project dashboard."""
    project = get_object_or_404(
        Project.objects.visible_for(request.user).available(), slug=slug
    )
    return render(
        request,
        "projects/project.html",
        {
            "project": project,
            "tags": (
                len(TagsTool(projects=[project], priority=True))
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

    locales = (
        Locale.objects.available().prefetch_project_locale(project).order_by("name")
    )

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

    tags_tool = TagsTool(projects=[project], priority=True,)

    return render(
        request,
        "projects/includes/tags.html",
        {"project": project, "tags": list(tags_tool)},
    )


@require_AJAX
def ajax_insights(request, slug):
    """Insights tab."""
    if not settings.ENABLE_INSIGHTS_TAB:
        raise ImproperlyConfigured("ENABLE_INSIGHTS_TAB variable not set in settings.")

    project = get_object_or_404(
        Project.objects.visible_for(request.user).available(), slug=slug
    )
    insights = get_project_insights(Q(project=project))

    return render(request, "projects/includes/insights.html", insights)


@require_AJAX
def ajax_info(request, slug):
    """Info tab."""
    project = get_object_or_404(
        Project.objects.visible_for(request.user).available(), slug=slug
    )

    return render(request, "projects/includes/info.html", {"project": project})


@permission_required_or_403("base.can_manage_project")
@transaction.atomic
@require_AJAX
def ajax_notifications(request, slug):
    """Notifications tab."""
    project = get_object_or_404(
        Project.objects.visible_for(request.user).available(), slug=slug
    )
    available_locales = project.locales.order_by("name")

    # Send notifications
    if request.method == "POST":
        form = forms.NotificationsForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        contributors = User.objects.filter(
            translation__entity__resource__project=project,
        )

        # For performance reasons, only filter contributors for selected
        # locales if different from all project locales
        available_ids = sorted(list(available_locales.values_list("id", flat=True)))
        selected_ids = sorted(split_ints(form.cleaned_data.get("selected_locales")))

        if available_ids != selected_ids:
            contributors = User.objects.filter(
                translation__entity__resource__project=project,
                translation__locale__in=available_locales.filter(id__in=selected_ids),
            )

        identifier = uuid.uuid4().hex
        for contributor in contributors.distinct():
            notify.send(
                request.user,
                recipient=contributor,
                verb="has sent a message in",
                target=project,
                description=form.cleaned_data.get("message"),
                identifier=identifier,
            )

    # Detect previously sent notifications using a unique identifier
    # TODO: We should simplify this with a custom Notifications model
    notifications = []

    identifiers = {
        data["identifier"]
        for data in list(
            Notification.objects.filter(
                description__isnull=False,
                target_content_type=ContentType.objects.get_for_model(project),
                target_object_id=project.id,
            ).values_list("data", flat=True)
        )
    }

    for identifier in identifiers:
        notifications.append(Notification.objects.filter(data__contains=identifier)[0])

    notifications.sort(key=lambda x: x.timestamp, reverse=True)

    # Recipient shortcuts
    incomplete = []
    complete = []
    for available_locale in available_locales:
        completion_percent = available_locale.get_chart(project)["completion_percent"]
        if completion_percent == 100:
            complete.append(available_locale.pk)
        else:
            incomplete.append(available_locale.pk)

    return render(
        request,
        "projects/includes/manual_notifications.html",
        {
            "form": forms.NotificationsForm(),
            "project": project,
            "available_locales": available_locales,
            "notifications": notifications,
            "incomplete": incomplete,
            "complete": complete,
        },
    )


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
