#!/usr/bin/env python
"""
This script builds up-to-date versions of Firefox Nightly language packs
from mozilla source code and localizations and makes them available
in a public repository.

A `langpacks` folder is required on the same directory level as this script,
with the following contents:
* `mozilla-central`: SOURCE_REPOSITORY checkout
* `mozilla-central/.mozconfig`: file set to reflect this folder structure, see https://developer.mozilla.org/docs/Mozilla/Creating_a_language_pack#Pre-build_steps
* `mozilla-central/langpacks/l10n`: contains L10N_REPOSITORIES checkouts
* `mozilla-central/langpacks/build`: empty folder to contain build
* `pontoon-langpacks`: TARGET_REPOSITORY checkout (you need write access)

Required libraries:
* lxml
* requests
"""


from lxml import html

import datetime
import os
import requests
import shutil
import subprocess


SOURCE_REPOSITORY = 'ssh://hg.mozilla.org/mozilla-central/'
TARGET_REPOSITORY = 'git@github.com:mathjazz/pontoon-langpacks.git'

L10N_REPOSITORIES = [{
    'url': 'ssh://hg.mozilla.org/l10n-central/{locale_code}/',
    'locales_url': 'https://hg.mozilla.org/l10n-central/'
}, {
    'url': 'ssh://hg@bitbucket.org/mozilla-l10n/{locale_code}/',
    'locales_url': 'https://api.bitbucket.org/2.0/repositories/mozilla-l10n'
}]


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

        code, output, error = execute(['hg', 'clone', url, target])
        if code == 0:
            write('Repository at ' + url + ' cloned.')
        else:
            write(str(error))


write('Building langpacks initiated.')

# Change working directory to the langpacks folder
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(os.path.join(dname, 'langpacks'))

# Update source repository
target = 'mozilla-central'
pull(SOURCE_REPOSITORY, target)

# Configure
write('Running ./mach configure. Please wait...')
execute(['sh', 'mach', 'configure'], 'mozilla-central')
write('Configuration complete.')

for repository in L10N_REPOSITORIES:
    # Update locale list
    write('Updating locale lists for {url}...'.format(url=repository['url']))
    r = requests.get(repository['locales_url'], verify=False)
    try:
        repository['locales'] = [repo['slug'] for repo in r.json()['values']]
    except ValueError:
        tree = html.fromstring(r.content)
        repository['locales'] = tree.xpath('//b/text()')
    write('Repository locale lists updated.')

    for locale in repository['locales']:
        # Update locale repositories
        url = repository['url'].format(locale_code=locale)
        target = os.path.join('mozilla-central/langpacks/l10n', locale)
        pull(url, target)

        # Build locale langpacks
        write('Building langpack for {locale}...'.format(locale=locale))
        target = 'mozilla-central/langpacks/build/browser/locales/'
        execute(['make', 'merge-' + locale, 'LOCALE_MERGEDIR=$(pwd)/mergedir'], target)
        execute(['make', 'langpack-' + locale, 'LOCALE_MERGEDIR=$(pwd)/mergedir'], target)
        write('Langpack for {locale} built!'.format(locale=locale))

write('Pushing changes to target repository...')

# Reset target repository to remote state
execute(["git", "fetch", "--all"], 'pontoon-langpacks')
code, output, error = execute(["git", "reset", "--hard", "origin"], 'pontoon-langpacks')
if code != 0:
    execute(["git", "clone", TARGET_REPOSITORY, 'pontoon-langpacks'])

# Move langpack to target repository
source = 'mozilla-central/langpacks/build/dist/linux-x86_64/xpi'
for filename in os.listdir(source):
    shutil.copyfile(
        os.path.join(source, filename),
        os.path.join('pontoon-langpacks', filename.split('.')[2] + '.xpi')
    )

# Push target repository
git_cmd = ['git', '-c', 'user.name=Mozilla Pontoon', '-c', 'user.email=pontoon@mozilla.com']
execute(git_cmd + ['add', '-A', '--'], 'pontoon-langpacks')
execute(git_cmd + ['commit', '-m', 'Update language packs'], 'pontoon-langpacks')
code, output, error = execute(["git", "push"], 'pontoon-langpacks')

if 'Everything up-to-date' in error:
    write('Nothing to commit.')
else:
    write('Changes pushed.')

write('Building langpacks complete.')
