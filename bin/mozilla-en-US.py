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

import datetime
import os
import shutil
import subprocess

TARGET_REPOS = {
    'firefox': {
        'folders': [
            'browser', 'browser/branding/official',
            'browser/extensions/pocket',
            'devtools/client', 'devtools/shared',
            'dom', 'netwerk', 'security/manager',
            'services/sync', 'toolkit', 'webapprt',
        ],
        'source': 'mozilla',
    },
    'firefox-for-android': {
        'folders': ['mobile', 'mobile/android', 'mobile/android/base'],
        'source': 'mozilla',
    },
    'thunderbird': {
        'folders': [
            'chat', 'editor/ui', 'mail',
            'other-licenses/branding/thunderbird'
        ],
        'source': 'comm',
    },
    'lightning': {
        'folders': ['calendar'],
        'source': 'comm',
    },
    'seamonkey': {
        'folders': ['suite'],
        'source': 'comm',
    },
}

SOURCE_REPOS = set(v["source"] for v in TARGET_REPOS.values())


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
        write(unicode(error))
        write('Clone instead.')

        code, output, error = execute(['hg', 'clone', url, target])
        if code == 0:
            write('Repository at ' + url + ' cloned.')
        else:
            write(unicode(error))


def push(path):
    # Add new and remove missing
    execute(['hg', 'addremove'], path)

    # Commit
    code, output, error = execute(['hg', 'commit', '-m', 'Update'], path)
    if code != 0 and len(error):
        write(unicode(error))

    # Push
    code, output, error = execute(['hg', 'push'], path)
    if code == 0:
        write('Repository at ' + path + ' pushed.')
    elif len(error):
        write(unicode(error))

# Change working directory to where script is located
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

for channel in ['aurora', 'beta']:
    for repo in SOURCE_REPOS:
        ending = repo + '-' + channel
        url = 'ssh://hg.mozilla.org/releases/' + ending
        target = os.path.join('source', ending)

        # Clone or update source repositories
        pull(url, target)

    for repo in TARGET_REPOS.keys():
        ending = repo + '-' + channel
        url = 'ssh://hg.mozilla.org/users/m_owca.info/' + ending
        target = os.path.join('target', ending)

        # Clone or update target repositories
        pull(url, target)

        # Copy folders from source to target
        folders = TARGET_REPOS[repo]['folders']
        source = TARGET_REPOS[repo]['source'] + '-' + channel

        for folder in folders:
            origin = os.path.join('source', source, folder, 'locales/en-US')
            destination = os.path.join('target', ending, folder)

            if os.path.exists(destination):
                shutil.rmtree(destination)

        # Needed temporarily because devtools aren't moved in beta yet
        if os.path.exists(origin):
            shutil.copytree(origin, destination)

        # Commit and push target repositories
        push(target)
