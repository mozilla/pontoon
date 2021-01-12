import os
from unittest.mock import call, patch, Mock
from urllib.parse import urlparse

import pytest

from pontoon.test.factories import ProjectLocaleFactory


@pytest.mark.django_db
def test_repo_checkout_path(repo_git, settings):
    """checkout_path should be determined by the repo URL."""
    # im a bit unclear about the mix of os.path and urlparse here
    # how would this work on windows <> linux ?
    assert repo_git.checkout_path == os.path.join(
        *[repo_git.project.checkout_path] + urlparse(repo_git.url).path.split("/")
    )
    settings.MEDIA_ROOT = "/media/root"
    assert repo_git.checkout_path == os.path.join(
        *[repo_git.project.checkout_path] + urlparse(repo_git.url).path.split("/")
    )
    assert repo_git.project.checkout_path.startswith("/media/root")


@pytest.mark.django_db
def test_repo_checkout_path_multi_locale(settings, repo_git):
    """
    The checkout_path for multi-locale repos should not include the
    locale_code variable.
    """
    repo_git.url = "https://example.com/path/to/{locale_code}/"
    repo_git.save()
    settings.MEDIA_ROOT = "/media/root"
    assert repo_git.checkout_path == (
        "/media/root/projects/%s/path/to" % repo_git.project.slug
    )


@pytest.mark.django_db
def test_repo_checkout_path_source_repo(settings, repo_git):
    """
    The checkout_path for a source repo should end with a templates
    directory.
    """
    repo_git.source_repo = True
    repo_git.url = "https://example.com/path/to/locale/"
    repo_git.save()
    assert repo_git.checkout_path == (
        "%s/projects/%s/path/to/locale/templates"
        % (settings.MEDIA_ROOT, repo_git.project.slug)
    )


@pytest.mark.django_db
def test_repo_locale_checkout_path(settings, repo_git, locale_a):
    """Append the locale code the the project's checkout_path."""
    repo_git.url = "https://example.com/path/{locale_code}/"
    repo_git.save()
    assert repo_git.locale_checkout_path(locale_a) == (
        "%s/projects/%s/path/%s"
        % (settings.MEDIA_ROOT, repo_git.project.slug, locale_a.code,)
    )


@pytest.mark.django_db
def test_repo_path_non_multi_locale(repo_git, locale_a):
    """If the repo isn't multi-locale, throw a ValueError."""
    assert repo_git.multi_locale is False

    with pytest.raises(ValueError):
        repo_git.locale_checkout_path(locale_a)


@pytest.mark.django_db
def test_repo_locale_url(repo_git, locale_a):
    """Fill in the {locale_code} variable in the URL."""

    repo_git.url = "https://example.com/path/to/{locale_code}/"
    repo_git.save()
    assert (
        repo_git.locale_url(locale_a)
        == "https://example.com/path/to/%s/" % locale_a.code
    )


@pytest.mark.django_db
def test_repo_locale_url_non_multi_locale(repo_git, locale_a):
    """If the repo isn't multi-locale, throw a ValueError."""
    with pytest.raises(ValueError):
        repo_git.locale_url(locale_a)


@pytest.mark.django_db
def test_repo_url_for_path(project_locale_a, repo_git, locale_b):
    """
    Return the first locale_checkout_path for locales active for the
    repo's project that matches the given path.
    """
    ProjectLocaleFactory.create(
        project=repo_git.project, locale=locale_b,
    )
    repo_git.url = "https://example.com/path/to/{locale_code}/"
    repo_git.save()
    assert (
        repo_git.url_for_path(
            os.path.join(
                repo_git.locale_checkout_path(project_locale_a.locale), "foo/bar.po"
            )
        )
        == "https://example.com/path/to/%s/" % project_locale_a.locale.code
    )


@pytest.mark.django_db
def test_repo_url_for_path_no_match(repo_git, locale_a, settings):
    repo_git.url = "https://example.com/path/to/{locale_code}/"
    repo_git.save()
    settings.MEDIA_ROOT = "/media/root"

    with pytest.raises(ValueError):
        repo_git.url_for_path("/media/root/path/to/match/foo/bar.po")


@pytest.mark.django_db
def test_repo_pull(repo_git):
    with patch(
        "pontoon.sync.vcs.repositories.update_from_vcs"
    ) as m_update_from_vcs, patch(
        "pontoon.sync.vcs.repositories.get_revision"
    ) as m_get_revision:
        repo_git.url = "https://example.com"
        m_get_revision.return_value = "asdf"
        assert repo_git.pull() == {"single_locale": "asdf"}
        assert m_update_from_vcs.call_args[0] == (
            "git",
            "https://example.com",
            repo_git.checkout_path,
            u"",
        )


@pytest.mark.django_db
def test_repo_pull_multi_locale(project_locale_a, repo_git, locale_b):
    """
    If the repo is multi-locale, pull all of the repos for the
    active locales.
    """
    locale_a = project_locale_a.locale
    ProjectLocaleFactory.create(
        project=repo_git.project, locale=locale_b,
    )

    with patch("pontoon.sync.vcs.repositories.update_from_vcs") as m_update_from_vcs:
        with patch("pontoon.sync.vcs.repositories.get_revision") as m_get_revision:
            repo_git.url = "https://example.com/{locale_code}/"
            repo_git.locale_url = lambda locale: "https://example.com/%s" % locale.code
            repo_git.locale_checkout_path = lambda locale: "/media/%s" % locale.code

            # Return path as the revision so different locales return
            # different values.
            m_get_revision.side_effect = lambda type, path: path
            assert repo_git.pull() == {
                locale_a.code: "/media/%s" % locale_a.code,
                locale_b.code: "/media/%s" % locale_b.code,
            }
            assert m_update_from_vcs.call_args_list == [
                call(
                    "git",
                    "https://example.com/%s" % locale_b.code,
                    "/media/%s" % locale_b.code,
                    "",
                ),
                call(
                    "git",
                    "https://example.com/%s" % locale_a.code,
                    "/media/%s" % locale_a.code,
                    "",
                ),
            ]


@pytest.mark.django_db
def test_repo_commit(repo_git):
    repo_git.url = "https://example.com"

    with patch("pontoon.sync.vcs.repositories.commit_to_vcs") as m:
        repo_git.commit("message", "author", "path")
        assert m.call_args[0] == (
            "git",
            "path",
            "message",
            "author",
            "",
            "https://example.com",
        )


@pytest.mark.django_db
def test_repo_commit_multi_locale(repo_git):
    """
    If the repo is multi-locale, use the url from url_for_path for
    committing.
    """
    repo_git.url = "https://example.com/{locale_code}/"

    repo_git.url_for_path = Mock(return_value="https://example.com/for_path")

    with patch("pontoon.sync.vcs.repositories.commit_to_vcs") as m:
        repo_git.commit("message", "author", "path")
        assert m.call_args[0] == (
            "git",
            "path",
            "message",
            "author",
            "",
            "https://example.com/for_path",
        )
        assert repo_git.url_for_path.call_args[0] == ("path",)
