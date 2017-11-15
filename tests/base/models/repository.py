
import os

from six.moves.urllib.parse import urlparse

import pytest

from mock import call, patch, Mock

from pontoon.base.models import ProjectLocale


@pytest.mark.django_db
def test_repo_checkout_path(repo_file0, settings):
    """checkout_path should be determined by the repo URL."""
    # im a bit unclear about the mix of os.path and urlparse here
    # how would this work on windows <> linux ?
    assert (
        repo_file0.checkout_path
        == os.path.join(
            *[repo_file0.project.checkout_path]
            + urlparse(repo_file0.url).path.split('/')))
    settings.MEDIA_ROOT = '/media/root'
    assert (
        repo_file0.checkout_path
        == os.path.join(
            *[repo_file0.project.checkout_path]
            + urlparse(repo_file0.url).path.split('/')))
    assert repo_file0.project.checkout_path.startswith("/media/root")


@pytest.mark.django_db
def test_repo_checkout_path_multi_locale(settings, repo_git0):
    """
    The checkout_path for multi-locale repos should not include the
    locale_code variable.
    """
    repo_git0.url = 'https://example.com/path/to/{locale_code}/'
    repo_git0.save()
    settings.MEDIA_ROOT = '/media/root'
    assert (
        repo_git0.checkout_path
        == ('/media/root/projects/%s/path/to'
            % repo_git0.project.slug))


@pytest.mark.django_db
def test_repo_checkout_path_source_repo(settings, repo_git0):
    """
    The checkout_path for a source repo should end with a templates
    directory.
    """
    repo_git0.source_repo = True
    repo_git0.url = 'https://example.com/path/to/locale/'
    repo_git0.save()
    assert (
        repo_git0.checkout_path
        == ('%s/projects/%s/path/to/locale/templates'
            % (settings.MEDIA_ROOT,
               repo_git0.project.slug)))


@pytest.mark.django_db
def test_repo_locale_checkout_path(settings, repo_git0, locale0):
    """Append the locale code the the project's checkout_path."""
    repo_git0.url = 'https://example.com/path/{locale_code}/'
    repo_git0.save()
    assert (
        repo_git0.locale_checkout_path(locale0)
        == ('%s/projects/%s/path/%s'
            % (settings.MEDIA_ROOT,
               repo_git0.project.slug,
               locale0.code)))


@pytest.mark.django_db
def test_repo_path_non_multi_locale(repo_git0, locale0):
    """If the repo isn't multi-locale, throw a ValueError."""
    assert repo_git0.multi_locale is False

    with pytest.raises(ValueError):
        repo_git0.locale_checkout_path(locale0)


@pytest.mark.django_db
def test_repo_locale_url(repo_git0, locale0):
    """Fill in the {locale_code} variable in the URL."""

    repo_git0.url = 'https://example.com/path/to/{locale_code}/'
    repo_git0.save()
    assert (
        repo_git0.locale_url(locale0)
        == 'https://example.com/path/to/%s/' % locale0.code)


@pytest.mark.django_db
def test_repo_locale_url_non_multi_locale(repo_git0, locale0):
    """If the repo isn't multi-locale, throw a ValueError."""
    with pytest.raises(ValueError):
        repo_git0.locale_url(locale0)


@pytest.mark.django_db
def test_repo_url_for_path(repo_git0, locale0, locale1):
    """
    Return the first locale_checkout_path for locales active for the
    repo's project that matches the given path.
    """
    ProjectLocale.objects.create(
        project=repo_git0.project, locale=locale0)
    ProjectLocale.objects.create(
        project=repo_git0.project, locale=locale1)
    repo_git0.url = 'https://example.com/path/to/{locale_code}/'
    repo_git0.save()
    assert (
        repo_git0.url_for_path(
            os.path.join(
                repo_git0.locale_checkout_path(locale0),
                'foo/bar.po'))
        == 'https://example.com/path/to/%s/' % locale0.code)


@pytest.mark.django_db
def test_repo_url_for_path_no_match(repo_git0, locale0):

    with pytest.raises(ValueError):
        repo_git0.url_for_path(
            os.path.join(
                repo_git0.locale_checkout_path(locale0),
                'foo/bar.po'))


@pytest.mark.django_db
def test_repo_pull(repo_git0):

    with patch('pontoon.base.models.update_from_vcs') as m_update_from_vcs:
        with patch('pontoon.base.models.get_revision') as m_get_revision:
            repo_git0.url = 'https://example.com'
            m_get_revision.return_value = 'asdf'
            assert (
                repo_git0.pull()
                == {'single_locale': 'asdf'})
            assert (
                m_update_from_vcs.call_args[0]
                == ('git',
                    'https://example.com',
                    repo_git0.checkout_path,
                    u''))


@pytest.mark.django_db
def test_repo_pull_multi_locale(repo_git0, locale0, locale1):
    """
    If the repo is multi-locale, pull all of the repos for the
    active locales.
    """

    ProjectLocale.objects.create(
        project=repo_git0.project, locale=locale0)
    ProjectLocale.objects.create(
        project=repo_git0.project, locale=locale1)

    with patch('pontoon.base.models.update_from_vcs') as m_update_from_vcs:
        with patch('pontoon.base.models.get_revision') as m_get_revision:
            repo_git0.url = 'https://example.com/{locale_code}/'
            repo_git0.locale_url = (
                lambda locale: (
                    'https://example.com/%s'
                    % locale.code))
            repo_git0.locale_checkout_path = (
                lambda locale: (
                    '/media/%s' % locale.code))

            # Return path as the revision so different locales return
            # different values.
            m_get_revision.side_effect = lambda type, path: path
            assert (
                repo_git0.pull()
                == {locale0.code: '/media/%s' % locale0.code,
                    locale1.code: '/media/%s' % locale1.code})
            assert (
                m_update_from_vcs.call_args_list
                == [call('git',
                         'https://example.com/%s' % locale0.code,
                         '/media/%s' % locale0.code, ''),
                    call('git',
                         'https://example.com/%s' % locale1.code,
                         '/media/%s' % locale1.code, '')])


@pytest.mark.django_db
def test_repo_commit(repo_git0):
    repo_git0.url = 'https://example.com'

    with patch('pontoon.base.models.commit_to_vcs') as m:
        repo_git0.commit('message', 'author', 'path')
        assert (
            m.call_args[0]
            == ('git',
                'path',
                'message',
                'author',
                '',
                'https://example.com'))


@pytest.mark.django_db
def test_repo_commit_multi_locale(repo_git0):
    """
    If the repo is multi-locale, use the url from url_for_path for
    committing.
    """
    repo_git0.url = 'https://example.com/{locale_code}/'

    repo_git0.url_for_path = Mock(
        return_value='https://example.com/for_path')

    with patch('pontoon.base.models.commit_to_vcs') as m:
        repo_git0.commit('message', 'author', 'path')
        assert (
            m.call_args[0]
            == ('git',
                'path',
                'message',
                'author',
                '',
                'https://example.com/for_path'))
        assert repo_git0.url_for_path.call_args[0] == ('path', )
