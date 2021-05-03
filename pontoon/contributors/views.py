import json

from dateutil.relativedelta import relativedelta
from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Q, Count
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.utils.html import escape

from pontoon.base import forms
from pontoon.base.models import Locale, Project
from pontoon.base.utils import require_AJAX
from pontoon.contributors.utils import (
    map_translations_to_events,
    users_with_translations_counts,
)
from pontoon.uxactionlog.utils import log_ux_action


@login_required(redirect_field_name="", login_url="/403")
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
        page = int(request.GET.get("page", 1))
    except ValueError:
        raise Http404("Invalid page number.")

    # Exclude obsolete translations
    contributor_translations = (
        user.contributed_translations.exclude(entity__obsolete=True)
        .extra({"day": "date(date)"})
        .order_by("-day")
    )

    counts_by_day = contributor_translations.values("day").annotate(count=Count("id"))

    try:
        events_paginator = Paginator(
            counts_by_day, django_settings.CONTRIBUTORS_TIMELINE_EVENTS_PER_PAGE
        )

        timeline_events = map_translations_to_events(
            events_paginator.page(page).object_list, contributor_translations
        )

        # Join is the last event in this reversed order.
        if page == events_paginator.num_pages:
            timeline_events.append({"date": user.date_joined, "type": "join"})

    except EmptyPage:
        # Return the join event if user reaches the last page.
        raise Http404("No events.")

    return render(
        request, "contributors/includes/timeline.html", {"events": timeline_events}
    )


def contributor(request, user):
    """Contributor profile."""

    return render(
        request,
        "contributors/profile.html",
        {"contributor": user, "translations": user.contributed_translations},
    )


@login_required(redirect_field_name="", login_url="/403")
@require_POST
@transaction.atomic
def toggle_user_profile_attribute(request, username):
    user = get_object_or_404(User, username=username)
    if user != request.user:
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: You don't have permission to edit this user",
            },
            status=403,
        )

    attribute = request.POST.get("attribute", None)
    if attribute not in ["quality_checks", "force_suggestions"]:
        return JsonResponse(
            {"status": False, "message": "Forbidden: Attribute not allowed"},
            status=403,
        )

    value = request.POST.get("value", None)
    if not value:
        return JsonResponse(
            {"status": False, "message": "Bad Request: Value not set"}, status=400
        )

    profile = user.profile
    setattr(profile, attribute, json.loads(value))
    profile.save()

    return JsonResponse({"status": True})


@login_required(redirect_field_name="", login_url="/403")
@require_POST
@transaction.atomic
def save_custom_homepage(request):
    """Save custom homepage."""
    form = forms.UserCustomHomepageForm(request.POST, instance=request.user.profile)

    if not form.is_valid():
        error = escape("\n".join(form.errors["custom_homepage"]))
        return HttpResponseBadRequest(error)

    form.save()

    return HttpResponse("ok")


@login_required(redirect_field_name="", login_url="/403")
@require_POST
@transaction.atomic
def save_preferred_source_locale(request):
    """Save preferred source locale."""
    form = forms.UserPreferredSourceLocaleForm(
        request.POST, instance=request.user.profile,
    )

    if not form.is_valid():
        error = escape("\n".join(form.errors["preferred_source_locale"]))
        return HttpResponseBadRequest(error)

    form.save()

    return HttpResponse("ok")


@login_required(redirect_field_name="", login_url="/403")
@require_AJAX
@transaction.atomic
def dismiss_addon_promotion(request):
    profile = request.user.profile
    profile.has_dismissed_addon_promotion = True
    profile.save()

    return JsonResponse({"status": True})


@login_required(redirect_field_name="", login_url="/403")
def settings(request):
    """View and edit user settings."""
    if request.method == "POST":
        locales_form = forms.UserLocalesOrderForm(
            request.POST, instance=request.user.profile,
        )
        profile_form = forms.UserProfileForm(request.POST, instance=request.user,)
        user = get_object_or_404(User, username=request.user.username)

        if locales_form.is_valid() and profile_form.is_valid():
            locales_form.save()
            profile_form.save()

            messages.success(request, "Settings saved.")

            if user.email != request.user.email:
                logout(request)
                return redirect(request.POST.get("return_url", "/"))
    else:
        profile_form = forms.UserProfileForm(instance=request.user)

    selected_locales = list(request.user.profile.sorted_locales)
    available_locales = Locale.objects.exclude(pk__in=[l.pk for l in selected_locales])

    default_homepage_locale = Locale(name="Default homepage", code="")
    all_locales = list(Locale.objects.all())
    all_locales.insert(0, default_homepage_locale)

    # Set custom homepage selector value
    custom_homepage_locale = request.user.profile.custom_homepage
    if custom_homepage_locale:
        custom_homepage_locale = Locale.objects.filter(
            code=custom_homepage_locale
        ).first()
    else:
        custom_homepage_locale = default_homepage_locale

    default_preferred_source_locale = Locale(name="Default project locale", code="")
    preferred_locales = list(Locale.objects.all())
    preferred_locales.insert(0, default_preferred_source_locale)

    # Set preferred source locale
    preferred_source_locale = request.user.profile.preferred_source_locale
    if preferred_source_locale:
        preferred_source_locale = Locale.objects.filter(
            code=preferred_source_locale
        ).first()
    else:
        preferred_source_locale = default_preferred_source_locale

    return render(
        request,
        "contributors/settings.html",
        {
            "selected_locales": selected_locales,
            "available_locales": available_locales,
            "locales": all_locales,
            "locale": custom_homepage_locale,
            "preferred_locales": preferred_locales,
            "preferred_locale": preferred_source_locale,
            "profile_form": profile_form,
        },
    )


@login_required(redirect_field_name="", login_url="/403")
def notifications(request):
    """View and edit user notifications."""
    notifications = request.user.notifications.prefetch_related(
        "actor", "target"
    ).order_by("-pk")
    projects = {}

    for notification in notifications:
        project = None
        if isinstance(notification.actor, Project):
            project = notification.actor
        elif isinstance(notification.target, Project):
            project = notification.target

        if project:
            if project.slug in projects:
                projects[project.slug]["notifications"].append(notification.id)
            else:
                projects[project.slug] = {
                    "name": project.name,
                    "notifications": [notification.id],
                }

    # Sort projects by the number of notifications
    ordered_projects = []
    for slug in sorted(
        projects, key=lambda slug: len(projects[slug]["notifications"]), reverse=True
    ):
        ordered_projects.append(slug)

    log_ux_action(
        action_type="Page load: Notifications",
        experiment="Notifications 1.0",
        data={"referrer": request.GET.get("referrer", "")},
    )

    return render(
        request,
        "contributors/notifications.html",
        {
            "notifications": notifications,
            "projects": projects,
            "ordered_projects": ordered_projects,
        },
    )


@login_required(redirect_field_name="", login_url="/403")
@require_AJAX
@transaction.atomic
def mark_all_notifications_as_read(request):
    """Mark all notifications of the currently logged in user as read"""
    request.user.notifications.mark_all_as_read()

    log_ux_action(
        action_type="Background action: Mark all notifications as read",
        experiment="Notifications 1.0",
        data={"utm_source": request.GET.get("utm_source")},
    )

    return JsonResponse({"status": True})


class ContributorsMixin:
    def contributors_filter(self, **kwargs):
        """
        Return Q() filters for fetching contributors. Fetches all by default.
        """
        return Q()

    def get_context_data(self, **kwargs):
        """Top contributors view."""
        context = super().get_context_data(**kwargs)
        try:
            period = int(self.request.GET["period"])
            if period <= 0:
                raise ValueError
            start_date = timezone.now() + relativedelta(months=-period)
        except (KeyError, ValueError):
            period = None
            start_date = None

        context["contributors"] = users_with_translations_counts(
            start_date, self.contributors_filter(**kwargs) & Q(user__isnull=False)
        )
        context["period"] = period
        return context


class ContributorsView(ContributorsMixin, TemplateView):
    """
    View returns top contributors.
    """

    template_name = "contributors/contributors.html"
