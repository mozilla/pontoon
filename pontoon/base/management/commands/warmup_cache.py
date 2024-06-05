from urllib.parse import urljoin

import requests

from django.core.cache import cache
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

    def warmup_url(self, url, keys=[], is_ajax=False):
        try:
            # Make sure cache data is refreshed by deleting it
            # before making a request which will populate it again.
            for key in keys:
                cache.delete(key)

            headers = {"x-requested-with": "XMLHttpRequest"} if is_ajax else None
            requests.get(url, headers=headers)
        except requests.exceptions.RequestException as e:
            self.stdout.write(f"Failed to warm up {url}: {e}")

    def warmup_contributors_cache(self):
        self.stdout.write("Warm up Contributors page.")
        path = reverse("pontoon.contributors")
        url = urljoin(SITE_URL, path)
        key = "pontoon.contributors.views.(AND:).None"
        self.warmup_url(url, keys=[key])
        self.stdout.write("Contributors page warmed up.")

        self.stdout.write("Warm up Project Contributors tabs.")
        for project in Project.objects.available():
            path = reverse(
                "pontoon.projects.ajax.contributors", kwargs={"slug": project.slug}
            )
            url = urljoin(SITE_URL, path)
            key = f"pontoon.contributors.views.(AND:('entity__resource__project',<Project:{project}>)).None".replace(
                " ", ""
            )
            self.warmup_url(url, keys=[key])
        self.stdout.write("Project Contributors tabs warmed up.")

        self.stdout.write("Warm up Team Contributors tabs.")
        for locale in Locale.objects.available():
            path = reverse(
                "pontoon.teams.ajax.contributors", kwargs={"locale": locale.code}
            )
            url = urljoin(SITE_URL, path)
            key = f"pontoon.contributors.views.(AND:('locale',<Locale:{locale}>)).None".replace(
                " ", ""
            )
            self.warmup_url(url, keys=[key])
        self.stdout.write("Team Contributors tabs warmed up.")

        # We do not warm up ProjectLocale pages, because there are too many of them and
        # they are faster to load even if the cache is cold.

    def warmup_insights_cache(self):
        self.stdout.write("Warm up Insights page.")
        path = reverse("pontoon.insights")
        url = urljoin(SITE_URL, path)
        keys = [
            "/pontoon.insights.views/team_pretranslation_quality",
            "/pontoon.insights.views/project_pretranslation_quality",
        ]
        self.warmup_url(url, keys=keys)
        self.stdout.write("Insights page warmed up.")

        self.stdout.write("Warm up Project Insights tabs.")
        for project in Project.objects.available():
            path = reverse(
                "pontoon.projects.ajax.insights", kwargs={"slug": project.slug}
            )
            url = urljoin(SITE_URL, path)
            key = f"/pontoon.projects.views/{project.slug}/insights"
            self.warmup_url(url, keys=[key], is_ajax=True)
        self.stdout.write("Project Insights tabs warmed up.")

        self.stdout.write("Warm up Team Insights tabs.")
        for locale in Locale.objects.available():
            path = reverse(
                "pontoon.teams.ajax.insights", kwargs={"locale": locale.code}
            )
            url = urljoin(SITE_URL, path)
            key = f"/pontoon.teams.views/{locale.code}/insights"
            self.warmup_url(url, keys=[key], is_ajax=True)
        self.stdout.write("Team Insights tabs warmed up.")

        # We do not warm up ProjectLocale pages, because there are too many of them and
        # they are faster to load even if the cache is cold.
