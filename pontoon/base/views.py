
import base64
import configparser
import codecs
import commonware
import datetime
import fnmatch
import json
import os
import polib
import requests
import silme.core
import silme.format.properties
import StringIO
import traceback
import urllib
import zipfile
import hashlib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator

from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
)

from django.shortcuts import render
from django.templatetags.static import static
from django.utils.datastructures import MultiValueDictKeyError
from django_browserid import verify as browserid_verify
from django_browserid import get_audience

from pontoon.base.models import (
    Locale,
    Project,
    Subpage,
    Entity,
    Translation,
    UserProfile
)

from pontoon.base.utils.permissions import add_can_localize
from session_csrf import anonymous_csrf_exempt


log = commonware.log.getLogger('pontoon')


def home(request, template='home.html'):
    """Home view."""
    log.debug("Home view.")

    data = {
        'locales': Locale.objects.all(),
        'projects': Project.objects.filter(
            pk__in=Entity.objects.values('project'))
    }

    translate_error = request.session.pop('translate_error', {})
    locale = translate_error.get('locale')
    project = translate_error.get('project')

    if locale is not None:
        data['locale_code'] = locale

    if project is not None:
        data['project'] = project

    return render(request, template, data)


def handle_error(request):
    """
    A view to handle errors during loading a website for translation
    by Pontoon. This view is bound with a generic URL which can
    be called from Pontoon's javascript with appropriate GET parameters
    and the page will get redirected to the home page showing proper
    error messages, url and locale.
    """
    messages.error(request, request.GET.get('error', ''))
    request.session['translate_error'] = {
        'locale': request.GET.get('locale'),
        'project': request.GET.get('project')
    }
    return HttpResponseRedirect(reverse('pontoon.home'))


def translate_site(request, locale, url, template='translate.html'):
    """Translate view: site."""
    log.debug("Translate view: site.")

    # Validate URL
    # Default configuration of Apache doesn't allow encoded slashes in URLs
    # https://github.com/mozilla/playdoh/issues/143
    url = urllib.unquote(url)
    log.debug("URL: " + url)
    validate = URLValidator()

    try:
        validate(url)
    except ValidationError as e:
        log.debug(e)
        request.session['translate_error'] = {
            'locale': locale,
        }
        messages.error(request, "Oops, this is not a valid URL.")
        return HttpResponseRedirect(reverse('pontoon.home'))

    # Validate locale
    log.debug("Locale: " + locale)
    try:
        l = Locale.objects.get(code=locale)
    except Locale.DoesNotExist:
        messages.error(request, "Oops, locale is not supported.")
        request.session['translate_error'] = {
            'locale': locale,
        }
        return HttpResponseRedirect(reverse('pontoon.home'))

    data = {
        'locale_code': locale,
        'locales': Locale.objects.all(),
        'project_url': url,
        'project': {},
        'projects': Project.objects.filter(
            pk__in=Entity.objects.values('project'))
    }

    try:
        p = Project.objects.get(url=url)
        try:
            # Select project and a subpage
            s = Subpage.objects.get(url=url)
            page = s.name
        except Subpage.DoesNotExist:
            # Select project, subpage does not exist
            page = None
    except Project.DoesNotExist:
        try:
            # Select subpage and its project
            s = Subpage.objects.get(url=url)
            p = s.project
            page = s.name
        except Subpage.DoesNotExist:
            # Project not stored in the DB
            data['project']['locales'] = Locale.objects.all()
            return render(request, template, data)

    # Check if user authenticated and has sufficient privileges
    if not p.name == 'Testpilot':
        if not request.user.is_authenticated():
            messages.error(request, "You need to sign in first.")
            return HttpResponseRedirect(reverse('pontoon.home'))

    # Project stored in the DB, add more data
    if page is None:
        return HttpResponseRedirect(reverse(
            'pontoon.translate.project',
            kwargs={'locale': locale, 'slug': p.slug}))
    else:
        return HttpResponseRedirect(reverse(
            'pontoon.translate.project.page',
            kwargs={'locale': locale, 'slug': p.slug, 'page': page}))


def _get_translation(entity, locale):
    """Get translation of given entity to given locale."""

    translations = Translation.objects.filter(entity=entity, locale=locale)

    if len(translations) > 0:
        try:
            t = translations.get(approved=True)
            return t
        except Translation.DoesNotExist:
            latest = translations.order_by("date").reverse()[0]
            return latest
    else:
        return Translation()


def _get_entities(project, locale, page=None):
    """Load all project entities and translations."""
    log.debug("Load all project entities and translations.")

    entities = Entity.objects.filter(project=project)
    if page is not None and entities[0].source != '':
        entities = entities.filter(source__endswith=page + '.properties')

    entities_array = []
    for e in entities:
        translation = _get_translation(entity=e, locale=locale)

        obj = {
            "original": e.string,
            "original_plural": e.string_plural,
            "comment": e.comment,
            "key": e.key,
            "pk": e.pk,
            "translation": translation.string,
            "approved": translation.approved,
        }

        entities_array.append(obj)
    return entities_array


def translate_project(request, locale, slug, page=None,
                      template='translate.html'):
    """Translate view: project."""
    log.debug("Translate view: project.")

    # Validate locale
    log.debug("Locale: " + locale)
    try:
        l = Locale.objects.get(code=locale)
    except Locale.DoesNotExist:
        messages.error(request, "Oops, locale is not supported.")
        return HttpResponseRedirect(reverse('pontoon.home'))

    # Validate project
    try:
        p = Project.objects.get(
            slug=slug, pk__in=Entity.objects.values('project'))
    except Project.DoesNotExist:
        messages.error(request, "Oops, project could not be found.")
        request.session['translate_error'] = {
            'locale': locale,
        }
        return HttpResponseRedirect(reverse('pontoon.home'))

    # Check if user authenticated and has sufficient privileges
    if not p.name == 'Testpilot':
        if not request.user.is_authenticated():
            messages.error(request, "You need to sign in first.")
            return HttpResponseRedirect(reverse('pontoon.home'))

    data = {
        'locale_code': locale,
        'locales': Locale.objects.all(),
        'pages': Subpage.objects.all(),
        'project_url': p.url,
        'project': p,
        'projects': Project.objects.filter(
            pk__in=Entity.objects.values('project'))
    }

    # Get profile image from Gravatar
    if request.user.is_authenticated():
        email = request.user.email
        size = 60

        gravatar_url = "http://www.gravatar.com/avatar/" + \
            hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'s': str(size)})
        if settings.SITE_URL != 'http://localhost:8000':
            default = settings.SITE_URL + static('img/user_icon&24.png')
            gravatar_url += urllib.urlencode({'d': default})

        data['gravatar_url'] = gravatar_url

    # Validate project locales
    if len(p.locales.filter(code=locale)) == 0:
        request.session['translate_error'] = {
            'locale': locale,
            'project': p.slug,
        }
        messages.error(
            request, "Oops, locale is not supported for this project.")
        return HttpResponseRedirect(reverse('pontoon.home'))

    # Validate subpages
    pages = Subpage.objects.filter(project=p)
    if len(pages) > 0:
        if page is None:
            try:
                # If page exist, but not specified in URL
                page = pages.filter(url__startswith=p.url)[0].name
            except IndexError:
                request.session['translate_error'] = {
                    'locale': locale,
                    'project': p.slug,
                }
                messages.error(
                    request, "Oops, project URL doesn't match any subpage.")
                return HttpResponseRedirect(reverse('pontoon.home'))
        else:
            try:
                data['project_url'] = pages.get(name=page).url
            except Subpage.DoesNotExist:
                request.session['translate_error'] = {
                    'locale': locale,
                    'project': p.slug,
                }
                messages.error(request, "Oops, subpage could not be found.")
                return HttpResponseRedirect(reverse('pontoon.home'))
        data['project_pages'] = pages
        data['current_page'] = page

    # Get entities
    if page is not None:
        page = page.lower().replace(" ", "")
    data['entities'] = json.dumps(_get_entities(p, l, page))

    return render(request, template, data)


def _request(method, project, resource, locale,
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


def get_translations_from_other_locales(request, template=None):
    """Get entity translations for all but specified locale."""
    log.debug("Get entity translation for all but specified locale.")

    if not request.is_ajax():
        log.error("Non-AJAX request")
        raise Http404

    try:
        entity = request.GET['entity']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    log.debug("Entity: " + entity)
    log.debug("Locale: " + locale)

    try:
        entity = Entity.objects.get(pk=entity)
    except Entity.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    try:
        locale = Locale.objects.get(code=locale)
    except Locale.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    payload = []
    locales = entity.project.locales.all().exclude(code=locale.code)

    for l in locales:
        translation = _get_translation(entity=entity, locale=l).string
        if translation != "":
            payload.append({
                "locale": {
                    "code": l.code,
                    "name": l.name
                },
                "translation": translation
            })

    if len(payload) == 0:
        log.debug("Translations do not exist")
        return HttpResponse("error")
    else:
        return HttpResponse(
            json.dumps(payload, indent=4), mimetype='application/json')


def get_translation_history(request, template=None):
    """Get history of translations of given entity to given locale."""
    log.debug("Get history of translations of given entity to given locale.")

    if not request.is_ajax():
        log.error("Non-AJAX request")
        raise Http404

    try:
        entity = request.GET['entity']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    log.debug("Entity: " + entity)
    log.debug("Locale: " + locale)

    try:
        entity = Entity.objects.get(pk=entity)
    except Entity.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    try:
        locale = Locale.objects.get(code=locale)
    except Locale.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    translations = Translation.objects \
        .filter(entity=entity, locale=locale) \
        .order_by('-approved', '-date')

    user = ''
    if entity.project.name == 'Testpilot':
        user = 'Anonymous'

    if len(translations) > 0:
        payload = []
        for t in translations:
            o = {
                "id": t.id,
                "user": getattr(t.user, 'email', user),  # Empty for imported
                "translation": t.string,
                "date": t.date.strftime("%b %d, %Y %H:%M"),
                "approved": t.approved,
            }
            payload.append(o)

        return HttpResponse(
            json.dumps(payload, indent=4), mimetype='application/json')

    else:
        log.debug("Translations do not exist")
        return HttpResponse("error")


def _unset_approved(translations):
    """Unset approved attribute for given translations."""
    log.debug("Unset approved attribute for given translations.")

    try:
        t = translations.get(approved=True)
        t.approved = False
        t.save()
    except Translation.DoesNotExist:
        pass


def approve_translation(request, template=None):
    """Approve given translation."""
    log.debug("Approve given translation.")

    if not request.user.has_perm('base.can_localize'):
        return render(request, '403.html', status=403)

    if not request.is_ajax():
        log.error("Non-AJAX request")
        raise Http404

    try:
        t = request.POST['translation']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    log.debug("Translation: " + t)

    try:
        translation = Translation.objects.get(pk=t)
    except Translation.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    entity = translation.entity
    locale = translation.locale

    translations = Translation.objects.filter(entity=entity, locale=locale)
    _unset_approved(translations)

    translation.approved = True
    translation.save()

    return HttpResponse(json.dumps({
        'type': 'approved',
    }), mimetype='application/json')


def delete_translation(request, template=None):
    """Delete given translation."""
    log.debug("Delete given translation.")

    if not request.is_ajax():
        log.error("Non-AJAX request")
        raise Http404

    try:
        t = request.POST['translation']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    log.debug("Translation: " + t)

    try:
        translation = Translation.objects.get(pk=t)
    except Translation.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    # Non-privileged users can only delete own non-approved translations
    if not request.user.has_perm('base.can_localize'):
        if translation.user == request.user:
            if translation.approved is True:
                log.error(
                    "Non-privileged users cannot delete approved translation")
                return HttpResponse("error")

        else:
            return render(request, '403.html', status=403)

    entity = translation.entity
    locale = translation.locale

    translation.delete()
    next = _get_translation(entity=entity, locale=locale)

    if next.id is not None and request.user.has_perm('base.can_localize'):
        next.approved = True
        next.save()

    return HttpResponse(json.dumps({
        'type': 'deleted',
        'next': next.id,
    }), mimetype='application/json')


def update_translation(request, template=None):
    """Update entity translation for the specified locale and user."""
    log.debug("Update entity translation for the specified locale and user.")

    if not request.is_ajax():
        log.error("Non-AJAX request")
        raise Http404

    if request.method != 'POST':
        log.error("Non-POST request")
        raise Http404

    try:
        entity = request.POST['entity']
        string = request.POST['translation']
        locale = request.POST['locale']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    log.debug("Entity: " + entity)
    log.debug("Translation: " + string)
    log.debug("Locale: " + locale)

    try:
        e = Entity.objects.get(pk=entity)
    except Entity.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    try:
        l = Locale.objects.get(code=locale)
    except Locale.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    user = request.user
    if not request.user.is_authenticated():
        if e.project.name != 'Testpilot':
            log.error("Not authenticated")
            return HttpResponse("error")
        else:
            user = None

    if string == '':
        return HttpResponse("Empty translations cannot be submitted.")
    else:
        can_localize = request.user.has_perm('base.can_localize')
        translations = Translation.objects.filter(entity=e, locale=l)

        # Translations exist
        if len(translations) > 0:
            # Same translation exist
            for t in translations:
                if t.string == string:
                    # If added by privileged user, approve it
                    if can_localize:
                        _unset_approved(translations)
                        t.approved = True
                        t.save()

                        return HttpResponse(json.dumps({
                            'type': 'updated',
                            'approved': can_localize,
                            'translation': t.string,
                        }), mimetype='application/json')
                    else:
                        return HttpResponse("Same translation already exist.")

            # Different translation added
            if can_localize:
                _unset_approved(translations)

            t = Translation(
                entity=e, locale=l, user=user, string=string,
                date=datetime.datetime.now(), approved=can_localize)
            t.save()

            active = _get_translation(entity=e, locale=l)

            return HttpResponse(json.dumps({
                'type': 'added',
                'approved': active.approved,
                'translation': active.string,
            }), mimetype='application/json')

        # No translations saved yet
        else:
            t = Translation(
                entity=e, locale=l, user=user, string=string,
                date=datetime.datetime.now(), approved=can_localize)
            t.save()

            return HttpResponse(json.dumps({
                'type': 'saved',
                'approved': can_localize,
                'translation': t.string,
            }), mimetype='application/json')


def translation_memory(request):
    """Get translation from translation memory service."""
    log.debug("Get translation from translation memory service.")

    try:
        text = request.GET['text']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    url = "http://transvision.mozfr.org/"
    payload = {
        "recherche": text,
        "sourcelocale": "en-US",
        "locale": locale,
        "perfect_match": "perfect_match",
        "repo": "aurora",
        "json": True,
    }

    try:
        r = requests.get(url, params=payload)

        if r.text != '[]':
            translation = r.json().itervalues().next().itervalues().next()

            # Use JSON to distinguish from error if such translation returned
            return HttpResponse(json.dumps({
                'translation': translation
            }), mimetype='application/json')

        else:
            return HttpResponse("no")

    except Exception as e:
        log.error(e)
        return HttpResponse("error")


def machine_translation(request):
    """Get translation from machine translation service."""
    log.debug("Get translation from machine translation service.")

    try:
        text = request.GET['text']
        to = request.GET['locale']
        check = request.GET['check']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    if hasattr(settings, 'MICROSOFT_TRANSLATOR_API_KEY'):
        api_key = settings.MICROSOFT_TRANSLATOR_API_KEY
    else:
        log.error("MICROSOFT_TRANSLATOR_API_KEY not set")
        return HttpResponse("apikey")

    import xml.etree.ElementTree as ET
    base = "http://api.microsofttranslator.com/V2/Http.svc/"

    # On first run, check if target language supported
    if check == "true":
        url = base + "GetLanguagesForTranslate"
        payload = {
            "appId": api_key,
        }

        try:
            r = requests.get(url, params=payload)
            log.debug(r.content)

            # Parse XML response
            root = ET.fromstring(r.content)
            supported = False
            for child in root:
                if to == child.text:
                    supported = True
                    break

            if not supported:
                log.debug("Locale not supported.")
                return HttpResponse("not-supported")

        except Exception as e:
            log.error(e)
            return HttpResponse("error")

    url = base + "Translate"
    payload = {
        "appId": api_key,
        "text": text,
        "from": "en",
        "to": to,
        "contentType": "text/html",
    }

    try:
        r = requests.get(url, params=payload)
        log.debug(r.content)

        # Parse XML response
        root = ET.fromstring(r.content)
        translation = root.text

        # Use JSON to distinguish from "error" if such translation returned
        return HttpResponse(json.dumps({
            'translation': translation
        }), mimetype='application/json')

    except Exception as e:
        log.error(e)
        return HttpResponse("error")


def _get_locale_repository_path(project, locale):
    """Get path to locale directory."""
    log.debug("Get path to locale directory.")

    path = os.path.join(
        settings.MEDIA_ROOT, project.repository_type, project.slug)

    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden files and folders
        filenames = [f for f in filenames if not f[0] == '.']
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        for dirname in fnmatch.filter(dirnames, locale):
            return os.path.join(root, dirname)

    # Fallback to project's repository_path
    return path


def _get_locale_paths(path, format):
    """Get paths to locale files."""

    locale_paths = []
    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden files and folders
        filenames = [f for f in filenames if not f[0] == '.']
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        for filename in fnmatch.filter(filenames, '*.' + format):
            locale_paths.append(os.path.join(root, filename))

    return locale_paths


def _update_files(p, locale, locale_repository_path):
    entities = Entity.objects.filter(project=p)
    locale_paths = _get_locale_paths(locale_repository_path, p.format)

    if p.format == 'po':
        for path in locale_paths:
            po = polib.pofile(path)
            valid_entries = [e for e in po if not e.obsolete]

            for entity in entities:
                entry = po.find(entity.string)
                if entry:
                    translation = _get_translation(
                        entity=entity, locale=locale).string
                    if translation != '':
                        entry.msgstr = translation

                    if 'fuzzy' in entry.flags:
                        entry.flags.remove('fuzzy')

            po.save()
            log.debug("File updated: " + path)

    elif p.format == 'properties':
        for path in locale_paths:
            format_parser = silme.format.properties.PropertiesFormatParser
            with codecs.open(path, 'r+', 'utf-8') as f:
                l10nobject = format_parser.get_structure(f.read())

                short_path = '/' + path.split('/' + locale.code + '/')[-1]
                entities_with_path = entities.filter(source=short_path)
                for entity in entities_with_path:
                    key = entity.key
                    translation = _get_translation(
                        entity=entity, locale=locale).string

                    try:
                        l10nobject.modify_entity(key, translation)
                    except KeyError:
                        # Only add new keys if translation available
                        if translation != '':
                            new_entity = silme.core.entity.Entity(
                                key, translation)
                            l10nobject.add_entity(new_entity)

                # Erase file and then write, otherwise content gets appended
                f.seek(0)
                f.truncate()
                content = format_parser.dump_structure(l10nobject)
                f.write(content)
                log.debug("File updated: " + locale_paths[0])

    elif p.format == 'ini':
        config = configparser.ConfigParser()
        with codecs.open(
                locale_paths[0], 'r+', 'utf-8', errors='replace') as f:
            try:
                config.read_file(f)
                if config.has_section(locale.code):

                    for entity in entities:
                        key = entity.key
                        translation = _get_translation(
                            entity=entity, locale=locale).string

                        config.set(locale.code, key, translation)

                    # Erase and then write, otherwise content gets appended
                    f.seek(0)
                    f.truncate()
                    config.write(f)
                    log.debug("File updated: " + locale_paths[0])

                else:
                    log.debug("Locale not available in the source file")
                    raise Exception("error")

            except Exception as e:
                log.debug("INI configparser: " + str(e))
                raise Exception("error")

    elif p.format == 'lang':
        for path in locale_paths:
            with codecs.open(path, 'r+', 'utf-8', errors='replace') as lines:
                content = []
                translation = None

                for line in lines:
                    if translation:
                        # Keep newlines and white spaces in line if present
                        trans_line = line.replace(line.strip(), translation)
                        content.append(trans_line)
                        translation = None
                        continue

                    content.append(line)
                    line = line.strip()

                    if not line:
                        continue

                    if line[0] == ';':
                        original = line[1:].strip()

                        try:
                            entity = Entity.objects.get(
                                project=p, string=original)
                        except Entity.DoesNotExist as e:
                            log.error(path + ": \
                                      Entity with string \"" + original +
                                      "\" does not exist in " + p.name)
                            continue

                        translation = _get_translation(
                            entity=entity, locale=locale).string
                        if translation != '':
                            translation = original

                # Erase file and then write, otherwise content gets appended
                lines.seek(0)
                lines.truncate()
                lines.writelines(content)
                log.debug("File updated: " + path)


def _generate_zip(pk, locale):
    """
    Generate .zip file of all project files for the specified locale.

    Args:
        pk: Primary key of the project
        locale: Locale code
    Returns:
        A string for generated ZIP content.
    """

    try:
        p = Project.objects.get(pk=pk)
    except Project.DoesNotExist as e:
        log.error(e)

    try:
        locale = Locale.objects.get(code=locale)
    except Locale.DoesNotExist as e:
        log.error(e)

    path = _get_locale_repository_path(p, locale.code)
    _update_files(p, locale, path)

    s = StringIO.StringIO()
    zf = zipfile.ZipFile(s, "w")

    for root, dirs, files in os.walk(path):
        for f in files:
            file_path = os.path.join(root, f)
            zip_path = os.path.relpath(file_path, os.path.join(path, '..'))
            zf.write(file_path, zip_path)

    zf.close()
    return s.getvalue()


@anonymous_csrf_exempt
def download(request, template=None):
    """Download translations in appropriate form."""
    log.debug("Download translations.")

    if request.method != 'POST':
        log.error("Non-POST request")
        raise Http404

    try:
        format = request.POST['type']
        content = request.POST['content']
        locale = request.POST['locale']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        raise Http404

    filename = locale
    response = HttpResponse()
    if format == 'html':
        response['Content-Type'] = 'text/html'
    elif format == 'json':
        response['Content-Type'] = 'application/json'
    elif format == 'zip':
        content = _generate_zip(content, locale)
        response['Content-Type'] = 'application/x-zip-compressed'

    response.content = content
    response['Content-Disposition'] = \
        'attachment; filename=' + filename + '.' + format
    return response


@login_required(redirect_field_name='', login_url='/403')
def commit_to_svn(request, template=None):
    """Commit translations to SVN."""
    log.debug("Commit translations to SVN.")

    if not request.user.has_perm('base.can_localize'):
        return render(request, '403.html', status=403)

    try:
        import pysvn
    except ImportError as e:
        log.error(e)
        return HttpResponse("error")

    if request.method != 'POST':
        log.error("Non-POST request")
        raise Http404

    try:
        data = json.loads(request.POST['data'])
    except MultiValueDictKeyError as e:
        log.error(e)
        return HttpResponse("error")

    try:
        locale = Locale.objects.get(code=data['locale'])
    except Locale.DoesNotExist as e:
        log.error(e)
        return HttpResponse("error")

    try:
        p = Project.objects.get(pk=data['pk'])
    except Project.DoesNotExist as e:
        log.error(e)
        return HttpResponse("error")

    project = p.name
    locale_repository_path = _get_locale_repository_path(p, locale.code)

    _update_files(p, locale, locale_repository_path)

    client = pysvn.Client()
    client.exception_style = 1

    """Check if user authenticated to SVN."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    username = data.get('auth', {}).get('username', profile.svn_username)
    password = data.get('auth', {}).get(
        'password', base64.decodestring(profile.svn_password))

    if len(username) > 0 and len(password) > 0:
        client.set_default_username(username)
        client.set_default_password(password)

    try:
        client.checkin(
            [locale_repository_path],
            'Pontoon: update ' + locale.code + ' localization of ' + project)
        log.info('Commited ' + locale.code + ' localization of ' + project)

    except pysvn.ClientError as e:
        log.debug(str(e))
        if "callback_get_login" in str(e):
            log.error('Subversion CommitError for %s: please authenticate' %
                      locale_repository_path)
            return HttpResponse(json.dumps({
                'type': 'authenticate',
                'message': 'Authentication failed.'
            }), mimetype='application/json')

        log.error('Subversion CommitError for %s: %s' %
                  (locale_repository_path, e))
        return HttpResponse(json.dumps({
            'type': 'error',
            'message': str(e)
        }), mimetype='application/json')

    """Save SVN username and password."""
    if data.get('auth', {}).get('remember', {}) == 1:
        if profile.svn_username != username:
            profile.svn_username = username
        if base64.decodestring(profile.svn_password) != password:
            profile.svn_password = base64.encodestring(password)
        profile.save()
        log.info("SVN username and password saved.")

    return HttpResponse("200")


@login_required(redirect_field_name='', login_url='/403')
def save_to_transifex(request, template=None):
    """Save translations to Transifex."""
    log.debug("Save to Transifex.")

    if request.method != 'POST':
        log.error("Non-POST request")
        raise Http404

    try:
        data = json.loads(request.POST['data'])
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    """Check if user authenticated to Transifex."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    username = data.get('auth', {}) \
                   .get('username', profile.transifex_username)
    password = data.get('auth', {}) \
                   .get('password',
                        base64.decodestring(profile.transifex_password))
    if len(username) == 0 or len(password) == 0:
        return HttpResponse("authenticate")

    """Make PUT request to Transifex API."""
    payload = []
    for entity in data.get('strings'):
        obj = {
            # Identify translation strings using hashes
            "source_entity_hash": hashlib.md5(
                ':'.join([entity['original'], ''])
                   .encode('utf-8')).hexdigest(),
            "translation": entity['translation']
        }
        payload.append(obj)
    log.debug(json.dumps(payload, indent=4))

    """Make PUT request to Transifex API."""
    try:
        p = Project.objects.get(url=data['url'])
    except Project.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")
    response = _request('put', p.transifex_project, p.transifex_resource,
                        data['locale'], username, password, payload)

    """Save Transifex username and password."""
    if data.get('auth', {}).get('remember', {}) == 1:
        profile.transifex_username = data['auth']['username']
        profile.transifex_password = base64.encodestring(
            data['auth']['password'])
        profile.save()

    try:
        return HttpResponse(response.status_code)
    except AttributeError:
        return HttpResponse(response)


@anonymous_csrf_exempt
def verify(request, template=None):
    """Verify BrowserID assertion, and return whether a user is registered."""
    log.debug("Verify BrowserID assertion.")

    if request.method != 'POST':
        log.error("Non-POST request")
        raise Http404

    assertion = request.POST['assertion']
    if assertion is None:
        return HttpResponseBadRequest()

    verification = browserid_verify(assertion, get_audience(request))
    if not verification:
        return HttpResponseForbidden()

    response = "error"
    user = authenticate(assertion=assertion, audience=get_audience(request))

    if user is not None:
        login(request, user)

        # Check for permission to localize if not granted on every login
        if not user.has_perm('base.can_localize'):
            user = User.objects.get(username=user)
            add_can_localize(user)

        response = {
            'browserid': verification,
            'manager': user.has_perm('base.can_manage'),
        }

    return HttpResponse(json.dumps(response), mimetype='application/json')


def get_csrf(request, template=None):
    """Get CSRF token."""
    log.debug("Get CSRF token.")

    if not request.is_ajax():
        log.error("Non-AJAX request")
        raise Http404

    return HttpResponse(request.csrf_token)
