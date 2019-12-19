from __future__ import absolute_import

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from pontoon.actionlog.utils import log_action
from pontoon.base import utils
from pontoon.base.models import (
    TranslatedResource,
    Translation,
)
from pontoon.checks.libraries import run_checks
from pontoon.checks.utils import are_blocking_checks
from pontoon.translations import forms


@require_POST
@utils.require_AJAX
@login_required(redirect_field_name="", login_url="/403")
@transaction.atomic
def create_translation(request):
    form = forms.CreateTranslationForm(request.POST)

    if not form.is_valid():
        problems = []
        for field, errors in form.errors.items():
            problems.append(
                'Error validating field `{0}`: "{1}"'.format(field, " ".join(errors))
            )
        return JsonResponse(
            {"status": False, "message": "\n".join(problems)}, status=400
        )

    entity = form.cleaned_data["entity"]
    string = form.cleaned_data["translation"]
    locale = form.cleaned_data["locale"]
    plural_form = form.cleaned_data["plural_form"]
    original = form.cleaned_data["original"]
    ignore_warnings = form.cleaned_data["ignore_warnings"]
    approve = form.cleaned_data["approve"]
    force_suggestions = form.cleaned_data["force_suggestions"]
    resources = form.cleaned_data["paths"]

    project = entity.resource.project

    # Read-only translations cannot saved
    if utils.readonly_exists(project, locale):
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: This string is in read-only mode.",
            },
            status=403,
        )

    now = timezone.now()
    user = request.user
    can_translate = user.can_translate(project=project, locale=locale) and (
        not force_suggestions or approve
    )
    translations = Translation.objects.filter(
        entity=entity, locale=locale, plural_form=plural_form
    )

    same_translations = translations.filter(string=string)

    # If same translation exists in the DB, don't save it again.
    if same_translations:
        return JsonResponse({"status": False, "same": True})

    # Check for errors.
    # Checks are disabled for the tutorial.
    use_checks = project.slug != "tutorial"

    failed_checks = None
    if use_checks:
        failed_checks = run_checks(
            entity, locale.code, original, string, user.profile.quality_checks,
        )

        if are_blocking_checks(failed_checks, ignore_warnings):
            return JsonResponse({"status": False, "failedChecks": failed_checks})

    translation = Translation(
        entity=entity,
        locale=locale,
        plural_form=plural_form,
        string=string,
        user=user,
        date=now,
        approved=can_translate,
    )

    if can_translate:
        translation.approved_user = user
        translation.approved_date = now

    translation.save(failed_checks=failed_checks)

    log_action("translation:created", user, translation=translation)

    if translations:
        translation = entity.reset_active_translation(
            locale=locale, plural_form=plural_form,
        )

    return JsonResponse(
        {
            "status": True,
            "translation": translation.serialize(),
            "stats": TranslatedResource.objects.stats(project, resources, locale),
        }
    )
