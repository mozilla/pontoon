import json

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.utils.html import escape

from pontoon.base import forms
from pontoon.base.models import Locale, Project, UserProfile
from pontoon.base.utils import require_AJAX
from pontoon.contributors import utils
from pontoon.uxactionlog.utils import log_ux_action


@login_required(redirect_field_name="", login_url="/403")
def profile(request):
    """Current user profile."""
    return contributor(request, request.user)


def contributor_email(request, email):
    user = get_object_or_404(User, email=email)
    return contributor(request, user)


def contributor_username(request, username):
    try:
        user = User.objects.get(username=username)
        if user.profile.username:
            return redirect(
                "pontoon.contributors.contributor.username",
                username=user.profile.username,
            )
    except User.DoesNotExist:
        user = get_object_or_404(UserProfile, username=username).user

    return contributor(request, user)


def contributor(request, user):
    """Contributor profile."""
    graph_data, graph_title = utils.get_contribution_graph_data(
        user, "all_contributions"
    )
    timeline_data, timeline_title = utils.get_contribution_timeline_data(
        user, "all_contributions"
    )

    context = {
        "contributor": user,
        "contact_for": user.contact_for.filter(
            disabled=False, system_project=False, visibility="public"
        ).order_by("-priority"),
        "all_time_stats": {
            "translations": user.contributed_translations,
        },
        "approvals_charts": utils.get_approvals_charts_data(user),
        "contribution_graph": {
            "contributions": json.dumps(graph_data),
            "title": graph_title,
        },
        "contribution_timeline": {
            "contributions": timeline_data,
            "title": timeline_title,
        },
    }

    return render(
        request,
        "contributors/profile.html",
        context,
    )


@require_AJAX
@transaction.atomic
def update_contribution_graph(request):
    try:
        user = User.objects.get(pk=request.GET["user"])
        contribution_type = request.GET["contribution_type"]
    except User.DoesNotExist as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    contributions, title = utils.get_contribution_graph_data(user, contribution_type)
    return JsonResponse({"contributions": contributions, "title": title})


@require_AJAX
@transaction.atomic
def update_contribution_timeline(request):
    try:
        user = User.objects.get(pk=request.GET["user"])
        contribution_type = request.GET["contribution_type"]
        day = request.GET.get("day", None)
        day = int(day) / 1000 if day else None
    except (User.DoesNotExist, ValueError) as e:
        return JsonResponse(
            {"status": False, "message": f"Bad Request: {e}"},
            status=400,
        )

    contributions, title = utils.get_contribution_timeline_data(
        user, contribution_type, day
    )

    return render(
        request,
        "contributors/includes/timeline.html",
        {
            "contribution_timeline": {
                "contributions": contributions,
                "title": title,
            },
        },
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

    boolean_attributes = [
        "quality_checks",
        "force_suggestions",
        "new_string_notifications",
        "project_deadline_notifications",
        "comment_notifications",
        "unreviewed_suggestion_notifications",
        "review_notifications",
        "new_contributor_notifications",
    ]

    visibility_attributes = [
        "visibility_email",
        "visibility_external_accounts",
        "visibility_self_approval",
        "visibility_approval",
    ]

    if attribute not in (boolean_attributes + visibility_attributes):
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
    if attribute in boolean_attributes:
        # Convert JS Boolean to Python
        setattr(profile, attribute, json.loads(value))
    elif attribute in visibility_attributes:
        setattr(profile, attribute, value)
    profile.save()

    return JsonResponse({"status": True})


@login_required(redirect_field_name="", login_url="/403")
@require_POST
@transaction.atomic
def toggle_theme(request, username):
    user = get_object_or_404(User, username=username)
    if user != request.user:
        return JsonResponse(
            {
                "status": False,
                "message": "Forbidden: You don't have permission to edit this user",
            },
            status=403,
        )

    theme = request.POST.get("theme", None)

    try:
        profile = user.profile
        profile.theme = theme
        profile.full_clean()
        profile.save()
    except ValidationError:
        return JsonResponse(
            {"status": False, "message": "Bad Request: Invalid theme"},
            status=400,
        )

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
        request.POST,
        instance=request.user.profile,
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
    profile = request.user.profile
    if request.method == "POST":
        locales_form = forms.UserLocalesOrderForm(
            request.POST,
            instance=profile,
        )
        user_form = forms.UserForm(
            request.POST,
            instance=request.user,
        )
        user_profile_form = forms.UserProfileForm(
            request.POST,
            instance=profile,
        )

        if (
            locales_form.is_valid()
            and user_form.is_valid()
            and user_profile_form.is_valid()
        ):
            locales_form.save()
            user_form.save()
            user_profile_form.save()

            if "contact_email" in user_profile_form.changed_data:
                profile.contact_email_verified = False
                profile.save(update_fields=["contact_email_verified"])

                token = utils.generate_verification_token(request.user)
                utils.send_verification_email(request, token)

            messages.success(request, "Settings saved.")
    else:
        user_form = forms.UserForm(instance=request.user)
        user_profile_form = forms.UserProfileForm(instance=profile)

    selected_locales = list(profile.sorted_locales)
    available_locales = Locale.objects.exclude(pk__in=[l.pk for l in selected_locales])

    default_homepage_locale = Locale(name="Default homepage", code="")
    all_locales = list(Locale.objects.all())
    all_locales.insert(0, default_homepage_locale)

    # Set custom homepage selector value
    custom_homepage_locale = profile.custom_homepage
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
    preferred_source_locale = profile.preferred_source_locale
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
            "user_form": user_form,
            "user_profile_form": user_profile_form,
            "user_profile_visibility_form": forms.UserProfileVisibilityForm(
                instance=profile
            ),
        },
    )


@login_required(redirect_field_name="", login_url="/403")
def verify_email_address(request, token):
    title, message = utils.check_verification_token(request.user, token)

    return render(
        request,
        "contributors/verify_email.html",
        {
            "title": title,
            "message": message,
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
    """Mark all notifications of the currently logged-in user as read"""
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

        context["contributors"] = utils.users_with_translations_counts(
            start_date,
            self.contributors_filter(**kwargs)
            & Q(user__isnull=False)
            & Q(user__profile__system_user=False),
            kwargs.get("locale"),
            100,
        )
        context["period"] = period
        return context


class ContributorsView(ContributorsMixin, TemplateView):
    """
    View returns top contributors.
    """

    template_name = "contributors/contributors.html"
