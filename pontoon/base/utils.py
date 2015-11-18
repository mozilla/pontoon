import codecs
import json
import logging
import os
import re
import requests
import uuid
from datetime import datetime

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import trans_real

from translate.filters import checks
from translate.storage import base as storage_base
from translate.storage.placeables import base, general, parse
from translate.storage.placeables.interfaces import BasePlaceable
from translate.lang import data as lang_data


log = logging.getLogger('pontoon')


def get_project_locale_from_request(request, locales):
    """Get Pontoon locale from Accept-language request header."""

    header = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    accept = trans_real.parse_accept_lang_header(header)

    for a in accept:
        try:
            return locales.get(code__iexact=a[0]).code
        except:
            continue


class NewlineEscapePlaceable(base.Ph):
    """Placeable handling newline escapes."""
    istranslatable = False
    regex = re.compile(r'\\n')
    parse = classmethod(general.regex_parse)


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


def mark_placeables(text):
    """Wrap placeables to easily distinguish and manipulate them.

    Source: http://bit.ly/1yQOC9B
    """

    PARSERS = [
        NewlineEscapePlaceable.parse,
        TabEscapePlaceable.parse,
        EscapePlaceable.parse,
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
        'NewlineEscapePlaceable': "Escaped newline",
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
                'EscapePlaceable': u'\\',
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


def aware_datetime(*args, **kwargs):
    """Return an aware datetime using Django's configured timezone."""
    return timezone.make_aware(datetime(*args, **kwargs))


def extension_in(filename, extensions):
    """
    Check if the extension for the given filename is in the list of
    allowed extensions. Uses os.path.splitext rules for getting the
    extension.
    """
    filename, extension = os.path.splitext(filename)
    if extension and extension[1:] in extensions:
        return True
    else:
        return False


def get_object_or_none(model, *args, **kwargs):
    """
    Get an instance of the given model, returning None instead of
    raising an error if an instance cannot be found.
    """
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def require_AJAX(f):
    """
    AJAX request required decorator
    """
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest('Bad Request: Request must be AJAX')
        return f(request, *args, **kwargs)
    return wrap


def _download_file(prefixes, dirnames, relative_path):
    for prefix in prefixes:
        for dirname in dirnames:
            url = os.path.join(prefix.format(locale_code=dirname), relative_path)
            r = requests.get(url, stream=True)
            if not r.ok:
                continue

            filename = str(uuid.uuid4()) + os.path.splitext(url)[1]
            with codecs.open(filename, 'wb') as destination:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        destination.write(chunk)
            return filename


def get_download_content(slug, code, relative_path):
    """
    Get content of the file to be downloaded.

    :param str slug: Project slug.
    :param str code: Locale code.
    :param str relative_path: Resource path.
    """
    # Avoid circular import; someday we should refactor to avoid.
    from pontoon.sync import formats
    from pontoon.sync.vcs_models import VCSProject
    from pontoon.base.models import (
        Entity,
        Locale,
        Project,
        Resource,
        Subpage,
    )

    # Check if relative path is actually subpage name
    try:
        subpage = Subpage.objects.get(project__slug=slug, name=relative_path)
        relative_path = subpage.resources.first().path
    except Subpage.DoesNotExist:
        pass

    project = get_object_or_404(Project, slug=slug)
    locale = get_object_or_404(Locale, code__iexact=code)
    resource = get_object_or_404(Resource, project__slug=slug, path=relative_path)

    # Get locale file
    locale_prefixes = (
        project.repositories.filter(permalink_prefix__contains='{locale_code}')
        .values_list('permalink_prefix', flat=True)
        .distinct()
    )
    dirnames = set([locale.code, locale.code.replace('-', '_')])
    locale_path = _download_file(locale_prefixes, dirnames, relative_path)
    if not locale_path:
        return None

    # Get source file if needed
    source_path = None
    if resource.is_asymmetric:
        source_prefixes = (
            project.repositories
            .values_list('permalink_prefix', flat=True)
            .distinct()
        )
        dirnames = VCSProject.SOURCE_DIR_NAMES
        source_path = _download_file(source_prefixes, dirnames, relative_path)
        if not source_path:
            return None

    # Update file from database
    resource_file = formats.parse(locale_path, source_path)
    entities_dict = {}
    entities_qs = Entity.objects.filter(
        changedentitylocale__locale=locale,
        resource__project=project,
        resource__path=relative_path,
        obsolete=False
    )

    for e in entities_qs:
        entities_dict[e.key] = e.translation_set.filter(approved=True, locale=locale)

    for vcs_translation in resource_file.translations:
        key = vcs_translation.key
        if key in entities_dict:
            vcs_translation.update_from_db(entities_dict[key])

    resource_file.save(locale)

    # Read download content
    with codecs.open(locale_path, 'r', 'utf-8') as f:
        content = f.read()

    # Remove temporary files
    os.remove(locale_path)
    if source_path:
        os.remove(source_path)

    return content, relative_path
