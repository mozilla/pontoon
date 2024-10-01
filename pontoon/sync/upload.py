from os.path import basename, join
from tempfile import TemporaryDirectory

from django.core.files import File
from django.utils import timezone

from pontoon.base.models import ChangedEntityLocale, Locale, Project, User
from pontoon.sync.core.paths import UploadPaths
from pontoon.sync.core.translations_from_repo import find_db_updates, write_db_updates


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
        ChangedEntityLocale.objects.bulk_create(
            (
                ChangedEntityLocale(entity_id=entity_id, locale_id=locale_id, when=now)
                for entity_id, locale_id in updates
            ),
            ignore_conflicts=True,
        )
