import json
import uuid

from guardian.decorators import permission_required_or_403
from notifications.signals import notify

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from pontoon.base.models import UserProfile
from pontoon.base.utils import require_AJAX
from pontoon.messaging import forms, utils


def messaging(request):
    if not request.user.has_perm("base.can_manage_project"):
        raise PermissionDenied

    return render(
        request,
        "messaging/messaging.html",
    )


@permission_required_or_403("base.can_manage_project")
@require_AJAX
@require_POST
@transaction.atomic
def send_message(request):
    # Send notifications
    if request.method == "POST":
        form = forms.MessageForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        # TODO: implement recipient filters
        from django.contrib.auth.models import User

        recipients = User.objects.filter(pk=request.user.pk)

        is_notification = form.cleaned_data.get("notification")
        is_email = form.cleaned_data.get("email")
        subject = form.cleaned_data.get("subject")
        body = form.cleaned_data.get("body")

        if is_notification:
            identifier = uuid.uuid4().hex
            for recipient in recipients.distinct():
                notify.send(
                    request.user,
                    recipient=recipient,
                    verb="has sent you a message",
                    target=None,
                    description=f"{subject}<br/><br/>{body}",
                    identifier=identifier,
                )

        if is_email:
            footer = """<br><br>
You’re receiving this email as a contributor to Mozilla localization on Pontoon. <br>To no longer receive emails like these, unsubscribe here: <a href="https://pontoon.mozilla.org/unsubscribe/{ uuid }">Unsubscribe</a>.
            """
            html_template = body + footer
            text_template = utils.html_to_plain_text_with_links(html_template)

            for recipient in recipients.distinct():
                unique_id = str(recipient.profile.unique_id)
                text = text_template.replace("{ uuid }", unique_id)
                html = html_template.replace("{ uuid }", unique_id)

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text,
                    from_email="Mozilla L10n Team <team@pontoon.mozilla.com>",
                    to=[recipient.contact_email],
                )
                msg.attach_alternative(html, "text/html")
                msg.send()

    return JsonResponse(
        {
            "status": True,
        }
    )


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


def unsubscribe(request, uuid):
    profile = get_object_or_404(UserProfile, unique_id=uuid)
    profile.email_communications_enabled = False
    profile.save(update_fields=["email_communications_enabled"])

    return render(
        request,
        "messaging/unsubscribe.html",
        {
            "uuid": uuid,
        },
    )


def subscribe(request, uuid):
    profile = get_object_or_404(UserProfile, unique_id=uuid)
    profile.email_communications_enabled = True
    profile.save(update_fields=["email_communications_enabled"])

    return render(
        request,
        "messaging/subscribe.html",
        {
            "uuid": uuid,
        },
    )
