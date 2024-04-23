from logging import Logger
import subprocess


class PullFromRepositoryException(Exception):
    pass


class CommitToRepositoryException(Exception):
    pass


def execute(
    command: list[str], cwd: str | None = None, env=None, log: Logger | None = None
) -> tuple[int, bytes, str | None]:
    try:
        sp = subprocess.PIPE
        proc = subprocess.Popen(
            command, stdout=sp, stderr=sp, stdin=sp, cwd=cwd, env=env
        )
        output, error = proc.communicate()
        strerror = error.decode() if error else None
        if log is not None and proc.returncode != 0:
            log.error(
                f"Error while executing command `{command}` in `{cwd}`: {strerror}"
            )
        return proc.returncode, output, strerror
    except OSError as error:
        return -1, b"", error.strerror
