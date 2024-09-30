from io import BytesIO
from zipfile import ZipFile
from os.path import basename

from django.utils import timezone

from pontoon.base.models import Locale, Project
from pontoon.base.models.changed_entity_locale import ChangedEntityLocale
from pontoon.sync.checkouts import get_checkouts
from pontoon.sync.paths import get_paths
from pontoon.sync.sync_translations_to_repo import update_changed_resources


def download_translations_zip(
    project: Project, locale: Locale
) -> tuple[bytes, str] | tuple[None, None]:
    checkouts = get_checkouts(project)
    paths = get_paths(project, checkouts)
    db_changes = ChangedEntityLocale.objects.filter(
        entity__resource__project=project, locale=locale
    ).select_related("entity__resource", "locale")
    update_changed_resources(project, paths, {}, [], db_changes, set(), timezone.now())

    bytes_io = BytesIO()
    zipfile = ZipFile(bytes_io, "w")
    for tgt_path in paths.all():
        lc_path = paths.format_target_path(tgt_path, locale.code)
        zipfile.write(lc_path, basename(tgt_path))
    zipfile.close()

    return bytes_io.getvalue(), f"{project.slug}.zip"
