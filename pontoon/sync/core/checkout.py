import logging

from os import sep, walk
from os.path import join, normpath, realpath, relpath
from typing import NamedTuple

from pontoon.base.models import Project, Repository
from pontoon.sync.repositories import get_repo


log = logging.getLogger(__name__)


def is_inside(root: str, path: str) -> bool:
    """
    Is `path` inside `root`, once the two have been fully resolved?

    Comparing paths as strings is not enough, because a path that looks
    contained may still resolve to a file elsewhere on the filesystem.
    """
    root = realpath(root)
    path = realpath(path)
    return path == root or path.startswith(root + sep)


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
            log.warning(f"[{slug}] Considering all files as changed")
            self.changed = []
            for root, dirnames, filenames in walk(self.path):
                dirnames[:] = (dn for dn in dirnames if not dn.startswith("."))
                rel_root = relpath(root, self.path) if root != self.path else ""
                self.changed.extend(
                    join(rel_root, fn) for fn in filenames if not fn.startswith(".")
                )
            self.removed = delta[1] if delta else []
            self.renamed = []

        # A repo can commit a symlink pointing anywhere on the filesystem.
        inside: list[str] = []
        for co_path in self.changed:
            if is_inside(self.path, join(self.path, co_path)):
                inside.append(co_path)
            else:
                log.error(f"[{slug}:{co_path}] Skipping path outside the checkout")
        self.changed = inside


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
    for repo in project.repositories.all():
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
