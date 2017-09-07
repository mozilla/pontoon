import json

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Count
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from pontoon.base import forms
from pontoon.base.models import Locale, Project
from pontoon.base.utils import require_AJAX


@login_required(redirect_field_name='', login_url='/403')
def profile(request):
    """Current user profile."""
    return contributor(request, request.user)


def contributor_email(request, email):
    user = get_object_or_404(User, email=email)
    return contributor(request, user)


def contributor_username(request, username):
    user = get_object_or_404(User, username=username)
    return contributor(request, user)


def contributor_timeline(request, username):
    """Contributor events in the timeline."""
    user = get_object_or_404(User, username=username)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        raise Http404('Invalid page number.')

    # Exclude obsolete translations
    contributor_translations = (
        user.contributed_translations
            .exclude(entity__obsolete=True)
            .extra({'day': "date(date)"})
            .order_by('-day')
    )

    counts_by_day = contributor_translations.values('day').annotate(count=Count('id'))

    try:
        events_paginator = Paginator(counts_by_day, 10)
        timeline_events = []

        timeline_events = User.objects.map_translations_to_events(
            events_paginator.page(page).object_list,
            contributor_translations
        )

        # Join is the last event in this reversed order.
        if page == events_paginator.num_pages:
            timeline_events.append({
                'date': user.date_joined,
                'type': 'join'
            })

    except EmptyPage:
        # Return the join event if user reaches the last page.
        raise Http404('No events.')

    return render(request, 'contributors/includes/timeline.html', {
        'events': timeline_events
    })


def contributor(request, user):
    """Contributor profile."""

    return render(request, 'contributors/profile.html', {
        'contributor': user,
        'translations': user.contributed_translations
    })


@login_required(redirect_field_name='', login_url='/403')
@require_POST
@transaction.atomic
def toggle_user_profile_attribute(request, username):
    user = get_object_or_404(User, username=username)
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
    form = forms.UserFirstNameForm(request.POST, instance=request.user)

    if not form.is_valid():
        return HttpResponseBadRequest(u'\n'.join(form.errors['first_name']))

    form.save()

    return HttpResponse('ok')


@login_required(redirect_field_name='', login_url='/403')
@require_POST
@transaction.atomic
def save_custom_homepage(request):
    """Save custom homepage."""
    form = forms.UserCustomHomepageForm(request.POST, instance=request.user.profile)

    if not form.is_valid():
        return HttpResponseBadRequest(u'\n'.join(form.errors['custom_homepage']))

    form.save()

    return HttpResponse('ok')


@login_required(redirect_field_name='', login_url='/403')
def settings(request):
    """View and edit user settings."""
    if request.method == 'POST':
        form = forms.UserLocalesOrderForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings saved.')
            return redirect(request.POST.get('return_url', '/'))

    selected_locales = list(request.user.profile.sorted_locales)
    available_locales = Locale.objects.exclude(pk__in=[l.pk for l in selected_locales])

    default_homepage_locale = Locale(name='Default homepage', code='')
    all_locales = list(Locale.objects.all())
    all_locales.insert(0, default_homepage_locale)

    # Set custom homepage selector value
    custom_homepage = request.user.profile.custom_homepage
    if custom_homepage:
        custom_homepage_locale = Locale.objects.filter(code=custom_homepage).first()
    else:
        custom_homepage_locale = default_homepage_locale

    return render(request, 'contributors/settings.html', {
        'selected_locales': selected_locales,
        'available_locales': available_locales,
        'locales': all_locales,
        'locale': custom_homepage_locale,
    })


@login_required(redirect_field_name='', login_url='/403')
def notifications(request):
    """View and edit user notifications."""
    notifications = request.user.notifications.prefetch_related('actor', 'target').order_by('-pk')
    projects = {}

    for notification in notifications:
        project = None
        if isinstance(notification.actor, Project):
            project = notification.actor
        elif isinstance(notification.target, Project):
            project = notification.target

        if project:
            if project.slug in projects:
                projects[project.slug]['notifications'].append(
                    notification.id
                )
            else:
                projects[project.slug] = {
                    'name': project.name,
                    'notifications': [notification.id],
                }

    # Sort projects by the number of notifications
    ordered_projects = []
    for slug in sorted(
        projects, key=lambda slug: len(projects[slug]['notifications']), reverse=True
    ):
        ordered_projects.append(slug)

    return render(request, 'contributors/notifications.html', {
        'notifications': notifications,
        'projects': projects,
        'ordered_projects': ordered_projects,
    })


@login_required(redirect_field_name='', login_url='/403')
@require_AJAX
@transaction.atomic
def mark_all_notifications_as_read(request):
    """Mark all notifications of the currently logged in user as read"""
    request.user.notifications.mark_all_as_read()

    return HttpResponse('ok')


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

        context['contributors'] = (
            User.translators
            .with_translation_counts(start_date, self.contributors_filter(**kwargs))
        )
        context['period'] = period
        return context


class ContributorsView(ContributorsMixin, TemplateView):
    """
    View returns top contributors.
    """
    template_name = 'contributors/contributors.html'
