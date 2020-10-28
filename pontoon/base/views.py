import logging
import re

from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
    StreamingHttpResponse,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import condition, require_POST
from django.views.generic.edit import FormView

from notifications.signals import notify

from pontoon.actionlog.utils import log_action
from pontoon.base import forms
from pontoon.base import utils
from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    ProjectLocale,
    TranslationMemoryEntry,
    TranslatedResource,
    Translation,
    Comment,
)
from pontoon.base.templatetags.helpers import provider_login_url
from pontoon.checks.libraries import run_checks
from pontoon.checks.utils import are_blocking_checks


log = logging.getLogger(__name__)


# TRANSLATE VIEWs


def translate_locale_agnostic(request, slug, part):
    """Locale Agnostic Translate view."""
    user = request.user
    query = urlparse(request.get_full_path()).query
    query = "?%s" % query if query else ""

    if slug.lower() == "all-projects":
        project_locales = Locale.objects.available()
    else:
        project = get_object_or_404(
            Project.objects.visible_for(request.user).available(), slug=slug
        )
        project_locales = project.locales

    if user.is_authenticated:
        locale = user.profile.custom_homepage

        if locale and project_locales.filter(code=locale).exists():
            path = reverse(
                "pontoon.translate",
                kwargs=dict(project=slug, locale=locale, resource=part),
            )
            return redirect("%s%s" % (path, query))

    locale = utils.get_project_locale_from_request(request, project_locales)
    path = (
        reverse(
            "pontoon.translate", kwargs=dict(project=slug, locale=locale, resource=part)
        )
        if locale
        else reverse("pontoon.projects.project", kwargs=dict(slug=slug))
    )
    return redirect("%s%s" % (path, query))


@utils.require_AJAX
def locale_projects(request, locale):
    """Get active projects for locale."""
    locale = get_object_or_404(Locale, code=locale)

    return JsonResponse(locale.available_projects_list(request.user), safe=False)


@utils.require_AJAX
def locale_stats(request, locale):
    """Get locale stats used in All Resources part."""
    locale = get_object_or_404(Locale, code=locale)
    return JsonResponse(locale.stats(), safe=False)


@utils.require_AJAX
def locale_project_parts(request, locale, slug):
    """Get locale-project pages/paths with stats."""
    try:
        locale = Locale.objects.get(code=locale)
    except Locale.DoesNotExist as e:
        return JsonResponse(
            {"status": False, "message": "Not Found: {error}".format(error=e)},
            status=404,
        )

    try:
        project = Project.objects.visible_for(request.user).get(slug=slug)
    except Project.DoesNotExist as e:
        return JsonResponse(
            {"status": False, "message": "Not Found: {error}".format(error=e)},
            status=404,
        )

    try:
        return JsonResponse(locale.parts_stats(project), safe=False)
    except ProjectLocale.DoesNotExist:
        return JsonResponse(
            {"status": False, "message": "Locale not enabled for selected project."},
            status=400,
        )


@utils.require_AJAX
def authors_and_time_range(request, locale, slug, part):
    locale = get_object_or_404(Locale, code=locale)
    project = get_object_or_404(
        Project.objects.visible_for(request.user).available(), slug=slug
    )
    paths = [part] if part != "all-resources" else None

    translations = Translation.for_locale_project_paths(locale, project, paths)

    return JsonResponse(
        {
            "authors": translations.authors(),
            "counts_per_minute": translations.counts_per_minute(),
        },
        safe=False,
    )


def _get_entities_list(locale, preferred_source_locale, project, form):
    """Return a specific list of entities, as defined by the `entity_ids` field of the form.

    This is used for batch editing.
    """
    entities = (
        Entity.objects.filter(pk__in=form.cleaned_data["entity_ids"])
        .distinct()
        .order_by("order")
    )

    return JsonResponse(
        {
            "entities": Entity.map_entities(locale, preferred_source_locale, entities),
            "stats": TranslatedResource.objects.stats(
                project, form.cleaned_data["paths"], locale
            ),
        },
        safe=False,
    )


def _get_all_entities(user, locale, preferred_source_locale, project, form, entities):
    """Return entities without pagination.

    This is used by the in-context mode of the Translate page.
    """
    has_next = False
    entities_to_map = Entity.for_project_locale(
        user,
        project,
        locale,
        paths=form.cleaned_data["paths"],
        exclude_entities=form.cleaned_data["exclude_entities"],
    )
    visible_entities = entities.values_list("pk", flat=True)

    return JsonResponse(
        {
            "entities": Entity.map_entities(
                locale, preferred_source_locale, entities_to_map, visible_entities,
            ),
            "has_next": has_next,
            "stats": TranslatedResource.objects.stats(
                project, form.cleaned_data["paths"], locale
            ),
        },
        safe=False,
    )


def _get_paginated_entities(locale, preferred_source_locale, project, form, entities):
    """Return a paginated list of entities.

    This is used by the regular mode of the Translate page.
    """
    paginator = Paginator(entities, form.cleaned_data["limit"])

    try:
        entities_page = paginator.page(1)
    except EmptyPage:
        return JsonResponse({"has_next": False, "stats": {}})

    has_next = entities_page.has_next()
    entities_to_map = entities_page.object_list

    # If requested entity not on the first page
    if form.cleaned_data["entity"]:
        entity_pk = form.cleaned_data["entity"]
        entities_to_map_pks = [e.pk for e in entities_to_map]

        # TODO: entities_to_map.values_list() doesn't return entities from selected page
        if entity_pk not in entities_to_map_pks:
            if entity_pk in entities.values_list("pk", flat=True):
                entities_to_map_pks.append(entity_pk)
                entities_to_map = entities.filter(pk__in=entities_to_map_pks)

    return JsonResponse(
        {
            "entities": Entity.map_entities(
                locale, preferred_source_locale, entities_to_map, []
            ),
            "has_next": has_next,
            "stats": TranslatedResource.objects.stats(
                project, form.cleaned_data["paths"], locale
            ),
        },
        safe=False,
    )


@csrf_exempt
@require_POST
@utils.require_AJAX
def entities(request):
    """Get entities for the specified project, locale and paths."""
    form = forms.GetEntitiesForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {
                "status": False,
                "message": "{error}".format(
                    error=form.errors.as_json(escape_html=True)
                ),
            },
            status=400,
        )

    locale = get_object_or_404(Locale, code=form.cleaned_data["locale"])

    preferred_source_locale = ""
    if request.user.is_authenticated:
        preferred_source_locale = request.user.profile.preferred_source_locale

    project_slug = form.cleaned_data["project"]
    if project_slug == "all-projects":
        project = Project(slug=project_slug)
    else:
        project = get_object_or_404(Project, slug=project_slug)

    # Only return entities with provided IDs (batch editing)
    if form.cleaned_data["entity_ids"]:
        return _get_entities_list(locale, preferred_source_locale, project, form)

    # `Entity.for_project_locale` only requires a subset of the fields the form contains. We thus
    # make a new dict with only the keys we want to pass to that function.
    restrict_to_keys = (
        "paths",
        "status",
        "search",
        "exclude_entities",
        "extra",
        "time",
        "author",
        "tag",
    )
    form_data = {
        k: form.cleaned_data[k] for k in restrict_to_keys if k in form.cleaned_data
    }

    try:
        entities = Entity.for_project_locale(request.user, project, locale, **form_data)
    except ValueError as error:
        return JsonResponse(
            {"status": False, "message": "{error}".format(error=error)}, status=500
        )

    # Only return a list of entity PKs (batch editing: select all)
    if form.cleaned_data["pk_only"]:
        return JsonResponse({"entity_pks": list(entities.values_list("pk", flat=True))})

    # In-place view: load all entities
    if form.cleaned_data["inplace_editor"]:
        return _get_all_entities(
            request.user, locale, preferred_source_locale, project, form, entities
        )

    # Out-of-context view: paginate entities
    return _get_paginated_entities(
        locale, preferred_source_locale, project, form, entities
    )


def _serialize_translation_values(query):
    translations = query.values(
        "locale__pk",
        "locale__code",
        "locale__name",
        "locale__direction",
        "locale__script",
        "string",
    )

    return [
        {
            "locale": {
                "pk": translation["locale__pk"],
                "code": translation["locale__code"],
                "name": translation["locale__name"],
                "direction": translation["locale__direction"],
                "script": translation["locale__script"],
            },
            "translation": translation["string"],
        }
        for translation in translations
    ]


@utils.require_AJAX
def get_translations_from_other_locales(request):
    """Get entity translations for all but specified locale."""
    try:
        entity = request.GET["entity"]
        locale = request.GET["locale"]
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    entity = get_object_or_404(Entity, pk=entity)
    locale = get_object_or_404(Locale, code=locale)
    plural_form = None if entity.string_plural == "" else 0

    translations = (
        Translation.objects.filter(
            entity=entity, plural_form=plural_form, approved=True,
        )
        .exclude(locale=locale)
        .order_by("locale__name")
    )

    if request.user.is_authenticated:
        preferred_locales = request.user.profile.preferred_locales
        preferred = translations.filter(locale__in=preferred_locales)
        other = translations.exclude(locale__in=preferred_locales)

        preferred_translations = sorted(
            _serialize_translation_values(preferred),
            key=lambda t: request.user.profile.locales_order.index(t["locale"]["pk"]),
        )

        if request.user.profile.preferred_source_locale:
            # TODO: De-hardcode as part of bug 1328879.
            preferred_translations.insert(
                0,
                {
                    "locale": Locale.objects.get(code="en-US").serialize(),
                    "translation": entity.string,
                },
            )
    else:
        other = translations
        preferred_translations = []

    other_translations = _serialize_translation_values(other)

    payload = {
        "preferred": preferred_translations,
        "other": other_translations,
    }

    return JsonResponse(payload, safe=False)


@utils.require_AJAX
def get_translation_history(request):
    """Get history of translations of given entity to given locale."""
    try:
        entity = request.GET["entity"]
        locale = request.GET["locale"]
        plural_form = request.GET["plural_form"]
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    entity = get_object_or_404(Entity, pk=entity)
    locale = get_object_or_404(Locale, code=locale)

    translations = Translation.objects.filter(
        entity=entity, locale=locale,
    ).prefetch_related("comments")

    if plural_form != "-1":
        translations = translations.filter(plural_form=plural_form)
    translations = translations.order_by("-active", "rejected", "-date")

    payload = []

    for t in translations:
        u = t.user or User(username="Imported", first_name="Imported", email="imported")
        translation_dict = t.serialize()
        translation_dict.update(
            {
                "user": u.name_or_email,
                "uid": u.id,
                "username": u.username,
                "user_gravatar_url_small": u.gravatar_url(88),
                "date": t.date.strftime("%b %d, %Y %H:%M"),
                "date_iso": t.date.isoformat(),
                "approved_user": User.display_name_or_blank(t.approved_user),
                "unapproved_user": User.display_name_or_blank(t.unapproved_user),
                "comments": [c.serialize() for c in t.comments.order_by("timestamp")],
                "machinery_sources": t.machinery_sources_values,
            }
        )
        payload.append(translation_dict)

    return JsonResponse(payload, safe=False)


@utils.require_AJAX
def get_team_comments(request):
    """Get team comments for given locale."""
    try:
        entity = request.GET["entity"]
        locale = request.GET["locale"]
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    entity = get_object_or_404(Entity, pk=entity)
    locale = get_object_or_404(Locale, code=locale)
    comments = (
        Comment.objects.filter(entity=entity)
        .filter(Q(locale=locale) | Q(pinned=True))
        .order_by("timestamp")
    )

    payload = [c.serialize() for c in comments]

    return JsonResponse(payload, safe=False)


def _send_add_comment_notifications(user, comment, entity, locale, translation):
    # On translation comment, notify:
    #   - authors of other translation comments in the thread
    #   - translation author
    #   - translation reviewers
    if translation:
        recipients = set(translation.comments.values_list("author__pk", flat=True))

        if translation.user:
            recipients.add(translation.user.pk)
        if translation.approved_user:
            recipients.add(translation.approved_user.pk)
        if translation.unapproved_user:
            recipients.add(translation.unapproved_user.pk)
        if translation.rejected_user:
            recipients.add(translation.rejected_user.pk)
        if translation.unrejected_user:
            recipients.add(translation.unrejected_user.pk)

    # On team comment, notify:
    #   - project-locale translators or locale translators
    #   - locale managers
    #   - authors of other team comments in the thread
    #   - authors of translation comments
    #   - translation authors
    #   - translation reviewers
    else:
        recipients = set()
        project_locale = ProjectLocale.objects.get(
            project=entity.resource.project, locale=locale,
        )
        translations = Translation.objects.filter(entity=entity, locale=locale)

        translators = []
        # Some projects (e.g. system projects) don't have translators group
        if project_locale.translators_group:
            # Only notify translators of the project if defined
            translators = project_locale.translators_group.user_set.values_list(
                "pk", flat=True
            )
        if not translators:
            translators = locale.translators_group.user_set.values_list("pk", flat=True)

        recipients = recipients.union(translators)
        recipients = recipients.union(
            locale.managers_group.user_set.values_list("pk", flat=True)
        )

        recipients = recipients.union(
            Comment.objects.filter(entity=entity, locale=locale).values_list(
                "author__pk", flat=True
            )
        )

        recipients = recipients.union(
            Comment.objects.filter(translation__in=translations).values_list(
                "author__pk", flat=True
            )
        )

        recipients = recipients.union(translations.values_list("user__pk", flat=True))
        recipients = recipients.union(
            translations.values_list("approved_user__pk", flat=True)
        )
        recipients = recipients.union(
            translations.values_list("unapproved_user__pk", flat=True)
        )
        recipients = recipients.union(
            translations.values_list("rejected_user__pk", flat=True)
        )
        recipients = recipients.union(
            translations.values_list("unrejected_user__pk", flat=True)
        )

    # Notify users, mentioned in a comment
    usernames = re.findall(r"<a href=\"\/contributors/([\w.@+-]+)/\">.+</a>", comment)
    recipients = recipients.union(
        User.objects.filter(username__in=usernames).values_list("pk", flat=True)
    )

    for recipient in User.objects.filter(pk__in=recipients).exclude(pk=user.pk):
        notify.send(
            user,
            recipient=recipient,
            verb="has added a comment in",
            action_object=locale,
            target=entity,
            description=comment,
        )


def _send_pin_comment_notifications(user, comment):
    # When pinning a comment, notify:
    #   - authors of existing translations across all locales
    #   - reviewers of existing translations across all locales
    recipient_data = defaultdict(list)
    entity = comment.entity
    translations = Translation.objects.filter(entity=entity)

    for t in translations:
        for u in (
            t.user,
            t.approved_user,
            t.unapproved_user,
            t.rejected_user,
            t.unrejected_user,
        ):
            if u:
                recipient_data[u.pk].append(t.locale.pk)

    for recipient in User.objects.filter(pk__in=recipient_data.keys()).exclude(
        pk=user.pk
    ):
        # Send separate notification for each locale (which results in links to corresponding translate views)
        for locale in Locale.objects.filter(pk__in=recipient_data[recipient.pk]):
            notify.send(
                user,
                recipient=recipient,
                verb="has pinned a comment in",
                action_object=locale,
                target=entity,
                description=comment.content,
            )


@require_POST
@utils.require_AJAX
@login_required(redirect_field_name="", login_url="/403")
@transaction.atomic
def add_comment(request):
    """Add a comment."""
    form = forms.AddCommentForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {
                "status": False,
                "message": "{error}".format(
                    error=form.errors.as_json(escape_html=True)
                ),
            },
            status=400,
        )

    user = request.user
    comment = form.cleaned_data["comment"]
    translationId = form.cleaned_data["translation"]
    entity = get_object_or_404(Entity, pk=form.cleaned_data["entity"])
    locale = get_object_or_404(Locale, code=form.cleaned_data["locale"])

    if translationId:
        translation = get_object_or_404(Translation, pk=translationId)
    else:
        translation = None

    # Translation comment
    if translation:
        c = Comment(author=user, translation=translation, content=comment)
        log_action("comment:added", user, translation=translation)

    # Team comment
    else:
        c = Comment(author=user, entity=entity, locale=locale, content=comment)
        log_action("comment:added", user, entity=entity, locale=locale)

    c.save()

    _send_add_comment_notifications(user, comment, entity, locale, translation)

    return JsonResponse({"status": True})


@login_required(redirect_field_name="", login_url="/403")
@require_POST
@transaction.atomic
def pin_comment(request):
    """ Update a comment as pinned """
    comment_id = request.POST.get("comment_id", None)
    if not comment_id:
        return JsonResponse({"status": False, "message": "Bad Request"}, status=400)

    comment = get_object_or_404(Comment, id=comment_id)

    comment.pinned = True
    comment.save()

    _send_pin_comment_notifications(request.user, comment)

    return JsonResponse({"status": True})


@login_required(redirect_field_name="", login_url="/403")
@require_POST
@transaction.atomic
def unpin_comment(request):
    """ Update a comment as unpinned """
    comment_id = request.POST.get("comment_id", None)
    if not comment_id:
        return JsonResponse({"status": False, "message": "Bad Request"}, status=400)

    comment = get_object_or_404(Comment, id=comment_id)

    comment.pinned = False
    comment.save()

    return JsonResponse({"status": True})


@utils.require_AJAX
@login_required(redirect_field_name="", login_url="/403")
def get_users(request):
    """Get all users."""
    users = User.objects.all()
    payload = []

    for u in users:
        payload.append(
            {
                "gravatar": u.gravatar_url(44),
                "name": u.name_or_email,
                "url": u.profile_url,
            }
        )

    return JsonResponse(payload, safe=False)


@utils.require_AJAX
def perform_checks(request):
    """Perform quality checks and return a list of any failed ones."""
    try:
        entity = request.POST["entity"]
        locale_code = request.POST["locale_code"]
        original = request.POST["original"]
        string = request.POST["string"]
        ignore_warnings = request.POST.get("ignore_warnings", "false") == "true"
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    try:
        entity = Entity.objects.get(pk=entity)
    except Entity.DoesNotExist as e:
        return JsonResponse(
            {"status": False, "message": "Bad Request: {error}".format(error=e)},
            status=400,
        )

    failed_checks = run_checks(
        entity, locale_code, original, string, request.user.profile.quality_checks,
    )

    if are_blocking_checks(failed_checks, ignore_warnings):
        return JsonResponse({"failedChecks": failed_checks})
    else:
        return JsonResponse({"status": True})


@transaction.atomic
def download_translations(request):
    """Download translated resource."""
    try:
        slug = request.GET["slug"]
        code = request.GET["code"]
        part = request.GET["part"]
    except MultiValueDictKeyError:
        raise Http404

    content, filename = utils.get_download_content(slug, code, part)

    if content is None:
        raise Http404

    response = HttpResponse()
    response.content = content
    if filename.endswith(".zip"):
        response["Content-Type"] = "application/zip"
    else:
        response["Content-Type"] = "text/plain"
    response["Content-Disposition"] = "attachment; filename=" + filename

    return response


@login_required(redirect_field_name="", login_url="/403")
@require_POST
@transaction.atomic
def upload(request):
    """Upload translated resource."""
    try:
        slug = request.POST["slug"]
        code = request.POST["code"]
        part = request.POST["part"]
    except MultiValueDictKeyError:
        raise Http404

    locale = get_object_or_404(Locale, code=code)
    project = get_object_or_404(Project.objects.visible_for(request.user), slug=slug)

    if not request.user.can_translate(
        project=project, locale=locale
    ) or utils.readonly_exists(project, locale):
        return HttpResponseForbidden("You don't have permission to upload files.")

    form = forms.UploadFileForm(request.POST, request.FILES)

    if form.is_valid():
        f = request.FILES["uploadfile"]
        utils.handle_upload_content(slug, code, part, f, request.user)
        messages.success(request, "Translations updated from uploaded file.")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)

    response = HttpResponse(content="", status=303)
    response["Location"] = reverse(
        "pontoon.translate", kwargs={"locale": code, "project": slug, "resource": part},
    )
    return response


@condition(etag_func=None)
def download_translation_memory(request, locale, slug):
    locale = get_object_or_404(Locale, code=locale)

    if slug.lower() == "all-projects":
        project_filter = Q()
    else:
        project = get_object_or_404(
            Project.objects.visible_for(request.user).available(), slug=slug
        )
        project_filter = Q(project=project)

    tm_entries = (
        TranslationMemoryEntry.objects.filter(project_filter)
        .filter(locale=locale, translation__isnull=False)
        .exclude(Q(source="") | Q(target=""))
        .exclude(translation__approved=False, translation__fuzzy=False)
    )
    filename = "{code}.{slug}.tmx".format(code=locale.code, slug=slug)

    response = StreamingHttpResponse(
        utils.build_translation_memory_file(
            datetime.now(),
            locale.code,
            tm_entries.values_list(
                "entity__resource__path",
                "entity__key",
                "source",
                "target",
                "project__name",
                "project__slug",
            ).order_by("project__slug", "source"),
        ),
        content_type="text/xml",
    )
    response["Content-Disposition"] = 'attachment; filename="{filename}"'.format(
        filename=filename
    )
    return response


@utils.require_AJAX
def user_data(request):
    user = request.user

    if not user.is_authenticated:
        if settings.AUTHENTICATION_METHOD == "django":
            login_url = reverse("standalone_login")
        else:
            login_url = provider_login_url(request)

        return JsonResponse({"is_authenticated": False, "login_url": login_url})

    if settings.AUTHENTICATION_METHOD == "django":
        logout_url = reverse("standalone_logout")
    else:
        logout_url = reverse("account_logout")

    return JsonResponse(
        {
            "is_authenticated": True,
            "is_admin": user.has_perm("base.can_manage_project"),
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "name_or_email": user.name_or_email,
            "username": user.username,
            "manager_for_locales": list(
                user.managed_locales.values_list("code", flat=True)
            ),
            "translator_for_locales": list(
                user.translated_locales.values_list("code", flat=True)
            ),
            "translator_for_projects": user.translated_projects,
            "settings": {
                "quality_checks": user.profile.quality_checks,
                "force_suggestions": user.profile.force_suggestions,
            },
            "tour_status": user.profile.tour_status,
            "logout_url": logout_url,
            "gravatar_url_small": user.gravatar_url(88),
            "gravatar_url_big": user.gravatar_url(176),
            "notifications": user.serialized_notifications,
        }
    )


class AjaxFormView(FormView):
    """A form view that when the form is submitted, it will return a json
    response containing either an ``errors`` object with a bad response status
    if the form fails, or a ``result`` object supplied by the form's save
    method
    """

    @method_decorator(utils.require_AJAX)
    def get(self, *args, **kwargs):
        return super(AjaxFormView, self).get(*args, **kwargs)

    @method_decorator(utils.require_AJAX)
    def post(self, *args, **kwargs):
        return super(AjaxFormView, self).post(*args, **kwargs)

    def form_invalid(self, form):
        return JsonResponse(dict(errors=form.errors), status=400)

    def form_valid(self, form):
        return JsonResponse(dict(data=form.save()))


class AjaxFormPostView(AjaxFormView):
    """An Ajax form view that only allows POST requests"""

    def get(self, *args, **kwargs):
        raise Http404
