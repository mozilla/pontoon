"""
Write-side business logic for the translation submission + review API.

These functions mirror, step for step, the web editor's flow in
``pontoon.translations.views`` (``create_translation`` and the review views),
but return plain result dicts instead of ``HttpResponse`` objects and omit the
UI-only badge / new-contributor notifications (which would spam on bulk
imports). They reuse the model-level machinery (``Translation.save``,
``Translation.approve`` / ``reject`` / ``unapprove``) rather than
reimplementing stats, active-translation swaps, or translation-memory upkeep.
"""

from moz.l10n.message import message_from_json, message_to_json

from django.db.models import Q
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.actionlog.utils import log_action
from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    Resource,
    Translation,
)
from pontoon.base.services import readonly_exists
from pontoon.base.user_utils import can_translate
from pontoon.checks.libraries import run_checks
from pontoon.checks.utils import are_blocking_checks
from pontoon.translations.utils import serialize_for_db


# Past-tense status returned for each successful review action.
_REVIEW_STATUS = {
    "approve": "approved",
    "reject": "rejected",
    "unapprove": "unapproved",
    "delete": "deleted",
}


class ItemError(Exception):
    """A per-item, client-facing processing error.

    Raised for anything that should surface as a failed item in the batch
    response (bad coordinates, permission denied, read-only, unserializable
    content, ...) without aborting the rest of the batch.
    """

    def __init__(self, message, extra=None):
        super().__init__(message)
        self.message = message
        self.extra = extra or {}


def _resolve(project_slug, resource_path, key, locale_code):
    """Resolve ``(project, resource, entity, locale)`` from stable coordinates.

    Raises :class:`ItemError` with a client-facing message on any failure.
    The ``ProjectLocale`` existence check must run before any use of
    ``can_translate``, which does ``ProjectLocale.objects.get`` and would
    otherwise raise ``DoesNotExist``.
    """
    try:
        project = Project.objects.get(slug=project_slug)
    except Project.DoesNotExist:
        raise ItemError(f"Project not found: {project_slug}")

    try:
        locale = Locale.objects.get(code=locale_code)
    except Locale.DoesNotExist:
        raise ItemError(f"Locale not found: {locale_code}")

    if not ProjectLocale.objects.filter(project=project, locale=locale).exists():
        raise ItemError(
            f"Locale {locale_code} is not enabled for project {project_slug}"
        )

    resources = list(project.resources.filter(path=resource_path))
    if not resources:
        raise ItemError(f"Resource not found: {resource_path}")
    if len(resources) > 1:
        raise ItemError(f"Ambiguous resource path: {resource_path}")
    resource = resources[0]

    entities = list(resource.entities.filter(key=key, obsolete=False))
    if not entities:
        raise ItemError(f"Entity not found for key {key} in {resource_path}")
    if len(entities) > 1:
        raise ItemError(f"Ambiguous entity key {key} in {resource_path}")
    entity = entities[0]

    return project, resource, entity, locale


def _prepare_content(entity, value, properties):
    """Validate the moz.l10n ``value`` / ``properties`` JSON and serialize it.

    Mirrors ``CreateTranslationForm``: returns
    ``(string, json_value, json_properties)`` where ``string`` is the DB
    representation and the JSON values are what gets stored on the row.
    """
    fmt = entity.resource.format

    if properties and fmt != Resource.Format.FLUENT:
        raise ItemError(f"Properties are not supported for {fmt}")

    try:
        msg_value = message_from_json(value).normalize()
    except Exception as err:
        raise ItemError(f"Invalid `value`: {err}")

    try:
        msg_properties = {
            k: message_from_json(v).normalize()
            for k, v in (properties or {}).items()
        }
    except Exception as err:
        raise ItemError(f"Invalid `properties`: {err}")

    try:
        string = serialize_for_db(entity, msg_value, msg_properties)
    except Exception:
        value_is = "Value is" if not msg_properties else "Value and properties are"
        raise ItemError(f"{value_is} not serializable as {fmt}")

    json_value = message_to_json(msg_value)
    json_properties = (
        {k: message_to_json(v) for k, v in msg_properties.items()} or None
    )
    return string, json_value, json_properties


def _coords(project_slug, resource_path, key, locale_code):
    return {
        "project": project_slug,
        "resource": resource_path,
        "key": key,
        "locale": locale_code,
    }


def submit_translation(
    *,
    user,
    project_slug,
    resource_path,
    key,
    locale_code,
    value,
    properties=None,
    ignore_warnings=False,
    approve=False,
    force_suggestions=False,
    machinery_sources=None,
):
    """Create a translation (approved or suggestion) for one entity+locale.

    Returns a result dict with ``status`` one of ``created`` / ``same`` /
    ``error``. Never raises :class:`ItemError` (caught internally); other
    exceptions propagate so the caller's ``transaction.atomic`` can roll back.
    """
    result = _coords(project_slug, resource_path, key, locale_code)
    try:
        project, resource, entity, locale = _resolve(
            project_slug, resource_path, key, locale_code
        )

        if readonly_exists(project, locale):
            raise ItemError("This string is in read-only mode.")

        string, json_value, json_properties = _prepare_content(
            entity, value, properties
        )

        # If the same translation already exists, don't create a duplicate.
        if (
            Translation.objects.filter(entity=entity, locale=locale)
            .filter(Q(value=json_value, properties=json_properties) | Q(string=string))
            .exists()
        ):
            return {**result, "status": "same"}

        # Quality checks (disabled for the tutorial, mirroring the editor).
        failed_checks = None
        if project.slug != "tutorial":
            failed_checks = run_checks(
                entity, locale.code, string, user.profile.quality_checks
            )
            if are_blocking_checks(failed_checks, ignore_warnings):
                return {
                    **result,
                    "status": "error",
                    "failed_checks": failed_checks,
                    "errors": ["Translation failed quality checks."],
                }

        now = timezone.now()
        approved = can_translate(user, project, locale) and (
            not force_suggestions or approve
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
            machinery_sources=machinery_sources or [],
        )
        if approved:
            translation.approved_user = user
            translation.approved_date = now

        translation.save(failed_checks=failed_checks)
        log_action(
            ActionLog.ActionType.TRANSLATION_CREATED, user, translation=translation
        )
        entity.reset_active_translation(locale=locale)

        return {**result, "status": "created", "translation": translation.serialize()}
    except ItemError as err:
        return {**result, "status": "error", "errors": [err.message], **err.extra}


def _locate_for_review(
    translation_id, project_slug, resource_path, key, locale_code, value
):
    """Find the translation targeted by a review request.

    Either ``translation_id`` (precise) or coordinates + ``value`` (which
    disambiguates among suggestions) must be provided.
    """
    if translation_id is not None:
        try:
            translation = Translation.objects.get(pk=translation_id)
        except Translation.DoesNotExist:
            raise ItemError(f"Translation not found: {translation_id}")
        entity = translation.entity
        return translation.entity.resource.project, entity, translation.locale, translation

    if not all([project_slug, resource_path, key, locale_code]):
        raise ItemError(
            "Provide `translation_id`, or project + resource + key + locale."
        )

    project, resource, entity, locale = _resolve(
        project_slug, resource_path, key, locale_code
    )
    if value is None:
        raise ItemError("Provide `value` to identify the translation.")

    string, json_value, _ = _prepare_content(entity, value, None)
    match = (
        Translation.objects.filter(entity=entity, locale=locale)
        .filter(Q(value=json_value) | Q(string=string))
        .order_by("-active", "-date")
        .first()
    )
    if match is None:
        raise ItemError("No matching translation found.")
    return project, entity, locale, match


def review_translation(
    *,
    user,
    action,
    translation_id=None,
    project_slug=None,
    resource_path=None,
    key=None,
    locale_code=None,
    value=None,
    ignore_warnings=False,
):
    """Approve / reject / unapprove / delete one translation.

    Mirrors the per-action permission and state guards of the editor's review
    views. Returns a result dict with ``status`` = the past-tense action or
    ``error``.
    """
    result = {"action": action}
    try:
        project, entity, locale, translation = _locate_for_review(
            translation_id, project_slug, resource_path, key, locale_code, value
        )
        result["translation_id"] = translation.pk

        if readonly_exists(project, locale):
            raise ItemError("This string is in read-only mode.")

        privileged = can_translate(user, project, locale)
        is_author = translation.user_id == user.id

        if action == "approve":
            if translation.approved:
                raise ItemError("This translation is already approved.")
            if not privileged:
                raise ItemError(
                    "You don't have permission to approve this translation."
                )
            if project.slug != "tutorial":
                failed_checks = run_checks(
                    entity, locale.code, translation.string, user.profile.quality_checks
                )
                if are_blocking_checks(failed_checks, ignore_warnings):
                    return {
                        **result,
                        "status": "error",
                        "failed_checks": failed_checks,
                        "errors": ["Translation failed quality checks."],
                    }
            translation.approve(user)
            log_action(
                ActionLog.ActionType.TRANSLATION_APPROVED, user, translation=translation
            )

        elif action == "reject":
            if not privileged:
                if is_author:
                    if translation.approved:
                        raise ItemError("You can't reject approved translations.")
                else:
                    raise ItemError(
                        "You can't reject translations from other users."
                    )
            translation.reject(user)
            log_action(
                ActionLog.ActionType.TRANSLATION_REJECTED, user, translation=translation
            )

        elif action == "unapprove":
            if not translation.approved or not (privileged or is_author):
                raise ItemError("You can't unapprove this translation.")
            translation.unapprove(user)
            log_action(
                ActionLog.ActionType.TRANSLATION_UNAPPROVED,
                user,
                translation=translation,
            )

        elif action == "delete":
            if not translation.rejected or not (privileged or is_author):
                raise ItemError("You can't delete this translation.")
            translation.delete()
            log_action(
                ActionLog.ActionType.TRANSLATION_DELETED,
                user,
                entity=entity,
                locale=locale,
            )
            return {**result, "status": "deleted"}

        else:
            raise ItemError(f"Unknown review action: {action}")

        entity.reset_active_translation(locale=locale)
        return {
            **result,
            "status": _REVIEW_STATUS[action],
            "translation": translation.serialize(),
        }
    except ItemError as err:
        return {**result, "status": "error", "errors": [err.message], **err.extra}
