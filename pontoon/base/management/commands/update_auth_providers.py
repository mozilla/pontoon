# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.fxa.provider import FirefoxAccountsProvider
from allauth.socialaccount.providers.github.provider import GitHubProvider
from allauth.socialaccount.providers.gitlab.provider import GitLabProvider
from allauth.socialaccount.providers.google.provider import GoogleProvider


FXA_PROVIDER_ID = FirefoxAccountsProvider.id
GITHUB_PROVIDER_ID = GitHubProvider.id
GITLAB_PROVIDER_ID = GitLabProvider.id
GOOGLE_PROVIDER_ID = GoogleProvider.id


class Command(BaseCommand):
    help = (
        "Ensures an allauth application exists and has credentials that match settings"
    )

    def update_provider(self, data):
        # Update the existing provider with current settings.
        try:
            app = SocialApp.objects.get(provider=data["provider"])
            for k, v in data.items():
                setattr(app, k, v)
            app.save()
            self.stdout.write(
                "Updated existing authentication provider (pk=%s)" % app.pk
            )

        # Create the provider if necessary.
        except ObjectDoesNotExist:
            app = SocialApp(**data)
            app.save()
            self.stdout.write("Created new authentication provider (pk=%s)" % app.pk)

        # Ensure the provider applies to the current default site.
        sites_count = app.sites.count()
        if sites_count == 0:
            default_site = Site.objects.get(pk=settings.SITE_ID)
            app.sites.add(default_site)

    def handle(self, *args, **options):
        # Check if FXA_* settings are configured
        if settings.FXA_CLIENT_ID is not None and settings.FXA_SECRET_KEY is not None:
            fxa_data = dict(
                name="FxA",
                provider=FXA_PROVIDER_ID,
                client_id=settings.FXA_CLIENT_ID,
                secret=settings.FXA_SECRET_KEY,
            )

            self.update_provider(fxa_data)

        # Check if GITHUB_* settings are configured
        if (
            settings.GITHUB_CLIENT_ID is not None
            and settings.GITHUB_SECRET_KEY is not None
        ):
            github_data = dict(
                name="GitHub",
                provider=GITHUB_PROVIDER_ID,
                client_id=settings.GITHUB_CLIENT_ID,
                secret=settings.GITHUB_SECRET_KEY,
            )

            self.update_provider(github_data)

        # Check if GITLAB_* settings are configured
        if (
            settings.GITLAB_CLIENT_ID is not None
            and settings.GITLAB_SECRET_KEY is not None
        ):
            gitlab_data = dict(
                name="GitLab",
                provider=GITLAB_PROVIDER_ID,
                client_id=settings.GITLAB_CLIENT_ID,
                secret=settings.GITLAB_SECRET_KEY,
            )

            self.update_provider(gitlab_data)

        # Check if GOOGLE_* settings are configured
        if (
            settings.GOOGLE_CLIENT_ID is not None
            and settings.GOOGLE_SECRET_KEY is not None
        ):
            google_data = dict(
                name="Google",
                provider=GOOGLE_PROVIDER_ID,
                client_id=settings.GOOGLE_CLIENT_ID,
                secret=settings.GOOGLE_SECRET_KEY,
            )

            self.update_provider(google_data)
