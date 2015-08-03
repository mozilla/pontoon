from datetime import datetime
from django.contrib.auth.models import Permission, User
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from pontoon.base.models import Translation

import urllib2
import json


class Command(BaseCommand):
    help = 'Import translation authors and dates from Verbatim.'

    option_list = NoArgsCommand.option_list + (
        make_option('--project', action='store', dest='project',
                    help='Project slug to import Verbatim data to'),
        make_option('--locale', action='store', dest='locale',
                    help='Locale code to import Verbatim data to'),
        make_option('--filename', action='store', dest='filename',
                    help='File name to import Verbatim data from'),
        )

    def handle(self, *args, **options):
        project = options.get('project', False)
        locale = options.get('locale', False)
        filename = options.get('filename', False)

        if not project or not locale or not filename:
            raise CommandError('You must provide project, locale and file name.')

        url = 'http://svn.mozilla.org/projects/l10n-misc/trunk/pontoon/verbatim/' + filename + '.json'
        response = urllib2.urlopen(url)
        verbatim = json.load(response)

        for path in verbatim.keys():
            for source in verbatim[path]:

                translations = Translation.objects.filter(
                    entity__resource__project__slug=project,
                    entity__resource__path=path,
                    entity__string=source,
                    locale__code=locale)

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
                        self.stdout.write("Pontoon user not found: " + email + '\n')
                    except Exception as e:
                        self.stdout.write("Whoops, an unknown error has occured: " + e + '\n')
