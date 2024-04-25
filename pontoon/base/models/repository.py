import logging
import re
from os import sep
from os.path import join
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils.functional import cached_property
from jsonfield import JSONField

log = logging.getLogger(__name__)


def repository_url_validator(url):
    # Regular URLs
    validator = URLValidator(["http", "https", "ftp", "ftps", "ssh", "svn+ssh"])

    # Git SCP-like URL
    pattern = r"git@[\w\.@]+[/:][\w-]+/[\w-]+(.git)?/?"

    try:
        validator(url)
    except ValidationError:
        if not re.match(pattern, url):
            raise ValidationError("Invalid URL")


class Repository(models.Model):
    """
    A remote VCS repository that stores resource files for a project.
    """

    class Type(models.TextChoices):
        GIT = "git", "Git"
        HG = "hg", "HG"
        SVN = "svn", "SVN"

    project = models.ForeignKey("Project", models.CASCADE, related_name="repositories")
    type = models.CharField(max_length=255, default=Type.GIT, choices=Type.choices)
    url = models.CharField(
        "URL", max_length=2000, validators=[repository_url_validator]
    )
    branch = models.CharField("Branch", blank=True, max_length=2000)

    website = models.URLField("Public Repository Website", blank=True, max_length=2000)

    # TODO: We should be able to remove this once we have persistent storage
    permalink_prefix = models.CharField(
        "Download prefix or path to TOML file",
        blank=True,
        max_length=2000,
        help_text="""
        A URL prefix for downloading localized files. For GitHub repositories,
        select any localized file on GitHub, click Raw and replace locale code
        and the following bits in the URL with `{locale_code}`. If you use a
        project configuration file, you need to provide the path to the raw TOML
        file on GitHub.
    """,
    )

    """
    Mapping of locale codes to VCS revisions of each repo at the last
    sync. If this isn't a multi-locale repo, the mapping has a single
    key named "single_locale" with the revision.
    """
    last_synced_revisions = JSONField(blank=True, default=dict)

    source_repo = models.BooleanField(
        default=False,
        help_text="""
        If true, this repo contains the source strings directly in the
        root of the repo. Checkouts of this repo will have "templates"
        appended to the end of their path so that they are detected as
        source directories.
    """,
    )

    def __repr__(self):
        repo_kind = "Repository"
        if self.source_repo:
            repo_kind = "SourceRepository"
        return f"<{repo_kind}[{self.pk}:{self.type}:{self.url}]"

    @property
    def multi_locale(self):
        """
        Checks if url contains locale code variable. System will replace
        this variable by the locale codes of all enabled locales for the
        project during pulls and commits.
        """
        return "{locale_code}" in self.url

    @property
    def is_source_repository(self):
        """
        Returns true if repository contains source strings.
        """
        return self == self.project.source_repository

    @property
    def is_translation_repository(self):
        """
        Returns true if repository contains translations.
        """
        return self.project.has_single_repo or not self.is_source_repository

    @property
    def checkout_path(self):
        """
        Path where the checkout for this repo is located. Does not
        include a trailing path separator.
        """
        path_components = [self.project.checkout_path]

        # Include path components from the URL in case it has locale
        # information, like https://hg.mozilla.org/gaia-l10n/fr/.
        # No worry about overlap between repos, any overlap of locale
        # directories is an error already.
        path_components += urlparse(self.url).path.split("/")
        if self.multi_locale:
            path_components = [c for c in path_components if c != "{locale_code}"]

        if self.source_repo:
            path_components.append("templates")

        # Remove trailing separator for consistency.
        return join(*path_components).rstrip(sep)

    @cached_property
    def api_config(self):
        """
        Repository API configuration consists of:
        - Endpoint: A URL pattern to get repository metadata from. Used during sync for faster
          retrieval of latest commit hashes in combination with the Key.
          Supports {locale_code} wildcard.
        - Key: A string used to retrieve the latest commit hash from the JSON response.
        """
        url = self.url

        if url.startswith("ssh://hg.mozilla.org/"):
            parsed_url = urlparse(url)
            endpoint = "https://{netloc}/{path}/json-rev/default".format(
                netloc=parsed_url.netloc, path=parsed_url.path.strip("/")
            )
            return {
                "endpoint": endpoint,
                "get_key": lambda x: x["node"],
            }

        if url.startswith("ssh://hg@bitbucket.org/"):
            parsed_url = urlparse(url)
            endpoint = "https://api.bitbucket.org/2.0/repositories/{path}/commit/default".format(
                path=parsed_url.path.strip("/")
            )
            return {
                "endpoint": endpoint,
                "get_key": lambda x: x["hash"],
            }

        return None

    def locale_checkout_path(self, locale):
        """
        Path where the checkout for the given locale for this repo is
        located. If this repo is not a multi-locale repo, a ValueError
        is raised.
        """
        if not self.multi_locale:
            raise ValueError(
                "Cannot get locale_checkout_path for non-multi-locale repos."
            )

        return join(self.checkout_path, locale.code)

    def locale_url(self, locale):
        """
        URL for the repo for the given locale. If this repo is not a
        multi-locale repo, a ValueError is raised.
        """
        if not self.multi_locale:
            raise ValueError("Cannot get locale_url for non-multi-locale repos.")

        return self.url.format(locale_code=locale.code)

    def url_for_path(self, path):
        """
        Determine the locale-specific repo URL for the given path.

        If this is not a multi-locale repo, raise a ValueError. If no
        repo is found for the given path, also raise a ValueError.
        """
        for locale in self.project.locales.all():
            if path.startswith(self.locale_checkout_path(locale)):
                return self.locale_url(locale)

        raise ValueError(f"No repo found for path: {path}")

    def pull(self, locales=None):
        """
        Pull changes from VCS. Returns the revision(s) of the repo after
        pulling.
        """
        from pontoon.sync.repositories import (
            PullFromRepositoryException,
            get_revision,
            update_from_vcs,
        )

        if not self.multi_locale:
            update_from_vcs(self.type, self.url, self.checkout_path, self.branch)
            return {"single_locale": get_revision(self.type, self.checkout_path)}
        else:
            current_revisions = {}
            locales = locales or self.project.locales.all()

            for locale in locales:
                repo_type = self.type
                url = self.locale_url(locale)
                checkout_path = self.locale_checkout_path(locale)
                repo_branch = self.branch

                try:
                    update_from_vcs(repo_type, url, checkout_path, repo_branch)
                    current_revisions[locale.code] = get_revision(
                        repo_type, checkout_path
                    )
                except PullFromRepositoryException as e:
                    log.error(f"{repo_type.upper()} Pull Error for {url}: {e}")

            return current_revisions

    def commit(self, message, author, path):
        """Commit changes to VCS."""
        # For multi-locale repos, figure out which sub-repo corresponds
        # to the given path.
        url = self.url
        if self.multi_locale:
            url = self.url_for_path(path)

        from pontoon.sync.repositories import commit_to_vcs

        return commit_to_vcs(self.type, path, message, author, self.branch, url)

    def set_last_synced_revisions(self, locales=None):
        """
        Set last_synced_revisions to a dictionary of revisions
        that are currently downloaded on the disk.
        """
        from pontoon.sync.repositories import get_revision

        current_revisions = {}

        if self.multi_locale:
            for locale in self.project.locales.all():
                if locales is not None and locale not in locales:
                    revision = self.last_synced_revisions.get(locale.code)
                else:
                    revision = get_revision(
                        self.type, self.locale_checkout_path(locale)
                    )

                if revision:
                    current_revisions[locale.code] = revision

        else:
            current_revisions["single_locale"] = get_revision(
                self.type, self.checkout_path
            )

        self.last_synced_revisions = current_revisions
        self.save(update_fields=["last_synced_revisions"])

    def get_last_synced_revisions(self, locale=None):
        """
        Get revision from the last_synced_revisions dictionary if exists.
        """
        if self.last_synced_revisions:
            key = locale or "single_locale"
            return self.last_synced_revisions.get(key)
        else:
            return None

    class Meta:
        unique_together = ("project", "url")
        ordering = ["id"]
