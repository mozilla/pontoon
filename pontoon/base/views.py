
import base64
import commonware
import datetime
import hashlib
import json
import os
import requests
import xml.etree.ElementTree as ET
import urllib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

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
from pontoon.administration.utils.vcs import commit_to_vcs
from pontoon.administration.utils import files
from pontoon.base import utils

from pontoon.base.models import (
    Locale,
    Project,
    Subpage,
    Entity,
    Translation,
    UserProfile,
    get_entities,
    get_translation,
    unset_approved,
)

from session_csrf import anonymous_csrf_exempt
from suds.client import Client, WebFault


log = commonware.log.getLogger('pontoon')


def home(request, template='base/home.html'):
    """Home view."""
    log.debug("Home view.")

    translate_error = request.session.pop('translate_error', {})

    data = {
        'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        .split(',')[0],
        'locale_code': translate_error.get('locale', None),
        'project': translate_error.get('project', None),
        'redirect': translate_error.get('redirect', None),
        'locales': Locale.objects.all(),
        'projects': Project.objects.filter(
            pk__in=Entity.objects.values('project'))
    }

    return render(request, template, data)


def locale(request, locale, template='base/locale.html'):
    """Locale view."""
    log.debug("Locale view.")

    # Validate locale
    try:
        l = Locale.objects.get(code=locale)
    except Locale.DoesNotExist:
        raise Http404

    # Check if user authenticated
    if not request.user.is_authenticated():
        messages.error(request, "You need to sign in first.")
        request.session['translate_error'] = {
            'redirect': request.get_full_path(),
        }
        return HttpResponseRedirect(reverse('pontoon.home'))

    data = {
        'projects': Project.objects.filter(
            pk__in=Entity.objects.values('project')).filter(locales=l),
        'locale': l,
    }

    return render(request, template, data)


def project(request, slug, template='base/project.html'):
    """Project view."""
    log.debug("Project view.")

    # Validate project
    try:
        p = Project.objects.get(slug=slug)
    except Project.DoesNotExist:
        messages.error(request, "Oops, project could not be found.")
        return HttpResponseRedirect(reverse('pontoon.home'))

    # Check if user authenticated
    if not request.user.is_authenticated():
        messages.error(request, "You need to sign in first.")
        request.session['translate_error'] = {
            'redirect': request.get_full_path(),
        }
        return HttpResponseRedirect(reverse('pontoon.home'))

    data = {
        'locales': p.locales.all(),
        'project': p,
    }

    return render(request, template, data)


def handle_error(request):
    """
    This view is bound with a generic URL which can be called from Pontoon's
    javascript with appropriate GET parameters and the page will get
    redirected to the home page showing proper error messages, url and locale.
    """
    messages.error(request, request.GET.get('error', ''))
    request.session['translate_error'] = {
        'locale': request.GET.get('locale'),
        'project': request.GET.get('project')
    }
    return HttpResponseRedirect(reverse('pontoon.home'))


def translate(request, locale, slug, page=None,
              template='base/translate.html'):
    """Translate view."""
    log.debug("Translate view.")

    invalid_locale = invalid_project = False

    # Validate locale
    try:
        l = Locale.objects.get(code=locale)
    except Locale.DoesNotExist:
        invalid_locale = True

    # Validate project
    try:
        p = Project.objects.get(
            slug=slug, pk__in=Entity.objects.values('project'))
    except Project.DoesNotExist:
        invalid_project = True

    if invalid_locale:
        if invalid_project:
            raise Http404
        else:
            messages.error(request, "Oops, locale is not supported.")
            request.session['translate_error'] = {
                'project': p.slug,
            }
            return HttpResponseRedirect(reverse('pontoon.home'))

    if invalid_project:
        messages.error(request, "Oops, project could not be found.")
        request.session['translate_error'] = {
            'locale': locale,
        }
        return HttpResponseRedirect(reverse('pontoon.home'))

    # Validate project locales
    if len(p.locales.filter(code=locale)) == 0:
        request.session['translate_error'] = {
            'locale': locale,
            'project': p.slug,
        }
        messages.error(
            request, "Oops, locale is not supported for this project.")
        return HttpResponseRedirect(reverse('pontoon.home'))

    # Check if user authenticated
    if not p.name == 'Testpilot':
        if not request.user.is_authenticated():
            messages.error(request, "You need to sign in first.")
            request.session['translate_error'] = {
                'redirect': request.get_full_path(),
            }
            return HttpResponseRedirect(reverse('pontoon.home'))

    data = {
        'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        .split(',')[0],
        'locale': l,
        'locales': Locale.objects.all(),
        'pages': Subpage.objects.all(),
        'project_url': p.url,
        'project': p,
        'projects': Project.objects.filter(
            pk__in=Entity.objects.values('project'))
    }

    # Set subpage
    pages = Subpage.objects.filter(project=p)
    if len(pages) > 0:
        try:
            page = pages.get(name=page)
        except Subpage.DoesNotExist:
            page = pages[0]  # If page not specified or doesn't exist

        data['current_page'] = page.name
        data['project_url'] = page.url
        data['project_pages'] = pages

        # Firefox OS Hack
        if page is not None:
            page = page.name.lower().replace(" ", "").replace(".", "")

    # Get profile image from Gravatar
    if request.user.is_authenticated():
        email = request.user.email
        size = 44

        gravatar_url = "//www.gravatar.com/avatar/" + \
            hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'s': str(size)})

        if settings.SITE_URL != 'http://localhost:8000':
            default = settings.SITE_URL + static('img/user_icon&24.png')
            gravatar_url += urllib.urlencode({'d': default})

        data['gravatar_url'] = gravatar_url

    # Get entities
    data['entities'] = json.dumps(get_entities(p, l, page))

    return render(request, template, data)


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
        translation = get_translation(entity=entity, locale=l)
        if translation.string != '' or translation.pk is not None:
            payload.append({
                "locale": {
                    "code": l.code,
                    "name": l.name
                },
                "translation": translation.string
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
        plural_form = request.GET['plural_form']
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

    translations = Translation.objects.filter(entity=entity, locale=locale)
    if plural_form != "-1":
        translations = translations.filter(plural_form=plural_form)
    translations = translations.order_by('-approved', '-date')

    user = 'Anonymous' if entity.project.name == 'Testpilot' else 'Imported'

    if len(translations) > 0:
        payload = []
        for t in translations:
            usr = t.user
            user = user if usr is None else usr.first_name or usr.email
            o = {
                "id": t.id,
                "user": user,
                "translation": t.string,
                "date": t.date.strftime('%b %d, %Y %H:%M'),
                "approved": t.approved,
            }
            payload.append(o)

        return HttpResponse(
            json.dumps(payload, indent=4), mimetype='application/json')

    else:
        log.debug("Translations do not exist")
        return HttpResponse("error")


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
    plural_form = translation.plural_form

    translations = Translation.objects.filter(
        entity=entity, locale=locale, plural_form=plural_form)
    unset_approved(translations)

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
    plural_form = translation.plural_form

    translation.delete()
    next = get_translation(
        entity=entity, locale=locale, plural_form=plural_form)

    if next.pk is not None and request.user.has_perm('base.can_localize'):
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
        plural_form = request.POST['plural_form']
        original = request.POST['original']
        ignore_check = request.POST['ignore_check']
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

    if plural_form == "-1":
        plural_form = None

    ignore = True if ignore_check == 'true' else False

    user = request.user
    if not request.user.is_authenticated():
        if e.project.name != 'Testpilot':
            log.error("Not authenticated")
            return HttpResponse("error")
        else:
            user = None

    can_localize = request.user.has_perm('base.can_localize')
    translations = Translation.objects.filter(
        entity=e, locale=l, plural_form=plural_form)

    # Translations exist
    if len(translations) > 0:
        # Same translation exist
        for t in translations:
            if t.string == string:

                # If added by privileged user, approve it
                if can_localize:
                    warnings = utils.quality_check(original, string, ignore)
                    if warnings:
                        return warnings

                    unset_approved(translations)
                    t.approved = True
                    t.fuzzy = False
                    t.save()

                    return HttpResponse(json.dumps({
                        'type': 'updated',
                        'translation': t.serialize(),
                    }), mimetype='application/json')

                # Non-priviliged users can unfuzzy existing translations
                else:
                    if t.fuzzy:
                        warnings = utils.quality_check(
                            original, string, ignore)
                        if warnings:
                            return warnings

                        t.approved = False
                        t.fuzzy = False
                        t.save()

                        return HttpResponse(json.dumps({
                            'type': 'updated',
                            'translation': t.serialize(),
                        }), mimetype='application/json')

                    return HttpResponse("Same translation already exist.")

        # Different translation added
        warnings = utils.quality_check(original, string, ignore)
        if warnings:
            return warnings

        if can_localize:
            unset_approved(translations)

        t = Translation(
            entity=e, locale=l, user=user, string=string,
            plural_form=plural_form, date=datetime.datetime.now(),
            approved=can_localize)
        t.save()

        active = get_translation(
            entity=e, locale=l, plural_form=plural_form)

        return HttpResponse(json.dumps({
            'type': 'added',
            'translation': active.serialize(),
        }), mimetype='application/json')

    # No translations saved yet
    else:
        warnings = utils.quality_check(original, string, ignore)
        if warnings:
            return warnings

        t = Translation(
            entity=e, locale=l, user=user, string=string,
            plural_form=plural_form, date=datetime.datetime.now(),
            approved=can_localize)
        t.save()

        return HttpResponse(json.dumps({
            'type': 'saved',
            'translation': t.serialize(),
        }), mimetype='application/json')


def translation_memory(request):
    """Get translations from internal translations."""
    log.debug("Get translations from internal translations.")

    try:
        text = request.GET['text']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    try:
        locale = Locale.objects.get(code=locale)
    except Locale.DoesNotExist as e:
        log.error(e)
        return HttpResponse("error")

    entities = Entity.objects.filter(obsolete=False, string=text)
    translations = set()
    for e in entities:
        translation = get_translation(entity=e, locale=locale)
        if translation.string != '' or translation.pk is not None:
            translations.add(translation.string)

    if len(translations) > 0:
        return HttpResponse(json.dumps({
            'translations': list(translations)
        }), mimetype='application/json')

    else:
        return HttpResponse("no")


def machine_translation(request):
    """Get translation from machine translation service."""
    log.debug("Get translation from machine translation service.")

    try:
        text = request.GET['text']
        locale = request.GET['locale']
        check = request.GET['check']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    if hasattr(settings, 'MICROSOFT_TRANSLATOR_API_KEY'):
        api_key = settings.MICROSOFT_TRANSLATOR_API_KEY
    else:
        log.error("MICROSOFT_TRANSLATOR_API_KEY not set")
        return HttpResponse("apikey")

    obj = {}

    # On first run, check if target language supported
    if check == "true":
        supported = False
        languages = settings.MICROSOFT_TRANSLATOR_LOCALES

        if locale in languages:
            supported = True

        else:
            for lang in languages:
                if lang.startswith(locale.split("-")[0]):  # Neutral locales
                    supported = True
                    locale = lang
                    break

        if not supported:
            log.debug("Locale not supported.")
            return HttpResponse("not-supported")

        obj['locale'] = locale

    url = "http://api.microsofttranslator.com/V2/Http.svc/Translate"
    payload = {
        "appId": api_key,
        "text": text,
        "from": "en",
        "to": locale,
        "contentType": "text/html",
    }

    try:
        r = requests.get(url, params=payload)
        log.debug(r.content)

        # Parse XML response
        root = ET.fromstring(r.content)
        translation = root.text
        obj['translation'] = translation

        return HttpResponse(json.dumps(obj), mimetype='application/json')

    except Exception as e:
        log.error(e)
        return HttpResponse("error")


def microsoft_terminology(request):
    """Get translations from Microsoft Terminology Service."""
    log.debug("Get translations from Microsoft Terminology Service.")

    try:
        text = request.GET['text']
        locale = request.GET['locale']
        check = request.GET['check']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    obj = {}
    locale = locale.lower()
    url = 'http://api.terminology.microsoft.com/Terminology.svc?singleWsdl'
    client = Client(url)

    # On first run, check if target language supported
    if check == "true":
        supported = False
        languages = settings.MICROSOFT_TERMINOLOGY_LOCALES

        if locale in languages:
            supported = True

        elif "-" not in locale:
            temp = locale + "-" + locale  # Try e.g. "de-de"
            if temp in languages:
                supported = True
                locale = temp

            else:
                for lang in languages:
                    if lang.startswith(locale + "-"):  # Try e.g. "de-XY"
                        supported = True
                        locale = lang
                        break

        if not supported:
            log.debug("Locale not supported.")
            return HttpResponse("not-supported")

        obj['locale'] = locale

    sources = client.factory.create('ns0:TranslationSources')
    sources["TranslationSource"] = ['Terms', 'UiStrings']

    payload = {
        'text': text,
        'from': 'en-US',
        'to': locale,
        'sources': sources,
        'maxTranslations': 5
    }

    try:
        r = client.service.GetTranslations(**payload)
        translations = []

        if len(r) != 0:
            for translation in r.Match:
                translations.append({
                    'source': translation.OriginalText,
                    'target': translation.Translations[0][0].TranslatedText,
                    'quality': translation.ConfidenceLevel,
                })

            obj['translations'] = translations

        return HttpResponse(json.dumps(obj), mimetype='application/json')

    except WebFault as e:
        log.error(e)
        return HttpResponse("error")


def amagama(request):
    """Get open source translations from amaGama service."""
    log.debug("Get open source translations from amaGama service.")

    try:
        text = request.GET['text']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    try:
        text = urllib.quote(text.encode('utf-8'))
    except KeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    url = "http://amagama.locamotion.org/tmserver" \
          "/en/%s/unit/%s?max_candidates=%s" \
          % (locale, text, 5)

    try:
        r = requests.get(url)

        if r.text != '[]':
            translations = r.json()

            return HttpResponse(json.dumps({
                'translations': translations
            }), mimetype='application/json')

        else:
            return HttpResponse("no")

    except Exception as e:
        log.error(e)
        return HttpResponse("error")


def transvision(request):
    """Get Mozilla translations from Transvision service."""
    log.debug("Get Mozilla translations from Transvision service.")

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


@anonymous_csrf_exempt
def download(request, template=None):
    """Download translations in appropriate form."""
    log.debug("Download translations.")

    if request.method != 'POST':
        log.error("Non-POST request")
        raise Http404

    try:
        format = request.POST['type']
        locale = request.POST['locale']
        project = request.POST['project']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        raise Http404

    if format in ('html', 'json'):
        try:
            content = request.POST['content']
        except MultiValueDictKeyError as e:
            log.error(str(e))
            raise Http404
    try:
        p = Project.objects.get(pk=project)
    except Project.DoesNotExist as e:
        log.error(e)
        raise Http404

    filename = '%s-%s' % (p.slug, locale)
    response = HttpResponse()

    if format == 'html':
        response['Content-Type'] = 'text/html'

    elif format == 'json':
        response['Content-Type'] = 'application/json'

    elif format == 'zip':
        content = files.generate_zip(p, locale)

        if content is False:
            raise Http404

        response['Content-Type'] = 'application/x-zip-compressed'

    response.content = content
    response['Content-Disposition'] = \
        'attachment; filename=' + filename + '.' + format
    return response


@login_required(redirect_field_name='', login_url='/403')
def commit_to_repository(request, template=None):
    """Commit translations to repository."""
    log.debug("Commit translations to repository.")

    if not request.user.has_perm('base.can_localize'):
        return render(request, '403.html', status=403)

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
        p = Project.objects.get(pk=data['project'])
    except Project.DoesNotExist as e:
        log.error(e)
        return HttpResponse("error")

    path = files.get_locale_directory(p, locale)["path"]
    if not path:
        return HttpResponse(json.dumps({
            'type': 'error',
            'message': 'Sorry, repository path not found.',
        }), mimetype='application/json')

    files.update_from_database(p, locale)

    name = request.user.email if not request.user.first_name else '%s (%s)' \
        % (request.user.first_name, request.user.email)
    message = 'Pontoon: Update %s (%s) localization of %s on behalf of %s.' \
        % (locale.name, locale.code, p.name, name)

    r = commit_to_vcs(p.repository_type, path, message, request.user, data)
    if r is not None:
        return HttpResponse(json.dumps(r), mimetype='application/json')

    return HttpResponse("ok")


@login_required(redirect_field_name='', login_url='/403')
def update_from_repository(request, template=None):
    """Update translations from repository."""
    log.debug("Update translations from repository.")

    if not request.user.has_perm('base.can_localize'):
        return render(request, '403.html', status=403)

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
        project = Project.objects.get(pk=data['project'])
    except Project.DoesNotExist as e:
        log.error(e)
        return HttpResponse("error")

    try:
        files.update_from_repository(project, [locale])
        files.extract_to_database(project, [locale])
    except Exception as e:
        log.error("Exception: " + str(e))
        return HttpResponse('error')

    return HttpResponse("ok")


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
    response = utils.req('put', p.transifex_project, p.transifex_resource,
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
            utils.add_can_localize(user)

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
