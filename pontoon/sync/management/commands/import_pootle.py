from bulk_update.helper import bulk_update
from collections import Counter
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from pontoon.base.models import Translation, Project, Locale

import requests


class Command(BaseCommand):
    help = "Import translation authors and dates from Verbatim."

    def add_arguments(self, parser):
        parser.add_argument(
            "--project",
            action="store",
            dest="project",
            help="Project slug to import Verbatim data to",
        )

        parser.add_argument(
            "--locale",
            action="store",
            dest="locale",
            help="Locale code to import Verbatim data to",
        )

    def handle(self, *args, **options):
        locale = options["locale"]
        project = options["project"]

        if not project and not locale:
            raise CommandError("You must provide a project or a locale.")

        elif project and locale:
            self.handle_project_locale(project, locale)

        elif project:
            locales = Project.objects.get(slug=project).locales.all()
            for locale in locales:
                self.handle_project_locale(project, locale.code)

        elif locale:
            projects = Locale.objects.get(code=locale).project_set.all()
            for project in projects:
                self.handle_project_locale(project.slug, locale)

    @transaction.atomic
    def handle_project_locale(self, project, locale):
        # Match locale code inconsistencies
        pootle_locale = locale.replace("-", "_")
        if pootle_locale == "ga_IE":
            pootle_locale = "ga"

        # Match project slug inconsistencies
        pootle_project = {
            "amo": "amo",
            "find-my-device": "findmydevice",
            "firefox-accounts": "accounts",
            "firefox-accounts-payments": "payments",
            "firefox-hello": "loop",
            "firefox-input": "input",
            "marketplace": "marketplace",
            "marketplace-commbadge": "commbadge",
            "marketplace-fireplace": "fireplace",
            "marketplace-spartacus": "spartacus",
            "marketplace-stats": "marketplace_stats",
            "marketplace-zippy": "zippy",
            "master-firefox-os": "masterfirefoxos",
            "mdn": "mdn",
            "mozillians": "mozillians",
            "social-api-directory": "socialapi-directory",
            "sumo": "sumo",
        }.get(project)

        if not pootle_project:
            return

        # Get Pootle data
        filename = pootle_locale + "_" + pootle_project + ".json"
        url = (
            "http://svn.mozilla.org/projects/l10n-misc/trunk/pontoon/verbatim/"
            + filename
        )

        try:
            pootle = requests.get(url).json()
        except ValueError:
            return self.stdout.write("--- Skipping missing file {}.".format(filename))

        # Get all Pontoon translations matching Pootle data
        paths = pootle.keys()
        entities = []
        strings = []
        emails = []

        for path in paths:
            for entity in pootle[path].keys():
                entities.append(entity)
                strings.append(pootle[path][entity]["translation"])
                emails.append(pootle[path][entity]["author"])

        translations = Translation.objects.filter(
            entity__resource__project__slug=project,
            entity__resource__path__in=paths,
            entity__string__in=entities,
            locale__code=locale,
            user=None,
            string__in=strings,
        )

        # Save user permissions and create dict to avoid hitting the DB later
        users_dict = {}
        users = User.objects.filter(email__in=emails)
        missing_users_list = []
        locale_translators_map = dict(
            Locale.objects.values_list("code", "translators_group")
        )
        for u in users:
            users_dict[u.email] = u

            if "base.can_translate_locale" not in u.get_all_permissions():
                u.groups.add(locale_translators_map[locale])
                self.stdout.write(
                    "Permission granted to user {} to locale: {}.".format(
                        u.email, locale
                    )
                )

        if users:
            bulk_update(users)

        for t in translations:
            try:
                pootle_translation = pootle[t.entity.resource.path][t.entity.string]
            # Path - entity mismatch, skip to next translation
            except KeyError:
                continue

            # Save user
            email = pootle_translation["author"]
            user = users_dict.get(email)

            if not user:
                missing_users_list.append(email)

            t.user = user
            t.approved_user = user

            # Save date
            date = pootle_translation["date"].split("+")[0]
            dateObj = timezone.make_aware(datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))
            t.date = dateObj
            t.approved_date = dateObj

        if translations:
            bulk_update(translations)

        missing_users = Counter(missing_users_list)
        for missing_user in missing_users.keys():
            self.stdout.write(
                "Pontoon user {} not found: {} translations.".format(
                    missing_user, missing_users[missing_user]
                )
            )

        self.stdout.write("+++ Imported data from file {}.".format(filename))
