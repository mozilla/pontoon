from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import OuterRef, Q, Subquery
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from pontoon.base.models.project import Project
from pontoon.sync.models import Sync


def sync_log_list(request: HttpRequest):
    sync_events = Sync.objects.filter(project=OuterRef("pk")).order_by("-start_time")
    show_no_changes = request.GET.get("no_changes") == "1"
    if not show_no_changes:
        sync_events = sync_events.exclude(status=Sync.Status.NO_CHANGES)
    projects = (
        Project.objects.filter(disabled=False)
        .order_by("name")
        .annotate(
            sync_start_time=Subquery(sync_events.values("start_time")[:1]),
            sync_end_time=Subquery(sync_events.values("end_time")[:1]),
            sync_status=Subquery(sync_events.values("status")[:1]),
        )
        .values("name", "slug", "sync_start_time", "sync_end_time", "sync_status")
    )
    for project in projects:
        project["sync_url"] = reverse(
            "pontoon.sync.log.project", kwargs={"project_slug": project["slug"]}
        )
    return render(
        request,
        "sync/log_list.html",
        {
            "is_manager": request.user.has_perm("base.can_manage_project"),
            "projects": projects,
            "show_no_changes": show_no_changes,
        },
    )


def sync_log_project(request: HttpRequest, project_slug: str):
    if not request.user.has_perm("base.can_manage_project"):
        raise PermissionDenied

    project = get_object_or_404(Project, slug=project_slug)
    sync_events = Sync.objects.filter(project__slug=project_slug).order_by(
        "-start_time"
    )
    paginator = Paginator(sync_events, 24)

    try:
        req_page = request.GET.get("page")
        sync_page = paginator.page(req_page)
    except PageNotAnInteger:
        sync_page = paginator.page(1)
    except EmptyPage:
        sync_page = paginator.page(paginator.num_pages)
    return render(
        request,
        "sync/log_project.html",
        {"project_name": project.name, "sync_page": sync_page},
    )


def sync_log_errors(request: HttpRequest):
    if not request.user.has_perm("base.can_manage_project"):
        raise PermissionDenied

    sync_events = (
        Sync.objects.filter(project__disabled=False)
        .exclude(Q(status=Sync.Status.DONE) | Q(status=Sync.Status.NO_CHANGES))
        .order_by("-start_time")
        .select_related("project")
    )
    paginator = Paginator(sync_events, 24)

    try:
        req_page = request.GET.get("page")
        sync_page = paginator.page(req_page)
    except PageNotAnInteger:
        sync_page = paginator.page(1)
    except EmptyPage:
        sync_page = paginator.page(paginator.num_pages)

    for sync in sync_page:
        setattr(
            sync,
            "project_sync_url",
            reverse(
                "pontoon.sync.log.project", kwargs={"project_slug": sync.project.slug}
            ),
        )

    return render(request, "sync/log_errors.html", {"sync_page": sync_page})
