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
from django.db.models import Count, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from pontoon.base.models import Locale, Project, Translation, UserProfile
from pontoon.base.utils import require_AJAX, split_ints
from pontoon.messaging import forms, utils
from pontoon.messaging.models import Message


log = logging.getLogger(__name__)


def messaging(request, pk=None):
    if not request.user.has_perm("base.can_manage_project"):
        raise PermissionDenied

    return render(
        request,
        "messaging/messaging.html",
        {
            "count": Message.objects.count(),
        },
    )


@require_AJAX
def ajax_compose(request):
    if not request.user.has_perm("base.can_manage_project"):
        raise PermissionDenied

    return render(
        request,
        "messaging/includes/compose.html",
        {
            "form": forms.MessageForm(),
            "available_locales": [],
            "selected_locales": Locale.objects.available(),
            "available_projects": [],
            "selected_projects": Project.objects.available().order_by("name"),
        },
    )


@require_AJAX
def ajax_use_as_template(request, pk):
    if not request.user.has_perm("base.can_manage_project"):
        raise PermissionDenied

    message = get_object_or_404(Message, pk=pk)

    return render(
        request,
        "messaging/includes/compose.html",
        {
            "form": forms.MessageForm(instance=message),
            "available_locales": Locale.objects.available().exclude(
                pk__in=message.locales.all()
            ),
            "selected_locales": message.locales.all(),
            "available_projects": Project.objects.available().exclude(
                pk__in=message.projects.all()
            ),
            "selected_projects": message.projects.all().order_by("name"),
        },
    )


@require_AJAX
def ajax_sent(request):
    if not request.user.has_perm("base.can_manage_project"):
        raise PermissionDenied

    return render(
        request,
        "messaging/includes/sent.html",
        {
            "sent_messages": Message.objects.order_by("-sent_at"),
        },
    )


def get_recipients(form):
    recipients = User.objects.none()

    """
    Filter recipients by user role, locale and project:
    - Contributors of selected Locales and Projects
    - Managers of selected Locales
    - Translators of selected Locales
    """
    locale_ids = sorted(split_ints(form.cleaned_data.get("locales")))
    project_ids = form.cleaned_data.get("projects")

    translations = Translation.objects.filter(
        locale_id__in=locale_ids,
        entity__resource__project_id__in=project_ids,
    )

    locales = Locale.objects.filter(pk__in=locale_ids)
    manager_ids = (
        locales.exclude(managers_group__user__isnull=True)
        .values("managers_group__user")
        .distinct()
    )
    translator_ids = (
        locales.exclude(translators_group__user__isnull=True)
        .values("translators_group__user")
        .distinct()
    )

    if form.cleaned_data.get("contributors"):
        contributors = translations.values("user").distinct()
        recipients = recipients | User.objects.filter(pk__in=contributors)

    if form.cleaned_data.get("managers"):
        recipients = recipients | User.objects.filter(pk__in=manager_ids)

    if form.cleaned_data.get("translators"):
        recipients = recipients | User.objects.filter(pk__in=translator_ids)

    """
    Filter recipients by login date:
    - Logged in after provided From date
    - Logged in before provided To date
    """
    login_from = form.cleaned_data.get("login_from")
    login_to = form.cleaned_data.get("login_to")

    if login_from:
        recipients = recipients.filter(last_login__gte=login_from)

    if login_to:
        recipients = recipients.filter(last_login__lte=login_to)

    """
    Filter recipients by translation submissions:
    - Submitted more than provided Minimum translations
    - Submitted less than provided Maximum translations
    - Submitted translations after provided From date
    - Submitted translations before provided To date
    """
    translation_minimum = form.cleaned_data.get("translation_minimum")
    translation_maximum = form.cleaned_data.get("translation_maximum")
    translation_from = form.cleaned_data.get("translation_from")
    translation_to = form.cleaned_data.get("translation_to")

    submitted = translations

    if translation_from:
        submitted = submitted.filter(date__gte=translation_from)

    if translation_to:
        submitted = submitted.filter(date__lte=translation_to)

    # For the Minimum count, no value is the same as 0
    # For the Maximum count, distinguish between no value and 0
    if translation_minimum or translation_maximum is not None:
        submitted = submitted.values("user").annotate(count=Count("user"))

    if translation_minimum:
        submitted = submitted.filter(count__gte=translation_minimum)

    if translation_maximum is not None:
        submitted = submitted.filter(count__lte=translation_maximum)

    """
    Filter recipients by reviews performed:
    - Reviewed more than provided Minimum translations
    - Reviewed less than provided Maximum translations
    - Reviewed translations after provided From date
    - Reviewed translations before provided To date
    """
    review_minimum = form.cleaned_data.get("review_minimum")
    review_maximum = form.cleaned_data.get("review_maximum")
    review_from = form.cleaned_data.get("review_from")
    review_to = form.cleaned_data.get("review_to")

    approved = translations.filter(approved_user__isnull=False).exclude(
        user=F("approved_user")
    )
    rejected = translations.filter(rejected_user__isnull=False).exclude(
        user=F("rejected_user")
    )

    if review_from:
        approved = approved.filter(approved_date__gte=review_from)
        rejected = rejected.filter(rejected_date__gte=review_from)

    if review_to:
        approved = approved.filter(approved_date__lte=review_to)
        rejected = rejected.filter(rejected_date__lte=review_to)

    # For the Minimum count, no value is the same as 0
    # For the Maximum count, distinguish between no value and 0
    if review_minimum or review_maximum is not None:
        approved = approved.values("approved_user").annotate(
            count=Count("approved_user")
        )
        rejected = rejected.values("rejected_user").annotate(
            count=Count("rejected_user")
        )

    if review_minimum:
        approved = approved.filter(count__gte=review_minimum)
        rejected = rejected.filter(count__gte=review_minimum)

    if review_maximum is not None:
        approved = approved.filter(count__lte=review_maximum)
        rejected = rejected.filter(count__lte=review_maximum)

    if (
        translation_from
        or translation_to
        or translation_minimum
        or translation_maximum is not None
    ):
        submission_filters = submitted.values_list("user", flat=True).distinct()
        recipients = recipients.filter(pk__in=submission_filters)

    if review_from or review_to or review_minimum or review_maximum is not None:
        approved_filters = approved.values_list("approved_user", flat=True).distinct()
        rejected_filters = rejected.values_list("rejected_user", flat=True).distinct()
        review_filters = approved_filters.union(rejected_filters)
        recipients = recipients.filter(pk__in=review_filters)

    return recipients


@permission_required_or_403("base.can_manage_project")
@require_AJAX
@require_POST
@transaction.atomic
def fetch_recipients(request):
    form = forms.MessageForm(request.POST)

    if not form.is_valid():
        return JsonResponse(dict(form.errors.items()), status=400)

    recipients = get_recipients(form).distinct().values_list("pk", flat=True)

    return JsonResponse(
        {
            "recipients": list(recipients),
        }
    )


@permission_required_or_403("base.can_manage_project")
@require_AJAX
@require_POST
@transaction.atomic
def send_message(request):
    form = forms.MessageForm(request.POST)

    if not form.is_valid():
        return JsonResponse(dict(form.errors.items()), status=400)

    is_notification = form.cleaned_data.get("notification")
    is_email = form.cleaned_data.get("email")
    is_transactional = form.cleaned_data.get("transactional")
    send_to_myself = form.cleaned_data.get("send_to_myself")
    recipient_ids = split_ints(form.cleaned_data.get("recipient_ids"))

    if send_to_myself:
        recipients = User.objects.filter(pk=request.user.pk)
    else:
        recipients = User.objects.filter(pk__in=recipient_ids)

    if is_email:
        recipients = recipients.prefetch_related("profile")

    log.info(f"Total recipients count: {len(recipients)}.")

    subject = form.cleaned_data.get("subject")
    body = form.cleaned_data.get("body")

    if is_notification:
        identifier = uuid.uuid4().hex

        for recipient in recipients:
            notify.send(
                request.user,
                recipient=recipient,
                verb="has sent you a message",
                target=None,
                description=f"{subject}<br/><br/>{body}",
                identifier=identifier,
                category="direct_message",
            )

        log.info(f"Notifications sent to {len(recipients)} users.")

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

        for recipient in recipients:
            if not recipient.profile.email_communications_enabled:
                continue

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

        log.info(f"Emails sent to {len(recipients)} users.")

    if not send_to_myself:
        message = form.save(commit=False)
        message.sender = request.user
        message.save()

        message.recipients.set(recipients)

        locale_ids = sorted(split_ints(form.cleaned_data.get("locales")))
        locales = Locale.objects.filter(pk__in=locale_ids)
        message.locales.set(locales)

        project_ids = form.cleaned_data.get("projects")
        projects = Project.objects.filter(pk__in=project_ids)
        message.projects.set(projects)

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
