#!/usr/bin/env python
"""
This script uses https://hg.mozilla.org/projects/comm-l10n/ repository to
create repositories with source strings only for Thunderbird and Seamonkey.
"""

import datetime
import os
import shutil
import subprocess
import sys

TARGET_REPOS = {
    "thunderbird": [
        "calendar",
        "chat",
        "mail",
    ],
    "seamonkey": [
        "suite",
    ],
}


def logmsg(text):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {text}")


def execute(command, cwd=None):
    try:
        st = subprocess.PIPE
        proc = subprocess.Popen(args=command, stdout=st, stderr=st, stdin=st, cwd=cwd)

        (output, error) = proc.communicate()
        return_code = proc.returncode
        return return_code, output.decode("utf-8"), str(error)

    except OSError as error:
        return -1, "", error


def clone(url, folder):
    return_code, output, error = execute(["hg", "clone", url, folder])
    if return_code == 0:
        logmsg(f"Repository {url} cloned in {folder}.")
    else:
        logmsg(f"Error: {error}")

    return return_code


def pull(url, folder):
    if os.path.isdir(folder):
        # Undo local changes and purge extra files
        execute(["hg", "update", "-C"], folder)
        execute(["hg", "purge", "--config", "extensions.purge="], folder)

        # Try to pull, or clone if that fails
        return_code, output, error = execute(["hg", "pull", "-u"], folder)
        if return_code == 0:
            logmsg(f"Updating local clone of {url}")
        else:
            logmsg(f"Error: {error}")
            logmsg("Pull failed, clone instead.")

            # Remove target directory on a failed pull
            shutil.rmtree(folder)
            return_code = clone(url, folder)
    else:
        logmsg(f"Folder does not exist. Cloning {url}")
        return_code = clone(url, folder)

    # In case of a non-zero error return code, we need to quit early
    # (see bug 1475603).
    if return_code != 0:
        sys.exit(return_code)
    else:
        return return_code


def commit(folder):
    logmsg("Check repository status")
    return_code, output, error = execute(["hg", "status"], folder)

    if output != "":
        # Add new and remove missing
        execute(["hg", "addremove"], folder)

        # Commit
        return_code, output, error = execute(["hg", "commit", "-m", "Update"], folder)
        if return_code != 0 and len(error):
            logmsg(f"Error: {error}")
        else:
            logmsg(f"Committed changes in {folder}")

        return return_code
    else:
        logmsg(f"SKIP: Nothing to commit in {folder}")
        return 1


def push(folder):
    return_code, output, error = execute(["hg", "push"], folder)
    if return_code == 0:
        logmsg(f"Pushed repository in {folder}")
    elif len(error):
        logmsg(f"Error: {error}")


script_folder = os.path.dirname(os.path.abspath(__file__))

# Clone or update source repository
source_folder = os.path.join(script_folder, "source")
pull("https://hg.mozilla.org/projects/comm-l10n/", source_folder)

for repo, folders in TARGET_REPOS.items():
    # Clone or update target repository
    target_folder = os.path.join(script_folder, "target", repo)
    pull(f"ssh://hg.mozilla.org/users/m_owca.info/{repo}", target_folder)

    # Prune all subdirectories in target folder, so that we can remove
    # subfolders that were eventually removed.
    logmsg(f"Clean target folder {target_folder}")
    for f in os.listdir(target_folder):
        if os.path.isdir(os.path.join(target_folder, f)) and not f.startswith("."):
            shutil.rmtree(os.path.join(target_folder, f))

    # Copy relevant folders from source to target.
    # Source folders for this product are within the en-US subfolder.
    logmsg(f"Copy folders to {target_folder}")
    for keep_folder in folders:
        origin = os.path.join(source_folder, "en-US", keep_folder)
        destination = os.path.join(target_folder, keep_folder)

        if os.path.isdir(origin):
            shutil.copytree(origin, destination)
        else:
            logmsg(f"Folder {keep_folder} does not exist for repo {repo}")

    # Commit and push target repositories
    return_code = commit(target_folder)
    if return_code == 0:
        push(target_folder)
