import base64
import hashlib
import json
import Levenshtein
import logging
import math
import requests
import xml.etree.ElementTree as ET
import urllib

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_comma_separated_integer_list
from django.db import transaction
from django.db.models import Count, F, Q

from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
)

from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from guardian.decorators import permission_required_or_403
from operator import itemgetter
from pontoon.administration import files
from pontoon.base import utils

from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    Resource,
    Stats,
    Translation,
    UserProfile,
    get_locales_with_project_stats,
    get_locales_with_stats,
    get_projects_with_stats,
    get_translation,
    unapprove,
    unfuzzy,
)

from session_csrf import anonymous_csrf_exempt
from suds.client import Client, WebFault


log = logging.getLogger('pontoon')


def home(request):
    """Home view."""
    log.debug("Home view.")

    project = Project.objects.get(id=1)
    locale = utils.get_project_locale_from_request(
        request, project.locales) or 'en-GB'
    path = Resource.objects.filter(project=project, stats__locale__code=locale)[0].path

    return translate(request, locale, project.slug, path)


def locale(request, locale, template='locale.html'):
    """Locale view."""
    log.debug("Locale view.")

    # Validate locale
    l = get_object_or_404(Locale, code__iexact=locale)

    projects = Project.objects.filter(
        disabled=False, pk__in=Resource.objects.values('project'), locales=l) \
        .order_by("name")

    if not projects:
        raise Http404

    data = {
        'projects': get_projects_with_stats(projects, l),
        'locale': l,
    }

    return render(request, template, data)


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
                log.debug(e)
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

    data = {
        'locale': l,
        'all_users': all_users,
        'contributors': contributors,
        'translators': translators,
        'managers': managers,
    }

    return render(request, 'locale_manage.html', data)


def locales(request):
    """Localization teams."""

    data = {
        'locales': get_locales_with_stats(),
    }

    return render(request, 'locales.html', data)


def project(request, slug, template='project.html'):
    """Project view."""
    log.debug("Project view.")

    p = get_object_or_404(Project, slug=slug, disabled=False,
            pk__in=Resource.objects.values('project'))

    data = {
        'locales': get_locales_with_project_stats(p),
        'project': p,
        'project_locales': json.dumps(
            [i.lower() for i in p.locales.values_list('code', flat=True)]),
    }

    return render(request, template, data)


def projects(request, template='projects.html'):
    """Project overview."""
    log.debug("Project overview.")

    projects = (
        Project.objects
        .filter(disabled=False, resources__isnull=False)
        .select_related('latest_translation')
        .distinct()
        .order_by("name")
    )

    data = {
        'projects': get_projects_with_stats(projects),
    }

    return render(request, template, data)


def locale_project(request, locale, slug):
    """Locale-project overview."""
    l = get_object_or_404(Locale, code__iexact=locale)

    projects = Project.objects.prefetch_related('subpage_set').distinct()
    project = get_object_or_404(projects, disabled=False, slug=slug, resources__isnull=False)

    # Amend the parts dict with latest activity info.
    stats_qs = (
        Stats.objects
        .filter(resource__project=project, locale=l)
        .select_related('resource', 'latest_translation')
    )
    stats = {s.resource.path: s for s in stats_qs}
    parts = project.locales_parts_stats(l)
    for part in parts:
        stat = stats.get(part['resource__path'], None)
        part['latest_activity'] = stat.latest_translation if stat else None

    data = {
        'locale': l,
        'project': project,
        'parts': parts,
    }

    return render(request, 'locale_project.html', data)


def translate(request, locale, slug, part):
    """Translate view."""

    # Validate locale and project
    l = get_object_or_404(Locale, code__iexact=locale)
    p = get_object_or_404(
        Project.objects.distinct(),
        slug=slug,
        disabled=False,
        resources__isnull=False
    )

    # Check if user authenticated
    if not request.user.is_authenticated() and not p.pk == 1:
        return render(request, '403.html', status=403)

    projects = (
        Project.objects.filter(
            disabled=False,
            pk__in=Resource.objects.values('project')
        )
        .prefetch_related('subpage_set')
        .order_by("name")
    )

    data = {
        'accept_language': utils.get_project_locale_from_request(request, Locale.objects),
        'locale': l,
        'locales': Locale.objects.all(),
        'part': part,
        'project': p,
        'projects': projects,
    }

    return render(request, 'translate.html', data)


@login_required(redirect_field_name='', login_url='/403')
def profile(request):
    """Current user profile."""
    log.debug("Current user profile.")

    return contributor(request, request.user.email)


def contributor(request, email, template='user.html'):
    """Contributor profile."""
    log.debug("Contributor profile.")

    # Validate user
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise Http404

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

    data = {
        'contributor': user,
        'timeline': timeline,
        'translations': translations,
    }

    return render(request, template, data)


class ContributorsMixin(object):
    def contributors_filter(self, **kwargs):
        """
        Return Q() filters for fetching contributors. Fetches all by default.
        """
        return None

    def get_context_data(self, **kwargs):
        """Top contributors view."""
        log.debug("Top contributors view.")

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


def search(request, template='search.html'):
    """Terminology search view."""
    log.debug("Terminology search view.")

    locale = utils.get_project_locale_from_request(
        request, Locale.objects) or 'en-GB'

    data = {
        'locale': Locale.objects.get(code__iexact=locale),
        'locales': Locale.objects.all(),
    }

    return render(request, template, data)


def get_project_details(request, slug):
    """Get project locales with their pages/paths and stats."""
    if not request.is_ajax():
        return HttpResponseBadRequest('Bad Request: Request must be AJAX')

    project = get_object_or_404(Project, slug=slug)

    data = {
        "slug": slug,
        "details": project.locales_parts_stats(),
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


def entities(request, template=None):
    """Get entities for the specified project, locale and paths."""
    log.debug("Get entities for the specified project, locale and paths.")

    if not request.is_ajax():
        log.error("Non-AJAX request")
        raise Http404

    try:
        project = request.GET['project']
        locale = request.GET['locale']
        paths = json.loads(request.GET['paths'])
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    log.debug("Project: " + project)
    log.debug("Locale: " + locale)
    log.debug("Paths: " + str(paths))

    try:
        project = Project.objects.get(slug=project)
    except Entity.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    try:
        locale = Locale.objects.get(code__iexact=locale)
    except Locale.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    search = None
    if request.GET.get('keyword', None):
        search = request.GET

    entities = Entity.for_project_locale(project, locale, paths, search)
    return HttpResponse(json.dumps(entities), content_type='application/json')


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
        locale = Locale.objects.get(code__iexact=locale)
    except Locale.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    payload = []
    locales = entity.resource.project.locales.all().exclude(
        code__iexact=locale.code)

    for l in locales:
        plural_form = None if entity.string_plural == "" else 0
        translation = get_translation(
            entity=entity, locale=l, plural_form=plural_form)

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
            json.dumps(payload, indent=4), content_type='application/json')


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
        locale = Locale.objects.get(code__iexact=locale)
    except Locale.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    translations = Translation.objects.filter(entity=entity, locale=locale)
    if plural_form != "-1":
        translations = translations.filter(plural_form=plural_form)
    translations = translations.order_by('-approved', '-date')

    if len(translations) > 0:
        payload = []
        offset = timezone.now().strftime('%z')

        for t in translations:
            u = t.user
            a = t.approved_user
            o = {
                "id": t.id,
                "user": "Imported" if u is None else u.first_name or u.email,
                "email": "" if u is None else u.email,
                "translation": t.string,
                "date": t.date.strftime('%b %d, %Y %H:%M'),
                "date_iso": t.date.isoformat() + offset,
                "approved": t.approved,
                "approved_user": "" if a is None else a.first_name or a.email,
            }
            payload.append(o)

        return HttpResponse(
            json.dumps(payload, indent=4), content_type='application/json')

    else:
        log.debug("Translations do not exist")
        return HttpResponse("error")


@transaction.atomic
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
    if not request.user.has_perm('base.can_translate_locale', translation.locale):
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

    # Mark next translation approved if needed
    next = get_translation(
        entity=entity, locale=locale, plural_form=plural_form)

    if next.pk is not None and request.user.has_perm('base.can_translate_locale', next.locale):
        next.approved = True
        next.approved_user = request.user
        next.approved_date = timezone.now()
        next.save()

    return HttpResponse(json.dumps({
        'type': 'deleted',
        'next': next.id,
    }), content_type='application/json')


@anonymous_csrf_exempt
@transaction.atomic
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
    except MultiValueDictKeyError as error:
        log.error(str(error))
        return HttpResponse("error")

    log.debug("Entity: " + entity)
    log.debug("Translation: " + string)
    log.debug("Locale: " + locale)

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
    can_translate = request.user.has_perm('base.can_translate_locale', l)
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

                unapprove(translations)
                unfuzzy(translations)

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

                return HttpResponse(json.dumps({
                    'type': 'updated',
                    'translation': t.serialize(),
                }), content_type='application/json')

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

                    return HttpResponse(json.dumps({
                        'type': 'updated',
                        'translation': t.serialize(),
                    }), content_type='application/json')

                return HttpResponse("Same translation already exists.")

        # Different translation added
        except:
            warnings = utils.quality_check(original, string, l, ignore)
            if warnings:
                return warnings

            if can_translate:
                unapprove(translations)

            unfuzzy(translations)

            t = Translation(
                entity=e, locale=l, user=user, string=string,
                plural_form=plural_form, date=now,
                approved=can_translate)

            if can_translate:
                t.approved_user = user
                t.approved_date = now

            if request.user.is_authenticated():
                t.save()

            active = get_translation(
                entity=e, locale=l, plural_form=plural_form)

            return HttpResponse(json.dumps({
                'type': 'added',
                'translation': active.serialize(),
            }), content_type='application/json')

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

        return HttpResponse(json.dumps({
            'type': 'saved',
            'translation': t.serialize(),
        }), content_type='application/json')


def translation_memory(request):
    """Get translations from internal translations."""
    log.debug("Get translations from internal translations.")

    try:
        text = request.GET['text']
        locale = request.GET['locale']
        pk = request.GET['pk']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    try:
        locale = Locale.objects.get(code__iexact=locale)
    except Locale.DoesNotExist as e:
        log.error(e)
        return HttpResponse("error")

    min_quality = 0.7
    max_results = 5
    length = len(text)
    min_dist = math.ceil(max(length * min_quality, 2))
    max_dist = math.floor(min(length / min_quality, 1000))

    # Only check entities with similar length
    entities = Entity.objects.all().extra(
        where=["CHAR_LENGTH(string) BETWEEN %s AND %s" % (min_dist, max_dist)])

    # Exclude existing entity
    if pk:
        entities = entities.exclude(pk=pk)

    translations = {}

    for e in entities:
        source = e.string
        quality = Levenshtein.ratio(text, source)

        if quality > min_quality:
            plural_form = None if e.string_plural == "" else 0
            translation = get_translation(
                entity=e, locale=locale, fuzzy=False, plural_form=plural_form)

            if translation.string != '' or translation.pk is not None:
                count = 1
                quality = quality * 100

                if translation.string in translations:
                    existing = translations[translation.string]
                    count = existing['count'] + 1

                    # Store data for best match among equal translations only
                    if quality < existing['quality']:
                        quality = existing['quality']
                        source = existing['source']

                translations[translation.string] = {
                    'source': source,
                    'quality': quality,
                    'count': count,
                }

    if len(translations) > 0:
        # Sort by translation count
        t = sorted(translations.iteritems(), key=itemgetter(1), reverse=True)
        translations_array = []

        for a, b in t[:max_results]:
            b["target"] = a
            translations_array.append(b)

        return HttpResponse(json.dumps({
            'translations': translations_array
        }), content_type='application/json')

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

        return HttpResponse(json.dumps(obj), content_type='application/json')

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

        return HttpResponse(json.dumps(obj), content_type='application/json')

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
            }), content_type='application/json')

        else:
            return HttpResponse("no")

    except Exception as e:
        log.error(e)
        return HttpResponse("error")


def transvision(request, repo, title):
    """Get Mozilla translations from Transvision service."""
    log.debug("Get Mozilla translations from Transvision service.")

    try:
        text = request.GET['text']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    src = "en-US"
    url = "https://transvision.mozfr.org/api/v1/tm/%s/%s/" \
          "%s/%s/?max_results=%s&min_quality=70" % (repo, src, locale, text, 5)

    try:
        r = requests.get(url)

        if r.text != '[]':
            translations = r.json()

            return HttpResponse(json.dumps({
                'translations': translations,
                'title': title,
            }), content_type='application/json')

        else:
            return HttpResponse("no")

    except Exception as e:
        log.error(e)
        return HttpResponse("error")


def transvision_aurora(request):
    return transvision(request, "aurora", "Mozilla Aurora")


def transvision_gaia(request):
    return transvision(request, "gaia", "Firefox OS")


def transvision_mozilla_org(request):
    return transvision(request, "mozilla_org", "Mozilla.org")


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
        p = Project.objects.get(slug=project)
    except Project.DoesNotExist as e:
        log.error(e)
        raise Http404

    filename = '%s-%s' % (project, locale)
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
    profile = UserProfile.objects.get(user=request.user)

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


@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def quality_checks_switch(request):
    """Turn quality checks on/off for the current user."""
    log.debug("Turn quality checks on/off for the current user.")

    if request.method != 'POST':
        log.error("Non-POST request")
        raise Http404

    profile = request.user.profile
    profile.quality_checks = not profile.quality_checks
    profile.save()

    return HttpResponse("ok")


@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def save_user_name(request):
    """Save user name."""
    log.debug("Save user name.")

    if request.method != 'POST':
        log.error("Non-POST request")
        raise Http404

    try:
        name = request.POST['name']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    if len(name) > 30:
        return HttpResponse("length")

    log.debug("New name: " + name)

    user = request.user
    user.first_name = name
    user.save()

    return HttpResponse("ok")


@login_required(redirect_field_name='', login_url='/403')
def request_locale(request):
    """Request new locale to be added to project."""
    log.debug("Request new locale to be added to project.")

    if request.method != 'POST':
        log.error("Non-POST request")
        raise Http404

    try:
        project = request.POST['project']
        locale = request.POST['locale']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    log.debug("Project: " + project)
    log.debug("Locale: " + locale)

    try:
        project = Project.objects.get(slug=project)
    except Entity.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    try:
        locale = Locale.objects.get(code__iexact=locale)
    except Locale.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    subject = '[Pontoon] Locale Request'
    message = 'Add locale %s (%s) to project %s (%s).' % (
        locale.name, locale.code, project.name, project.slug)
    sender = request.user.email

    if settings.ADMINS[0][1] != '':
        recipients = [settings.ADMINS[0][1]]
        send_mail(subject, message, sender, recipients)
    else:
        log.error("ADMIN not defined in settings. Email recipient unknown.")
        return HttpResponse("error")

    return HttpResponse()


def get_csrf(request, template=None):
    """Get CSRF token."""
    log.debug("Get CSRF token.")

    if not request.is_ajax():
        log.error("Non-AJAX request")
        raise Http404

    return HttpResponse(request.csrf_token)
