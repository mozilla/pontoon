import re

from html import escape
from io import BytesIO
from json import loads
from os.path import basename, exists, join, relpath
from re import compile
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from moz.l10n.formats import Format
from moz.l10n.formats.android import android_serialize_message
from moz.l10n.message import parse_message
from moz.l10n.model import Message, PatternMessage

from django.core.files import File
from django.utils import timezone

from pontoon.base.models import ChangedEntityLocale, Locale, Project, User
from pontoon.base.models.repository import Repository
from pontoon.messaging.notifications import send_badge_notification
from pontoon.sync.core.checkout import checkout_repos
from pontoon.sync.core.paths import UploadPaths, find_paths
from pontoon.sync.core.stats import update_stats
from pontoon.sync.core.translations_from_repo import find_db_updates, write_db_updates
from pontoon.sync.core.translations_to_repo import update_changed_resources


# FIXME This is a temporary hack, to be replaced by 04/2025 with proper downloads.
def translations_target_url(
    project: Project, locale: Locale, resource_path: str
) -> str | None:
    """The target repository URL for a resource, for direct download."""

    if project.repositories.count() > 1:
        # HACK: Let's assume that no config is used, and the target repo root is the right base.
        target_repo: Repository = project.repositories.get(source_repo=False)
        rel_path = f"{locale.code}/{resource_path}"
    else:
        checkouts = checkout_repos(project, shallow=True)
        target_repo = checkouts.target.repo
        paths = find_paths(project, checkouts)
        target, _ = paths.target(resource_path)
        if not target:
            return None
        abs_path = paths.format_target_path(target, locale.code)
        rel_path = relpath(abs_path, checkouts.target.path).replace("\\", "/")

    github = re.search(r"\bgithub\.com[:/]([^/]+)/([^/]+)\.git$", target_repo.url)
    if github:
        org, repo = github.groups()
        ref = f"refs/heads/{target_repo.branch}" if target_repo.branch else "HEAD"
        return f"https://raw.githubusercontent.com/{org}/{repo}/{ref}/{rel_path}"

    gitlab = re.search(r"gitlab\.com[:/]([^/]+)/([^/]+)\.git$", target_repo.url)
    if gitlab:
        org, repo = gitlab.groups()
        ref = target_repo.branch or "HEAD"
        return f"https://gitlab.com/{org}/{repo}/-/raw/{ref}/{rel_path}?inline=false"

    # Default to bare repo link
    return re.sub(r"^.*?(://|@)", "https://", target_repo.url, count=1)


# FIXME Currently not in use, to be refactored for proper download support
def download_translations_zip(
    project: Project, locale: Locale
) -> tuple[bytes, str] | tuple[None, None]:
    checkouts = checkout_repos(project, shallow=True)
    paths = find_paths(project, checkouts)
    db_changes = ChangedEntityLocale.objects.filter(
        entity__resource__project=project, locale=locale
    ).select_related("entity__resource", "locale")
    update_changed_resources(project, paths, {}, [], db_changes, set(), timezone.now())

    bytes_io = BytesIO()
    zipfile = ZipFile(bytes_io, "w")
    for _, tgt_path in paths.all():
        filename = paths.format_target_path(tgt_path, locale.code)
        if exists(filename):
            arcname = relpath(filename, checkouts.target.path)
            zipfile.write(filename, arcname)
    zipfile.close()

    return bytes_io.getvalue(), f"{project.slug}.zip"


def import_uploaded_file(
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
        translation_before_level = user.badges_translation_level
        review_before_level = user.badges_review_level
        write_db_updates(project, updates, user, now)
        update_stats(project)
        ChangedEntityLocale.objects.bulk_create(
            (
                ChangedEntityLocale(entity_id=entity_id, locale_id=locale_id, when=now)
                for entity_id, locale_id in updates
            ),
            ignore_conflicts=True,
        )

        badge_name = ""
        badge_level = 0
        if user.badges_translation_level > translation_before_level:
            badge_name = "Translation Champion"
            badge_level = user.badges_translation_level
            send_badge_notification(user, badge_name, badge_level)
        if user.badges_review_level > review_before_level:
            badge_name = "Review Master"
            badge_level = user.badges_review_level
            send_badge_notification(user, badge_name, badge_level)
        return badge_name, badge_level
    else:
        raise Exception("Upload failed.")


android_nl = compile(r"\s*\n\s*")
android_esc = compile(r"(?<!\\)\\([nt])\s*")


def parse_pontoon_message(
    db_format: str, string: str, meta: list[list[str]]
) -> Message:
    """
    Parse an Entity.string or a Translation.string as a moz.l10n Message.

    TODO: This function should be removed once the string message representations are removed.
    """
    xliff_is_xcode = False
    match db_format:
        case "webext":
            ph = next((loads(v) for k, v in meta if k == "placeholders"), None)
            return parse_message(Format.webext, string, webext_placeholders=ph)
        case "lang" | "properties" | "":
            return PatternMessage([string])

        case "android":
            format = Format.android
            string = android_nl.sub(" ", string)
            string = android_esc.sub(lambda m: "\n" if m[1] == "n" else "\t", string)
            string = android_serialize_message(string, allow_cdata=True)
        case "gettext":
            format = Format.mf2
        case "xcode":
            format = Format.xliff
            string = escape(string)
            xliff_is_xcode = True
        case "xliff":
            format = Format.xliff
            string = escape(string)
        case _:
            format = Format[db_format]
    return parse_message(format, string, xliff_is_xcode=xliff_is_xcode)
