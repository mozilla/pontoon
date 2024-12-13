import logging

from textwrap import dedent

from django.db import connection

from pontoon.base.models import Project


log = logging.getLogger(__name__)


def update_stats(project: Project, *, update_locales: bool = True) -> None:
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

        # Translated resource total strings are counted from entities and expected locale plurals.
        # The source entity count is offset by the number of gettext plural source strings
        # multiplied by one less than the count of plural categories of the target locale,
        # which equals the number of commas in cldr_plurals.
        cursor.execute(
            dedent(
                """
                UPDATE base_translatedresource tr
                SET total_strings = agg.total
                FROM (
                    SELECT
                        tr.id AS "id",
                        COUNT(*) +
                            (LENGTH(loc.cldr_plurals) - LENGTH(REPLACE(loc.cldr_plurals, ',', ''))) *
                            COUNT(*) FILTER (WHERE ent.string_plural != '')
                        AS "total"
                    FROM "base_translatedresource" tr
                    LEFT OUTER JOIN "base_resource" res ON (tr.resource_id = res.id)
                    LEFT OUTER JOIN "base_locale" loc ON (tr.locale_id = loc.id)
                    LEFT OUTER JOIN "base_entity" ent ON (tr.resource_id = ent.resource_id)
                    WHERE NOT ent.obsolete AND res.project_id = %s
                    GROUP BY tr.id, loc.cldr_plurals
                ) AS agg
                WHERE agg.id = tr.id
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
                        COUNT(*) FILTER (WHERE trans.approved AND err.id IS NULL AND warn.id IS NULL) AS "approved",
                        COUNT(*) FILTER (WHERE trans.pretranslated AND err.id IS NULL AND warn.id IS NULL) AS "pretranslated",
                        COUNT(*) FILTER (WHERE (trans.approved OR trans.pretranslated OR trans.fuzzy) AND err.id IS NOT NULL) AS "errors",
                        COUNT(*) FILTER (WHERE (trans.approved OR trans.pretranslated OR trans.fuzzy) AND warn.id IS NOT NULL) AS "warnings",
                        COUNT(*) FILTER (WHERE NOT trans.approved AND NOT trans.pretranslated AND NOT trans.rejected AND NOT trans.fuzzy) AS "unreviewed"
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

        # Project locales, counted from translated resources
        cursor.execute(
            dedent(
                """
                UPDATE base_projectlocale pl
                SET
                    total_strings = agg.total,
                    approved_strings = agg.approved,
                    pretranslated_strings = agg.pretranslated,
                    strings_with_errors = agg.errors,
                    strings_with_warnings = agg.warnings,
                    unreviewed_strings = agg.unreviewed
                FROM (
                    SELECT
                        tr.locale_id AS "locale_id",
                        SUM(tr.total_strings) AS "total",
                        SUM(tr.approved_strings) AS "approved",
                        SUM(tr.pretranslated_strings) AS "pretranslated",
                        SUM(tr.strings_with_errors) AS "errors",
                        SUM(tr.strings_with_warnings) AS "warnings",
                        SUM(tr.unreviewed_strings) AS "unreviewed"
                    FROM "base_translatedresource" tr
                    INNER JOIN "base_resource" res ON (tr.resource_id = res.id)
                    WHERE res.project_id = %s
                    GROUP BY tr.locale_id
                ) AS agg
                WHERE agg.locale_id = pl.locale_id AND pl.project_id = %s
                """
            ),
            [project.id, project.id],
        )
        pl_count = cursor.rowcount

        # Project, counted from project locales
        cursor.execute(
            dedent(
                """
                UPDATE base_project proj
                SET
                    total_strings = GREATEST(agg.total, 0),
                    approved_strings = GREATEST(agg.approved, 0),
                    pretranslated_strings = GREATEST(agg.pretranslated, 0),
                    strings_with_errors = GREATEST(agg.errors, 0),
                    strings_with_warnings = GREATEST(agg.warnings, 0),
                    unreviewed_strings = GREATEST(agg.unreviewed, 0)
                FROM (
                    SELECT
                        SUM(pl.total_strings) AS "total",
                        SUM(pl.approved_strings) AS "approved",
                        SUM(pl.pretranslated_strings) AS "pretranslated",
                        SUM(pl.strings_with_errors) AS "errors",
                        SUM(pl.strings_with_warnings) AS "warnings",
                        SUM(pl.unreviewed_strings) AS "unreviewed"
                    FROM "base_projectlocale" pl
                    WHERE pl.project_id = %s
                ) AS agg
                WHERE proj.id = %s
                """
            ),
            [project.id, project.id],
        )

        lc_count = _update_locales(cursor) if update_locales else 0

    tr_str = (
        "1 translated resource" if tr_count == 1 else f"{tr_count} translated resources"
    )
    pl_str = "1 projectlocale" if pl_count == 1 else f"{pl_count} projectlocales"
    lc_str = "1 locale" if lc_count == 1 else f"{lc_count} locales"
    summary = (
        f"{tr_str} and {pl_str}"
        if lc_count == 0
        else f"{tr_str}, {pl_str}, and {lc_str}"
    )
    log.info(f"[{project.slug}] Updated stats for {summary}")


def update_locale_stats() -> None:
    with connection.cursor() as cursor:
        lc_count = _update_locales(cursor)
    lc_str = "1 locale" if lc_count == 1 else f"{lc_count} locales"
    log.info(f"Updated stats for {lc_str}")


def _update_locales(cursor) -> int:
    # All locales, counted from project locales
    cursor.execute(
        dedent(
            """
            UPDATE base_locale loc
            SET
                total_strings = agg.total,
                approved_strings = agg.approved,
                pretranslated_strings = agg.pretranslated,
                strings_with_errors = agg.errors,
                strings_with_warnings = agg.warnings,
                unreviewed_strings = agg.unreviewed
            FROM (
                SELECT
                    pl.locale_id AS "locale_id",
                    SUM(pl.total_strings) AS "total",
                    SUM(pl.approved_strings) AS "approved",
                    SUM(pl.pretranslated_strings) AS "pretranslated",
                    SUM(pl.strings_with_errors) AS "errors",
                    SUM(pl.strings_with_warnings) AS "warnings",
                    SUM(pl.unreviewed_strings) AS "unreviewed"
                FROM "base_projectlocale" pl
                INNER JOIN "base_project" proj ON (pl.project_id = proj.id)
                WHERE NOT proj.disabled AND NOT proj.system_project AND proj.visibility = 'public'
                GROUP BY pl.locale_id
            ) AS agg
            WHERE agg.locale_id = loc.id
            """
        )
    )
    return cursor.rowcount
