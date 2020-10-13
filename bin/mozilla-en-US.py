#!/usr/bin/env python
"""
This script creates or updates en-US repositories from Mozilla source
code to use for Mozilla product localization.

The author of the original script is Ognyan Kulev (ogi):
https://twitter.com/OgnyanKulev

This is his code:
https://bitbucket.org/ogi/mozilla-l10n-po/
"""

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
        write(str(error))
        write('Clone instead.')

        # Clean up target directory on a failed pull, so that it's empty for a clone
        command = ["rm", "-rf", target]
        code, output, error = execute(command)

        code, output, error = execute(['hg', 'clone', url, target])
        if code == 0:
            write('Repository at ' + url + ' cloned.')
        else:
            write(str(error))

    return code


def push(path):
    # Add new and remove missing
    execute(['hg', 'addremove'], path)

    # Commit
    code, output, error = execute(['hg', 'commit', '-m', 'Update'], path)
    if code != 0 and len(error):
        write(str(error))

    # Push
    code, output, error = execute(['hg', 'push'], path)
    if code == 0:
        write('Repository at ' + path + ' pushed.')
    elif len(error):
        write(str(error))


def quit_or_pass(code):
    # In case of a non-zero error code, quit early (bug 1475603)
    if code != 0:
        quit(code)


# Change working directory to where script is located
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Clone or update source repository
url = 'https://hg.mozilla.org/l10n/gecko-strings/'
target = 'source'
code = pull(url, target)

quit_or_pass(code)

for repo in TARGET_REPOS.keys():
    ending = repo + '-central'
    url = 'ssh://hg.mozilla.org/users/m_owca.info/' + ending
    target = os.path.join('target', ending)

    # Clone or update target repository
    code = pull(url, target)

    quit_or_pass(code)

    # Prune all subdirectories in target repository in case they get removed from source
    for subdir in os.listdir(target):
        if not subdir.startswith('.'):
            shutil.rmtree(os.path.join(target, subdir))

    # Copy folders from source to target
    for folder in TARGET_REPOS[repo]:
        origin = os.path.join('source', folder)
        destination = os.path.join('target', ending, folder)

        if os.path.exists(origin):
            shutil.copytree(origin, destination)

    # Commit and push target repositories
    push(target)
