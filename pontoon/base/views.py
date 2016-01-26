from __future__ import division

import json
import logging
import math
import requests
import xml.etree.ElementTree as ET
import urllib

from collections import defaultdict
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage
from django.core.validators import validate_comma_separated_integer_list
from django.db import transaction, DataError
from django.db.models import Count, F, Q

from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse
)

from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from guardian.decorators import permission_required_or_403

from pontoon.base import forms
from pontoon.base import utils
from pontoon.base.utils import require_AJAX

from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    Resource,
    TranslatedResource,
    Translation,
    TranslationMemoryEntry,
    UserProfile,
)

from session_csrf import anonymous_csrf_exempt
from suds.client import Client, WebFault


log = logging.getLogger('pontoon')


def home(request):
    """Home view."""
    project = Project.objects.get(id=1)
    locale = utils.get_project_locale_from_request(
        request, project.locales) or 'en-GB'
    path = Resource.objects.filter(project=project, translatedresources__locale__code=locale)[0].path

    return translate(request, locale, project.slug, path)


def locale(request, locale):
    """Locale view."""
    l = get_object_or_404(Locale, code__iexact=locale)

    projects = (
        Project.objects.available()
        .order_by('name')
    )

    if not projects:
        raise Http404

    return render(request, 'locale.html', {
        'projects': projects,
        'locale': l,
    })


@login_required(redirect_field_name='', login_url='/403')
@permission_required_or_403('base.can_translate_locale', (Locale, 'code', 'locale'))
@transaction.atomic
def locale_manage(request, locale):
    l = get_object_or_404(Locale, code__iexact=locale)

    def update_group(group, name):
        current = set(group.user_set.values_list("id", flat=True))
        selected = request.POST[name]
        new = set()

        if selected:
            try:
                # TODO: Use ModelMultipleChoiceField
                validate_comma_separated_integer_list(selected)
                new = set(map(int, selected.split(',')))
            except ValidationError as e:
                log.error(e)
                return HttpResponseBadRequest(e)

        if current != new:
            group.user_set = User.objects.filter(pk__in=new)
            group.save()

    if request.method == 'POST':
        update_group(l.translators_group, 'translators')
        update_group(l.managers_group, 'managers')

    managers = l.managers_group.user_set.all()
    translators = l.translators_group.user_set.exclude(pk__in=managers).all()
    all_users = User.objects.exclude(pk__in=managers).exclude(pk__in=translators).exclude(email="")
    contributors = User.translators.filter(translation__locale=l).distinct()

    return render(request, 'locale_manage.html', {
        'locale': l,
        'all_users': all_users,
        'contributors': contributors,
        'translators': translators,
        'managers': managers,
    })


def locales(request):
    """Localization teams."""
    locales = (
        Locale.objects.available()
    )

    return render(request, 'locales.html', {
        'locales': locales,
    })


def project(request, slug):
    """Project view."""
    project = get_object_or_404(Project.objects.available(), slug=slug)

    locales = (
        project.locales.all()
        .prefetch_latest_translation(project)
        .order_by('name')
    )

    return render(request, 'project.html', {
        'locales': locales,
        'project': project,
    })


def projects(request):
    """Project overview."""
    projects = (
        Project.objects.available()
        .select_related('latest_translation__user')
        .order_by('name')
    )

    return render(request, 'projects.html', {
        'projects': projects,
    })


def locale_project(request, locale, slug):
    """Locale-project overview."""
    l = get_object_or_404(Locale, code__iexact=locale)

    project = get_object_or_404(
        Project.objects.available().prefetch_related('subpage_set'),
        slug=slug
    )

    # Amend the parts dict with latest activity info.
    translatedresources_qs = (
        TranslatedResource.objects
        .filter(resource__project=project, locale=l)
        .select_related('resource', 'latest_translation')
    )

    if not len(translatedresources_qs):
        raise Http404

    translatedresources = {s.resource.path: s for s in translatedresources_qs}
    parts = l.parts_stats(project)

    for part in parts:
        stat = translatedresources.get(part['title'], None)
        part['latest_activity'] = stat.latest_translation if stat else None

        part['chart'] = {
            'translated_strings': part['translated_strings'],
            'fuzzy_strings': part['fuzzy_strings'],
            'total_strings': part['resource__total_strings'],
            'approved_strings': part['approved_strings'],
            'approved_share': round(part['approved_strings'] / part['resource__total_strings'] * 100),
            'translated_share': round(part['translated_strings'] / part['resource__total_strings'] * 100),
            'fuzzy_share': round(part['fuzzy_strings'] / part['resource__total_strings'] * 100),
            'approved_percent': int(math.floor(part['approved_strings'] / part['resource__total_strings'] * 100)),
        }

    return render(request, 'locale_project.html', {
        'locale': l,
        'project': project,
        'parts': parts,
    })


def translate(request, locale, slug, part):
    """Translate view."""
    locale = get_object_or_404(Locale, code__iexact=locale)
    project = get_object_or_404(Project.objects.available(), slug=slug)

    if locale not in project.locales.all():
        raise Http404

    projects = (
        Project.objects.available()
        .prefetch_related('subpage_set')
        .order_by('name')
    )

    return render(request, 'translate.html', {
        'download_form': forms.DownloadFileForm(),
        'upload_form': forms.UploadFileForm(),
        'locale': locale,
        'locales': Locale.objects.available(),
        'part': part,
        'project': project,
        'projects': projects,
    })


@login_required(redirect_field_name='', login_url='/403')
def profile(request):
    """Current user profile."""
    return contributor(request, request.user.email)


def contributor(request, email):
    """Contributor profile."""
    user = get_object_or_404(User, email=email)

    # Exclude unchanged translations
    translations = (
        Translation.objects.filter(user=user)
        .exclude(string=F('entity__string'))
        .exclude(string=F('entity__string_plural'))
    )

    # Exclude obsolete translations
    current = translations.exclude(entity__obsolete=True) \
        .extra({'day': "date(date)"}).order_by('day')

    # Timeline
    timeline = [{
        'date': user.date_joined,
        'type': 'join',
    }]

    for event in current.values('day').annotate(count=Count('id')):
        daily = current.filter(date__startswith=event['day'])
        example = daily[0]

        timeline.append({
            'date': example.date,
            'type': 'translation',
            'count': event['count'],
            'project': example.entity.resource.project,
            'translation': example,
        })

    timeline.reverse()

    return render(request, 'user.html', {
        'contributor': user,
        'timeline': timeline,
        'translations': translations,
    })


class ContributorsMixin(object):
    def contributors_filter(self, **kwargs):
        """
        Return Q() filters for fetching contributors. Fetches all by default.
        """
        return None

    def get_context_data(self, **kwargs):
        """Top contributors view."""
        context = super(ContributorsMixin, self).get_context_data(**kwargs)
        try:
            period = int(self.request.GET['period'])
            if period <= 0:
                raise ValueError
            start_date = (timezone.now() + relativedelta(months=-period))
        except (KeyError, ValueError):
            period = None
            start_date = None

        context['contributors'] = User.translators.with_translation_counts(start_date, self.contributors_filter(**kwargs))
        context['period'] = period
        return context


class ContributorsView(ContributorsMixin, TemplateView):
    """
    View returns top contributors.
    """
    template_name = 'users.html'


class LocaleContributorsView(ContributorsMixin, DetailView):
    """
    View renders page of the contributors for the locale.
    """
    template_name = 'locale_contributors.html'
    model = Locale
    slug_field = 'code__iexact'
    slug_url_kwarg = 'code'

    def get_context_object_name(self, obj):
        return 'locale'

    def contributors_filter(self, **kwargs):
        return Q(translation__locale=self.object)


class ProjectContributorsView(ContributorsMixin, DetailView):
    """
    Renders an subpage of the project and displays its contributors.
    """
    template_name = 'project_contributors.html'
    model = Project

    def get_context_object_name(self, obj):
        return 'project'

    def contributors_filter(self, **kwargs):
        return Q(translation__entity__resource__project=self.object)


def search(request):
    """Terminology search view."""
    locale = utils.get_project_locale_from_request(
        request, Locale.objects) or 'en-GB'

    return render(request, 'search.html', {
        'locale': Locale.objects.get(code__iexact=locale),
        'locales': Locale.objects.all(),
    })


@require_AJAX
def locale_projects(request, locale):
    """Get active projects for locale."""
    locale = get_object_or_404(Locale, code=locale)

    return JsonResponse(locale.available_projects_list(), safe=False)


@require_AJAX
def locale_project_parts(request, locale, slug):
    """Get locale-project pages/paths with stats."""
    locale = get_object_or_404(Locale, code=locale)
    project = get_object_or_404(Project, slug=slug)

    return JsonResponse(locale.parts_stats(project), safe=False)


@csrf_exempt
@require_POST
@require_AJAX
def entities(request):
    """Get entities for the specified project, locale and paths."""
    try:
        project = request.POST['project']
        locale = request.POST['locale']
        paths = request.POST.getlist('paths[]')
        limit = int(request.POST.get('limit', 50))
    except (MultiValueDictKeyError, ValueError) as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    project = get_object_or_404(Project, slug=project)
    locale = get_object_or_404(Locale, code__iexact=locale)

    filter_type = request.POST.get('filterType', '')
    filter_search = request.POST.get('filterSearch', '')

    exclude_entities = request.POST.getlist('excludeEntities[]', [])
    entities = Entity.for_project_locale(
        project, locale, paths, exclude_entities, filter_type, filter_search
    )

    # In-place view: load all entities
    if request.POST.get('inplaceEditor', None):
        has_next = False
        entities_to_map = entities

    # Out-of-context view: paginate entities
    else:
        paginator = Paginator(entities, limit)

        try:
            entities_page = paginator.page(1)
        except EmptyPage:
            return JsonResponse({
                'has_next': False,
                'stats': {},
            })

        has_next = entities_page.has_next()
        entities_to_map = entities_page.object_list

    return JsonResponse({
        'entities': Entity.map_entities(locale, entities_to_map),
        'has_next': has_next,
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    }, safe=False)


@require_AJAX
def get_translations_from_other_locales(request):
    """Get entity translations for all but specified locale."""
    try:
        entity = request.GET['entity']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    entity = get_object_or_404(Entity, pk=entity)
    locales = entity.resource.project.locales.exclude(code__iexact=locale)
    plural_form = None if entity.string_plural == "" else 0

    translations = Translation.objects.filter(
        entity=entity,
        locale__in=locales,
        plural_form=plural_form,
        approved=True
    )

    payload = list(translations.values('locale__code', 'locale__name', 'string'))
    return JsonResponse(payload, safe=False)


@require_AJAX
def get_translation_history(request):
    """Get history of translations of given entity to given locale."""
    try:
        entity = request.GET['entity']
        locale = request.GET['locale']
        plural_form = request.GET['plural_form']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    entity = get_object_or_404(Entity, pk=entity)
    locale = get_object_or_404(Locale, code__iexact=locale)

    translations = Translation.objects.filter(entity=entity, locale=locale)
    if plural_form != "-1":
        translations = translations.filter(plural_form=plural_form)
    translations = translations.order_by('-approved', '-date')

    payload = []
    offset = timezone.now().strftime('%z')

    for t in translations:
        u = t.user
        a = t.approved_user
        o = {
            "id": t.id,
            "user": "Imported" if u is None else u.name_or_email,
            "email": "" if u is None else u.email,
            "translation": t.string,
            "date": t.date.strftime('%b %d, %Y %H:%M'),
            "date_iso": t.date.isoformat() + offset,
            "approved": t.approved,
            "approved_user": "" if a is None else a.name_or_email,
        }
        payload.append(o)

    return JsonResponse(payload, safe=False)


@require_AJAX
@transaction.atomic
def delete_translation(request):
    """Delete given translation."""
    try:
        t = request.POST['translation']
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    translation = get_object_or_404(Translation, pk=t)

    # Non-privileged users can only delete own unapproved translations
    if not request.user.has_perm('base.can_translate_locale', translation.locale):
        if translation.user == request.user:
            if translation.approved is True:
                return HttpResponseForbidden(
                    "Forbidden: Can't delete approved translations"
                )
        else:
            return HttpResponseForbidden(
                "Forbidden: Can't delete translations from other users"
            )

    translation.delete()

    return JsonResponse({
        'stats': TranslatedResource.objects.stats(translation.entity.resource.project, paths, translation.locale)
    })


@anonymous_csrf_exempt
@require_POST
@require_AJAX
@transaction.atomic
def update_translation(request):
    """Update entity translation for the specified locale and user."""
    try:
        entity = request.POST['entity']
        string = request.POST['translation']
        locale = request.POST['locale']
        plural_form = request.POST['plural_form']
        original = request.POST['original']
        ignore_check = request.POST['ignore_check']
        approve = json.loads(request.POST['approve'])
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    try:
        e = Entity.objects.get(pk=entity)
    except Entity.DoesNotExist as error:
        log.error(str(error))
        return HttpResponse("error")

    try:
        l = Locale.objects.get(code__iexact=locale)
    except Locale.DoesNotExist as error:
        log.error(str(error))
        return HttpResponse("error")

    if plural_form == "-1":
        plural_form = None

    user = request.user
    if not request.user.is_authenticated():
        if e.resource.project.pk != 1:
            log.error("Not authenticated")
            return HttpResponse("error")
        else:
            user = None

    try:
        quality_checks = UserProfile.objects.get(user=user).quality_checks
    except UserProfile.DoesNotExist as error:
        quality_checks = True

    ignore = False
    if ignore_check == 'true' or not quality_checks:
        ignore = True

    now = timezone.now()
    can_translate = (
        request.user.has_perm('base.can_translate_locale', l)
        and (not request.user.profile.force_suggestions or approve)
    )
    translations = Translation.objects.filter(
        entity=e, locale=l, plural_form=plural_form)

    # Newlines are not allowed in .lang files (bug 1190754)
    if e.resource.format == 'lang' and '\n' in string:
        return HttpResponse('Newline characters are not allowed.')

    # Translations exist
    if len(translations) > 0:

        # Same translation exists
        try:
            t = translations.get(string=string)

            # If added by privileged user, approve and unfuzzy it
            if can_translate:

                # Unless there's nothing to be changed
                if t.user is not None and t.approved and t.approved_user \
                        and t.approved_date and not t.fuzzy:
                    return HttpResponse("Same translation already exists.")

                warnings = utils.quality_check(original, string, l, ignore)
                if warnings:
                    return warnings

                translations.update(approved=False, approved_user=None, approved_date=None)
                translations.update(fuzzy=False)

                if t.user is None:
                    t.user = user

                t.approved = True
                t.approved_date = timezone.now()
                t.fuzzy = False

                if t.approved_user is None:
                    t.approved_user = user
                    t.approved_date = now

                if request.user.is_authenticated():
                    t.save()

                return JsonResponse({
                    'type': 'updated',
                    'translation': t.serialize(),
                    'stats': TranslatedResource.objects.stats(e.resource.project, paths, l),
                })

            # If added by non-privileged user, unfuzzy it
            else:
                if t.fuzzy:
                    warnings = utils.quality_check(original, string, l, ignore)
                    if warnings:
                        return warnings

                    if t.user is None:
                        t.user = user

                    t.approved = False
                    t.approved_user = None
                    t.approved_date = None
                    t.fuzzy = False

                    if request.user.is_authenticated():
                        t.save()

                    return JsonResponse({
                        'type': 'updated',
                        'translation': t.serialize(),
                        'stats': TranslatedResource.objects.stats(e.resource.project, paths, l),
                    })

                return HttpResponse("Same translation already exists.")

        # Different translation added
        except:
            warnings = utils.quality_check(original, string, l, ignore)
            if warnings:
                return warnings

            if can_translate:
                translations.update(approved=False, approved_user=None, approved_date=None)

            translations.update(fuzzy=False)

            t = Translation(
                entity=e, locale=l, user=user, string=string,
                plural_form=plural_form, date=now,
                approved=can_translate)

            if can_translate:
                t.approved_user = user
                t.approved_date = now

            if request.user.is_authenticated():
                t.save()

            # Return active (approved or latest) translation
            try:
                active = translations.filter(approved=True).latest("date")
            except Translation.DoesNotExist:
                active = translations.latest("date")

            return JsonResponse({
                'type': 'added',
                'translation': active.serialize(),
                'stats': TranslatedResource.objects.stats(e.resource.project, paths, l)
            })

    # No translations saved yet
    else:
        warnings = utils.quality_check(original, string, l, ignore)
        if warnings:
            return warnings

        t = Translation(
            entity=e, locale=l, user=user, string=string,
            plural_form=plural_form, date=now,
            approved=can_translate)

        if can_translate:
            t.approved_user = user
            t.approved_date = now

        if request.user.is_authenticated():
            t.save()

        return JsonResponse({
            'type': 'saved',
            'translation': t.serialize(),
            'stats': TranslatedResource.objects.stats(e.resource.project, paths, l)
        })


def translation_memory(request):
    """Get translations from internal translations memory."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
        pk = request.GET['pk']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    max_results = 5
    locale = get_object_or_404(Locale, code__iexact=locale)
    entries = TranslationMemoryEntry.objects.minimum_levenshtein_ratio(text).filter(locale=locale)

    # Exclude existing entity
    if pk:
        entries = entries.exclude(entity__pk=pk)

    entries = entries.values('source', 'target', 'quality').order_by('-quality')
    suggestions = defaultdict(lambda: {'count': 0, 'quality': 0})

    try:
        for entry in entries:
            if entry['target'] not in suggestions or entry['quality'] > suggestions[entry['target']]['quality']:
                suggestions[entry['target']].update(entry)
            suggestions[entry['target']]['count'] += 1
    except DataError as e:
        # Catches 'argument exceeds the maximum length of 255 bytes' Error
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    return JsonResponse(sorted(suggestions.values(), key=lambda e: e['count'], reverse=True)[:max_results], safe=False)


def machine_translation(request):
    """Get translation from machine translation service."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
        check = request.GET['check']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

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

        # Parse XML response
        root = ET.fromstring(r.content)
        translation = root.text
        obj['translation'] = translation

        return JsonResponse(obj)

    except Exception as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))


def microsoft_terminology(request):
    """Get translations from Microsoft Terminology Service."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
        check = request.GET['check']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

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

        return JsonResponse(obj)

    except WebFault as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))


def amagama(request):
    """Get open source translations from amaGama service."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    try:
        text = urllib.quote(text.encode('utf-8'))
    except KeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    # No trailing slash at the end or slash becomes part of the source text
    url = (
        u'https://amagama-live.translatehouse.org/api/v1/en/{locale}/unit/'
        .format(locale=locale)
    )

    payload = {
        'source': text,
        'max_candidates': 5,
        'min_similarity': 70,
    }

    try:
        r = requests.get(url, params=payload)
        return JsonResponse(r.json(), safe=False)

    except Exception as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))


def transvision(request):
    """Get Mozilla translations from Transvision service."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    try:
        text = urllib.quote(text.encode('utf-8'))
    except KeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    url = (
        u'https://transvision.mozfr.org/api/v1/tm/global/en-US/{locale}/{text}/'
        .format(locale=locale, text=text)
    )

    payload = {
        'max_results': 5,
        'min_quality': 70,
    }

    try:
        r = requests.get(url, params=payload)
        if 'error' in r.json():
            error = r.json()['error']
            log.error('Transvision error: {error}'.format(error))
            return HttpResponseBadRequest('Bad Request: {error}'.format(error=error))

        return JsonResponse(r.json(), safe=False)

    except Exception as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))


@require_POST
@transaction.atomic
def download(request):
    """Download translated resource."""
    try:
        slug = request.POST['slug']
        code = request.POST['code']
        part = request.POST['part']
    except MultiValueDictKeyError:
        raise Http404

    content, filename = utils.get_download_content(slug, code, part)

    if not content:
        raise Http404

    response = HttpResponse()
    response.content = content
    response['Content-Type'] = 'text/plain'
    response['Content-Disposition'] = 'attachment; filename=' + filename

    return response


@login_required(redirect_field_name='', login_url='/403')
@require_POST
@transaction.atomic
def upload(request):
    """Upload translated resource."""
    try:
        slug = request.POST['slug']
        code = request.POST['code']
        part = request.POST['part']
    except MultiValueDictKeyError:
        raise Http404

    locale = get_object_or_404(Locale, code=code)
    if not request.user.has_perm('base.can_translate_locale', locale):
        return HttpResponseForbidden("Forbidden: You don't have permission to upload files")

    form = forms.UploadFileForm(request.POST, request.FILES)

    if form.is_valid():
        f = request.FILES['uploadfile']
        utils.handle_upload_content(slug, code, part, f, request.user)
        messages.success(request, 'Translations updated from uploaded file.')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)

    return translate(request, code, slug, part)


@login_required(redirect_field_name='', login_url='/403')
@require_POST
@transaction.atomic
def toggle_user_profile_attribute(request, email):
    user = get_object_or_404(User, email=email)
    if user != request.user:
        return HttpResponseForbidden("Forbidden: You don't have permission to edit this user")

    attribute = request.POST.get('attribute', None)
    if attribute not in ['quality_checks', 'force_suggestions']:
        return HttpResponseForbidden('Forbidden: Attribute not allowed')

    value = request.POST.get('value', None)
    if not value:
        return HttpResponseBadRequest('Bad Request: Value not set')

    profile = user.profile
    setattr(profile, attribute, json.loads(value))
    profile.save()

    return HttpResponse('ok')


@login_required(redirect_field_name='', login_url='/403')
@require_POST
@transaction.atomic
def save_user_name(request):
    """Save user name."""
    try:
        name = request.POST['name']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    if len(name) > 30:
        return HttpResponse('length')

    user = request.user
    user.first_name = name
    user.save()

    return HttpResponse('ok')


@login_required(redirect_field_name='', login_url='/403')
@require_POST
def request_projects(request, locale):
    """Request projects to be added to locale."""
    slug_list = request.POST.getlist('projects[]')
    locale = get_object_or_404(Locale, code__iexact=locale)

    # Validate projects
    project_list = Project.objects.available().filter(slug__in=slug_list)
    if not project_list:
        return HttpResponseBadRequest('Bad Request: Non-existent projects specified')

    projects = ''.join('- {} ({})\n'.format(p.name, p.slug) for p in project_list)

    if settings.ADMINS[0][1] != '':
        EmailMessage(
            'Project request for {locale} ({code})'.format(locale=locale.name, code=locale.code),
            'Please add the following projects to {locale} ({code}):\n{projects}'.format(
                locale=locale.name, code=locale.code, projects=projects
            ),
            'pontoon@mozilla.com',
            [settings.ADMINS[0][1]],
            reply_to=[request.user.email]).send()
    else:
        raise ImproperlyConfigured("ADMIN not defined in settings. Email recipient unknown.")

    return HttpResponse('ok')


@require_AJAX
def get_csrf(request):
    """Get CSRF token."""
    return HttpResponse(request.csrf_token)
