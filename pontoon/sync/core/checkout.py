import logging

from os import walk
from os.path import join, normpath, relpath
from typing import NamedTuple, cast

from django.db.models.manager import BaseManager

from pontoon.base.models import Project, Repository
from pontoon.sync.repositories import get_repo


log = logging.getLogger(__name__)


class Checkout:
    repo: Repository
    is_source: bool
    url: str
    path: str
    prev_commit: str | None
    commit: str | None
    changed: list[str]
    """Relative paths from the checkout base"""
    removed: list[str]
    """Relative paths from the checkout base"""
    renamed: list[tuple[str, str]]
    """Relative paths (old, new) from the checkout base"""

    def __init__(
        self,
        slug: str,
        db_repo: Repository,
        *,
        pull: bool = True,
        force: bool = False,
        shallow: bool = False,
    ) -> None:
        self.repo = db_repo
        self.is_source = db_repo.source_repo
        self.url = db_repo.url
        self.path = normpath(db_repo.checkout_path)
        self.prev_commit = db_repo.last_synced_revision

        versioncontrol = get_repo(db_repo.type)
        if pull:
            versioncontrol.update(self.url, self.path, db_repo.branch, shallow)
        else:
            log.info(f"[{slug}] Skipping pull")
        self.commit = versioncontrol.revision(self.path)
        str_updated = (
            f"at {self.commit}"
            if not self.prev_commit or self.prev_commit == self.commit
            else f"updated from {self.prev_commit} to {self.commit}"
        )
        log.info(f"[{slug}] Repo {str_updated}")

        delta = (
            versioncontrol.changed_files(self.path, self.prev_commit)
            if not shallow and isinstance(self.prev_commit, str)
            else None
        )
        if shallow:
            self.changed = []
            self.removed = []
            self.renamed = []
        elif delta is not None and not force:
            self.changed, self.removed, self.renamed = delta
        else:
            # Initially and on error & when forced, consider all files changed
            log.warning(f"[{slug}] Considering all files as changed (f={force},s={shallow},d={delta})")
            self.changed = []
            for root, dirnames, filenames in walk(self.path):
                dirnames[:] = (dn for dn in dirnames if not dn.startswith("."))
                rel_root = relpath(root, self.path) if root != self.path else ""
                self.changed.extend(
                    join(rel_root, fn) for fn in filenames if not fn.startswith(".")
                )
            self.removed = delta[1] if delta else []
            self.renamed = []


class Checkouts(NamedTuple):
    source: Checkout
    target: Checkout


def checkout_repos(
    project: Project,
    *,
    pull: bool = True,
    force: bool = False,
    shallow: bool = False,
) -> Checkouts:
    """
    For each project repository,
    update its local checkout (unless `pull` is false),
    and provide a `Checkout` representing their current state.
    """
    source: Checkout | None = None
    target: Checkout | None = None

    # If the project using configuration file has unsynced locales, perform forced sync
    if not force and project.configuration_file and project.unsynced_locales:
        force = True

    for repo in cast(BaseManager[Repository], project.repositories).all():
        if repo.source_repo:
            if source:
                raise Exception("Multiple source repositories")
            source = Checkout(
                project.slug, repo, force=force, pull=pull, shallow=shallow
            )
            log.debug(f"[{project.slug}] source root: {source.path}")
        elif target:
            raise Exception("Multiple target repositories")
        else:
            target = Checkout(
                project.slug, repo, force=force, pull=pull, shallow=shallow
            )
            log.debug(f"[{project.slug}] target root: {target.path}")
    if source is None and target is None:
        raise Exception("No repository found")
    return Checkouts(source or target, target or source)
