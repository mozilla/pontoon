from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from pontoon.base.utils import require_AJAX
from pontoon.uxactionlog import forms, utils


@login_required(redirect_field_name="", login_url="/403")
@require_POST
@require_AJAX
@transaction.atomic
def log_ux_action(request):
    """Save a new UX action in the database."""
    form = forms.UXActionLogForm(request.POST)

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
