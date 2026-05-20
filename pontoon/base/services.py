import uuid

from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from pontoon.actionlog.models import ActionLog
from pontoon.api.models import PersonalAccessToken
from pontoon.base.models.comment import Comment
from pontoon.base.models.locale import Locale, LocaleCodeHistory
from pontoon.base.models.permission_changelog import PermissionChangelog
from pontoon.base.models.project import Project, ProjectSlugHistory
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.base.models.translation import Translation
from pontoon.terminology.models import Term


def readonly_exists(projects, locale):
    if not isinstance(projects, (QuerySet, tuple, list)):
        projects = [projects]

    return ProjectLocale.objects.filter(
        project__in=projects,
        locale=locale,
        readonly=True,
    ).exists()


def get_project_or_redirect(
    slug, redirect_view_name, slug_arg_name, request_user, **kwargs
):
    """
    Attempts to get a project with the given slug. If the project doesn't exist, it checks if the slug is in the
    ProjectSlugHistory and if so, it redirects to the current project slug URL. If the old slug is not found in the
    history, it raises an Http404 error.
    """

    try:
        project = Project.objects.visible_for(request_user).available().get(slug=slug)
        return project
    except Project.DoesNotExist:
        slug_history = (
            ProjectSlugHistory.objects.filter(old_slug=slug)
            .order_by("-created_at")
            .first()
        )
        if slug_history is not None:
            redirect_kwargs = {slug_arg_name: slug_history.project.slug}
            redirect_kwargs.update(kwargs)
            redirect_url = reverse(redirect_view_name, kwargs=redirect_kwargs)
            return redirect(redirect_url)
        else:
            raise Http404


def get_locale_or_redirect(code, redirect_view_name=None, url_arg_name=None, **kwargs):
    """
    Attempts to retrieve a locale using the given code. If the locale does not exist, it checks the LocaleCodeHistory
    for a record of the old code. If an entry is found, it either redirects to the view specified by redirect_view_name
    using the new locale code or returns the Locale object if no redirect_view_name is provided.
    The url_arg_name parameter specifies the argument name for the locale code used in the URL pattern of the redirect view.
    If the old code is not found in the history, it raises an Http404 error.
    """

    try:
        return Locale.objects.get(code=code)
    except Locale.DoesNotExist:
        code_history = (
            LocaleCodeHistory.objects.filter(old_code=code)
            .order_by("-created_at")
            .first()
        )
    if code_history:
        if not redirect_view_name or not url_arg_name:
            return code_history.locale

        redirect_kwargs = {url_arg_name: code_history.locale.code}
        redirect_kwargs.update(kwargs)
        redirect_url = reverse(redirect_view_name, kwargs=redirect_kwargs)
        return redirect(redirect_url)

    raise Http404


def anonymize_user(user):
    random_hash = uuid.uuid4().hex
    new_user = User.objects.create_user(
        username="deleted-user-" + random_hash,
        email="deleted-user-" + random_hash + "@example.com",
        first_name="Deleted User",
        is_active=False,
    )

    ActionLog.objects.filter(performed_by=user).update(performed_by=new_user)
    PermissionChangelog.objects.filter(performed_by=user).update(performed_by=new_user)
    PermissionChangelog.objects.filter(performed_on=user).update(performed_on=new_user)
    Project.objects.filter(contact=user).update(contact=new_user)
    Translation.objects.filter(user=user).update(user=new_user)
    Translation.objects.filter(approved_user=user).update(approved_user=new_user)
    Translation.objects.filter(unapproved_user=user).update(unapproved_user=new_user)
    Translation.objects.filter(rejected_user=user).update(rejected_user=new_user)
    Translation.objects.filter(unrejected_user=user).update(unrejected_user=new_user)
    Term.objects.filter(created_by=user).update(created_by=new_user)
    Comment.objects.filter(author=user).update(author=new_user)
    PersonalAccessToken.objects.filter(user=user).update(revoked=True)
