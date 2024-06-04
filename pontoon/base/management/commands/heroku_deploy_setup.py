import os

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from pontoon.base.models import User
from urllib.parse import urlparse


class Command(BaseCommand):
    help = "Setup an instance of Pontoon deployed via Heroku Deploy."

    def handle(self, *args, **options):
        site_url = os.environ.get("SITE_URL")
        app_host = urlparse(site_url).netloc
        admin_email = os.environ.get("ADMIN_EMAIL")
        admin_password = os.environ.get("ADMIN_PASSWORD")

        User.objects.create_superuser(admin_email, admin_email, admin_password)
        Site.objects.filter(pk=1).update(name=app_host, domain=app_host)
