import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import Q, Count
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.views.decorators.http import require_POST
from django.views.generic.detail import DetailView

import bleach
from guardian.decorators import permission_required_or_403

from pontoon.base import forms
from pontoon.base.models import Locale, Project
from pontoon.base.utils import require_AJAX
from pontoon.contributors.views import ContributorsMixin
from pontoon.teams.forms import LocaleRequestForm


def teams(request):
    """List all active localization teams."""
    locales = (
        Locale.objects.visible()
        .prefetch_related('latest_translation__user')
    )

    form = LocaleRequestForm()

    if not locales:
        raise Http404

    return render(request, 'teams/teams.html', {
        'locales': locales,
        'form': form,
        'top_instances': locales.get_top_instances(),
    })


def team(request, locale):
    """Team dashboard."""
    locale = get_object_or_404(Locale, code=locale)
    count = locale.project_set.visible().count()

    if not count:
        raise Http404

    return render(request, 'teams/team.html', {
        'count': count,
        'locale': locale,
    })


@require_AJAX
def ajax_projects(request, locale):
    """Projects tab."""
    locale = get_object_or_404(Locale, code=locale)

    projects = (
        Project.objects.visible()
        .filter(Q(locales=locale) | Q(can_be_requested=True))
        .prefetch_project_locale(locale)
        .order_by('name')
        .annotate(enabled_locales=Count('project_locale', distinct=True))
    )

    if not projects:
        raise Http404

    return render(request, 'teams/includes/projects.html', {
        'locale': locale,
        'projects': projects,
    })


@require_AJAX
def ajax_info(request, locale):
    """Info tab."""
    locale = get_object_or_404(Locale, code=locale)

    return render(request, 'teams/includes/info.html', {
        'locale': locale,
    })


@require_POST
@permission_required_or_403('base.can_manage_locale', (Locale, 'code', 'locale'))
@transaction.atomic
def ajax_update_info(request, locale):
    team_description = request.POST.get('team_info', None)
    team_description = bleach.clean(
        team_description, strip=True,
        tags=settings.ALLOWED_TAGS, attributes=settings.ALLOWED_ATTRIBUTES
    )
    locale = get_object_or_404(Locale, code=locale)
    locale.team_description = team_description
    locale.save()
    return HttpResponse(team_description)


@permission_required_or_403('base.can_manage_locale', (Locale, 'code', 'locale'))
@transaction.atomic
def ajax_permissions(request, locale):
    locale = get_object_or_404(Locale, code=locale)
    project_locales = locale.project_locale.visible()

    if request.method == 'POST':
        locale_form = forms.LocalePermsForm(
            request.POST,
            instance=locale,
            prefix='general',
            user=request.user
        )
        project_locale_form = forms.ProjectLocalePermsFormsSet(
            request.POST,
            prefix='project-locale',
            queryset=project_locales,
            form_kwargs={
                'user': request.user
            }
        )

        if locale_form.is_valid() and project_locale_form.is_valid():
            locale_form.save()
            project_locale_form.save()

        else:
            errors = locale_form.errors
            errors.update(project_locale_form.errors_dict)
            return HttpResponseBadRequest(json.dumps(errors))

    else:
        project_locale_form = forms.ProjectLocalePermsFormsSet(
            prefix='project-locale',
            queryset=project_locales,
            form_kwargs={
                'user': request.user
            }
        )

    managers = locale.managers_group.user_set.order_by('email')
    translators = locale.translators_group.user_set.exclude(pk__in=managers).order_by('email')
    all_users = (
        User.objects
            .exclude(pk__in=managers | translators)
            .exclude(email='')
            .order_by('email')
    )

    contributors_emails = set(
        contributor.email
        for contributor in User.translators.with_translation_counts(None, Q(locale=locale), None)
    )

    locale_projects = locale.projects_permissions

    return render(request, 'teams/includes/permissions.html', {
        'locale': locale,
        'all_users': all_users,
        'contributors_emails': contributors_emails,
        'translators': translators,
        'managers': managers,
        'locale_projects': locale_projects,
        'project_locale_form': project_locale_form,
        'all_projects_in_translation': all([x[5] for x in locale_projects])
    })


@login_required(redirect_field_name='', login_url='/403')
@require_POST
def request_item(request, _type=None, code=None):
    """Request projects and teams to be added."""
    user = request.user

    # Request projects to be enabled for team
    if code and _type == 'projects':
        slug_list = request.POST.getlist('items[]')
        locale = get_object_or_404(Locale, code=code)

        # Validate projects
        project_list = (
            Project.objects.visible()
            .filter(slug__in=slug_list, can_be_requested=True)
        )
        if not project_list:
            return HttpResponseBadRequest('Bad Request: Non-existent projects specified')

        projects = ''.join('- {} ({})\n'.format(p.name, p.slug) for p in project_list)

        mail_subject = u'Project request for {locale} ({code})'.format(
            locale=locale.name, code=locale.code
        )

        payload = {
            'locale': locale.name,
            'code': locale.code,
            'projects': projects,
            'user': user.display_name_and_email,
            'user_role': user.locale_role(locale),
            'user_url': request.build_absolute_uri(user.profile_url)
        }

    # Request teams to be enabled for project
    elif code and _type == 'teams':
        code_list = request.POST.getlist('items[]')
        project = get_object_or_404(Project, slug=code)

        # Validate projects
        locale_list = (
            Locale.objects.available()
            .filter(code__in=code_list)
        )
        if not locale_list:
            return HttpResponseBadRequest('Bad Request: Non-existent teams specified')

        locales = ''.join('- {} ({})\n'.format(l.name, l.code) for l in locale_list)

        mail_subject = u'Team request for {project} ({slug})'.format(
            project=project.name, slug=project.slug
        )

        payload = {
            'project': project.name,
            'slug': project.slug,
            'locales': locales,
            'user': user.display_name_and_email,
            'user_role': user.role(),
            'user_url': request.build_absolute_uri(user.profile_url)
        }

    # Request new teams to be enabled
    else:
        form = LocaleRequestForm(request.POST)
        if not form.is_valid():
            if form.has_error('code', 'unique'):
                return HttpResponse('This team already exists.', status=409)
            return HttpResponseBadRequest(form.errors.as_json())

        code = form.cleaned_data['code']
        name = form.cleaned_data['name']

        mail_subject = u'New team request: {locale} ({code})'.format(
            locale=name, code=code
        )

        payload = {
            'locale': name,
            'code': code,
            'user': user.display_name_and_email,
            'user_role': user.role(),
            'user_url': request.build_absolute_uri(user.profile_url)
        }

    if settings.PROJECT_MANAGERS[0] != '':
        template = get_template('teams/email_request_item.jinja')
        mail_body = template.render(payload)

        EmailMessage(
            subject=mail_subject,
            body=mail_body,
            from_email='pontoon@mozilla.com',
            to=settings.PROJECT_MANAGERS,
            cc=locale.managers_group.user_set.exclude(pk=user.pk)
            .values_list('email', flat=True) if _type is not None else '',
            reply_to=[user.email],
        ).send()
    else:
        raise ImproperlyConfigured(
            "PROJECT_MANAGERS not defined in settings. Email recipient unknown."
        )

    return HttpResponse('ok')


class LocaleContributorsView(ContributorsMixin, DetailView):
    """
    Renders view of contributors for the team.
    """
    template_name = 'teams/includes/contributors.html'
    model = Locale
    slug_field = 'code'
    slug_url_kwarg = 'code'

    def get_context_object_name(self, obj):
        return 'locale'

    def contributors_filter(self, **kwargs):
        return Q(locale=self.object)
