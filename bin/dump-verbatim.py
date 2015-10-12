from django.core.management.base import (
    BaseCommand,
    CommandError,
    NoArgsCommand,
)
from optparse import make_option
from pootle_store.models import Store, Unit

import codecs
import json
import subprocess


class Command(BaseCommand):
    help = 'Dump translation authors and dates for given project and locale.'

    option_list = NoArgsCommand.option_list + (
        make_option('--project', action='store', dest='project',
                    help='Project code to dump translations from'),
        make_option('--locale', action='store', dest='locale',
                    help='Locale code to dump translations from'),
        )

    def handle(self, *args, **options):
        project = options.get('project', False)
        locale = options.get('locale', False)

        if not project or not locale:
            raise CommandError('You must provide project and locale.')

        output = {}

        # Loop stores (files)
        for store in Store.objects.filter(
            translation_project__project__code=project,
            translation_project__language__code=locale
        ):

            path = {}

            # Loop units (original-translation pairs)
            for unit in Unit.objects.filter(store=store):
                if unit.state == 200 and unit.submitted_by:

                    path[unit.source_f] = {
                        "translation": unit.target_f,
                        "date": str(unit.submitted_on),
                        "author": unit.submitted_by.user.email
                    }

            output[store.path] = path

        filename = "%s_%s.json" % (locale, project)

        # Export to file
        with codecs.open("verbatim/" + filename, 'w+', 'utf-8') as f:
            f.seek(0)
            f.truncate()
            content = json.dumps(output, indent=4, ensure_ascii=False)
            f.write(content)

        # Commit to SVN
        try:
            s = subprocess.PIPE
            add = ["svn", "add", "verbatim/" + filename, "verbatim"]
            proc = subprocess.Popen(args=add, stdout=s, stderr=s, stdin=s)

            commit = ["svn", "commit", "-m", "Added " + filename, "verbatim"]
            proc = subprocess.Popen(args=commit, stdout=s, stderr=s, stdin=s)

            (output, error) = proc.communicate()
            code = proc.returncode
        except OSError as error:
            code = -1

        if code == 0:
            self.stdout.write("Committed " + filename + ".\n")
        else:
            self.stdout.write(error + "\n")
