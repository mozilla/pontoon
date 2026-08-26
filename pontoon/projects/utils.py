import csv

from collections import defaultdict
from io import StringIO
from typing import Iterable

from django.contrib import messages
from django.contrib.auth.models import User
from django.db import connection, transaction
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from pontoon.base.models import Project, Translation
from pontoon.base.user_utils import can_translate
from pontoon.translations.utils import parse_db_string_to_json


# Formats whose Entity.key is a JSON path, encoded in the CSV as a dot-joined
# string. All other formats join key elements with \x04 (see get_translation_key).
JSON_KEY_FORMATS = {"plain_json", "webext"}


def generate_translation_stats_csv(project: Project, user: User) -> HttpResponse:
    """
    Stream all non-obsolete entities and their approved translations for the
    given project as a CSV file.

    Column layout: Resource | Translation Key | Translation Source String | <locale> …

    Entity keys are stored as a PostgreSQL text array (ArrayField). They are
    serialised to CSV as follows so that import can reconstruct them exactly:
      - plain_json / webext: array elements joined with "."  (e.g. "section.key")
      - all other formats:   array elements joined with \\x04 (ASCII Unit Separator),
                             a character that does not appear in normal source strings

    Only approved translations are exported; other states (unreviewed, rejected,
    etc.) appear as an empty cell.
    """
    project_locales = project.project_locale.all()
    pl_names = [pl.locale.name for pl in project_locales]
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="{project.slug}_translations_stats.csv"'
    )

    headers = [
        "Resource",
        "Translation Key",
        "Translation Source String",
    ] + pl_names
    writer = csv.writer(response, quoting=csv.QUOTE_ALL)
    writer.writerow(headers)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                r.path AS resource_path,
                r.format AS resource_format,
                e.key AS entity_key,
                e.string AS entity_string,
                json_agg(json_build_object(
                    'locale_id', t.locale_id,
                    'string', t.string,
                    'approved', t.approved,
                    'pretranslated', t.pretranslated,
                    'rejected', t.rejected,
                    'fuzzy', t.fuzzy
                )) AS translations
            FROM
                base_resource r
            JOIN
                base_entity e ON e.resource_id = r.id
            LEFT JOIN
                base_translation t ON t.entity_id = e.id
            WHERE
                r.project_id = %s AND e.obsolete = FALSE
            GROUP BY
                r.path, r.format, e.key, e.string
            ORDER BY
                r.path ASC,
                e.key ASC
            """,
            [project.id],
        )

        rows = cursor.fetchall()

    for row in rows:
        (resource_path, resource_format, entity_key, entity_string, translations) = row
        if resource_format in JSON_KEY_FORMATS:
            entity_key = ".".join(entity_key)
        else:
            entity_key = "\x04".join(entity_key)

        row_data = [resource_path, entity_key, entity_string]

        for pl in project_locales:
            translation = next(
                (
                    tr["string"]
                    for tr in translations
                    if tr["locale_id"] == pl.locale.id and tr["approved"]
                ),
                "",
            )
            row_data.append(translation)
        writer.writerow(row_data)
    return response


def upload_translations(csv_file, project: Project, user: User, request=None):
    """
    Import translations from a CSV file produced by generate_translation_stats_csv.

    Returns a JsonResponse with an error message (status 400) when the file as a
    whole is unusable (missing columns, locale names that don't belong to the
    project), or None otherwise (the view then issues a redirect).

    Problems with an individual row never abort the import: unknown resource
    paths, unsupported/unset resource formats and keys that don't match an
    existing entity are counted and reported back through `request` (Django
    messages) once the rest of the file has been imported. A full CSV export
    legitimately contains such rows — e.g. resources with no format set — and
    rejecting the whole upload because of them made import unusable on real
    projects.

    Rows are skipped — not rejected — when a locale cell is blank or contains
    one of UNTRANSLATED_MARKS, or when the same translation string already
    exists for that entity/locale pair.

    Whether the created translation is approved depends on whether the uploading
    user has translator rights for the project locale (via can_translate). If
    they do, the new translation becomes active/approved and any existing active
    translation is deactivated in the same atomic block.
    """
    # Status strings that appear in locale cells of the exported CSV when there
    # is no approved translation (e.g. the cell held a review-status label from
    # an earlier Pontoon export format). These rows carry no translateable content
    # and must be skipped rather than saved as translation strings.
    UNTRANSLATED_MARKS = ["MISSING", "PRETRANSLATED", "REJECTED", "FUZZY", "UNREVIEWED"]

    csv_data = csv_file.read().decode("utf-8-sig")
    reader = csv.DictReader(StringIO(csv_data))
    headers = reader.fieldnames
    # The first two columns are dereferenced by name below, so their names have
    # to be checked, not just the column count.
    if (
        not isinstance(headers, Iterable)
        or len(headers) < 4
        or headers[0] != "Resource"
        or headers[1] != "Translation Key"
    ):
        return JsonResponse(
            data={
                "error": "Wrong CSV headers: should at least have 4 columns: Resource, Translation Key,"
                " Translation Source String, and 1 locale column."
            },
            status=400,
        )
    locale_names = headers[3:]
    project_locale_names = [loc.name for loc in project.locales.all()]
    if wrong_locales := set(locale_names) - set(project_locale_names):
        return JsonResponse(
            data={
                "error": f"Wrong CSV headers - Not recognizable locale names: {list(wrong_locales)}."
            },
            status=400,
        )

    locales = project.locales.filter(
        name__in=set(project_locale_names) & set(locale_names)
    )
    translations = [row for row in reader if any(row.values())]
    created = 0
    skipped: dict[str, int] = defaultdict(int)
    for tr in translations:
        if qs := project.resources.filter(path=tr["Resource"]):
            resource = qs.first()
        else:
            skipped[f"unknown resource: {tr['Resource']}"] += 1
            continue

        if (
            key := get_translation_key(
                key=tr["Translation Key"], format=resource.format
            )
        ) is None:
            skipped[f'unsupported format "{resource.format}" in {resource.path}'] += 1
            continue

        if not (qs := resource.entities.filter(key=key, obsolete=False)):
            skipped[f"unknown translation key in {resource.path}"] += 1
            continue

        entity = qs.first()

        for locale in locales:
            # DictReader yields None for columns missing from a short row.
            tr_string = tr.get(locale.name) or ""
            if tr_string.strip() == "" or tr_string in UNTRANSLATED_MARKS:
                continue
            # if same translation exists for the entity, skip creating translation
            if entity.translation_set.filter(locale=locale, string=tr_string):
                continue

            activate_new_translation = False
            if can_translate(user=user, project=project, locale=locale):
                activate_new_translation = True

            # Create new translation for the entity
            value, properties = parse_db_string_to_json(resource.format, tr_string)
            new_trans = Translation(
                string=tr_string,
                value=value,
                properties=properties,
                user=user,
                locale=locale,
                entity=entity,
                active=False,
                approved=False,
                date=timezone.now(),
                rejected=False,
                rejected_user=None,
                rejected_date=None,
                pretranslated=False,
                fuzzy=False,
            )

            if activate_new_translation:
                new_trans.active = True
                new_trans.approved = True
                new_trans.approved_user = user
                new_trans.approved_date = timezone.now()
                if current_translation := entity.translation_set.filter(
                    locale=locale, active=True
                ).first():
                    with transaction.atomic():
                        current_translation.active = False
                        current_translation.save()
                        new_trans.save()
                else:
                    new_trans.save()
            else:
                new_trans.save()
            created += 1

    if request is not None:
        summary = f"CSV import: {created} translation(s) created."
        if skipped:
            reasons = sorted(skipped.items(), key=lambda kv: -kv[1])
            details = ", ".join(
                f"{reason} ({count} row(s))" for reason, count in reasons[:5]
            )
            if len(reasons) > 5:
                details += f" and {len(reasons) - 5} other reason(s)"
            summary += f" Skipped rows — {details}."
            messages.warning(request, summary)
        else:
            messages.success(request, summary)


def get_translation_key(key: str, format: str) -> list | None:
    """
    Convert a CSV "Translation Key" cell back to the list that matches
    Entity.key (an ArrayField) for database lookup.

    The encoding mirrors how generate_translation_stats_csv serialises keys:
      - plain_json / webext: dot-joined path → split on "."
      - everything else:     \\x04-joined elements → split on "\\x04"

    Returns None for unrecognised formats; the caller treats this as an
    unsupported-format error rather than a lookup failure.
    """
    match format:
        case "plain_json" | "webext":
            return key.split(".")
        case (
            "gettext"
            | "android"
            | "dtd"
            | "properties"
            | "ini"
            | "fluent"
            | "xcode"
            | "xliff"
        ):
            # \x04 (ASCII Unit Separator) is used as a delimiter because it
            # never appears in source strings, making the split unambiguous.
            return key.split("\x04")
        case _:
            return None
