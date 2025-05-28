from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from pontoon.base.utils import require_AJAX
from pontoon.uxactionlog import forms, utils


@require_POST
@require_AJAX
@transaction.atomic
def log_ux_action(request):
    """Save a new UX action in the database."""
    form = forms.UXActionLogForm(request.POST)
    user = request.user

    if not user.is_authenticated:
        print("hello")
        return JsonResponse({"is_authenticated": False}, status=403)

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

    utils.log_ux_action(
        action_type=form.cleaned_data["action_type"],
        experiment=form.cleaned_data["experiment"],
        data=form.cleaned_data["data"],
    )

    return JsonResponse({"status": True})
