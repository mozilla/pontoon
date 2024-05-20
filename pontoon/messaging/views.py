import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST


@login_required(redirect_field_name="", login_url="/403")
def email_consent(request):
    return render(
        request,
        "messaging/email_consent.html",
    )


@login_required(redirect_field_name="", login_url="/403")
@require_POST
@transaction.atomic
def dismiss_email_consent(request):
    value = request.POST.get("value", None)

    if not value:
        return JsonResponse(
            {
                "status": False,
                "message": "Bad Request: Value not set",
            },
            status=400,
        )

    profile = request.user.profile
    profile.email_communications_enabled = json.loads(value)
    profile.email_consent_dismissed_at = timezone.now()
    profile.save()

    return JsonResponse(
        {
            "status": True,
            "next": request.session.get("next_path", "/"),
        }
    )
