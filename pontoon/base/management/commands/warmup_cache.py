import requests

from urllib.parse import urljoin

from django.core.management.base import BaseCommand
from django.urls import reverse

from pontoon.base.models import Locale, Project
from pontoon.settings.base import SITE_URL


class Command(BaseCommand):
    help = """
        Keep cache warm.

        We cache data for some of the views (e.g. Contributors) for a day. Some of them
        don't get a lot of visits, not even one per day, meaning that the visitors of
        these pages often hit the cold cache.

        We use this command to refresh data in the cache every day, because it changes
        often.

        The command is designed to run daily.
        """

    def handle(self, *args, **options):
        self.warmup_contributors_cache()
        self.warmup_insights_cache()

    def warmup_url(self, url, is_ajax=False):
        try:
            headers = {"x-requested-with": "XMLHttpRequest"} if is_ajax else None
            requests.get(url, headers=headers)
        except requests.exceptions.RequestException as e:
            self.stdout.write(f"Failed to warm up {url}: {e}")

    def warmup_contributors_cache(self):
        self.stdout.write("Warm up Contributors page.")
        path = reverse("pontoon.contributors")
        url = urljoin(SITE_URL, path)
        self.warmup_url(url)
        self.stdout.write("Contributors page warmed up.")

        self.stdout.write("Warm up Project Contributors tabs.")
        for project in Project.objects.available():
            path = reverse(
                "pontoon.projects.ajax.contributors", kwargs={"slug": project.slug}
            )
            url = urljoin(SITE_URL, path)
            self.warmup_url(url)
        self.stdout.write("Project Contributors tabs warmed up.")

        self.stdout.write("Warm up Team Contributors tabs.")
        for locale in Locale.objects.available():
            path = reverse(
                "pontoon.teams.ajax.contributors", kwargs={"locale": locale.code}
            )
            url = urljoin(SITE_URL, path)
            self.warmup_url(url)
        self.stdout.write("Team Contributors tabs warmed up.")

        # We do not warm up ProjectLocale pages, because there are too many of them and
        # they are faster to load even if the cache is cold.

    def warmup_insights_cache(self):
        self.stdout.write("Warm up Insights page.")
        path = reverse("pontoon.insights")
        url = urljoin(SITE_URL, path)
        self.warmup_url(url)
        self.stdout.write("Insights page warmed up.")

        self.stdout.write("Warm up Project Insights tabs.")
        for project in Project.objects.available():
            path = reverse(
                "pontoon.projects.ajax.insights", kwargs={"slug": project.slug}
            )
            url = urljoin(SITE_URL, path)
            self.warmup_url(url, is_ajax=True)
        self.stdout.write("Project Insights tabs warmed up.")

        self.stdout.write("Warm up Team Insights tabs.")
        for locale in Locale.objects.available():
            path = reverse(
                "pontoon.teams.ajax.insights", kwargs={"locale": locale.code}
            )
            url = urljoin(SITE_URL, path)
            self.warmup_url(url, is_ajax=True)
        self.stdout.write("Team Insights tabs warmed up.")

        # We do not warm up ProjectLocale pages, because there are too many of them and
        # they are faster to load even if the cache is cold.
