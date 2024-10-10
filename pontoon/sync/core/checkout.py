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

    def __init__(self, slug: str, db_repo: Repository, pull: bool, force: bool) -> None:
        self.repo = db_repo
        self.is_source = db_repo.source_repo
        self.url = db_repo.url
        self.path = normpath(db_repo.checkout_path)
        self.prev_commit = db_repo.last_synced_revision

        versioncontrol = get_repo(db_repo.type)
        if pull:
            log.info(f"[{slug}] Pulling updates from {self.url}")
            versioncontrol.update(self.url, self.path, db_repo.branch)
        else:
            log.info(f"[{slug}] Skipping pull")
        self.commit = versioncontrol.revision(self.path)
        log.info(f"[{slug}] Repo {self.url} now at {self.commit}")

        delta = (
            versioncontrol.changed_files(self.path, self.prev_commit)
            if isinstance(self.prev_commit, str)
            else None
        )
        if delta is not None and not force:
            self.changed, self.removed, self.renamed = delta
        else:
            # Initially and on error & when forced, consider all files changed
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
    project: Project, pull: bool = True, force: bool = False
) -> Checkouts:
    """
    For each project repository,
    update its local checkout (unless `pull` is false),
    and provide a `Checkout` representing their current state.
    """
    source: Checkout | None = None
    target: Checkout | None = None
    for repo in cast(BaseManager[Repository], project.repositories).all():
        if repo.source_repo:
            if source:
                raise Exception("Multiple source repositories")
            source = Checkout(project.slug, repo, pull, force)
        elif target:
            raise Exception("Multiple target repositories")
        else:
            target = Checkout(project.slug, repo, pull, force)
    if source is None and target is None:
        raise Exception("No repository found")
    return Checkouts(source or target, target or source)
