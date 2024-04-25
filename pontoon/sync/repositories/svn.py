import logging
from os import environ, path
from typing import Any

from django.conf import settings

from .utils import CommitToRepositoryException, PullFromRepositoryException, execute

log = logging.getLogger(__name__)


def update(source: str, target: str, branch: str | None) -> None:
    log.debug("Subversion: Checkout or update repository.")

    if path.exists(target):
        status = "updated"
        command = ["svn", "update", "--accept", "theirs-full", target]

    else:
        status = "checked out"
        command = [
            "svn",
            "checkout",
            "--trust-server-cert",
            "--non-interactive",
            source,
            target,
        ]

    code, _output, error = execute(command, env=get_svn_env())

    if code != 0:
        raise PullFromRepositoryException(error)

    log.debug(f"Subversion: Repository at {source} {status}.")


def commit(path: str, message: str, user: Any, branch: str | None, url: str) -> None:
    log.debug("Subversion: Commit to repository.")

    # Commit
    commit = [
        "svn",
        "commit",
        "-m",
        message,
        "--with-revprop",
        f"author={user.display_name_and_email}",
        path,
    ]
    code, output, error = execute(commit, env=get_svn_env())
    if code != 0:
        raise CommitToRepositoryException(error)

    if not output and not error:
        return log.warning("Nothing to commit")

    log.info(message)


def revision(path: str) -> str | None:
    cmd = ["svnversion", path]
    code, output, _error = execute(cmd, env=get_svn_env(), log=log)
    return output.decode().strip() if code == 0 else None


def changed_files(path: str, from_revision: str) -> tuple[list[str], list[str]] | None:
    # Remove all non digit characters from the revision number.
    rev = "".join(filter(lambda c: c.isdigit(), from_revision))
    cmd = ["svn", "diff", "-r", f"{rev}:HEAD", "--summarize"]
    code, output, _error = execute(cmd, path, env=get_svn_env(), log=log)
    if code != 0:
        return None
    changed = []
    removed = []
    for line in output.decode().split("\n"):
        if line.startswith(("A", "M")):
            changed.append(line.split(None, 2)[1])
        elif line.startswith("D"):
            removed.append(line.split(None, 2)[1])
    return changed, removed


def get_svn_env():
    """Return an environment dict for running SVN in."""
    if settings.SVN_LD_LIBRARY_PATH:
        env = environ.copy()
        env[
            "LD_LIBRARY_PATH"
        ] = f"{settings.SVN_LD_LIBRARY_PATH}:{env['LD_LIBRARY_PATH']}"
        return env
    else:
        return None
