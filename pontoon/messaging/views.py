import json
import logging
import uuid

from guardian.decorators import permission_required_or_403
from notifications.signals import notify

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from pontoon.base.models import Locale, Project, Translation, UserProfile
from pontoon.base.utils import require_AJAX, split_ints
from pontoon.messaging import forms, utils


log = logging.getLogger(__name__)


def messaging(request):
    if not request.user.has_perm("base.can_manage_project"):
        raise PermissionDenied

    return render(
        request,
        "messaging/messaging.html",
        {
            "available_locales": Locale.objects.available(),
            "available_projects": Project.objects.available().order_by("name"),
            "today": timezone.now().date(),
            "year_ago": timezone.now().date() - timezone.timedelta(days=365),
        },
    )


@permission_required_or_403("base.can_manage_project")
@require_AJAX
@require_POST
@transaction.atomic
def send_message(request):
    form = forms.MessageForm(request.POST)

    if not form.is_valid():
        return JsonResponse(dict(form.errors.items()))

    recipients = User.objects.none()

    locale_ids = sorted(split_ints(form.cleaned_data.get("locales")))
    project_ids = sorted(split_ints(form.cleaned_data.get("projects")))

    if form.cleaned_data.get("contributors"):
        contributors = (
            Translation.objects.filter(
                locale_id__in=locale_ids,
                entity__resource__project_id__in=project_ids,
            )
            .values("user")
            .distinct()
        )
        recipients = recipients | User.objects.filter(pk__in=contributors)

    if form.cleaned_data.get("managers"):
        managers = Locale.objects.filter(pk__in=locale_ids).values(
            "managers_group__user"
        )
        recipients = recipients | User.objects.filter(pk__in=managers)

    if form.cleaned_data.get("translators"):
        translators = Locale.objects.filter(pk__in=locale_ids).values(
            "translators_group__user"
        )
        recipients = recipients | User.objects.filter(pk__in=translators)

    log.info(
        f"{recipients.count()} Recipients: {list(recipients.values_list('email', flat=True))}"
    )

    # While the feature is in development, notifications and emails are sent only to the current user.
    # TODO: Remove this line when the feature is ready
    recipients = User.objects.filter(pk=request.user.pk)

    is_notification = form.cleaned_data.get("notification")
    is_email = form.cleaned_data.get("email")
    is_transactional = form.cleaned_data.get("transactional")
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

        log.info(
            f"Notifications sent to the following {recipients.count()} users: {recipients.values_list('email', flat=True)}."
        )

    if is_email:
        footer = (
            """<br><br>
You’re receiving this email as a contributor to Mozilla localization on Pontoon. <br>To no longer receive emails like these, unsubscribe here: <a href="https://pontoon.mozilla.org/unsubscribe/{ uuid }">Unsubscribe</a>.
        """
            if not is_transactional
            else ""
        )
        html_template = body + footer
        text_template = utils.html_to_plain_text_with_links(html_template)

        email_recipients = recipients.filter(
            profile__email_communications_enabled=True
        )

        for recipient in email_recipients.distinct():
            unique_id = str(recipient.profile.unique_id)
            text = text_template.replace("{ uuid }", unique_id)
            html = html_template.replace("{ uuid }", unique_id)

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient.contact_email],
            )
            msg.attach_alternative(html, "text/html")
            msg.send()

        log.info(
            f"Email sent to the following {email_recipients.count()} users: {email_recipients.values_list('email', flat=True)}."
        )

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
