from collections.abc import Iterable, Mapping
from typing import cast

from moz.l10n.message import message_to_json
from moz.l10n.model import Message

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.http import require_POST

from pontoon.actionlog.models import ActionLog
from pontoon.actionlog.utils import log_action
from pontoon.base import utils
from pontoon.base.badge_utils import badges_review_count, badges_translation_count
from pontoon.base.models import (
    Entity,
    Locale,
    Resource,
    TranslatedResource,
    Translation,
)
from pontoon.base.services import readonly_exists
from pontoon.base.user_utils import can_translate
from pontoon.checks.libraries import run_checks
from pontoon.checks.utils import are_blocking_checks
from pontoon.messaging.notifications import send_badge_notification, send_notification

from .forms import CreateTranslationForm


def _add_stats(response_data, resource: Resource, locale: Locale, stats):
    if stats:
        paths = [resource.path] if stats == "resource" else []
        response_data["stats"] = TranslatedResource.objects.query_stats(
            resource.project, paths, locale
        )


def _add_badge_data(response_data, user, badge_name, badge_level):
    response_data["badge_update"] = {
        "name": badge_name,
        "level": badge_level,
    }
    send_badge_notification(
        user,
        badge_name,
        badge_level,
    )


def _contains_null_char(x) -> bool:
    if isinstance(x, str):
        return "\x00" in x
    if isinstance(x, Mapping):
        return any(_contains_null_char(y) for y in x.items())
    if isinstance(x, Iterable):
        return any(_contains_null_char(y) for y in x)
    return False


@require_POST
@utils.require_AJAX
@login_required(redirect_field_name="", login_url="/403")
@transaction.atomic
def create_translation(request):
    """
    Create a new translation.
    """
    form = CreateTranslationForm(request.POST)
    if not form.is_valid():
        problems = [
            f'Error validating field `{field}`: "{error}"'
            for field, errors in form.errors.items()
            for error in errors
        ]
        return JsonResponse(
            {"status": False, "message": "\n".join(problems)}, status=400
        )
    req_data = form.cleaned_data

    entity = cast(Entity, req_data["entity"])
    locale = cast(Locale, req_data["locale"])
    value = cast(Message, req_data["value"])
    properties = cast(dict[str, Message], req_data["properties"])
    string = cast(str, req_data["string"])

    resource = entity.resource
    project = resource.project

    if entity.obsolete:
        return JsonResponse(
            {"status": False, "message": "Forbidden: This string is obsolete."},
            status=403,
        )

    # Read-only translations cannot saved
    if readonly_exists(project, locale):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: This string is in read-only mode.",
            },
            status=403,
        )

    json_value = message_to_json(value)
    json_properties = {k: message_to_json(v) for k, v in properties.items()} or None

    if _contains_null_char((string, json_value, json_properties)):
        # PostgreSQL does not support null characters in text or jsonb
        return JsonResponse(
            {"status": False, "message": "Unsupported null character"}, status=400
        )

    # If same translation exists in the DB, don't save it again.
    if (
        Translation.objects.filter(entity=entity, locale=locale)
        .filter(Q(value=json_value, properties=json_properties) | Q(string=string))
        .exists()
    ):
        return JsonResponse({"status": False, "same": True})

    # Look for failed checks.
    # Checks are disabled for the tutorial.
    use_checks = project.slug != "tutorial"
    user = request.user

    failed_checks = None
    if use_checks:
        failed_checks = run_checks(
            entity,
            locale.code,
            string,
            user.profile.quality_checks,
        )
        if are_blocking_checks(failed_checks, req_data["ignore_warnings"]):
            return JsonResponse({"status": False, "failedChecks": failed_checks})

    now = timezone.now()
    approved = can_translate(user, project, locale) and (
        not req_data["force_suggestions"] or req_data["approve"]
    )

    translation = Translation(
        entity=entity,
        locale=locale,
        string=string,
        value=json_value,
        properties=json_properties,
        user=user,
        date=now,
        approved=approved,
        machinery_sources=req_data["machinery_sources"],
    )

    if approved:
        translation.approved_user = user
        translation.approved_date = now

    translation.save(failed_checks=failed_checks)

    log_action(ActionLog.ActionType.TRANSLATION_CREATED, user, translation=translation)

    active_translation = entity.reset_active_translation(locale=locale)

    # When user makes their first contribution to the team, notify team managers
    first_contribution = (
        not project.system_project
        and user != project.contact
        and (
            Translation.objects.filter(user=user, locale=locale)
            .exclude(entity__resource__project__system_project=True)
            .count()
            == 1
        )
    )
    if first_contribution:
        description = render_to_string(
            "messaging/notifications/new_contributor.html",
            {
                "entity": entity,
                "locale": locale,
                "project": project,
                "user": user,
            },
        )

        for manager in locale.managers_group.user_set.filter(
            profile__new_contributor_notifications=True,
        ):
            send_notification(
                sender=manager,
                recipient=manager,
                verb="has reviewed suggestions",  # Triggers render of description only
                description=description,
                category="new_contributor",
            )

    response_data = {"status": True, "translation": active_translation}
    _add_stats(response_data, resource, locale, req_data["stats"])

    # Send Translation Champion Badge notification information
    translation_count = badges_translation_count(user)
    if translation_count in settings.BADGES_TRANSLATION_THRESHOLDS:
        badge_name = "Translation Champion"
        badge_level = (
            settings.BADGES_TRANSLATION_THRESHOLDS.index(translation_count) + 1
        )
        _add_badge_data(response_data, user, badge_name, badge_level)

    return JsonResponse(response_data)


@utils.require_AJAX
@login_required(redirect_field_name="", login_url="/403")
@transaction.atomic
def delete_translation(request):
    """Delete given translation."""
    try:
        translation_id = request.POST["translation"]
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    translation = get_object_or_404(Translation, pk=translation_id)
    entity = translation.entity
    project = entity.resource.project
    locale = translation.locale

    # Read-only translations cannot be deleted
    if readonly_exists(project, locale):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: This string is in read-only mode.",
            },
            status=403,
        )

    # Only privileged users or authors can delete translations
    if not translation.rejected or not (
        can_translate(request.user, project, locale) or request.user == translation.user
    ):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: You can't delete this translation.",
            },
            status=403,
        )

    translation.delete()

    log_action(
        ActionLog.ActionType.TRANSLATION_DELETED,
        request.user,
        entity=entity,
        locale=locale,
    )

    return JsonResponse({"status": True})


@utils.require_AJAX
@login_required(redirect_field_name="", login_url="/403")
@transaction.atomic
def approve_translation(request):
    """Approve given translation."""
    try:
        t = request.POST["translation"]
        ignore_warnings = request.POST.get("ignore_warnings", "false") == "true"
        stats = request.POST.get("stats", "")
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    translation = get_object_or_404(Translation, pk=t)
    entity = translation.entity
    resource = entity.resource
    project = resource.project
    locale = translation.locale
    user = request.user

    # Read-only translations cannot be approved
    if readonly_exists(project, locale):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: This string is in read-only mode.",
            },
            status=403,
        )

    if translation.approved:
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: This translation is already approved.",
            },
            status=403,
        )

    # Only privileged users can approve translations
    if not can_translate(user, project, locale):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: You don't have permission to approve this translation.",
            },
            status=403,
        )

    # Check for errors.
    # Checks are disabled for the tutorial.
    use_checks = project.slug != "tutorial"

    if use_checks:
        failed_checks = run_checks(
            entity,
            locale.code,
            translation.string,
            user.profile.quality_checks,
        )

        if are_blocking_checks(failed_checks, ignore_warnings):
            return JsonResponse(
                {"string": translation.string, "failedChecks": failed_checks}
            )

    translation.approve(user)

    log_action(ActionLog.ActionType.TRANSLATION_APPROVED, user, translation=translation)

    active_translation = entity.reset_active_translation(locale=locale)
    response_data = {"status": True, "translation": active_translation}
    _add_stats(response_data, resource, locale, stats)

    # Send Review Master Badge notification information
    review_count = badges_review_count(user)
    if review_count in settings.BADGES_REVIEW_THRESHOLDS:
        badge_name = "Review Master"
        badge_level = settings.BADGES_REVIEW_THRESHOLDS.index(review_count) + 1
        _add_badge_data(response_data, user, badge_name, badge_level)

    return JsonResponse(response_data)


@utils.require_AJAX
@login_required(redirect_field_name="", login_url="/403")
@transaction.atomic
def unapprove_translation(request):
    """Unapprove given translation."""
    try:
        t = request.POST["translation"]
        stats = request.POST.get("stats", "")
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    translation = get_object_or_404(Translation, pk=t)
    entity = translation.entity
    resource = entity.resource
    project = resource.project
    locale = translation.locale

    # Read-only translations cannot be un-approved
    if readonly_exists(project, locale):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: This string is in read-only mode.",
            },
            status=403,
        )

    # Only privileged users or authors can un-approve translations
    if not translation.approved or not (
        can_translate(request.user, project, locale) or request.user == translation.user
    ):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: You can't unapprove this translation.",
            },
            status=403,
        )

    translation.unapprove(request.user)

    log_action(
        ActionLog.ActionType.TRANSLATION_UNAPPROVED,
        request.user,
        translation=translation,
    )

    active_translation = entity.reset_active_translation(locale=locale)
    response_data = {"status": True, "translation": active_translation}
    _add_stats(response_data, resource, locale, stats)
    return JsonResponse(response_data)


@utils.require_AJAX
@login_required(redirect_field_name="", login_url="/403")
@transaction.atomic
def reject_translation(request):
    """Reject given translation."""
    try:
        t = request.POST["translation"]
        stats = request.POST.get("stats", "")
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    translation = get_object_or_404(Translation, pk=t)
    entity = translation.entity
    resource = entity.resource
    project = resource.project
    locale = translation.locale

    # Read-only translations cannot be rejected
    if readonly_exists(project, locale):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: This string is in read-only mode.",
            },
            status=403,
        )

    # Non-privileged users can only reject own unapproved translations
    if not can_translate(request.user, project, locale):
        if translation.user == request.user:
            if translation.approved is True:
                return JsonResponse(
                    {
                        "status": False,
                        "message": "Forbidden: You can't reject approved translations.",
                    },
                    status=403,
                )
        else:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Forbidden: You can't reject translations from other users.",
                },
                status=403,
            )

    translation.reject(request.user)

    log_action(
        ActionLog.ActionType.TRANSLATION_REJECTED, request.user, translation=translation
    )

    active_translation = entity.reset_active_translation(locale=locale)
    response_data = {"status": True, "translation": active_translation}
    _add_stats(response_data, resource, locale, stats)

    # Send Review Master Badge notification information
    review_count = badges_review_count(request.user)
    if review_count in settings.BADGES_REVIEW_THRESHOLDS:
        badge_name = "Review Master"
        badge_level = settings.BADGES_REVIEW_THRESHOLDS.index(review_count) + 1
        _add_badge_data(response_data, request.user, badge_name, badge_level)

    return JsonResponse(response_data)


@utils.require_AJAX
@login_required(redirect_field_name="", login_url="/403")
@transaction.atomic
def unreject_translation(request):
    """Unreject given translation."""
    try:
        t = request.POST["translation"]
        stats = request.POST.get("stats", "")
    except MultiValueDictKeyError as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    translation = get_object_or_404(Translation, pk=t)
    entity = translation.entity
    resource = entity.resource
    project = resource.project
    locale = translation.locale

    # Read-only translations cannot be un-rejected
    if readonly_exists(project, locale):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: This string is in read-only mode.",
            },
            status=403,
        )

    # Only privileged users or authors can un-reject translations
    if not translation.rejected or not (
        can_translate(request.user, project, locale) or request.user == translation.user
    ):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: You can't unreject this translation.",
            },
            status=403,
        )

    translation.unreject(request.user)

    log_action(
        ActionLog.ActionType.TRANSLATION_UNREJECTED,
        request.user,
        translation=translation,
    )

    active_translation = translation.entity.reset_active_translation(locale=locale)
    response = {"status": True, "translation": active_translation}
    _add_stats(response, resource, locale, stats)
    return JsonResponse(response)
