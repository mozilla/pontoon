# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.fxa.provider import FirefoxAccountsProvider
from allauth.socialaccount.providers.github.provider import GitHubProvider


FXA_PROVIDER_ID = FirefoxAccountsProvider.id
GITHUB_PROVIDER_ID = GitHubProvider.id


class Command(BaseCommand):
    help = ('Ensures an allauth application exists and has credentials that match settings')

    def update_provider(self, data):
        # Update the existing provider with current settings.
        try:
            app = SocialApp.objects.get(provider=data['provider'])
            for k, v in data.items():
                setattr(app, k, v)
            self.stdout.write("Updating existing authentication provider (pk=%s)" % app.pk)
            app.save()

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
        if settings.FXA_CLIENT_ID is not None or settings.FXA_SECRET_KEY is not None:
            fxa_data = dict(
                name='FxA',
                provider=FXA_PROVIDER_ID,
                client_id=settings.FXA_CLIENT_ID,
                secret=settings.FXA_SECRET_KEY
            )

            self.update_provider(fxa_data)

        # Check if GitHub_* settings are configured
        if settings.GITHUB_CLIENT_ID is not None or settings.GITHUB_SECRET_KEY is not None:
            github_data = dict(
                name='GitHub',
                provider=GITHUB_PROVIDER_ID,
                client_id=settings.GITHUB_CLIENT_ID,
                secret=settings.GITHUB_SECRET_KEY
            )

            self.update_provider(github_data)
