import json
import logging
import re
import xml.etree.ElementTree as ET

from typing import cast

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
from django.db.models import Count, F, Prefetch, Q, TextField
from django.db.models.functions import Cast
from django.db.models.manager import BaseManager
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
from pontoon.base.aggregated_stats import get_top_instances
from pontoon.base.models import (
    Locale,
    Project,
    TranslatedResource,
    TranslationMemoryEntry,
    User,
)
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.base.models.translation import Translation
from pontoon.base.utils import get_locale_or_redirect, require_AJAX
from pontoon.contributors.views import ContributorsMixin
from pontoon.insights.utils import get_locale_insights
from pontoon.teams.forms import LocaleRequestForm


log = logging.getLogger(__name__)


def teams(request):
    """List all active localization teams."""
    locales = Locale.objects.visible().prefetch_related(
        "latest_translation__entity__resource",
        "latest_translation__user",
        "latest_translation__approved_user",
    )

    form = LocaleRequestForm()

    if not locales:
        return render(request, "no_projects.html", {"title": "Teams"})

    locale_stats = locales.stats_data_as_dict()
    return render(
        request,
        "teams/teams.html",
        {
            "locales": locales,
            "all_locales_stats": TranslatedResource.objects.all().string_stats(),
            "locale_stats": locale_stats,
            "form": form,
            "top_instances": get_top_instances(locales, locale_stats),
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

    locale_stats = TranslatedResource.objects.filter(locale=locale).string_stats(
        request.user
    )

    return render(
        request,
        "teams/team.html",
        {"count": visible_count, "locale": locale, "locale_stats": locale_stats},
    )


@require_AJAX
def ajax_projects(request, locale):
    """Team Projects tab."""
    locale = get_object_or_404(Locale, code=locale)

    projects = cast(
        BaseManager[Project],
        Project.objects.visible().visible_for(request.user),
    ).order_by("name")

    enabled_projects = list(projects.filter(locales=locale))

    latest_activities = {
        trans.project_id: trans.latest_activity
        for trans in Translation.objects.filter(
            id__in=(
                ProjectLocale.objects.filter(
                    locale=locale, project__in=enabled_projects
                )
                .order_by()
                .values_list("latest_translation_id", flat=True)
            ),
        )
        .select_related("user", "approved_user")
        .prefetch_related("entity__resource")
        .annotate(project_id=F("entity__resource__project__id"))
    }

    projects_to_request = (
        projects.exclude(locales=locale)
        .filter(can_be_requested=True)
        .annotate(enabled_locales=Count("project_locale", distinct=True))
        if request.user.is_authenticated
        else []
    )

    if not enabled_projects and not projects_to_request:
        raise Http404

    if (
        request.user.is_authenticated
        and locale.code in settings.GOOGLE_AUTOML_SUPPORTED_LOCALES
    ):
        pretranslated_project_ids = set(
            ProjectLocale.objects.filter(
                locale=locale,
                pretranslation_enabled=True,
                project__in=enabled_projects,
            )
            .order_by()
            .values_list("project_id", flat=True)
        )
        pretranslation_request_enabled = (
            len(pretranslated_project_ids) < len(enabled_projects)
            and request.user.can_translate_locales.filter(id=locale.id).exists()
        )
    else:
        pretranslated_project_ids = set()
        pretranslation_request_enabled = False

    return render(
        request,
        "teams/includes/projects.html",
        {
            "locale": locale,
            "project_stats": Project.objects.all().stats_data_as_dict(locale),
            "latest_activities": latest_activities,
            "enabled_projects": enabled_projects,
            "projects_to_request": projects_to_request,
            "pretranslated_project_ids": pretranslated_project_ids,
            "pretranslation_request_enabled": pretranslation_request_enabled,
        },
    )


@require_AJAX
def ajax_insights(request, locale):
    """Team Insights tab."""
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
    """Team Info tab."""
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

    community_builder_level_reached = 0
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
            community_builder_level_reached = locale_form.save()
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
            "community_builder_level_reached": community_builder_level_reached,
        },
    )


@require_AJAX
@permission_required_or_403("base.can_translate_locale", (Locale, "code", "locale"))
@transaction.atomic
def ajax_translation_memory(request, locale):
    """Translation Memory tab."""
    locale = get_object_or_404(Locale, code=locale)
    search_query = request.GET.get("search", "").strip()

    try:
        first_page_number = int(request.GET.get("page", 1))
        page_count = int(request.GET.get("pages", 1))
    except ValueError as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

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

    entries_per_page = 100
    paginator = Paginator(tm_entries, entries_per_page)

    combined_entries = []

    for page_number in range(first_page_number, first_page_number + page_count):
        if page_number > paginator.num_pages:
            break
        page = paginator.get_page(page_number)
        combined_entries.extend(page.object_list)

    # For the inital load, render the entire tab. For subsequent requests
    # (determined by the "page" attribute), only render the entries.
    template = (
        "teams/widgets/translation_memory_entries.html"
        if "page" in request.GET
        else "teams/includes/translation_memory.html"
    )

    return render(
        request,
        template,
        {
            "locale": locale,
            "search_query": search_query,
            "tm_entries": combined_entries,
            "has_next": paginator.num_pages > page_number,
        },
    )


@require_AJAX
@require_POST
@permission_required_or_403("base.can_translate_locale", (Locale, "code", "locale"))
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
@permission_required_or_403("base.can_translate_locale", (Locale, "code", "locale"))
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


@require_AJAX
@require_POST
@permission_required_or_403("base.can_translate_locale", (Locale, "code", "locale"))
@transaction.atomic
def ajax_translation_memory_upload(request, locale):
    """Upload Translation Memory entries from a .TMX file."""
    try:
        file = request.FILES["tmx_file"]
    except MultiValueDictKeyError:
        return JsonResponse(
            {"status": False, "message": "No file uploaded."},
            status=400,
        )

    if file.size > 20 * 1024 * 1024:
        return JsonResponse(
            {
                "status": False,
                "message": "File size limit exceeded. The maximum allowed size is 20 MB.",
            },
            status=400,
        )

    if not file.name.endswith(".tmx"):
        return JsonResponse(
            {
                "status": False,
                "message": "Invalid file format. Only .TMX files are supported.",
            },
            status=400,
        )

    locale = get_object_or_404(Locale, code=locale)
    code = locale.code

    # Parse the TMX file
    try:
        tree = ET.parse(file)
        root = tree.getroot()
    except ET.ParseError as e:
        return JsonResponse(
            {"status": False, "message": f"Invalid XML file: {e}"}, status=400
        )

    # Extract TM entries
    file_entries = []
    srclang_pattern = re.compile(r"^en(?:[-_](us))?$", re.IGNORECASE)
    ns = {"xml": "http://www.w3.org/XML/1998/namespace"}

    header = root.find("header")
    header_srclang = header.attrib.get("srclang", "") if header else ""

    def get_seg_text(tu, lang, ns):
        # Try to find <tuv> with the xml:lang attribute
        seg = tu.find(f"./tuv[@xml:lang='{lang}']/seg", namespaces=ns)

        # If not found, try the lang attribute
        if seg is None:
            seg = tu.find(f"./tuv[@lang='{lang}']/seg")

        return seg.text.strip() if seg is not None and seg.text else None

    tu_elements = root.findall(".//tu")
    for tu in tu_elements:
        try:
            srclang = tu.attrib.get("srclang", header_srclang)
            tu_str = ET.tostring(tu, encoding="unicode")

            if not srclang_pattern.match(srclang):
                log.info(f"Skipping <tu> with unsupported srclang: {tu_str}")
                continue

            source = get_seg_text(tu, srclang, ns)
            target = get_seg_text(tu, code, ns)

            if source and target:
                file_entries.append({"source": source, "target": target})
            else:
                log.info(f"Skipping <tu> with missing or empty segment: {tu_str}")

        except Exception as e:
            log.info(f"Error processing <tu>: {e}")

    if not file_entries:
        return JsonResponse(
            {"status": False, "message": "No valid translation entries found."},
            status=400,
        )

    # Create TranslationMemoryEntry objects
    tm_entries = [
        TranslationMemoryEntry(
            source=entry["source"],
            target=entry["target"],
            locale=locale,
        )
        for entry in file_entries
    ]

    # Filter out entries that already exist in the database
    existing_combinations = set(
        TranslationMemoryEntry.objects.filter(locale=locale).values_list(
            "source", "target"
        )
    )
    tm_entries_to_create = [
        entry
        for entry in tm_entries
        if (entry.source, entry.target) not in existing_combinations
    ]

    created_entries = TranslationMemoryEntry.objects.bulk_create(
        tm_entries_to_create, batch_size=1000
    )

    log_action(
        ActionLog.ActionType.TM_ENTRIES_UPLOADED,
        request.user,
        tm_entries=created_entries,
    )

    parsed = len(file_entries)
    skipped_on_parse = len(tu_elements) - parsed
    imported = len(created_entries)
    duplicates = parsed - len(tm_entries_to_create)

    message = f"Importing TM entries complete. Imported: {imported}."
    if imported == 0:
        message = "No TM entries imported."

    if duplicates:
        message += f" Skipped duplicates: {duplicates}."

    return JsonResponse(
        {
            "status": True,
            "message": message,
            "parsed": parsed,
            "skipped_on_parse": skipped_on_parse,
            "imported": imported,
            "duplicates": duplicates,
        }
    )


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
    if not user.has_perm("base.can_translate_locale", locale):
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
