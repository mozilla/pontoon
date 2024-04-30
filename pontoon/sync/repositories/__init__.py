import os
from typing import Any

from . import git, hg, svn
from .utils import CommitToRepositoryException, PullFromRepositoryException

__all__ = [
    "CommitToRepositoryException",
    "PullFromRepositoryException",
    "commit_to_vcs",
    "get_changed_files",
    "get_revision",
    "update_from_vcs",
]


def update_from_vcs(repo_type: str, url: str, path: str, branch: str | None) -> None:
    get_repo(repo_type).update(url, path, branch)


def commit_to_vcs(
    repo_type: str, path: str, message: str, user: Any, branch: str | None, url: str
) -> None:
    repo = get_repo(repo_type)
    try:
        repo.commit(path, message, user, branch, url)
    except CommitToRepositoryException as e:
        repo.log.debug(f"{repo_type.upper()} Commit Error for {path}: {e}")
        raise e


def get_revision(repo_type: str, path: str) -> str | None:
    return get_repo(repo_type).revision(path)


def get_changed_files(
    repo_type: str, path: str, revision: str | None
) -> tuple[list[str], list[str]]:
    """Return a list of changed files for the repository."""
    repo = get_repo(repo_type)
    repo.log.info(f"Retrieving changed files for: {path}:{revision}")

    if revision is not None:
        delta = repo.changed_files(path, revision)
        if delta is not None:
            return delta

    # If there's no latest revision we should return all the files in the latest
    # version of repository
    paths = []
    for root, _, files in os.walk(path):
        for f in files:
            if root[0] == "." or "/." in root:
                continue
            paths.append(os.path.join(root, f).replace(path + "/", ""))
    return paths, []


def get_repo(type: str):
    type = type.lower()
    if type == "git":
        return git
    elif type == "hg":
        return hg
    elif type == "svn":
        return svn
    else:
        raise NotImplementedError
