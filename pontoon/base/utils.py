
import commonware.log
import json
import requests

from django.conf import settings
from django.contrib.auth.models import Permission
from django.http import HttpResponse
from translate.filters import checks


log = commonware.log.getLogger('pontoon')


def add_can_localize(user):

    email = user.email
    log.debug(email)

    # Grant permission to Mozilla localizers
    url = "https://mozillians.org/api/v1/users/"
    payload = {
        "app_name": "pontoon",
        "app_key": settings.MOZILLIANS_API_KEY,
        "email": email,
        "is_vouched": True,
        "groups": "localization",
    }

    try:
        response = requests.get(url, params=payload)
        mozillians = response.json()["objects"]

        if len(mozillians) > 0:
            can_localize = Permission.objects.get(codename="can_localize")
            user.user_permissions.add(can_localize)
            log.debug("Permission can_localize set.")

            # Fallback if profile does not allow accessing data
            user.first_name = mozillians[0].get("full_name", email)
            user.save()

    except Exception as e:
        log.debug(e)
        log.debug("Is your MOZILLIANS_API_KEY set?")
        user.save()


def quality_check(original, string, ignore):
    """Check for obvious errors like blanks and missing interpunction."""

    if not ignore:
        warnings = checks.runtests(original, string)
        if warnings:

            # https://github.com/translate/pootle/
            check_names = {
                'accelerators': 'Accelerators',
                'acronyms': 'Acronyms',
                'blank': 'Blank',
                'brackets': 'Brackets',
                'compendiumconflicts': 'Compendium conflict',
                'credits': 'Translator credits',
                'doublequoting': 'Double quotes',
                'doublespacing': 'Double spaces',
                'doublewords': 'Repeated word',
                'emails': 'E-mail',
                'endpunc': 'Ending punctuation',
                'endwhitespace': 'Ending whitespace',
                'escapes': 'Escapes',
                'filepaths': 'File paths',
                'functions': 'Functions',
                'gconf': 'GConf values',
                'kdecomments': 'Old KDE comment',
                'long': 'Long',
                'musttranslatewords': 'Must translate words',
                'newlines': 'Newlines',
                'nplurals': 'Number of plurals',
                'notranslatewords': 'Don\'t translate words',
                'numbers': 'Numbers',
                'options': 'Options',
                'printf': 'printf()',
                'puncspacing': 'Punctuation spacing',
                'purepunc': 'Pure punctuation',
                'sentencecount': 'Number of sentences',
                'short': 'Short',
                'simplecaps': 'Simple capitalization',
                'simpleplurals': 'Simple plural(s)',
                'singlequoting': 'Single quotes',
                'startcaps': 'Starting capitalization',
                'startpunc': 'Starting punctuation',
                'startwhitespace': 'Starting whitespace',
                'tabs': 'Tabs',
                'unchanged': 'Unchanged',
                'untranslated': 'Untranslated',
                'urls': 'URLs',
                'validchars': 'Valid characters',
                'variables': 'Placeholders',
                'xmltags': 'XML tags',
            }

            warnings_array = []
            for key in warnings.keys():
                warning = check_names.get(key, key)
                warnings_array.append(warning)

            return HttpResponse(json.dumps({
                'warnings': warnings_array,
            }), mimetype='application/json')


def req(method, project, resource, locale,
        username, password, payload=False):
    """
    Make request to Transifex server.

    Args:
        method: Request method
        project: Transifex project name
        resource: Transifex resource name
        locale: Locale code
        username: Transifex username
        password: Transifex password
        payload: Data to be sent to the server
    Returns:
        A server response or error message.
    """
    url = os.path.join(
        'https://www.transifex.com/api/2/project/', project,
        'resource', resource, 'translation', locale, 'strings')

    try:
        if method == 'get':
            r = requests.get(
                url + '?details', auth=(username, password), timeout=10)
        elif method == 'put':
            r = requests.put(url, auth=(username, password), timeout=10,
                             data=json.dumps(payload),
                             headers={'content-type': 'application/json'})
        log.debug(r.status_code)
        if r.status_code == 401:
            return "authenticate"
        elif r.status_code != 200:
            log.debug("Response not 200")
            return "error"
        return r
    # Network problem (DNS failure, refused connection, etc.)
    except requests.exceptions.ConnectionError as e:
        log.debug('ConnectionError: ' + str(e))
        return "error"
    # Invalid HTTP response
    except requests.exceptions.HTTPError as e:
        log.debug('HTTPError: ' + str(e))
        return "error"
    # A valid URL is required
    except requests.exceptionsURLRequired as e:
        log.debug('URLRequired: ' + str(e))
        return "error"
    # Request times out
    except requests.exceptions.Timeout as e:
        log.debug('Timeout: ' + str(e))
        return "error"
    # Request exceeds the number of maximum redirections
    except requests.exceptions.TooManyRedirects as e:
        log.debug('TooManyRedirects: ' + str(e))
        return "error"
    # Ambiguous exception occurres
    except requests.exceptions.RequestException as e:
        log.debug('RequestException: ' + str(e))
        return "error"
    except Exception:
        log.debug('Generic exception: ' + traceback.format_exc())
        return "error"
