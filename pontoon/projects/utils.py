import csv
import json

from io import StringIO
from typing import Iterable

from django.contrib.auth.models import User
from django.db import connection, transaction
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from pontoon.base.models import Project, Translation


def generate_translation_stats_csv(project: Project, user: User) -> HttpResponse:
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
                r.path, e.key, e.string
            ORDER BY
                r.path ASC,
                e.key ASC
            """,
            [project.id],
        )

        rows = cursor.fetchall()

    for row in rows:
        (resource_path, entity_key, entity_string, translations) = row
        if resource_path.endswith("json"):
            entity_key = ".".join(json.loads(entity_key))
        elif resource_path.endswith("xliff"):
            entity_key = entity_key.split("\x04")[-1]

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


def upload_translations(csv_file, project: Project, user: User):
    UNTRANSLATED_MARKS = ["MISSING", "PRETRANSLATED", "REJECTED", "FUZZY", "UNREVIEWED"]

    csv_data = csv_file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(csv_data))
    headers = reader.fieldnames
    if not isinstance(headers, Iterable) or len(headers) < 4:
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
    translations = [row for row in reader if any(cell for cell in row)]
    for tr in translations:
        if qs := project.resources.filter(path=tr["Resource"]):
            resource = qs.first()
        else:
            return JsonResponse(data={"error": f"Resource not found: {tr['Resource']}"})

        if (
            key := get_translation_key(
                key=tr["Translation Key"], format=resource.format
            )
        ) is None:
            return JsonResponse(
                data={
                    "error": f'"{resource.format}" formated strings are not supported for '
                    "translation uploading via CSV file."
                },
                status=400,
            )

        if not (qs := resource.entities.filter(key=key, obsolete=False)):
            return JsonResponse(
                data={
                    "error": f"Wrong data: translation key {key} does not exist in "
                    f"{resource.path} of project {project.name}"
                },
                status=400,
            )

        entity = qs.first()

        for locale in locales:
            if tr[locale.name].strip() == "" or tr[locale.name] in UNTRANSLATED_MARKS:
                continue
            # if same translation exists for the entity, skip creating translation
            tr_string = tr[locale.name]
            if entity.translation_set.filter(locale=locale, string=tr_string):
                continue

            activate_new_translation = False
            if user.can_translate(project=project, locale=locale):
                activate_new_translation = True

            # Create new translation for the entity
            new_trans = Translation(
                string=tr_string,
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


def get_translation_key(key: str, format: str) -> str | None:
    match format:
        case "json":
            return str(key.split(".")).replace("'", '"')
        case "po" | "xml":
            return key
        case _:
            return None
