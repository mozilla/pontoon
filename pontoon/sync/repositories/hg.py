import logging

from .utils import CommitToRepositoryException, PullFromRepositoryException, execute


log = logging.getLogger(__name__)


def update(source: str, target: str, branch: str | None, shallow: bool) -> None:
    log.debug(f"Mercurial: Updating repo {source}")

    # Undo local changes: Mercurial doesn't offer anything more elegant
    command = ["rm", "-rf", target]
    code, _, error = execute(command)

    command = ["hg", "clone", source, target]
    code, _, error = execute(command)

    if code == 0:
        log.debug(f"Mercurial: Repository at {source} cloned.")

    else:
        raise PullFromRepositoryException(error)


def commit(path: str, message: str, author: str, branch: str | None, url: str) -> None:
    log.debug("Mercurial: Commit to repository.")

    # Add new and remove missing paths
    execute(["hg", "addremove"], path)

    # Commit
    commit = ["hg", "commit", "-m", message, "-u", author]
    code, output, error = execute(commit, path)
    if code != 0 and error:
        raise CommitToRepositoryException(error)

    # Push
    code, output, error = execute(["hg", "push"], path)

    if code == 1 and b"no changes found" in output:
        return log.warning("Nothing to commit")

    if code != 0 and error:
        raise CommitToRepositoryException(error)

    log.info(message)


def revision(path: str) -> str | None:
    cmd = ["hg", "identify", "--id", "--rev=default"]
    code, output, _ = execute(cmd, path, log=log)
    return output.decode().strip() if code == 0 else None


def changed_files(
    path: str, from_revision: str
) -> tuple[list[str], list[str], list[tuple[str, str]]] | None:
    # Ignore trailing + in revision number. It marks local changes.
    rev = from_revision.rstrip("+")
    cmd = ["hg", "status", "-a", "-m", "-r", f"--rev={rev}", "--rev=default"]
    code, output, _ = execute(cmd, path, log=log)
    if code != 0:
        return None
    changed = []
    removed = []
    for line in output.decode().split("\n"):
        if line:
            if line.startswith(("A", "M")):
                changed.append(line.split(None, 2)[1])
            elif line.startswith("R"):
                removed.append(line.split(None, 2)[1])
    return changed, removed, []
