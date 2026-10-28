import logging

from celery import shared_task

from django.core.cache import cache

from pontoon.base.models import Entity, Locale, TranslatedResource, Translation, User
from pontoon.base.tasks import PontoonTask
from pontoon.batch.actions import pretranslate_translations


log = logging.getLogger(__name__)


@shared_task(base=PontoonTask, name="batch_pretranslate")
def batch_pretranslate_task(user_pk, locale_pk, entity_pks):
    lock_name = f"batch_pretranslate_{locale_pk}"
    try:
        user = User.objects.get(pk=user_pk)
        locale = Locale.objects.get(pk=locale_pk)
        entities = Entity.objects.filter(pk__in=entity_pks)
        action_status = pretranslate_translations(user, locale, entities)

        tr_pks = [tr.pk for tr in action_status["translated_resources"]]
        TranslatedResource.objects.filter(pk__in=tr_pks).calculate_stats()

        if action_status["count"] > 0:
            Translation.objects.filter(
                pk__in=action_status["changed_translation_pks"]
            ).bulk_mark_changed()

            changed_entity_pks = [e.pk for e in action_status["changed_entities"]]
            for e in Entity.objects.filter(
                pk__in=changed_entity_pks,
                resource__project__slug="terminology",
            ):
                e.reset_term_translation(locale)

            if action_status["latest_translation_pk"]:
                Translation.objects.get(
                    pk=action_status["latest_translation_pk"]
                ).update_latest_translation()

        cache.set(
            f"{lock_name}_result",
            {
                "count": action_status["count"],
                "invalid_translation_count": len(
                    action_status.get("invalid_translation_pks", [])
                )
                + len(action_status.get("invalid_entity_pks", [])),
            },
            timeout=3600,
        )
    except Exception:
        log.exception("Batch pretranslation failed")
        cache.set(f"{lock_name}_result", {"error": True}, timeout=3600)
        raise
    finally:
        cache.delete(lock_name)
