import logging
from typing import Any

from django.conf import settings

from .utils import CommitToRepositoryException, PullFromRepositoryException, execute

log = logging.getLogger(__name__)


def update(source: str, target: str, branch: str | None) -> None:
    log.debug("Git: Update repository.")

    command = ["git", "fetch", "--all"]
    execute(command, target)

    # Undo local changes
    remote = f"origin/{branch}" if branch else "origin"

    command = ["git", "reset", "--hard", remote]
    code, _output, error = execute(command, target)

    if code != 0:
        log.info(f"Git: {error}")
        log.debug("Git: Clone instead.")
        command = ["git", "clone", source, target]
        code, _output, error = execute(command)

        if code != 0:
            raise PullFromRepositoryException(error)

        log.debug(f"Git: Repository at {source} cloned.")
    else:
        log.debug(f"Git: Repository at {source} updated.")

    if branch:
        command = ["git", "checkout", branch]
        code, _output, error = execute(command, target)

        if code != 0:
            raise PullFromRepositoryException(error)

        log.debug(f"Git: Branch {branch} checked out.")


def commit(path: str, message: str, user: Any, branch: str | None, url: str) -> None:
    log.debug("Git: Commit to repository.")

    # Embed git identity info into commands
    git_cmd = [
        "git",
        "-c",
        f"user.name={settings.VCS_SYNC_NAME}",
        "-c",
        f"user.email={settings.VCS_SYNC_EMAIL}",
    ]

    # Add new and remove missing paths
    execute(git_cmd + ["add", "-A", "--", path], path)

    # Commit
    commit = git_cmd + [
        "commit",
        "-m",
        message,
        "--author",
        user.display_name_and_email,
    ]
    code, _output, error = execute(commit, path)
    if code != 0 and error:
        raise CommitToRepositoryException(error)

    # Push
    push = ["git", "push", url, branch or "HEAD"]
    code, _output, error = execute(push, path)

    if code != 0:
        if (
            "Updates were rejected because the remote contains work that you do"
            in error
        ):
            error = "Remote contains work that you do not have locally. " + error
        raise CommitToRepositoryException(error)

    if "Everything up-to-date" in error:
        return log.warning("Nothing to commit")

    log.info(message)


def revision(path: str) -> str | None:
    cmd = ["git", "rev-parse", "HEAD"]
    code, output, _error = execute(cmd, path, log=log)
    return output.decode().strip() if code == 0 else None


def changed_files(path: str, from_revision: str) -> tuple[list[str], list[str]] | None:
    cmd = ["git", "diff", "--name-status", f"{from_revision}..HEAD", "--", path]
    code, output, _error = execute(cmd, path, log=log)
    if code != 0:
        return None
    changed = []
    removed = []
    for line in output.decode().split("\n"):
        if line:
            if line.startswith(("A", "M")):
                changed.append(line.split(None, 2)[1])
            elif line.startswith("D"):
                removed.append(line.split(None, 2)[1])
    return changed, removed
