#!/usr/bin/env python
"""
Usage: update_site.py [options]
Updates a server's sources, vendor libraries, packages CSS/JS
assets, migrates the database, and other nifty deployment tasks.

Options:
  -h, --help            show this help message and exit
  -e ENVIRONMENT, --environment=ENVIRONMENT
                        Type of environment. One of (prod|dev|stage) Example:
                        update_site.py -e stage
  -v, --verbose         Echo actions before taking them.
"""

import os
import sys
from textwrap import dedent
from optparse import  OptionParser
from hashlib import md5

# Constants
PROJECT = 0
VENDOR  = 1

ENV_BRANCH = {
    # 'environment': [PROJECT_BRANCH, VENDOR_BRANCH],
    'dev':   ['base',   'master'],
    'stage': ['master', 'master'],
    'prod':  ['prod',   'master'],
}

# The URL of the SVN repository with the localization files (*.po). If you set 
# it to a non-empty value, remember to `git rm --cached -r locale` in the root 
# of the project.  Example:
# LOCALE_REPO_URL = 'https://svn.mozilla.org/projects/l10n-misc/trunk/playdoh/locale'
LOCALE_REPO_URL = ''

GIT_PULL = "git pull -q origin %(branch)s"
GIT_SUBMODULE = "git submodule update --init"
SVN_CO = "svn checkout --force %(url)s locale"
SVN_UP = "svn update"
COMPILE_MO = "./bin/compile-mo.sh %(localedir)s %(unique)s"

EXEC = 'exec'
CHDIR = 'chdir'


def update_site(env, debug):
    """Run through commands to update this site."""
    error_updating = False
    here = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    locale = os.path.join(here, 'locale')
    unique = md5(locale).hexdigest()
    project_branch = {'branch': ENV_BRANCH[env][PROJECT]}
    vendor_branch = {'branch': ENV_BRANCH[env][VENDOR]}

    commands = [
        (CHDIR, here),
        (EXEC,  GIT_PULL % project_branch),
        (EXEC,  GIT_SUBMODULE),
    ]

    # Checkout the locale repo into locale/ if the URL is known
    if LOCALE_REPO_URL and not os.path.exists(os.path.join(locale, '.svn')):
        commands += [
            (EXEC, SVN_CO % {'url': LOCALE_REPO_URL}),
            (EXEC, COMPILE_MO % {'localedir': locale, 'unique': unique}),
        ]

    # Update locale dir if applicable
    if os.path.exists(os.path.join(locale, '.svn')):
        commands += [
            (CHDIR, locale),
            (EXEC, SVN_UP),
            (CHDIR, here),
            (EXEC, COMPILE_MO % {'localedir': locale, 'unique': unique}),
        ]
    elif os.path.exists(os.path.join(locale, '.git')):
        commands += [
            (CHDIR, locale),
            (EXEC, GIT_PULL % 'master'),
            (CHDIR, here),
        ]

    commands += [
        (CHDIR, os.path.join(here, 'vendor')),
        (EXEC,  GIT_PULL % vendor_branch),
        (EXEC,  GIT_SUBMODULE),
        (CHDIR, os.path.join(here)),
        (EXEC, 'python2.6 vendor/src/schematic/schematic migrations/'),
        (EXEC, 'python2.6 manage.py compress_assets'),
    ]

    for cmd, cmd_args in commands:
        if CHDIR == cmd:
            if debug:
                sys.stdout.write("cd %s\n" % cmd_args)
            os.chdir(cmd_args)
        elif EXEC == cmd:
            if debug:
                sys.stdout.write("%s\n" % cmd_args)
            if not 0 == os.system(cmd_args):
                error_updating = True
                break
        else:
            raise Exception("Unknown type of command %s" % cmd)

    if error_updating:
        sys.stderr.write("There was an error while updating. Please try again "
                         "later. Aborting.\n")


def main():
    """ Handels command line args. """
    debug = False
    usage = dedent("""\
        %prog [options]
        Updates a server's sources, vendor libraries, packages CSS/JS
        assets, migrates the database, and other nifty deployment tasks.
        """.rstrip())

    options = OptionParser(usage=usage)
    e_help = "Type of environment. One of (%s) Example: update_site.py \
        -e stage" % '|'.join(ENV_BRANCH.keys())
    options.add_option("-e", "--environment", help=e_help)
    options.add_option("-v", "--verbose",
                       help="Echo actions before taking them.",
                       action="store_true", dest="verbose")
    (opts, _) = options.parse_args()

    if opts.verbose:
        debug = True
    if opts.environment in ENV_BRANCH.keys():
        update_site(opts.environment, debug)
    else:
        sys.stderr.write("Invalid environment!\n")
        options.print_help(sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
