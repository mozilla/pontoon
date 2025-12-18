import calendar
import datetime
import logging

from collections import defaultdict

from celery import shared_task
from dateutil.relativedelta import relativedelta
from django_jinja.backend import Jinja2
from notifications.models import Notification

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count, F, Min, Prefetch, Q, Sum
from django.template.loader import get_template
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import Locale, UserProfile
from pontoon.insights.models import LocaleInsightsSnapshot
from pontoon.messaging.models import EmailContent
from pontoon.messaging.utils import html_to_plain_text_with_links


jinja_env = Jinja2.get_default().env
log = logging.getLogger(__name__)


def _get_monthly_user_actions(users, months_ago):
    month_date = timezone.now() - relativedelta(months=months_ago)

    actions = (
        ActionLog.objects.filter(
            performed_by__in=users,
            created_at__month=month_date.month,
            created_at__year=month_date.year,
        )
        .values("performed_by")
        .annotate(
            submitted=Count("id", filter=Q(action_type="translation:created")),
            reviewed=Count(
                "id",
                filter=Q(
                    action_type__in=["translation:approved", "translation:rejected"]
                ),
            ),
        )
    )

    return {action["performed_by"]: action for action in actions}


def _get_monthly_locale_actions(months_ago):
    month_date = timezone.now() - relativedelta(months=months_ago)

    snapshots = (
        LocaleInsightsSnapshot.objects.filter(
            created_at__month=month_date.month,
            created_at__year=month_date.year,
        )
        .values("locale")
        .annotate(
            added_source_strings=Sum("new_source_strings"),
            submitted=Sum(F("human_translations") + F("machinery_translations")),
            reviewed=Sum(F("peer_approved") + F("rejected")),
        )
    )

    return {snapshot["locale"]: snapshot for snapshot in snapshots}


def _get_monthly_locale_stats(months_ago):
    month_date = timezone.now() - relativedelta(months=months_ago)
    last_day = calendar.monthrange(month_date.year, month_date.month)[1]

    snapshots = LocaleInsightsSnapshot.objects.filter(
        created_at__day=last_day,
        created_at__month=month_date.month,
        created_at__year=month_date.year,
    )

    return {snapshot.locale_id: snapshot for snapshot in snapshots}


def _get_monthly_locale_contributors(locales, months_ago):
    month_date = timezone.now() - relativedelta(months=months_ago)

    actions = ActionLog.objects.filter(
        performed_by__profile__system_user=False,
        # Exclude system projects
        translation__entity__resource__project__system_project=False,
    )

    # Get contributors that started contributing to the locale in the given month
    first_contributions = (
        actions.values("performed_by", "translation__locale")
        .annotate(first_contribution_date=Min("created_at"))
        .filter(
            first_contribution_date__month=month_date.month,
            first_contribution_date__year=month_date.year,
        )
    )

    new_locale_contributors = {
        (entry["translation__locale"], entry["performed_by"])
        for entry in first_contributions
    }

    # Get all contributors in the given month,
    # grouped by locale and orderd by contribution count
    monthly_contributors = (
        actions.filter(
            created_at__month=month_date.month,
            created_at__year=month_date.year,
        )
        .values("translation__locale", "performed_by")
        .annotate(contribution_count=Count("id"))
        .order_by("-contribution_count")
    )

    # Group contributors by locale and user role
    results = {}
    all_locale_pks = [entry["translation__locale"] for entry in monthly_contributors]
    locales_dict = {locale.pk: locale for locale in locales}

    all_user_pks = [entry["performed_by"] for entry in monthly_contributors]
    users = User.objects.filter(pk__in=all_user_pks)
    users_dict = {user.pk: user for user in users}

    for locale_pk in all_locale_pks:
        locale_entries = [
            entry
            for entry in monthly_contributors
            if entry["translation__locale"] == locale_pk
        ]
        locale = locales_dict.get(locale_pk)

        new_contributors = []
        active_managers = []
        active_translators = []
        active_contributors = []

        for entry in locale_entries:
            user_pk = entry["performed_by"]
            user = users_dict.get(user_pk)

            if (locale_pk, user_pk) in new_locale_contributors:
                # Exclude staff users from new contributors
                if not user.is_staff:
                    new_contributors.append(user)

            if user in locale.managers_group.fetched_managers:
                active_managers.append(user)
            elif user in locale.translators_group.fetched_translators:
                active_translators.append(user)
            else:
                active_contributors.append(user)

        results[locale_pk] = {
            "new_contributors": new_contributors,
            "active_managers": active_managers,
            "active_translators": active_translators,
            "active_contributors": active_contributors,
        }

    return results


def send_monthly_activity_summary():
    """
    Sends Monthly activity summary emails.
    """
    log.info("Start sending Monthly activity summary emails.")

    # Get user monthly actions
    users = User.objects.filter(is_active=True, profile__monthly_activity_summary=True)
    user_month_actions = _get_monthly_user_actions(users, months_ago=1)
    previous_user_month_actions = _get_monthly_user_actions(users, months_ago=2)

    for user in users:
        user.month_actions = user_month_actions.get(user.pk, {})
        user.previous_month_actions = previous_user_month_actions.get(user.pk, {})

    # Get locale monthly actions
    locales = Locale.objects.prefetch_related(
        Prefetch("managers_group__user_set", to_attr="fetched_managers"),
        Prefetch("translators_group__user_set", to_attr="fetched_translators"),
    )

    locale_month_actions = _get_monthly_locale_actions(months_ago=1)
    locale_previous_month_actions = _get_monthly_locale_actions(months_ago=2)

    locale_month_stats = _get_monthly_locale_stats(months_ago=1)
    locale_previous_month_stats = _get_monthly_locale_stats(months_ago=2)

    locale_contributors = _get_monthly_locale_contributors(locales, months_ago=1)

    for locale in locales:
        locale.month_actions = locale_month_actions.get(locale.pk, {})
        locale.previous_month_actions = locale_previous_month_actions.get(locale.pk, {})
        locale.month_stats = locale_month_stats.get(locale.pk, {})
        locale.previous_month_stats = locale_previous_month_stats.get(locale.pk, {})
        locale.contributors = locale_contributors.get(locale.pk, {})

    # Create a map of users to locales in which they are managers or translators,
    # which determines if the user should receive the Team activity section of the email
    user_locales = defaultdict(set)
    for locale in locales:
        for user in locale.managers_group.fetched_managers:
            user_locales[user].add(locale)
        for user in locale.translators_group.fetched_translators:
            user_locales[user].add(locale)

    # Process and send email for each user
    subject = "Monthly activity summary"
    template = get_template("messaging/emails/monthly_activity_summary.html")

    now = timezone.now()
    current_month = now.month
    report_month = calendar.month_name[(current_month - 1) or 12]

    current_year = now.year
    report_year = current_year if current_month > 1 else current_year - 1

    for user in users:
        body_html = template.render(
            {
                "subject": subject,
                "month": report_month,
                "year": report_year,
                "user": user,
                "locales": user_locales.get(user, []),
                "settings": settings,
            }
        )
        body_text = html_to_plain_text_with_links(body_html)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.contact_email],
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()

    recipient_count = len(users)

    log.info(f"Monthly activity summary emails sent to {recipient_count} users.")


def send_notification_digest(frequency="Daily"):
    """
    Sends notification email digests to users based on the specified frequency (Daily or Weekly).
    """
    log.info(f"Start sending {frequency} notification email digests.")

    if frequency == "Daily":
        start_time = timezone.now() - datetime.timedelta(days=1)
    elif frequency == "Weekly":
        start_time = timezone.now() - datetime.timedelta(weeks=1)

    users = (
        User.objects.filter(is_active=True)
        # Users with the selected notification email frequency
        .filter(profile__notification_email_frequency=frequency)
        # Users subscribed to at least one email notification type
        .filter(
            Q(profile__new_string_notifications_email=True)
            | Q(profile__project_deadline_notifications_email=True)
            | Q(profile__comment_notifications_email=True)
            | Q(profile__unreviewed_suggestion_notifications_email=True)
            | Q(profile__review_notifications_email=True)
            | Q(profile__new_contributor_notifications_email=True)
        )
    )

    notifications = Notification.objects.filter(
        recipient__in=users,
        timestamp__gte=start_time,
    ).select_related("recipient__profile")

    # Group notifications by user
    notifications_map = defaultdict(list)
    for notification in notifications:
        recipient = notification.recipient

        # Only include notifications the user chose to receive via email
        if recipient.is_subscribed_to_notification(notification):
            notifications_map[recipient].append(notification)

    subject = f"{frequency} notifications summary"
    template = get_template("messaging/emails/notification_digest.html")

    # Process and send email for each user
    for user, user_notifications in notifications_map.items():
        body_html = template.render(
            {
                "notifications": user_notifications,
                "subject": subject,
            }
        )
        body_text = html_to_plain_text_with_links(body_html)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.contact_email],
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()

    recipient_count = len(notifications_map.keys())

    log.info(f"Notification email digests sent to {recipient_count} users.")


def send_onboarding_email_1(user):
    """
    Sends 1st onboarding email to a new user.
    """
    email_content = EmailContent.objects.get(email="onboarding_1")
    content = jinja_env.from_string(email_content.body).render()

    subject = email_content.subject
    template = get_template("messaging/emails/transactional.html")

    body_html = template.render(
        {
            "content": content,
            "subject": subject,
        }
    )
    body_text = html_to_plain_text_with_links(body_html)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.contact_email],
    )
    msg.attach_alternative(body_html, "text/html")
    msg.send()

    profile = user.profile
    profile.onboarding_email_status = 1
    profile.save(update_fields=["onboarding_email_status"])

    log.info(f"1st onboarding email sent to {user.contact_email}.")


def send_onboarding_emails_2(users):
    """
    Sends 2nd onboarding emails to new users.
    """
    log.info("Start sending 2nd onboarding emails.")

    email_content = EmailContent.objects.get(email="onboarding_2")
    content = jinja_env.from_string(email_content.body).render()

    subject = email_content.subject
    template = get_template("messaging/emails/transactional.html")

    body_html = template.render(
        {
            "content": content,
            "subject": subject,
        }
    )
    body_text = html_to_plain_text_with_links(body_html)

    for user in users:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.contact_email],
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()

    pks = users.values_list("pk", flat=True)
    UserProfile.objects.filter(user__in=pks).update(onboarding_email_status=2)

    log.info(f"2nd onboarding emails sent to {len(users)} users.")


def send_onboarding_emails_3(users):
    """
    Sends 3rd onboarding emails to new users.
    """
    log.info("Start sending 3rd onboarding emails.")

    email_content = EmailContent.objects.get(email="onboarding_3")
    content = jinja_env.from_string(email_content.body).render()

    subject = email_content.subject
    template = get_template("messaging/emails/transactional.html")

    body_html = template.render(
        {
            "content": content,
            "subject": subject,
        }
    )
    body_text = html_to_plain_text_with_links(body_html)

    for user in users:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.contact_email],
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()

    pks = users.values_list("pk", flat=True)
    UserProfile.objects.filter(user__in=pks).update(onboarding_email_status=3)

    log.info(f"3rd onboarding emails sent to {len(users)} users.")


def send_inactive_contributor_emails(users):
    """
    Sends an email to an inactive contributor.
    """
    log.info("Start sending inactive contributor emails.")

    email_content = EmailContent.objects.get(email="inactive_contributor")
    content = jinja_env.from_string(email_content.body).render()

    subject = email_content.subject
    template = get_template("messaging/emails/transactional.html")

    body_html = template.render(
        {
            "content": content,
            "settings": settings,
            "subject": subject,
        }
    )
    body_text = html_to_plain_text_with_links(body_html)

    for user in users:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.contact_email],
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()

    pks = users.values_list("pk", flat=True)
    now = timezone.now()
    UserProfile.objects.filter(user__in=pks).update(last_inactive_reminder_sent=now)

    log.info(f"Inactive contributor emails sent to {len(users)} users.")


def send_inactive_translator_emails(users, translator_map):
    """
    Sends an email to an inactive translator.
    """
    log.info("Start sending inactive translator emails.")

    email_content = EmailContent.objects.get(email="inactive_translator")
    subject = email_content.subject
    template = get_template("messaging/emails/transactional.html")

    for user in users:
        try:
            locale = list(translator_map[user.pk])[0]
        except IndexError:
            log.error(f"User {user} is not a translator of any locale.")
            continue

        content = jinja_env.from_string(email_content.body).render({"locale": locale})
        body_html = template.render(
            {
                "content": content,
                "settings": settings,
                "subject": subject,
            }
        )
        body_text = html_to_plain_text_with_links(body_html)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.contact_email],
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()

    pks = users.values_list("pk", flat=True)
    now = timezone.now()
    UserProfile.objects.filter(user__in=pks).update(last_inactive_reminder_sent=now)

    log.info(f"Inactive translator emails sent to {len(users)} users.")


def send_inactive_manager_emails(users, manager_map):
    """
    Sends an email to an inactive manager.
    """
    log.info("Start sending inactive manager emails.")

    email_content = EmailContent.objects.get(email="inactive_manager")
    subject = email_content.subject
    template = get_template("messaging/emails/transactional.html")

    for user in users:
        try:
            locale = list(manager_map[user.pk])[0]
        except IndexError:
            log.error(f"User {user} is not a manager of any locale.")
            continue

        content = jinja_env.from_string(email_content.body).render({"locale": locale})
        body_html = template.render(
            {
                "content": content,
                "settings": settings,
                "subject": subject,
            }
        )
        body_text = html_to_plain_text_with_links(body_html)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.contact_email],
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()

    pks = users.values_list("pk", flat=True)
    now = timezone.now()
    UserProfile.objects.filter(user__in=pks).update(last_inactive_reminder_sent=now)

    log.info(f"Inactive manager emails sent to {len(users)} users.")


def send_verification_email(user, link):
    """
    Sends a contact email address verification email.
    """
    template = get_template("messaging/emails/verification_email.html")
    subject = "Verify email address for Pontoon"

    body_html = template.render(
        {
            "subject": subject,
            "display_name": user.display_name,
            "link": link,
        }
    )
    body_text = html_to_plain_text_with_links(body_html)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.contact_email],
    )
    msg.attach_alternative(body_html, "text/html")
    msg.send()

    log.info(f"Verification email sent to {user.contact_email}.")


@shared_task(bind=True)
def send_manual_emails(self, users, subject, body, is_transactional):
    """
    Sends manual emails composed in the Messaging Center.
    """
    template = get_template("messaging/emails/manual.html")

    for user in users:
        body_html = template.render(
            {
                "subject": subject,
                "content": body,
                "is_transactional": is_transactional,
                "settings": settings,
                "user": user,
            }
        )
        body_text = html_to_plain_text_with_links(body_html)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.contact_email],
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()

    log.info(f"Emails sent to {len(users)} users.")
