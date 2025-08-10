import logging

from textwrap import dedent

from django.db import connection

from pontoon.base.models import Project


log = logging.getLogger(__name__)


def update_stats(project: Project) -> None:
    """Uses raw SQL queries for performance."""

    with connection.cursor() as cursor:
        # Resources, counted from entities
        cursor.execute(
            dedent(
                """
                UPDATE base_resource res
                SET total_strings = agg.total
                FROM (
                    SELECT ent.resource_id AS "resource_id", COUNT(*) AS "total"
                    FROM "base_entity" ent
                    LEFT OUTER JOIN "base_resource" res ON (ent.resource_id = res.id)
                    WHERE NOT ent.obsolete AND res.project_id = %s
                    GROUP BY ent.resource_id
                ) AS agg
                WHERE res.id = agg.resource_id AND res.project_id = %s
                """
            ),
            [project.id, project.id],
        )

        # Translated resources, copied from resources
        cursor.execute(
            dedent(
                """
                UPDATE "base_translatedresource" tr
                SET total_strings = res.total_strings
                FROM "base_resource" res
                WHERE tr.resource_id = res.id AND res.project_id = %s
                """
            ),
            [project.id],
        )

        # Other translated resource string counts, counted directly from translations
        cursor.execute(
            dedent(
                """
                UPDATE base_translatedresource tr
                SET
                    approved_strings = agg.approved,
                    pretranslated_strings = agg.pretranslated,
                    strings_with_errors = agg.errors,
                    strings_with_warnings = agg.warnings,
                    unreviewed_strings = agg.unreviewed
                FROM (
                    SELECT
                        trans.locale_id AS "locale_id",
                        ent.resource_id AS "resource_id",
                        COUNT(DISTINCT trans.id) FILTER (WHERE trans.approved AND err.id IS NULL AND warn.id IS NULL) AS "approved",
                        COUNT(DISTINCT trans.id) FILTER (WHERE trans.pretranslated AND err.id IS NULL AND warn.id IS NULL) AS "pretranslated",
                        COUNT(DISTINCT trans.id) FILTER (WHERE (trans.approved OR trans.pretranslated OR trans.fuzzy) AND err.id IS NOT NULL) AS "errors",
                        COUNT(DISTINCT trans.id) FILTER (WHERE (trans.approved OR trans.pretranslated OR trans.fuzzy) AND warn.id IS NOT NULL) AS "warnings",
                        COUNT(DISTINCT trans.id) FILTER (WHERE NOT trans.approved AND NOT trans.pretranslated AND NOT trans.rejected AND NOT trans.fuzzy) AS "unreviewed"
                    FROM "base_translation" trans
                    LEFT OUTER JOIN "checks_error" err ON (trans.id = err.translation_id)
                    LEFT OUTER JOIN "checks_warning" warn ON (trans.id = warn.translation_id)
                    LEFT OUTER JOIN "base_entity" ent ON (trans.entity_id = ent.id)
                    LEFT OUTER JOIN "base_resource" res ON (ent.resource_id = res.id)
                    WHERE NOT ent.obsolete AND res.project_id = %s
                    GROUP BY trans.locale_id, ent.resource_id
                ) AS agg
                WHERE agg.locale_id = tr.locale_id AND agg.resource_id = tr.resource_id
                """
            ),
            [project.id],
        )
        tr_count = cursor.rowcount

    tr_str = (
        "1 translated resource" if tr_count == 1 else f"{tr_count} translated resources"
    )
    log.info(f"[{project.slug}] Updated stats for {tr_str}")
