import json
import logging
import os
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
from django.core.validators import validate_comma_separated_integer_list
from django.db import transaction
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
    Stats,
    Translation,
    TranslationMemoryEntry,
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
    project = Project.objects.get(id=1)
    locale = utils.get_project_locale_from_request(
        request, project.locales) or 'en-GB'
    path = Resource.objects.filter(project=project, stats__locale__code=locale)[0].path

    return translate(request, locale, project.slug, path)


def locale(request, locale):
    """Locale view."""
    l = get_object_or_404(Locale, code__iexact=locale)

    projects = Project.objects.filter(
        disabled=False, pk__in=Resource.objects.values('project'), locales=l) \
        .order_by("name")

    if not projects:
        raise Http404

    return render(request, 'locale.html', {
        'projects': get_projects_with_stats(projects, l),
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
    return render(request, 'locales.html', {
        'locales': get_locales_with_stats(),
    })


def project(request, slug):
    """Project view."""
    p = get_object_or_404(Project, slug=slug, disabled=False,
            pk__in=Resource.objects.values('project'))

    return render(request, 'project.html', {
        'locales': get_locales_with_project_stats(p),
        'project': p,
        'project_locales': json.dumps(
            [i.lower() for i in p.locales.values_list('code', flat=True)]),
    })


def projects(request):
    """Project overview."""
    projects = (
        Project.objects
        .filter(disabled=False, resources__isnull=False)
        .select_related('latest_translation')
        .distinct()
        .order_by("name")
    )

    return render(request, 'projects.html', {
        'projects': get_projects_with_stats(projects),
    })


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

    return render(request, 'locale_project.html', {
        'locale': l,
        'project': project,
        'parts': parts,
    })


def translate(request, locale, slug, part):
    """Translate view."""
    locale = get_object_or_404(Locale, code__iexact=locale)
    project = get_object_or_404(
        Project.objects.distinct(),
        slug=slug,
        disabled=False,
        resources__isnull=False
    )

    projects = (
        Project.objects.filter(
            disabled=False,
            pk__in=Resource.objects.values('project')
        )
        .prefetch_related('subpage_set')
        .order_by("name")
    )

    return render(request, 'translate.html', {
        'accept_language': utils.get_project_locale_from_request(request, Locale.objects),
        'download_form': forms.DownloadFileForm(),
        'upload_form': forms.UploadFileForm(),
        'locale': locale,
        'locales': Locale.objects.all(),
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
def get_project_details(request, slug):
    """Get project locales with their pages/paths and stats."""
    project = get_object_or_404(Project, slug=slug)

    return JsonResponse({
        "slug": slug,
        "details": project.locales_parts_stats(),
    })


@require_AJAX
def entities(request):
    """Get entities for the specified project, locale and paths."""
    try:
        project = request.GET['project']
        locale = request.GET['locale']
        paths = json.loads(request.GET['paths'])
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

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
    return JsonResponse(entities, safe=False)


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
        log.error(str(e))
        return HttpResponse("error")

    entity = get_object_or_404(Entity, pk=entity)
    locale = get_object_or_404(Locale, code__iexact=locale)

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

        return JsonResponse(payload, safe=False)

    else:
        return HttpResponse("error")


@require_AJAX
@transaction.atomic
def delete_translation(request):
    """Delete given translation."""
    try:
        t = request.POST['translation']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

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

    return JsonResponse({
        'type': 'deleted',
        'next': next.id,
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
    except MultiValueDictKeyError as error:
        log.error(str(error))
        return HttpResponse("error")

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
        and not request.user.profile.force_suggestions
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

                return JsonResponse({
                    'type': 'updated',
                    'translation': t.serialize(),
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
                    })

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

            return JsonResponse({
                'type': 'added',
                'translation': active.serialize(),
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
        })


def translation_memory(request):
    """Get translations from internal translations memory."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
        pk = request.GET['pk']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse('error')

    try:
        locale = Locale.objects.get(code__iexact=locale)
    except Locale.DoesNotExist as e:
        log.error(e)
        return HttpResponse('error')

    max_results = 5
    entries = TranslationMemoryEntry.objects.minimum_levenshtein_ratio(text).filter(locale=locale)

    # Exclude existing entity
    if pk:
        entries = entries.exclude(entity__pk=pk)

    entries = entries.values('source', 'target', 'quality').order_by('-quality')
    suggestions = defaultdict(lambda: {'count': 0, 'quality': 0})

    for entry in entries:
        if entry['target'] not in suggestions or entry['quality'] > suggestions[entry['target']]['quality']:
            suggestions[entry['target']].update(entry)
        suggestions[entry['target']]['count'] += 1

    if len(suggestions) > 0:
        return JsonResponse({
            'translations': sorted(suggestions.values(), key=lambda e: e['count'], reverse=True)[:max_results],
        })
    else:
        return HttpResponse('no')


def machine_translation(request):
    """Get translation from machine translation service."""
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
        log.error(e)
        return HttpResponse("error")


def microsoft_terminology(request):
    """Get translations from Microsoft Terminology Service."""
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
        log.error(e)
        return HttpResponse("error")


def amagama(request):
    """Get open source translations from amaGama service."""
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

            return JsonResponse({
                'translations': translations
            })

        else:
            return HttpResponse("no")

    except Exception as e:
        log.error(e)
        return HttpResponse("error")


def transvision(request):
    """Get Mozilla translations from Transvision service."""

    try:
        text = request.GET['text']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

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
        if r.text != '[]':
            return JsonResponse(r.json(), safe=False)
        else:
            return HttpResponse("no")

    except Exception as e:
        log.error(e)
        return HttpResponse("error")


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

    content, path = utils.get_download_content(slug, code, part)

    if not content:
        raise Http404

    filename = os.path.basename(path)
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
        log.error(str(e))
        return HttpResponse("error")

    if len(name) > 30:
        return HttpResponse("length")

    user = request.user
    user.first_name = name
    user.save()

    return HttpResponse("ok")


@login_required(redirect_field_name='', login_url='/403')
@require_POST
def request_locale(request):
    """Request new locale to be added to project."""
    try:
        project = request.POST['project']
        locale = request.POST['locale']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    project = get_object_or_404(Project, slug=project)
    locale = get_object_or_404(Locale, code__iexact=locale)

    if settings.ADMINS[0][1] != '':
        EmailMessage(
            'Locale request: {locale} ({code})'.format(locale=locale.name, code=locale.code),
            'Please add locale {locale} ({code}) to project {project} ({slug}).'.format(
                locale=locale.name, code=locale.code, project=project.name, slug=project.slug
            ),
            'pontoon@mozilla.com',
            [settings.ADMINS[0][1]],
            reply_to=[request.user.email]).send()
    else:
        raise ImproperlyConfigured("ADMIN not defined in settings. Email recipient unknown.")

    return HttpResponse()


@require_AJAX
def get_csrf(request):
    """Get CSRF token."""
    return HttpResponse(request.csrf_token)
