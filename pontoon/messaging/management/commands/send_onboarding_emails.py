from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta

from pontoon.messaging.emails import send_onboarding_emails_2, send_onboarding_emails_3


class Command(BaseCommand):
    help = "Send the 2nd and 3rd onboarding emails to new users."

    def handle(self, *args, **kwargs):
        # Send the 2nd onboarding email to users that have received the 1st email
        # and have joined at least ONBOARDING_EMAIL_2_DELAY days ago.
        users_for_email_2 = User.objects.filter(
            is_active=True,
            profile__onboarding_email_status=1,
            date_joined__lt=(now() - timedelta(days=settings.ONBOARDING_EMAIL_2_DELAY)),
        )

        send_onboarding_emails_2(users_for_email_2)

        # Send the 3rd onboarding email to users that have received the 2nd email
        # and have joined at least ONBOARDING_EMAIL_3_DELAY days ago.
        users_for_email_3 = User.objects.filter(
            is_active=True,
            profile__onboarding_email_status=2,
            date_joined__lt=(now() - timedelta(days=settings.ONBOARDING_EMAIL_3_DELAY)),
        )

        send_onboarding_emails_3(users_for_email_3)
