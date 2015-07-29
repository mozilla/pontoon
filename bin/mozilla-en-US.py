#!/usr/bin/env python
"""This script creates or updates en-US repositories from Mozilla source
   code to use for Mozilla product localization."""

from __future__ import print_function

import os
import shutil
import subprocess

TARGET_REPOS = {
    'firefox-aurora': {
        'folders': [
            'browser', 'browser/branding/official', 'dom', 'netwerk',
            'security/manager', 'services/sync', 'toolkit', 'webapprt',
        ],
        'repository': 'mozilla-aurora',
    },
    'firefox-for-android-aurora': {
        'folders': ['mobile', 'mobile/android', 'mobile/android/base'],
        'repository': 'mozilla-aurora',
    },
    'thunderbird-aurora': {
        'folders': [
            'chat', 'editor/ui', 'mail',
            'other-licenses/branding/thunderbird'
        ],
        'repository': 'comm-aurora',
    },
    'lightning-aurora': {
        'folders': ['calendar'],
        'repository': 'comm-aurora',
    },
    'seamonkey-aurora': {
        'folders': ['suite'],
        'repository': 'comm-aurora',
    },
}

SOURCE_REPOS = set(v["repository"] for v in TARGET_REPOS.values())


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
    code, output, error = execute(['hg', 'pull', '-u'], target)
    if code == 0:
        print('Repository at ' + url + ' updated.')

    # Clone
    else:
        print(unicode(error))
        print('Clone instead.')

        code, output, error = execute(['hg', 'clone', url, target])
        if code == 0:
            print('Repository at ' + url + ' cloned.')
        else:
            print(unicode(error))


def push(path):
    # Add
    execute(['hg', 'add'], path)

    # Commit
    code, output, error = execute(['hg', 'commit', '-m', 'Update'], path)
    if code != 0 and len(error):
        print(unicode(error))

    # Push
    code, output, error = execute(['hg', 'push'], path)
    if code == 0:
        print('Repository at ' + path + ' pushed.')
    elif len(error):
        print(unicode(error))

# Change working directory to where script is located
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Clone or update source repositories
for repo in SOURCE_REPOS:
    base = 'ssh://hg.mozilla.org/releases/'
    url = os.path.join(base, repo)
    target = os.path.join('source', repo)
    pull(url, target)

for repo in TARGET_REPOS.keys():
    base = 'ssh://hg.mozilla.org/users/m_owca.info/'
    url = os.path.join(base, repo)
    target = os.path.join('target', repo)

    # Clone or update target repositories
    pull(url, target)

    # Copy folders from source to target
    folders = TARGET_REPOS[repo]['folders']
    source = TARGET_REPOS[repo]['repository']

    for folder in folders:
        origin = os.path.join('source', source, folder, 'locales/en-US')
        destination = os.path.join('target', repo, folder)

        if os.path.exists(destination):
            shutil.rmtree(destination)

        shutil.copytree(origin, destination)

    # Commit and push target repositories
    push(target)
