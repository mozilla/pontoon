import json

import bleach

from guardian.decorators import permission_required_or_403

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.aggregates import ArrayAgg, StringAgg
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Prefetch, Q, TextField
from django.db.models.functions import Cast
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.http import require_POST
from django.views.generic.detail import DetailView

from pontoon.actionlog.models import ActionLog
from pontoon.actionlog.utils import log_action
from pontoon.base import forms
from pontoon.base.models import Locale, Project, TranslationMemoryEntry, User
from pontoon.base.utils import get_locale_or_redirect, require_AJAX
from pontoon.contributors.views import ContributorsMixin
from pontoon.insights.utils import get_locale_insights
from pontoon.teams.forms import LocaleRequestForm


def teams(request):
    """List all active localization teams."""
    locales = Locale.objects.available().prefetch_related(
        "latest_translation__user", "latest_translation__approved_user"
    )

    form = LocaleRequestForm()

    if not locales:
        return render(request, "no_projects.html", {"title": "Teams"})

    return render(
        request,
        "teams/teams.html",
        {
            "locales": locales,
            "form": form,
            "top_instances": locales.get_top_instances(),
        },
    )


def team(request, locale):
    """Team dashboard."""
    locale = get_locale_or_redirect(locale, "pontoon.teams.team", "locale")
    if isinstance(locale, HttpResponseRedirect):
        return locale
    available_count = locale.project_set.available().visible_for(request.user).count()
    visible_count = locale.project_set.visible().visible_for(request.user).count()

    if not available_count:
        raise Http404

    return render(
        request, "teams/team.html", {"count": visible_count, "locale": locale}
    )


@require_AJAX
def ajax_projects(request, locale):
    """Projects tab."""
    locale = get_object_or_404(Locale, code=locale)

    projects = (
        Project.objects.visible()
        .visible_for(request.user)
        .filter(Q(locales=locale) | Q(can_be_requested=True))
        .prefetch_project_locale(locale)
        .order_by("name")
        .annotate(enabled_locales=Count("project_locale", distinct=True))
    )

    enabled_projects = projects.filter(locales=locale)
    no_visible_projects = enabled_projects.count() == 0

    project_request_enabled = (
        request.user.is_authenticated and projects.exclude(locales=locale).count() > 0
    )

    pretranslated_projects = enabled_projects.filter(
        project_locale__pretranslation_enabled=True, project_locale__locale=locale
    )

    pretranslation_request_enabled = (
        request.user.is_authenticated
        and locale in request.user.can_translate_locales
        and locale.code in settings.GOOGLE_AUTOML_SUPPORTED_LOCALES
        and pretranslated_projects.count() < enabled_projects.count()
    )

    if not projects:
        raise Http404

    return render(
        request,
        "teams/includes/projects.html",
        {
            "locale": locale,
            "projects": projects,
            "enabled_projects": enabled_projects,
            "no_visible_projects": no_visible_projects,
            "project_request_enabled": project_request_enabled,
            "pretranslated_projects": pretranslated_projects,
            "pretranslation_request_enabled": pretranslation_request_enabled,
        },
    )


@require_AJAX
def ajax_insights(request, locale):
    """Insights tab."""
    if not settings.ENABLE_INSIGHTS:
        raise ImproperlyConfigured("ENABLE_INSIGHTS variable not set in settings.")

    locale = get_object_or_404(Locale, code=locale)

    # Cannot use cache.get_or_set(), because it always calls the slow function
    # get_locale_insights(). The reason we use cache in first place is to avoid that.
    key = f"/{__name__}/{locale.code}/insights"
    insights = cache.get(key)
    if not insights:
        insights = get_locale_insights(Q(locale=locale))
        cache.set(key, insights, settings.VIEW_CACHE_TIMEOUT)

    return render(request, "teams/includes/insights.html", insights)


@require_AJAX
def ajax_info(request, locale):
    """Info tab."""
    locale = get_object_or_404(Locale, code=locale)

    return render(request, "teams/includes/info.html", {"locale": locale})


@require_POST
@permission_required_or_403("base.can_manage_locale", (Locale, "code", "locale"))
@transaction.atomic
def ajax_update_info(request, locale):
    team_description = request.POST.get("team_info", None)
    team_description = bleach.clean(
        team_description,
        strip=True,
        tags=settings.ALLOWED_TAGS,
        attributes=settings.ALLOWED_ATTRIBUTES,
    )
    locale = get_object_or_404(Locale, code=locale)
    locale.team_description = team_description
    locale.save()
    return HttpResponse(team_description)


@permission_required_or_403("base.can_manage_locale", (Locale, "code", "locale"))
@transaction.atomic
def ajax_permissions(request, locale):
    locale = get_object_or_404(Locale, code=locale)
    project_locales = locale.project_locale.visible().visible_for(request.user)

    if request.method == "POST":
        locale_form = forms.LocalePermsForm(
            request.POST, instance=locale, prefix="general", user=request.user
        )
        project_locale_form = forms.ProjectLocalePermsFormsSet(
            request.POST,
            prefix="project-locale",
            queryset=project_locales,
            form_kwargs={"user": request.user},
        )

        if locale_form.is_valid() and project_locale_form.is_valid():
            locale_form.save()
            project_locale_form.save()

        else:
            errors = locale_form.errors
            errors.update(project_locale_form.errors_dict)
            error_msg = bleach.clean(json.dumps(errors))
            return HttpResponseBadRequest(error_msg)

    else:
        project_locale_form = forms.ProjectLocalePermsFormsSet(
            prefix="project-locale",
            queryset=project_locales,
            form_kwargs={"user": request.user},
        )

    managers = locale.managers_group.user_set.order_by("email")
    translators = locale.translators_group.user_set.exclude(pk__in=managers).order_by(
        "email"
    )

    locale_contributors = (
        User.objects.filter(
            translation__locale=locale, profile__system_user=False, is_active=True
        )
        .distinct()
        .order_by("email")
    )
    contributors = [
        contributor
        for contributor in locale_contributors
        if contributor not in managers and contributor not in translators
    ]

    project_locales = project_locales.prefetch_related(
        "project",
        Prefetch(
            "translators_group__user_set",
            queryset=User.objects.order_by("email"),
            to_attr="fetched_translators",
        ),
    ).order_by("project__name")

    for project_locale in project_locales:
        if not project_locale.has_custom_translators:
            continue

        project_locale.translators = (
            project_locale.translators_group.fetched_translators
        )
        project_locale.contributors = [
            contributor
            for contributor in locale_contributors
            if contributor not in project_locale.translators
        ]

    hide_project_selector = all([pl.has_custom_translators for pl in project_locales])

    return render(
        request,
        "teams/includes/permissions.html",
        {
            "locale": locale,
            "contributors": contributors,
            "translators": translators,
            "managers": managers,
            "project_locale_form": project_locale_form,
            "project_locales": project_locales,
            "hide_project_selector": hide_project_selector,
        },
    )


@require_AJAX
@permission_required_or_403("base.can_manage_locale", (Locale, "code", "locale"))
@transaction.atomic
def ajax_translation_memory(request, locale):
    """Translation Memory tab."""
    locale = get_object_or_404(Locale, code=locale)
    search_query = request.GET.get("search", "").strip()
    page_number = request.GET.get("page", 1)

    tm_entries = TranslationMemoryEntry.objects.filter(locale=locale)

    # Apply search filter if a search query is provided
    if search_query:
        tm_entries = tm_entries.filter(
            Q(source__icontains=search_query) | Q(target__icontains=search_query)
        )

    tm_entries = (
        # Group by "source" and "target"
        tm_entries.values("source", "target").annotate(
            count=Count("id"),
            ids=ArrayAgg("id"),
            # Concatenate entity IDs
            entity_ids=StringAgg(
                Cast("entity_id", output_field=TextField()), delimiter=","
            ),
        )
    )

    per_page = 100  # Number of entries per page
    paginator = Paginator(tm_entries, per_page)
    page = paginator.get_page(page_number)

    # If the subsequent page is requested, return only the entries
    template = (
        "teams/widgets/translation_memory_entries.html"
        if page_number != 1
        else "teams/includes/translation_memory.html"
    )

    return render(
        request,
        template,
        {
            "locale": locale,
            "search_query": search_query,
            "tm_entries": page,
            "has_next": page.has_next(),
        },
    )


@require_AJAX
@require_POST
@permission_required_or_403("base.can_manage_locale", (Locale, "code", "locale"))
@transaction.atomic
def ajax_translation_memory_edit(request, locale):
    """Edit Translation Memory entries."""
    ids = request.POST.getlist("ids[]")

    try:
        target = request.POST["target"]
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    tm_entries = TranslationMemoryEntry.objects.filter(id__in=ids)
    tm_entries.update(target=target)

    log_action(
        ActionLog.ActionType.TM_ENTRIES_EDITED,
        request.user,
        tm_entries=tm_entries,
    )

    return HttpResponse("ok")


@require_AJAX
@require_POST
@permission_required_or_403("base.can_manage_locale", (Locale, "code", "locale"))
@transaction.atomic
def ajax_translation_memory_delete(request, locale):
    """Delete Translation Memory entries."""
    ids = request.POST.getlist("ids[]")
    tm_entries = TranslationMemoryEntry.objects.filter(id__in=ids)

    for tm_entry in tm_entries:
        if tm_entry.entity and tm_entry.locale:
            log_action(
                ActionLog.ActionType.TM_ENTRY_DELETED,
                request.user,
                entity=tm_entry.entity,
                locale=tm_entry.locale,
            )

    tm_entries.delete()

    return HttpResponse("ok")


@login_required(redirect_field_name="", login_url="/403")
@require_POST
def request_item(request, locale=None):
    """Request projects and teams to be added."""
    user = request.user

    # Request projects to be enabled for team
    if locale:
        slug_list = request.POST.getlist("projects[]")
        locale = get_object_or_404(Locale, code=locale)

        # Validate projects
        project_list = (
            Project.objects.visible()
            .visible_for(user)
            .filter(slug__in=slug_list, can_be_requested=True)
        )
        if not project_list:
            return HttpResponseBadRequest(
                "Bad Request: Non-existent projects specified"
            )

        projects = "".join(f"- {p.name} ({p.slug})\n" for p in project_list)

        mail_subject = "Project request for {locale} ({code})".format(
            locale=locale.name, code=locale.code
        )

        payload = {
            "locale": locale.name,
            "code": locale.code,
            "projects": projects,
            "user": user.display_name_and_email,
            "user_role": user.locale_role(locale),
            "user_url": request.build_absolute_uri(user.profile_url),
        }

    # Request new teams to be enabled
    else:
        form = LocaleRequestForm(request.POST)
        if not form.is_valid():
            if form.has_error("code", "unique"):
                return HttpResponse("This team already exists.", status=409)
            return HttpResponseBadRequest(form.errors.as_json())

        code = form.cleaned_data["code"]
        name = form.cleaned_data["name"]

        mail_subject = "New team request: {locale} ({code})".format(
            locale=name, code=code
        )

        payload = {
            "locale": name,
            "code": code,
            "user": user.display_name_and_email,
            "user_role": user.role(),
            "user_url": request.build_absolute_uri(user.profile_url),
        }

    if settings.PROJECT_MANAGERS[0] != "":
        template = get_template("teams/email_request_item.jinja")
        mail_body = template.render(payload)
        cc = {user.contact_email}
        if locale:
            cc.update(
                set(locale.managers_group.user_set.values_list("email", flat=True))
            )

        EmailMessage(
            subject=mail_subject,
            body=mail_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=settings.PROJECT_MANAGERS,
            cc=cc,
            reply_to=[user.contact_email],
        ).send()
    else:
        raise ImproperlyConfigured(
            "PROJECT_MANAGERS not defined in settings. Email recipient unknown."
        )

    return HttpResponse("ok")


@login_required(redirect_field_name="", login_url="/403")
@require_POST
def request_pretranslation(request, locale):
    """Request pretranslation to be enabled for projects."""
    user = request.user
    slug_list = request.POST.getlist("projects[]")
    locale = get_object_or_404(Locale, code=locale)

    # Validate user
    if locale not in user.can_translate_locales:
        return HttpResponseBadRequest(
            "Bad Request: Requester is not a translator or manager for the locale"
        )

    # Validate locale
    if locale.code not in settings.GOOGLE_AUTOML_SUPPORTED_LOCALES:
        return HttpResponseBadRequest("Bad Request: Locale not supported")

    # Validate projects
    project_list = (
        Project.objects.visible().visible_for(user).filter(slug__in=slug_list)
    )
    if not project_list:
        return HttpResponseBadRequest("Bad Request: Non-existent projects specified")

    projects = "".join(f"- {p.name} ({p.slug})\n" for p in project_list)

    mail_subject = "Pretranslation request for {locale} ({code})".format(
        locale=locale.name, code=locale.code
    )

    payload = {
        "locale": locale,
        "projects": projects,
        "user": user.display_name_and_email,
        "user_role": user.locale_role(locale),
        "user_url": request.build_absolute_uri(user.profile_url),
    }

    if settings.PROJECT_MANAGERS[0] != "":
        template = get_template("teams/email_request_pretranslation.jinja")
        mail_body = template.render(payload)
        cc = {user.contact_email}
        cc.update(set(locale.managers_group.user_set.values_list("email", flat=True)))

        EmailMessage(
            subject=mail_subject,
            body=mail_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=settings.PROJECT_MANAGERS,
            cc=cc,
            reply_to=[user.contact_email],
        ).send()
    else:
        raise ImproperlyConfigured(
            "PROJECT_MANAGERS not defined in settings. Email recipient unknown."
        )

    return HttpResponse("ok")


class LocaleContributorsView(ContributorsMixin, DetailView):
    """
    Renders view of contributors for the team.
    """

    template_name = "teams/includes/contributors.html"
    model = Locale
    slug_field = "code"
    slug_url_kwarg = "locale"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(locale=self.object, **kwargs)
        contributors = context["contributors"]
        context["managers"] = [
            c for c in contributors if c.user_locale_role == "Manager"
        ]
        context["translators"] = [
            c for c in contributors if c.user_locale_role == "Translator"
        ]
        context["regular_contributors"] = [
            c
            for c in contributors
            if c not in context["managers"] and c not in context["translators"]
        ]
        return context

    def get_context_object_name(self, obj):
        return "locale"

    def contributors_filter(self, **kwargs):
        return Q(locale=self.object)
