from io import BytesIO
from os.path import basename, join
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from django.core.files import File
from django.utils import timezone

from pontoon.base.models import ChangedEntityLocale, Locale, Project, User
from pontoon.sync.core.checkout import checkout_repos
from pontoon.sync.core.paths import UploadPaths, find_paths
from pontoon.sync.core.stats import update_stats
from pontoon.sync.core.translations_from_repo import find_db_updates, write_db_updates
from pontoon.sync.core.translations_to_repo import update_changed_resources


def download_translations_zip(
    project: Project, locale: Locale
) -> tuple[bytes, str] | tuple[None, None]:
    checkouts = checkout_repos(project)
    paths = find_paths(project, checkouts)
    db_changes = ChangedEntityLocale.objects.filter(
        entity__resource__project=project, locale=locale
    ).select_related("entity__resource", "locale")
    update_changed_resources(project, paths, {}, [], db_changes, set(), timezone.now())

    bytes_io = BytesIO()
    zipfile = ZipFile(bytes_io, "w")
    for _, tgt_path in paths.all():
        lc_path = paths.format_target_path(tgt_path, locale.code)
        zipfile.write(lc_path, basename(tgt_path))
    zipfile.close()

    return bytes_io.getvalue(), f"{project.slug}.zip"


def sync_uploaded_file(
    project: Project, locale: Locale, res_path: str, upload: File, user: User
):
    """Update translations in the database from an uploaded file."""

    with TemporaryDirectory() as root:
        file_path = join(root, basename(res_path))
        with open(file_path, "wb") as file:
            for chunk in upload.chunks():
                file.write(chunk)
        paths = UploadPaths(res_path, locale.code, file_path)
        updates = find_db_updates(
            project, {locale.code: locale}, [file_path], paths, []
        )
    if updates:
        now = timezone.now()
        write_db_updates(project, updates, user, now)
        update_stats(project)
        ChangedEntityLocale.objects.bulk_create(
            (
                ChangedEntityLocale(entity_id=entity_id, locale_id=locale_id, when=now)
                for entity_id, locale_id in updates
            ),
            ignore_conflicts=True,
        )
    else:
        raise Exception("Upload failed.")
