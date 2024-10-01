from . import git, hg, svn
from .utils import CommitToRepositoryException, PullFromRepositoryException


__all__ = [
    "CommitToRepositoryException",
    "PullFromRepositoryException",
    "commit_to_vcs",
    "get_revision",
    "update_from_vcs",
]


def update_from_vcs(repo_type: str, url: str, path: str, branch: str | None) -> None:
    get_repo(repo_type).update(url, path, branch)


def commit_to_vcs(
    repo_type: str, path: str, message: str, author: str, branch: str | None, url: str
) -> None:
    repo = get_repo(repo_type)
    try:
        repo.commit(path, message, author, branch, url)
    except CommitToRepositoryException as e:
        repo.log.debug(f"{repo_type.upper()} Commit Error for {path}: {e}")
        raise e


def get_revision(repo_type: str, path: str) -> str | None:
    return get_repo(repo_type).revision(path)


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
