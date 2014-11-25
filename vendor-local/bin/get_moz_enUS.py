#!/Library/WebServer/Documents/pontoon/env/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Virtaal.
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

import os
import shutil
from ConfigParser import ConfigParser, NoSectionError


srccheckout = "mozilla"
l10ncheckout = "l10n"
product = "browser"
verbose = False


def path_neutral(path):
    """Convert a path specified using Unix path seperator into a
    platform path"""
    newpath = ""
    for seg in path.split("/"):
        if not seg:
            newpath = os.sep
        newpath = os.path.join(newpath, seg)
    return newpath


def process_l10n_ini(inifile):
    """Read a Mozilla l10n.ini file and process it to find the localisation
    files needed by a project"""

    l10n = ConfigParser()
    l10n.readfp(open(path_neutral(inifile)))
    l10n_ini_path = os.path.dirname(inifile)

    for dir in l10n.get('compare', 'dirs').split():
        frompath = os.path.join(l10n_ini_path, l10n.get('general', 'depth'),
                                dir, 'locales', 'en-US')
        topath = os.path.join(l10ncheckout, 'en-US', dir)
        if not os.path.exists(frompath):
            if verbose:
                print("[Missing source]: %s" % frompath)
            continue
        if os.path.exists(topath):
            if verbose:
                print("[Existing target]: %s" % topath)
            continue
        if verbose:
            print('%s -> %s' % (frompath, topath))
        try:
            shutil.copytree(frompath, topath)
        except OSError as e:
            print(e)

    try:
        for include in l10n.options('includes'):
            include_ini = os.path.join(
                l10n_ini_path, l10n.get('general', 'depth'),
                l10n.get('includes', include)
            )
            if os.path.isfile(include_ini):
                process_l10n_ini(include_ini)
    except TypeError:
        pass
    except NoSectionError:
        pass


def create_option_parser():
    from argparse import ArgumentParser
    p = ArgumentParser()

    p.add_argument(
        '-s', '--src',
        type=str,
        dest='srcdir',
        default='mozilla',
        help='The directory containing the Mozilla l10n sources.'
    )
    p.add_argument(
        '-d', '--dest',
        type=str,
        dest='destdir',
        default='l10n',
        help='The destination directory to copy the en-US locale files to.'
    )
    p.add_argument(
        '-p', '--mozproduct',
        type=str,
        dest='mozproduct',
        default='browser',
        help='The Mozilla product name.'
    )
    p.add_argument(
        '--delete-dest',
        dest='deletedest',
        default=False,
        action='store_true',
        help='Delete the destination directory (if it exists).'
    )

    p.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Be more noisy'
    )

    return p

if __name__ == '__main__':
    args = create_option_parser().parse_args()
    srccheckout = args.srcdir
    l10ncheckout = args.destdir
    product = args.mozproduct

    enUS_dir = os.path.join(l10ncheckout, 'en-US')
    if args.deletedest and os.path.exists(enUS_dir):
        shutil.rmtree(enUS_dir)
    if not os.path.exists(enUS_dir):
        os.makedirs(enUS_dir)

    if args.verbose:
        print("%s -s %s -d %s -p %s -v %s" %
              (__file__, srccheckout, l10ncheckout, product,
               args.deletedest and '--delete-dest' or ''))
    product_ini = os.path.join(srccheckout, product, 'locales', 'l10n.ini')
    if not os.path.isfile(product_ini):
        # Done for Fennec
        product_ini = os.path.join(srccheckout, 'locales', 'l10n.ini')
    process_l10n_ini(product_ini)
