import json
import logging
import os
import re
import requests
import traceback

from django.conf import settings
from django.contrib.auth.models import Permission
from django.http import HttpResponse
from django.utils.translation import trans_real
from translate.filters import checks
from translate.storage import base as storage_base
from translate.storage.placeables import base, general, parse
from translate.storage.placeables.interfaces import BasePlaceable
from translate.lang import data as lang_data


log = logging.getLogger('pontoon')


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


def get_project_locale_from_request(request, locales):
    """Get Pontoon locale from Accept-language request header."""

    header = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    accept = trans_real.parse_accept_lang_header(header)

    for a in accept:
        try:
            return locales.get(code__iexact=a[0]).code
        except:
            continue


def mark_placeables(text):
    """Wrap placeables to easily distinguish and manipulate them.

    Source: http://bit.ly/1yQOC9B
    """

    class TabEscapePlaceable(base.Ph):
        """Placeable handling tab escapes."""
        istranslatable = False
        regex = re.compile(r'\t')
        parse = classmethod(general.regex_parse)

    class EscapePlaceable(base.Ph):
        """Placeable handling escapes."""
        istranslatable = False
        regex = re.compile(r'\\')
        parse = classmethod(general.regex_parse)

    class SpacesPlaceable(base.Ph):
        """Placeable handling spaces."""
        istranslatable = False
        regex = re.compile('^ +| +$|[\r\n\t] +| {2,}')
        parse = classmethod(general.regex_parse)

    PARSERS = [
        TabEscapePlaceable.parse,
        EscapePlaceable.parse,
        general.NewlinePlaceable.parse,
        # The spaces placeable can match '\n  ' and mask the newline,
        # so it has to come later.
        SpacesPlaceable.parse,
        general.XMLTagPlaceable.parse,
        general.AltAttrPlaceable.parse,
        general.XMLEntityPlaceable.parse,
        general.PythonFormattingPlaceable.parse,
        general.JavaMessageFormatPlaceable.parse,
        general.FormattingPlaceable.parse,
        # The Qt variables can consume the %1 in %1$s which will mask a printf
        # placeable, so it has to come later.
        general.QtFormattingPlaceable.parse,
        general.UrlPlaceable.parse,
        general.FilePlaceable.parse,
        general.EmailPlaceable.parse,
        general.CapsPlaceable.parse,
        general.CamelCasePlaceable.parse,
        general.OptionPlaceable.parse,
        general.PunctuationPlaceable.parse,
        general.NumberPlaceable.parse,
    ]

    TITLES = {
        'TabEscapePlaceable': "Escaped tab",
        'EscapePlaceable': "Escaped sequence",
        'SpacesPlaceable': "Unusual space in string",
        'AltAttrPlaceable': "'alt' attribute inside XML tag",
        'NewlinePlaceable': "New-line",
        'NumberPlaceable': "Number",
        'QtFormattingPlaceable': "Qt string formatting variable",
        'PythonFormattingPlaceable': "Python string formatting variable",
        'JavaMessageFormatPlaceable': "Java Message formatting variable",
        'FormattingPlaceable': "String formatting variable",
        'UrlPlaceable': "URI",
        'FilePlaceable': "File location",
        'EmailPlaceable': "Email",
        'PunctuationPlaceable': "Punctuation",
        'XMLEntityPlaceable': "XML entity",
        'CapsPlaceable': "Long all-caps string",
        'CamelCasePlaceable': "Camel case string",
        'XMLTagPlaceable': "XML tag",
        'OptionPlaceable': "Command line option",
    }

    output = u""

    # Get a flat list of placeables and StringElem instances
    flat_items = parse(text, PARSERS).flatten()

    for item in flat_items:

        # Placeable: mark
        if isinstance(item, BasePlaceable):
            class_name = item.__class__.__name__
            placeable = unicode(item)

            # CSS class used to mark the placeable
            css = {
                'TabEscapePlaceable': "escape ",
                'EscapePlaceable': "escape ",
                'SpacesPlaceable': "space ",
                'NewlinePlaceable': "escape ",
            }.get(class_name, "")

            title = TITLES.get(class_name, "Unknown placeable")

            spaces = '&nbsp;' * len(placeable)
            if not placeable.startswith(' '):
                spaces = placeable[0] + '&nbsp;' * (len(placeable) - 1)

            # Correctly render placeables in translation editor
            content = {
                'TabEscapePlaceable': u'\\t',
                'EscapePlaceable': u'\\\\',
                'SpacesPlaceable': spaces,
                'NewlinePlaceable': {
                    u'\r\n': u'\\r\\n<br/>\n',
                    u'\r': u'\\r<br/>\n',
                    u'\n': u'\\n<br/>\n',
                }.get(placeable),
                'XMLEntityPlaceable': placeable.replace('&', '&amp;'),
                'XMLTagPlaceable':
                    placeable.replace('<', '&lt;').replace('>', '&gt;'),
            }.get(class_name, placeable)

            output += ('<mark class="%splaceable" title="%s">%s</mark>') \
                % (css, title, content)

        # Not a placeable: skip
        else:
            output += unicode(item).replace('<', '&lt;').replace('>', '&gt;')

    return output


def quality_check(original, string, locale, ignore):
    """Check for obvious errors like blanks and missing interpunction."""

    if not ignore:
        original = lang_data.normalized_unicode(original)
        string = lang_data.normalized_unicode(string)

        unit = storage_base.TranslationUnit(original)
        unit.target = string
        checker = checks.StandardChecker(
            checkerconfig=checks.CheckerConfig(targetlanguage=locale.code))

        warnings = checker.run_filters(unit)
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
            }), content_type='application/json')


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


def first(collection, test, default=None):
    """
    Return the first item that, when passed to the given test function,
    returns True. If no item passes the test, return the default value.
    """
    return next((c for c in collection if test(c)), default)


def match_attr(collection, **attributes):
    """
    Return the first item that has matching values for the given
    attributes, or None if no item is found to match.
    """
    return first(
        collection,
        lambda i: all(getattr(i, attrib) == value
                      for attrib, value in attributes.items()),
        default=None
    )
