from os.path import join
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from compare_locales.paths import ProjectFiles, TOMLParser
from django.utils.functional import cached_property


class DownloadTOMLParser(TOMLParser):
    """
    This wrapper is a workaround for the lack of the shared and persistent filesystem
    on Heroku workers.
    Related: https://bugzilla.mozilla.org/show_bug.cgi?id=1530988
    """

    def __init__(self, checkout_path, permalink_prefix, configuration_file):
        self.checkout_path = join(checkout_path, "")
        self.permalink_prefix = permalink_prefix
        self.config_path = urlparse(permalink_prefix).path
        self.config_file = configuration_file

    def get_local_path(self, path):
        """Return the directory in which the config file should be stored."""
        local_path = path.replace(self.config_path, "")

        return join(self.checkout_path, local_path)

    def get_remote_path(self, path):
        """Construct the link to the remote resource based on the local path."""
        remote_config_path = path.replace(self.checkout_path, "")

        return urljoin(self.permalink_prefix, remote_config_path)

    def get_project_config(self, path):
        """Download the project config file and return its local path."""
        local_path = Path(self.get_local_path(path))
        local_path.parent.mkdir(parents=True, exist_ok=True)

        with local_path.open("wb") as f:
            remote_path = self.get_remote_path(path)
            config_file = requests.get(remote_path)
            config_file.raise_for_status()
            f.write(config_file.content)
        return str(local_path)

    def parse(self, path=None, env=None, ignore_missing_includes=True):
        """Download the config file before it gets parsed."""
        return super().parse(
            self.get_project_config(path or self.config_file),
            env,
            ignore_missing_includes,
        )


class VCSConfiguration:
    """
    Container for the project configuration, provided by the optional
    configuration file.

    For more information, see:
    https://moz-l10n-config.readthedocs.io/en/latest/fileformat.html.
    """

    def __init__(self, vcs_project):
        self.vcs_project = vcs_project
        self.configuration_file = vcs_project.db_project.configuration_file
        self.project_files = {}

    @cached_property
    def l10n_base(self):
        """
        If project configuration provided, files could be stored in multiple
        directories, so we just use the translation repository checkout path
        """
        return self.vcs_project.db_project.translation_repositories()[0].checkout_path

    @cached_property
    def parsed_configuration(self):
        """Return parsed project configuration file."""
        if self.vcs_project.db_project.source_repository.permalink_prefix:
            """If we have a permalink we download the configuration file"""
            return DownloadTOMLParser(
                self.vcs_project.db_project.source_repository.checkout_path,
                self.vcs_project.db_project.source_repository.permalink_prefix,
                self.configuration_file,
            ).parse(env={"l10n_base": self.l10n_base})
        else:
            """If we don't have a permalink we use the configuration file from the checkout path"""
            return TOMLParser().parse(
                join(
                    self.vcs_project.db_project.source_repository.checkout_path,
                    self.configuration_file,
                ),
                env={"l10n_base": self.l10n_base},
                ignore_missing_includes=True,
            )

    def add_locale(self, locale_code):
        """
        Add new locale to project configuration.
        """
        locales = self.parsed_configuration.locales or []
        locales.append(locale_code)
        self.parsed_configuration.set_locales(locales)

        """
        TODO: For now we don't make changes to the configuration file to
        avoid committing it to the VCS. The pytoml serializer messes with the
        file layout (indents and newlines) pretty badly. We should fix the
        serializer and replace the content of this method with the following
        code:

        # Update configuration file
        with open(self.configuration_path, 'r+b') as f:
            data = pytoml.load(f)
            data['locales'].append(locale_code)
            f.seek(0)
            f.write(pytoml.dumps(data, sort_keys=True))
            f.truncate()

        # Invalidate cached parsed configuration
        del self.__dict__['parsed_configuration']

        # Commit configuration file to VCS
        commit_message = 'Update configuration file'
        commit_author = User(
            first_name=settings.VCS_SYNC_NAME,
            email=settings.VCS_SYNC_EMAIL,
        )
        repo = self.vcs_project.db_project.source_repository
        repo.commit(commit_message, commit_author, repo.checkout_path)
        """

    def get_or_set_project_files(self, locale_code):
        """
        Get or set project files for the given locale code. This approach
        allows us to cache the files for later use.

        Also, make sure that the requested locale_code is available in the
        configuration file.
        """
        if (
            locale_code is not None
            and locale_code not in self.parsed_configuration.all_locales
        ):
            self.add_locale(locale_code)

        return self.project_files.setdefault(
            locale_code,
            ProjectFiles(locale_code, [self.parsed_configuration]),
        )

    def l10n_path(self, locale, reference_path):
        """
        Return l10n path for the given locale and reference path.
        """
        project_files = self.get_or_set_project_files(locale.code)

        m = project_files.match(reference_path)
        return m[0] if m is not None else None

    def reference_path(self, locale, l10n_path):
        """
        Return reference path for the given locale and l10n path.
        """
        project_files = self.get_or_set_project_files(locale.code)

        m = project_files.match(l10n_path)
        return m[1] if m is not None else None

    def locale_resources(self, locale):
        """
        Return a list of Resource instances, which need to be enabled for the
        given locale.
        """
        resources = []
        project_files = self.get_or_set_project_files(locale.code)

        for resource in self.vcs_project.db_project.resources.all():
            absolute_resource_path = join(
                self.vcs_project.source_directory_path, resource.path
            )

            if project_files.match(absolute_resource_path):
                resources.append(resource)

        return resources
