from datetime import datetime
from django.contrib.auth.models import Permission, User
from django.core.management.base import (
    BaseCommand,
    CommandError,
    NoArgsCommand,
)
from pontoon.base.models import Translation

import requests


class Command(BaseCommand):
    help = 'Import translation authors and dates from Verbatim.'

    def add_arguments(self, parser):

        parser.add_argument(
            '--project',
            action='store',
            dest='project',
            required=True,
            help='Project slug to import Verbatim data to'
        )

        parser.add_argument(
            '--locale',
            action='store',
            dest='locale',
            required=True,
            help='Locale code to import Verbatim data to'
        )

        parser.add_argument(
            '--filename',
            action='store',
            dest='filename',
            required=True,
            help='File name to import Verbatim data from'
        )

    def handle(self, *args, **options):
        url = 'http://svn.mozilla.org/projects/l10n-misc/trunk/pontoon/verbatim/' + options['filename']
        verbatim = requests.get(url).json()

        for path in verbatim.keys():
            for source in verbatim[path]:

                translations = Translation.objects.filter(
                    entity__resource__project__slug=options['project'],
                    entity__resource__path=path,
                    entity__string=source,
                    locale__code=options['locale'])

                for t in translations:
                    try:
                        # Save user
                        email = verbatim[path][source]["author"]
                        user = User.objects.get(email=email)
                        t.user = user
                        t.approved_user = user

                        # Save date
                        date = verbatim[path][source]["date"].split("+")[0]
                        dateObj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                        t.date = dateObj
                        t.approved_date = dateObj

                        t.save()

                        # Save permissions
                        if not user.has_perm('base.can_localize'):
                            can_localize = Permission.objects.get(codename="can_localize")
                            user.user_permissions.add(can_localize)
                            user.save()

                    except User.DoesNotExist:
                        # TODO: create missing user?
                        self.stdout.write("Pontoon user not found: " + email)
