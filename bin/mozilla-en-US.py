#!/usr/bin/env python
"""
This script creates or updates en-US repositories from Mozilla source
code to use for Mozilla product localization.

The author of the original script is Ognyan Kulev (ogi):
https://twitter.com/OgnyanKulev

This is his code:
https://bitbucket.org/ogi/mozilla-l10n-po/
"""

from __future__ import print_function
from six import text_type

import datetime
import os
import shutil
import subprocess

TARGET_REPOS = {
    'firefox': [
        'browser',
        'devtools',
        'dom',
        'netwerk',
        'security',
        'services',
        'toolkit',
    ],
    'firefox-for-android': [
        'mobile',
    ],
    'thunderbird': [
        'chat',
        'editor',
        'mail',
        'other-licenses',
    ],
    'lightning': [
        'calendar',
    ],
    'seamonkey': [
        'suite',
    ],
}


def write(text):
    timestamp = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ')
    print(timestamp + text)


def execute(command, cwd=None):
    try:
        st = subprocess.PIPE
        proc = subprocess.Popen(
            args=command, stdout=st, stderr=st, stdin=st, cwd=cwd)

        (output, error) = proc.communicate()
        code = proc.returncode
        return code, output, error

    except OSError as error:
        return -1, '', error


def pull(url, target):
    # Undo local changes
    execute(['hg', 'revert', '--all', '--no-backup'], target)

    # Pull
    code, output, error = execute(['hg', 'pull'], target)
    code, output, error = execute(['hg', 'update', '-c'], target)
    if code == 0:
        write('Repository at ' + url + ' updated.')

    # Clone
    else:
        write(text_type(error))
        write('Clone instead.')

        code, output, error = execute(['hg', 'clone', url, target])
        if code == 0:
            write('Repository at ' + url + ' cloned.')
        else:
            write(text_type(error))


def push(path):
    # Add new and remove missing
    execute(['hg', 'addremove'], path)

    # Commit
    code, output, error = execute(['hg', 'commit', '-m', 'Update'], path)
    if code != 0 and len(error):
        write(text_type(error))

    # Push
    code, output, error = execute(['hg', 'push'], path)
    if code == 0:
        write('Repository at ' + path + ' pushed.')
    elif len(error):
        write(text_type(error))

# Change working directory to where script is located
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Clone or update source repository
url = 'ssh://hg.mozilla.org/users/axel_mozilla.com/gecko-strings/'
target = 'source'
pull(url, target)

for repo in TARGET_REPOS.keys():
    ending = repo + '-central'
    url = 'ssh://hg.mozilla.org/users/m_owca.info/' + ending
    target = os.path.join('target', ending)

    # Clone or update target repository
    pull(url, target)

    # Copy folders from source to target
    for folder in TARGET_REPOS[repo]:
        origin = os.path.join('source', folder)
        destination = os.path.join('target', ending, folder)

        if os.path.exists(destination):
            shutil.rmtree(destination)

        if os.path.exists(origin):
            shutil.copytree(origin, destination)

    # Commit and push target repositories
    push(target)
