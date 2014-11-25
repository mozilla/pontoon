#!/Library/WebServer/Documents/pontoon/env/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Create a XPI language pack from Mozilla sources and translated l10n files.
This script has only been tested with Firefox 3.1 beta sources.

(Basically the process described at
https://developer.mozilla.org/en/Creating_a_Language_Pack)

Example usage::

    buildxpi.py -L /path/to/l10n -s /path/to/mozilla-central -o /path/to/xpi_output af ar

- "/path/to/l10n" is the path to a the parent directory of the "af" and "ar"
  directories containing the Afrikaans and Arabic translated files.
- "/path/to/mozilla-central" is the path to the Firefox sources checked out
  from Mercurial. Note that --mozproduct is not specified, because the default
  is "browser". For Thunderbird (>=3.0) it should be "/path/to/comm-central"
  and "--mozproduct mail" should be specified, although this is not yet
  working.
- "/path/to/xpi_output" is the path to the output directory.
- "af ar" are the languages (Afrikaans and Arabic in this case) to build
  language packs for.

NOTE: The .mozconfig in Firefox source directory gets backed up,
overwritten and replaced.
"""

import logging
import os
import re
from glob import glob
from shutil import move, rmtree
from subprocess import PIPE, CalledProcessError, Popen
from tempfile import mkdtemp


logger = logging.getLogger(__name__)


class RunProcessError(CalledProcessError):
    """Subclass of CalledProcessError exception with custom message strings
    """
    _default_message = "Command '%s' returned exit status %d"

    def __init__(self, message=None, **kwargs):
        """Use and strip string message='' from kwargs"""
        self._message = message or self._default_message
        super(RunProcessError, self).__init__(**kwargs)

    def __str__(self):
        """Format exception message string (avoiding TypeErrors)"""
        output = ''
        message = self._message
        if message.count('%') != 2:
            output += message + '\n'
            message = self._default_message

        output += message % (self.cmd, self.returncode)
        return output


def run(cmd, expected_status=0, fail_msg=None, stdout=-1, stderr=-1):
    """Run a command
    """
    # Default is to capture (and log) std{out,error} unless run as script
    if __name__ == '__main__' or logger.getEffectiveLevel() == logging.DEBUG:
        std = None
    else:
        std = PIPE

    if stdout == -1:
        stdout = std
    if stderr == -1:
        stderr = std

    cmdstring = isinstance(str, basestring) and cmd or ' '.join(cmd)
    logger.debug('>>> %s $ %s', os.getcwd(), cmdstring)
    p = Popen(cmd, stdout=stdout, stderr=stderr)
    (output, error) = p.communicate()
    cmd_status = p.wait()

    if stdout == PIPE:
        if cmd_status != expected_status:
            logger.info('%s', output)
    elif stderr == PIPE:
        logger.warning('%s', error)

    if cmd_status != expected_status:
        raise RunProcessError(returncode=cmd_status, cmd=cmdstring,
                              message=fail_msg)
    return cmd_status


def build_xpi(l10nbase, srcdir, outputdir, langs, product, delete_dest=False,
              soft_max_version=False):
    MOZCONFIG = os.path.join(srcdir, '.mozconfig')
    # Backup existing .mozconfig if it exists
    backup_name = ''
    if os.path.exists(MOZCONFIG):
        backup_name = MOZCONFIG + '.tmp'
        os.rename(MOZCONFIG, backup_name)

    # Create a temporary directory for building
    builddir = mkdtemp('', 'buildxpi')

    try:
        # Create new .mozconfig
        content = """
ac_add_options --disable-compile-environment
ac_add_options --disable-gstreamer
ac_add_options --disable-ogg
ac_add_options --disable-opus
ac_add_options --disable-webrtc
ac_add_options --disable-wave
ac_add_options --disable-webm
ac_add_options --disable-alsa
ac_add_options --disable-pulseaudio
ac_add_options --disable-libjpeg-turbo
mk_add_options MOZ_OBJDIR=%(builddir)s
ac_add_options --with-l10n-base=%(l10nbase)s
ac_add_options --enable-application=%(product)s
""" % \
            {
                'builddir': builddir,
                'l10nbase': l10nbase,
                'product': product
            }

        mozconf = open(MOZCONFIG, 'w').write(content)

        # Try to make sure that "environment shell" is defined
        # (python/mach/mach/mixin/process.py)
        if not any (var in os.environ
                    for var in ('SHELL', 'MOZILLABUILD', 'COMSPEC')):
            os.environ['SHELL'] = '/bin/sh'

        # Start building process.
        # See https://developer.mozilla.org/en/Creating_a_Language_Pack for
        # more details.
        olddir = os.getcwd()
        os.chdir(srcdir)
        run(['make', '-f', 'client.mk', 'configure'],
            fail_msg="Build environment error - "
                     "check logs, fix errors, and try again")

        os.chdir(builddir)
        run(['make', '-C', 'config'],
            fail_msg="Unable to successfully configure build for XPI!")

        moz_app_version = []
        if soft_max_version:
            version = open(os.path.join(srcdir, product, 'config', 'version.txt')).read().strip()
            version = re.sub(r'(^[0-9]*\.[0-9]*).*', r'\1.*', version)
            moz_app_version = ['MOZ_APP_MAXVERSION=%s' % version]
        run(['make', '-C', os.path.join(product, 'locales')] +
            ['langpack-%s' % lang for lang in langs] + moz_app_version,
            fail_msg="Unable to successfully build XPI!")

        destfiles = []
        for lang in langs:
            xpiglob = glob(
                os.path.join(
                    builddir,
                    product == 'mail' and 'mozilla' or '',
                    'dist',
                    '*',
                    'xpi',
                    '*.%s.langpack.xpi' % lang
                )
            )[0]
            filename = os.path.split(xpiglob)[1]
            destfile = os.path.join(outputdir, filename)
            destfiles.append(destfile)
            if delete_dest:
                if os.path.isfile(destfile):
                    os.unlink(destfile)
            move(xpiglob, outputdir)

    finally:
        os.chdir(olddir)
        # Clean-up
        rmtree(builddir)
        if backup_name:
            os.remove(MOZCONFIG)
            os.rename(backup_name, MOZCONFIG)

    return destfiles


def create_option_parser():
    from argparse import ArgumentParser
    usage = 'Usage: buildxpi.py [<options>] <lang> [<lang2> ...]'
    p = ArgumentParser(usage=usage)

    p.add_argument(
        '-L', '--l10n-base',
        type=str,
        dest='l10nbase',
        default='l10n',
        help='The directory containing the <lang> subdirectory.'
    )
    p.add_argument(
        '-o', '--output-dir',
        type=str,
        dest='outputdir',
        default='.',
        help='The directory to copy the built XPI to (default: current directory).'
    )
    p.add_argument(
        '-p', '--mozproduct',
        type=str,
        dest='mozproduct',
        default='browser',
        help='The Mozilla product name (default: "browser").'
    )
    p.add_argument(
        '-s', '--src',
        type=str,
        dest='srcdir',
        default='mozilla',
        help='The directory containing the Mozilla l10n sources.'
    )
    p.add_argument(
        '-d', '--delete-dest',
        dest='delete_dest',
        action='store_true',
        default=False,
        help='Delete output XPI if it already exists.'
    )

    p.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Be more noisy'
    )

    p.add_argument(
        '--soft-max-version',
        dest='soft_max_version',
        action='store_true',
        default=False,
        help='Override a fixed max version with one to cover the whole cycle '
             'e.g. 24.0a1 becomes 24.0.*'
    )

    p.add_argument(
        "langs",
        nargs="+"
    )

    return p

if __name__ == '__main__':
    args = create_option_parser().parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    build_xpi(
        l10nbase=os.path.abspath(args.l10nbase),
        srcdir=os.path.abspath(args.srcdir),
        outputdir=os.path.abspath(args.outputdir),
        langs=args.langs,
        product=args.mozproduct,
        delete_dest=args.delete_dest,
        soft_max_version=args.soft_max_version
    )
