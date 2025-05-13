import logging
import re

from os.path import join, normpath
from urllib.parse import urlparse

from jsonfield import JSONField

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils.functional import cached_property


log = logging.getLogger(__name__)


def repository_url_validator(url):
    # Regular URLs
    validator = URLValidator(["http", "https", "ftp", "ftps", "ssh"])

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

    project = models.ForeignKey("Project", models.CASCADE, related_name="repositories")
    type = models.CharField(max_length=255, default=Type.GIT, choices=Type.choices)
    url = models.CharField(
        "URL", max_length=2000, validators=[repository_url_validator]
    )
    branch = models.CharField("Branch", blank=True, max_length=2000)

    website = models.URLField("Public Repository Website", blank=True, max_length=2000)

    last_synced_revisions = JSONField(blank=True, default=dict)
    """
    Mapping with a single key named "single_locale" with the VCS revision of its last sync.
    """

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
    def checkout_path(self):
        """
        Path where the checkout for this repo is located. Does not
        include a trailing path separator.
        """

        # Include path components from the URL in case it has locale
        # information, like https://hg.mozilla.org/gaia-l10n/fr/.
        # No worry about overlap between repos, any overlap of locale
        # directories is an error already.
        path_components = [
            self.project.checkout_path,
            *urlparse(self.url).path.split("/"),
        ]

        # Normalize path for consistency.
        return normpath(join(*path_components))

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

    @property
    def last_synced_revision(self) -> str | None:
        return (
            self.last_synced_revisions.get("single_locale", None)
            if self.last_synced_revisions
            else None
        )

    @last_synced_revision.setter
    def last_synced_revision(self, revision: str) -> None:
        self.last_synced_revisions = {"single_locale": revision}
        self.save(update_fields=["last_synced_revisions"])

    class Meta:
        unique_together = ("project", "url")
        ordering = ["id"]
