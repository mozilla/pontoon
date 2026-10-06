import logging

from typing import cast

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.utils.datastructures import MultiValueDictKeyError

from pontoon.administration.forms import (
    ExternalResourceInlineFormSet,
    ProjectForm,
    RepositoryInlineFormSet,
    TagInlineFormSet,
)
from pontoon.administration.tasks import calculate_stats_task
from pontoon.base import utils
from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    Repository,
    Resource,
)
from pontoon.base.models.project import ProjectQuerySet
from pontoon.base.utils import require_AJAX
from pontoon.pretranslation.tasks import pretranslate_task
from pontoon.sync.tasks import sync_project_task


log = logging.getLogger(__name__)


def admin(request):
    """Admin interface."""
    if not request.user.has_perm("base.can_manage_project"):
        raise PermissionDenied

    projects = (
        Project.objects.filter(
            Exists(Repository.objects.filter(project=OuterRef("pk")))
        )
        .prefetch_related(
            "latest_translation__entity__resource",
            "latest_translation__locale",
            "latest_translation__user",
            "latest_translation__approved_user",
        )
        .order_by("name")
    )

    enabled_projects = projects.filter(disabled=False)
    disabled_projects = projects.filter(disabled=True)
    project_stats = projects.stats_data_as_dict()

    return render(
        request,
        "admin.html",
        {
            "admin": True,
            "enabled_projects": enabled_projects,
            "disabled_projects": disabled_projects,
            "project_stats": project_stats,
        },
    )


@login_required(redirect_field_name="", login_url="/403")
@require_AJAX
def get_slug(request):
    """Convert project name to slug."""
    if not request.user.has_perm("base.can_manage_project"):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: You don't have permission to retrieve the project slug.",
            },
            status=403,
        )

    try:
        name = request.GET["name"]
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    slug = slugify(name)
    return HttpResponse(slug)


@login_required(redirect_field_name="", login_url="/403")
@require_AJAX
def get_project_locales(request):
    """Get a map of project names and corresponding locale codes."""
    if not request.user.has_perm("base.can_manage_project"):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: You don't have permission to retrieve project locales.",
            },
            status=403,
        )

    data = {}
    for p in Project.objects.prefetch_related("locales"):
        data[p.name] = [locale.pk for locale in p.locales.all()]

    return JsonResponse(data, safe=False)


@transaction.atomic
def manage_project(request, slug=None, template="admin_project.html"):
    """Admin project."""
    log.debug("Admin project.")

    if not request.user.has_perm("base.can_manage_project"):
        raise PermissionDenied

    form = ProjectForm()
    repo_formset = RepositoryInlineFormSet()
    external_resource_formset = ExternalResourceInlineFormSet()
    tag_formset = TagInlineFormSet()
    locales_readonly = Locale.objects.none()
    locales_selected = Locale.objects.none()
    locales_pretranslate = Locale.objects.none()
    subtitle = "Add project"
    pk = None
    project = None

    # Save project
    if request.method == "POST":
        locales_readonly = Locale.objects.filter(
            pk__in=request.POST.getlist("locales_readonly")
        )
        locales_selected = Locale.objects.filter(
            pk__in=request.POST.getlist("locales")
        ).exclude(pk__in=locales_readonly)
        locales_pretranslate = Locale.objects.filter(
            pk__in=request.POST.getlist("locales_pretranslate")
        )

        # Update existing project
        try:
            pk = request.POST["pk"]
            project = (
                cast(ProjectQuerySet, Project.objects)
                .visible_for(request.user)
                .get(pk=pk)
            )
            if not project.has_repositories:
                raise Http404
            form = ProjectForm(request.POST, instance=project)
            # Needed if form invalid
            repo_formset = RepositoryInlineFormSet(request.POST, instance=project)
            tag_formset = (
                TagInlineFormSet(request.POST, instance=project)
                if project.tags_enabled
                else None
            )
            external_resource_formset = ExternalResourceInlineFormSet(
                request.POST, instance=project
            )
            subtitle = "Edit project"

        # Add a new project
        except MultiValueDictKeyError:
            form = ProjectForm(request.POST)
            # Needed if form invalid
            repo_formset = RepositoryInlineFormSet(request.POST)
            external_resource_formset = ExternalResourceInlineFormSet(request.POST)
            tag_formset = None

        if form.is_valid():
            project = cast(Project, form.save(commit=False))
            repo_formset = RepositoryInlineFormSet(request.POST, instance=project)
            external_resource_formset = ExternalResourceInlineFormSet(
                request.POST, instance=project
            )
            if tag_formset:
                tag_formset = TagInlineFormSet(request.POST, instance=project)
            formsets_valid = (
                repo_formset.is_valid()
                and external_resource_formset.is_valid()
                and (tag_formset.is_valid() if tag_formset else True)
            )
            if formsets_valid:
                project.save()
                pk = project.pk
                data = form.cleaned_data

                if data.get("set_locales_from_repo", False):
                    project_locales = ProjectLocale.objects.filter(project=project)
                else:
                    # Manually save ProjectLocales due to intermediary model
                    locales_form = data.get("locales", set())
                    locales_readonly_form = data.get("locales_readonly", set())
                    locales = locales_form | locales_readonly_form

                    ProjectLocale.objects.filter(project=project).exclude(
                        locale__pk__in=[loc.pk for loc in locales]
                    ).delete()

                    for locale in locales:
                        # The implicit pre_save and post_save signals sent here are required
                        # to maintain django-guardian permissions.
                        ProjectLocale.objects.get_or_create(
                            project=project, locale=locale
                        )

                    project_locales = ProjectLocale.objects.filter(project=project)

                    # Update readonly flags
                    locales_readonly_pks = [loc.pk for loc in locales_readonly_form]
                    project_locales.filter(readonly=True).exclude(
                        locale__pk__in=locales_readonly_pks
                    ).update(readonly=False)
                    project_locales.filter(
                        locale__pk__in=locales_readonly_pks, readonly=False
                    ).update(readonly=True)

                # Update pretranslate flags
                locales_pretranslate_form = data.get("locales_pretranslate", [])
                locales_pretranslate_pks = [loc.pk for loc in locales_pretranslate_form]
                project_locales.filter(pretranslation_enabled=True).exclude(
                    locale__pk__in=locales_pretranslate_pks,
                ).update(pretranslation_enabled=False)
                project_locales.filter(
                    locale__pk__in=locales_pretranslate_pks,
                    pretranslation_enabled=False,
                ).update(pretranslation_enabled=True)

                repo_formset.save()
                external_resource_formset.save()
                if tag_formset:
                    tag_formset.save()

                # Properly displays formsets, but removes errors (if valid only)
                repo_formset = RepositoryInlineFormSet(instance=project)
                external_resource_formset = ExternalResourceInlineFormSet(
                    instance=project
                )
                if project.tags_enabled:
                    tag_formset = TagInlineFormSet(instance=project)
                subtitle += ". Saved."
            else:
                subtitle += ". Error."
        else:
            subtitle += ". Error."

    # If URL specified and found, show edit, otherwise show add form
    elif slug is not None:
        try:
            project = Project.objects.get(slug=slug)
            if not project.has_repositories:
                raise Http404
            pk = project.pk
            form = ProjectForm(instance=project)
            repo_formset = RepositoryInlineFormSet(instance=project)
            tag_formset = (
                TagInlineFormSet(instance=project) if project.tags_enabled else None
            )
            external_resource_formset = ExternalResourceInlineFormSet(instance=project)
            locales_readonly = Locale.objects.filter(
                project_locale__readonly=True,
                project_locale__project=project,
            )
            locales_selected = project.locales.exclude(pk__in=locales_readonly)
            locales_pretranslate = Locale.objects.filter(
                project_locale__pretranslation_enabled=True,
                project_locale__project=project,
            )
            subtitle = "Edit project"
        except Project.DoesNotExist:
            form = ProjectForm(initial={"slug": slug})

    # Override default label suffix
    form.label_suffix = ""

    projects = sorted([p.name for p in Project.objects.all()])

    locales_available = Locale.objects.exclude(pk__in=locales_readonly).exclude(
        pk__in=locales_selected
    )

    locales_pretranslate_available = locales_selected.exclude(
        pk__in=locales_pretranslate
    )

    # Admins reason in terms of locale codes (see bug 1394194)
    locales_readonly = locales_readonly.order_by("code")
    locales_selected = locales_selected.order_by("code")
    locales_available = locales_available.order_by("code")
    locales_pretranslate = locales_pretranslate.order_by("code")
    locales_pretranslate_available = locales_pretranslate_available.order_by("code")

    data = {
        "slug": slug,
        "form": form,
        "repo_formset": repo_formset,
        "tag_formset": tag_formset,
        "external_resource_formset": external_resource_formset,
        "locales_readonly": locales_readonly,
        "locales_selected": locales_selected,
        "locales_available": locales_available,
        "locales_pretranslate": locales_pretranslate,
        "locales_pretranslate_available": locales_pretranslate_available,
        "subtitle": subtitle,
        "pk": pk,
        "project": project,
        "projects": projects,
    }

    # Set locale in Translate link
    if (
        project
        and project.pk
        and Resource.objects.current().filter(project=project).exists()
        and locales_selected
    ):
        locale = (
            utils.get_project_locale_from_request(request, project.locales)
            or locales_selected[0].code
        )
        if locale:
            data["translate_locale"] = locale

    return render(request, template, data)


@login_required(redirect_field_name="", login_url="/403")
@require_AJAX
def manually_calculate_stats(request):
    if not request.user.has_perm("base.can_manage_project"):
        return HttpResponseForbidden(
            "Forbidden: You don't have permission for calculating statistics"
        )

    calculate_stats_task.delay()

    return HttpResponse("ok")


@login_required(redirect_field_name="", login_url="/403")
@require_AJAX
def manually_sync_project(request, slug):
    if not request.user.has_perm("base.can_manage_project") or not settings.MANUAL_SYNC:
        return HttpResponseForbidden(
            "Forbidden: You don't have permission for syncing projects"
        )

    project = Project.objects.get(slug=slug)
    sync_project_task.delay(project.pk)

    return HttpResponse("ok")


@login_required(redirect_field_name="", login_url="/403")
@require_AJAX
def manually_pretranslate_project(request, slug):
    if not request.user.has_perm("base.can_manage_project"):
        return HttpResponseForbidden(
            "Forbidden: You don't have permission for pretranslating projects"
        )

    project = Project.objects.get(slug=slug)
    pretranslate_task.delay(project.pk)

    return HttpResponse("ok")
