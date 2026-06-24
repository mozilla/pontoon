import logging

from collections import defaultdict
from datetime import datetime

from django.db.models import Count
from django.utils import timezone

from pontoon.base.models import (
    ChangedEntityLocale,
    Entity,
    Locale,
    Project,
    ProjectLocale,
    TranslatedResource,
    Translation,
    User,
)
from pontoon.messaging.notifications import send_notification
from pontoon.pretranslation.tasks import pretranslate
from pontoon.sync.core.checkout import checkout_repos
from pontoon.sync.core.entities import sync_resources_from_repo
from pontoon.sync.core.paths import find_paths
from pontoon.sync.core.stats import update_stats
from pontoon.sync.core.translations_from_repo import sync_translations_from_repo
from pontoon.sync.core.translations_to_repo import sync_translations_to_repo


log = logging.getLogger(__name__)


def sync_project(
    project: Project,
    *,
    pull: bool = True,
    commit: bool = True,
    force: bool = False,
) -> tuple[bool, bool]:
    """`(db_changed, repo_changed)`"""
    # Mark "now" at the start of sync to avoid messing with
    # translations submitted during sync.
    now = timezone.now()

    log_prefix = f"[{project.slug}]"
    log.info(f"{log_prefix} Sync start")

    try:
        checkouts = checkout_repos(project, force=force, pull=pull)
        paths = find_paths(project, checkouts)
    except Exception as e:
        log.error(f"{log_prefix} {e}")
        raise e

    locale_map: dict[str, Locale]
    if project.set_locales_from_repo:
        if not paths.locales:
            errmsg = "No locales found in repo"
            log.error(f"{log_prefix} {errmsg}")
            raise Exception(errmsg)
        locales = Locale.objects.filter(code__in=paths.locales).order_by("code")
        locale_map = {lc.code: lc for lc in locales}

        # Update project locales
        ProjectLocale.objects.filter(project=project).exclude(
            locale__in=locales
        ).delete()
        for locale in locales:
            # The implicit pre_save and post_save signals sent here are required
            # to maintain django-guardian permissions.
            ProjectLocale.objects.get_or_create(project=project, locale=locale)
        ProjectLocale.objects.filter(project=project, readonly=True).update(
            readonly=False
        )
    else:
        locale_map = {lc.code: lc for lc in project.locales.order_by("code")}
    paths.locales = list(locale_map.keys())

    added_entities_count, changed_paths, removed_paths = sync_resources_from_repo(
        project, locale_map, checkouts.source, paths, now
    )

    db_changes = ChangedEntityLocale.objects.filter(
        entity__resource__project=project, when__lte=now
    ).select_related("entity__resource", "locale")
    del_trans_count, updated_trans_count = sync_translations_from_repo(
        project, locale_map, checkouts, paths, db_changes, now
    )
    db_changed = bool(
        added_entities_count
        or changed_paths
        or removed_paths
        or del_trans_count
        or updated_trans_count
    )
    if added_entities_count > 0:
        notify_users(project, now)
    repo_changed = sync_translations_to_repo(
        project,
        commit,
        locale_map,
        checkouts,
        paths,
        db_changes,
        changed_paths,
        removed_paths,
        now,
    )
    if commit:
        db_changes.delete()

    checkouts.source.repo.last_synced_revision = checkouts.source.commit
    if checkouts.target != checkouts.source:
        checkouts.target.repo.last_synced_revision = checkouts.target.commit
    if db_changed:
        update_stats(project)
    log.info(f"{log_prefix} Sync done")

    if project.pretranslation_enabled and changed_paths:
        # Pretranslate changed and added resources for all locales
        pretranslate(project, changed_paths)

    return db_changed, repo_changed


def notify_users(project: Project, now: datetime) -> None:
    # Strings added during the same sync operation have date_created == now.
    new_by_resource = dict(
        Entity.objects.filter(
            resource__project=project, date_created=now, obsolete=False
        )
        .values_list("resource_id")
        .annotate(count=Count("id"))
    )
    if not new_by_resource:
        return

    # Get accurate per-locale totals.
    locale_counts: dict[int, int] = defaultdict(int)
    for locale_id, resource_id in TranslatedResource.objects.filter(
        resource_id__in=new_by_resource.keys()
    ).values_list("locale_id", "resource_id"):
        locale_counts[locale_id] += new_by_resource[resource_id]

    # Map each translator who chose to receive notifications to the affected
    # locales they contribute to.
    translations = Translation.objects.filter(
        entity__resource__project=project,
        locale_id__in=locale_counts.keys(),
        user__profile__new_string_notifications=True,
    )
    # Private projects are only visible to superusers, so don't leak their
    # activity to other past contributors.
    if project.visibility != Project.Visibility.PUBLIC:
        translations = translations.filter(user__is_superuser=True)
    user_locales: dict[int, set[int]] = defaultdict(set)
    for user_id, locale_id in translations.values_list(
        "user_id", "locale_id"
    ).distinct():
        user_locales[user_id].add(locale_id)
    if not user_locales:
        return

    # Map locale code to internal ID. This is used to match a user's custom
    # homepage locale.
    locale_id_by_code = dict(
        Locale.objects.filter(id__in=locale_counts.keys()).values_list("code", "id")
    )
    # Stored on notification.data so both the bell menu and digest can link to
    # the exact batch via the created_time URL filter on Entity.date_created.
    created_time = now.strftime("%Y%m%d%H%M")
    # One notification per user. The link is locale-agnostic, so it resolves to
    # the user's homepage locale: report that locale's count when the user
    # contributes to it, otherwise fall back to the largest count among the
    # locales they contributed to.
    users = User.objects.filter(id__in=user_locales.keys()).select_related("profile")
    for user in users:
        locale_ids = user_locales[user.id]
        homepage_id = locale_id_by_code.get(user.profile.custom_homepage)
        if homepage_id in locale_ids:
            count = locale_counts[homepage_id]
        else:
            count = max(locale_counts[locale_id] for locale_id in locale_ids)
        new_strings = f"{count} new {'string' if count == 1 else 'strings'}"
        send_notification(
            project,
            recipient=user,
            verb=f"updated with {new_strings}",
            category="new_string",
            created_time=created_time,
        )
    log.info(f"[{project.slug}] Notifying {len(user_locales)} users about new strings")
