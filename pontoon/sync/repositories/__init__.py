from . import git, hg
from .utils import CommitToRepositoryException, PullFromRepositoryException


__all__ = [
    "CommitToRepositoryException",
    "PullFromRepositoryException",
    "get_repo",
]


def get_repo(type: str):
    type = type.lower()
    if type == "git":
        return git
    elif type == "hg":
        return hg
    else:
        raise NotImplementedError
