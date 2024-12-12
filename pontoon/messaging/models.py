from django.db import models
from django.db.models import Q
from django.utils import timezone

from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project
from pontoon.base.models.user import User


class Message(models.Model):
    sent_at = models.DateTimeField(default=timezone.now)
    sender = models.ForeignKey(User, models.CASCADE, related_name="messages")
    recipients = models.ManyToManyField(User, related_name="received_messages")

    notification = models.BooleanField(default=False)
    email = models.BooleanField(default=False)
    transactional = models.BooleanField(default=False)

    subject = models.CharField(max_length=255)
    body = models.TextField()

    managers = models.BooleanField(default=True)
    translators = models.BooleanField(default=True)
    contributors = models.BooleanField(default=True)

    locales = models.ManyToManyField(Locale, related_name="messages")
    projects = models.ManyToManyField(Project, related_name="messages")

    translation_minimum = models.PositiveIntegerField(blank=True, null=True)
    translation_maximum = models.PositiveIntegerField(blank=True, null=True)
    translation_from = models.DateField(blank=True, null=True)
    translation_to = models.DateField(blank=True, null=True)

    review_minimum = models.PositiveIntegerField(blank=True, null=True)
    review_maximum = models.PositiveIntegerField(blank=True, null=True)
    review_from = models.DateField(blank=True, null=True)
    review_to = models.DateField(blank=True, null=True)

    login_from = models.DateField(blank=True, null=True)
    login_to = models.DateField(blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(notification=True) | Q(email=True),
                name="at_least_one_message_type",
            ),
            models.CheckConstraint(
                check=Q(managers=True) | Q(translators=True) | Q(contributors=True),
                name="at_least_one_user_role",
            ),
        ]

    def is_new(self):
        return self.sent_at > timezone.now() - timezone.timedelta(minutes=1)


class EmailContent(models.Model):
    email = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
