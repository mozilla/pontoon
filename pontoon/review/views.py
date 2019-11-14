from __future__ import absolute_import

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError

from pontoon.base import utils
from pontoon.base.models import (
    TranslatedResource,
    Translation,
)
from pontoon.checks.libraries import run_checks
from pontoon.checks.utils import are_blocking_checks


@utils.require_AJAX
@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def approve_translation(request):
    """Approve given translation."""
    try:
        t = request.POST['translation']
        ignore_warnings = request.POST.get('ignore_warnings', 'false') == 'true'
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    translation = get_object_or_404(Translation, pk=t)
    entity = translation.entity
    project = entity.resource.project
    locale = translation.locale
    user = request.user

    # Read-only translations cannot be approved
    if utils.readonly_exists(project, locale):
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This string is in read-only mode.',
        }, status=403)

    if translation.approved:
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This translation is already approved.',
        }, status=403)

    # Only privileged users can approve translations
    if not user.can_translate(locale, project):
        return JsonResponse({
            'status': False,
            'message': "Forbidden: You don't have permission to approve this translation.",
        }, status=403)

    # Check for errors.
    # Checks are disabled for the tutorial.
    use_checks = project.slug != 'tutorial'

    if use_checks:
        failed_checks = run_checks(
            entity,
            locale.code,
            entity.string,
            translation.string,
            user.profile.quality_checks,
        )

        if are_blocking_checks(failed_checks, ignore_warnings):
            return JsonResponse({
                'string': translation.string,
                'failedChecks': failed_checks,
            })

    translation.approve(user)

    active_translation = translation.entity.reset_active_translation(
        locale=locale,
        plural_form=translation.plural_form,
    )

    return JsonResponse({
        'translation': active_translation.serialize(),
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    })


@utils.require_AJAX
@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def unapprove_translation(request):
    """Unapprove given translation."""
    try:
        t = request.POST['translation']
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    translation = get_object_or_404(Translation, pk=t)
    project = translation.entity.resource.project
    locale = translation.locale

    # Read-only translations cannot be un-approved
    if utils.readonly_exists(project, locale):
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This string is in read-only mode.',
        }, status=403)

    # Only privileged users or authors can un-approve translations
    if not (
        request.user.can_translate(locale, project) or
        request.user == translation.user or
        translation.approved
    ):
        return JsonResponse({
            'status': False,
            'message': "Forbidden: You can't unapprove this translation.",
        }, status=403)

    translation.unapprove(request.user)

    active_translation = translation.entity.reset_active_translation(
        locale=locale,
        plural_form=translation.plural_form,
    )

    return JsonResponse({
        'translation': active_translation.serialize(),
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    })


@utils.require_AJAX
@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def reject_translation(request):
    """Reject given translation."""
    try:
        t = request.POST['translation']
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    translation = get_object_or_404(Translation, pk=t)
    project = translation.entity.resource.project
    locale = translation.locale

    # Read-only translations cannot be rejected
    if utils.readonly_exists(project, locale):
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This string is in read-only mode.',
        }, status=403)

    # Non-privileged users can only reject own unapproved translations
    if not request.user.can_translate(locale, project):
        if translation.user == request.user:
            if translation.approved is True:
                return JsonResponse({
                    'status': False,
                    'message': "Forbidden: You can't reject approved translations.",
                }, status=403)
        else:
            return JsonResponse({
                'status': False,
                'message': "Forbidden: You can't reject translations from other users.",
            }, status=403)

    translation.reject(request.user)

    active_translation = translation.entity.reset_active_translation(
        locale=locale,
        plural_form=translation.plural_form,
    )

    return JsonResponse({
        'translation': active_translation.serialize(),
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    })


@utils.require_AJAX
@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def unreject_translation(request):
    """Unreject given translation."""
    try:
        t = request.POST['translation']
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    translation = get_object_or_404(Translation, pk=t)
    project = translation.entity.resource.project
    locale = translation.locale

    # Read-only translations cannot be un-rejected
    if utils.readonly_exists(project, locale):
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This string is in read-only mode.',
        }, status=403)

    # Only privileged users or authors can un-reject translations
    if not (
        request.user.can_translate(locale, project) or
        request.user == translation.user or
        translation.approved
    ):
        return JsonResponse({
            'status': False,
            'message': "Forbidden: You can't unreject this translation.",
        }, status=403)

    translation.unreject(request.user)

    active_translation = translation.entity.reset_active_translation(
        locale=locale,
        plural_form=translation.plural_form,
    )

    return JsonResponse({
        'translation': active_translation.serialize(),
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    })
