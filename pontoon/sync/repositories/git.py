import logging

from django.conf import settings

from .utils import CommitToRepositoryException, PullFromRepositoryException, execute


log = logging.getLogger(__name__)


def update(source: str, target: str, branch: str | None) -> None:
    log.debug(f"Git: Updating repo {source}")

    command = ["git", "fetch", "--all"]
    execute(command, target)

    # Undo local changes
    remote = f"origin/{branch}" if branch else "origin"

    command = ["git", "reset", "--hard", remote]
    code, output, error = execute(command, target)

    if code != 0:
        if error != "No such file or directory":
            log.debug(output)
            log.warning(f"Git: {error}")
        log.debug("Git: Cloning repo...")
        command = ["git", "clone", source, target]
        code, output, error = execute(command)

        if code != 0:
            log.debug(output)
            raise PullFromRepositoryException(error)

        log.debug("Git: Repo cloned.")
    else:
        log.debug("Git: Repo updated.")

    if branch:
        command = ["git", "checkout", branch]
        code, output, error = execute(command, target)

        if code != 0:
            log.debug(output)
            raise PullFromRepositoryException(error)

        log.debug(f"Git: Branch {branch} checked out.")


def commit(path: str, message: str, author: str, branch: str | None, url: str) -> None:
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
    commit = git_cmd + ["commit", "-m", message, "--author", author]
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
    cmd = ["git", "rev-parse", "--short", "HEAD"]
    code, output, _error = execute(cmd, path, log=log)
    return output.decode().strip() if code == 0 else None


def changed_files(
    path: str, from_revision: str
) -> tuple[list[str], list[str], list[tuple[str, str]]] | None:
    cmd = [
        "git",
        "diff",
        "--name-status",
        "--find-renames=100%",
        f"{from_revision}..HEAD",
        "--",
        path,
    ]
    code, output, _error = execute(cmd, path, log=log)
    if code != 0:
        return None
    changed: list[str] = []
    removed: list[str] = []
    renamed: list[tuple[str, str]] = []  # [(from, to)]
    for line in output.decode().strip().split("\n"):
        if line.startswith(("A", "M")):
            changed.append(line.split(None, 2)[1])
        elif line.startswith("D"):
            removed.append(line.split(None, 2)[1])
        elif line.startswith("R"):
            parts = line.split()
            if len(parts) == 3:
                renamed.append((parts[1], parts[2]))
            else:
                log.warning(f"Git: Failed to parse diff line: {line}")
                return None
        else:
            log.warning(f"Git: Failed to parse diff line: {line}")
            return None
    return changed, removed, renamed
