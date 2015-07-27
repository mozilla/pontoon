#!/usr/bin/env python
"""This script creates or updates en-US repository from Mozilla source
   code to use for Mozilla product localization."""

import os
import shutil
import subprocess


CONFIG = {
    'sources': ['comm-aurora', 'mozilla-aurora'],
    'target': 'mozilla-aurora',
    'folders': [
        'browser', 'browser/branding/official', 'dom', 'netwerk',
        'security/manager', 'services/sync', 'toolkit', 'webapprt',
        'mobile', 'mobile/android', 'mobile/android/base',
        'chat', 'editor/ui', 'mail', 'other-licenses/branding/thunderbird',
        'calendar',
        'suite',
    ],
}


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

    code, output, error = execute(['hg', 'pull', '-u'], target)
    if code == 0:
        print('Repository at ' + url + ' updated.')

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
for repo in CONFIG['sources']:
    base = 'ssh://hg.mozilla.org/releases/'
    url = os.path.join(base, repo)
    target = os.path.join('source', repo)
    pull(url, target)

# Clone or update target repository
repo = CONFIG['target']
base = 'ssh://hg.mozilla.org/users/m_owca.info/'
url = os.path.join(base, repo)
target = os.path.join('target', repo)
pull(url, target)

# Copy folders from source to target
for folder in CONFIG['folders']:
    for source in CONFIG['sources']:
        origin = os.path.join('source', source, folder, 'locales/en-US')
        destination = os.path.join('target', repo, folder)

        if os.path.exists(origin):
            if os.path.exists(destination):
                shutil.rmtree(destination)

            shutil.copytree(origin, destination)

# Commit and push target repository
push(target)
