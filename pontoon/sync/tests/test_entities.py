from os import makedirs
from os.path import join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest.mock import Mock

import pytest

from moz.l10n.paths import L10nDiscoverPaths

from django.conf import settings
from django.utils import timezone

from pontoon.base.models import Entity, Project, TranslatedResource
from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    RepositoryFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    TranslationFactory,
)
from pontoon.sync.core.checkout import Checkout, Checkouts
from pontoon.sync.core.entities import sync_entities_from_repo
from pontoon.sync.core.paths import find_paths
from pontoon.sync.core.stats import update_stats
from pontoon.sync.tests.utils import build_file_tree


now = timezone.now()


def test_no_changes():
    assert sync_entities_from_repo(
        Mock(Project),
        {},
        Mock(Checkout, changed=[], removed=[], renamed=[]),
        Mock(L10nDiscoverPaths),
        now,
    ) == (0, set(), set())


@pytest.mark.django_db
def test_remove_resource():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-rm", locales=[locale], repositories=[repo]
        )
        res_a = ResourceFactory.create(project=project, path="a.ftl", format="ftl")
        res_b = ResourceFactory.create(project=project, path="b.po", format="po")
        res_c = ResourceFactory.create(project=project, path="c.ftl", format="ftl")
        TranslatedResourceFactory.create(locale=locale, resource=res_a)
        TranslatedResourceFactory.create(locale=locale, resource=res_b)
        TranslatedResourceFactory.create(locale=locale, resource=res_c)

        # Filesystem setup
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.ftl": "", "b.pot": ""},
                "fr-Test": {"a.ftl": "", "b.po": "", "c.ftl": ""},
            },
        )

        # Paths setup
        mock_checkout = Mock(
            Checkout,
            path=repo.checkout_path,
            changed=[],
            removed=[join("en-US", "c.ftl")],
            renamed=[],
        )
        paths = find_paths(project, Checkouts(mock_checkout, mock_checkout))

        # Test
        assert sync_entities_from_repo(
            project, locale_map, mock_checkout, paths, now
        ) == (0, set(), {"c.ftl"})
        assert {res.path for res in project.resources.all()} == {"a.ftl", "b.po"}
        with pytest.raises(TranslatedResource.DoesNotExist):
            TranslatedResource.objects.get(resource=res_c)


@pytest.mark.django_db
def test_rename_resource():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-mv", locales=[locale], repositories=[repo]
        )
        res_a = ResourceFactory.create(project=project, path="a.ftl", format="ftl")
        res_b = ResourceFactory.create(project=project, path="b.po", format="po")
        res_c = ResourceFactory.create(project=project, path="c.ftl", format="ftl")
        TranslatedResourceFactory.create(locale=locale, resource=res_a)
        TranslatedResourceFactory.create(locale=locale, resource=res_b)
        TranslatedResourceFactory.create(locale=locale, resource=res_c)

        # Filesystem setup
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.ftl": "", "b.pot": "", "d.ftl": ""},
                "fr-Test": {"a.ftl": "", "b.po": "", "c.ftl": ""},
            },
        )

        # Paths setup
        mock_checkout = Mock(
            Checkout,
            path=repo.checkout_path,
            changed=[],
            removed=[],
            renamed=[(join("en-US", "c.ftl"), join("en-US", "d.ftl"))],
        )
        paths = find_paths(project, Checkouts(mock_checkout, mock_checkout))

        # Test
        assert sync_entities_from_repo(
            project, locale_map, mock_checkout, paths, now
        ) == (0, {"d.ftl"}, set())
        assert {res.path for res in project.resources.all()} == {
            "a.ftl",
            "b.po",
            "d.ftl",
        }
        res_c.refresh_from_db()
        assert res_c.path == "d.ftl"


@pytest.mark.django_db
def test_add_resource():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-add", locales=[locale], repositories=[repo]
        )
        res_a = ResourceFactory.create(project=project, path="a.ftl", format="ftl")
        res_b = ResourceFactory.create(project=project, path="b.po", format="po")
        TranslatedResourceFactory.create(locale=locale, resource=res_a)
        TranslatedResourceFactory.create(locale=locale, resource=res_b)

        # Filesystem setup
        c_ftl = dedent(
            """
            key-1 = Message 1
            key-2 = Message 2
            key-3 = Message 3
            """
        )
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.ftl": "", "b.pot": "", "c.ftl": c_ftl},
                "fr-Test": {"a.ftl": "", "b.po": ""},
            },
        )

        # Paths setup
        mock_checkout = Mock(
            Checkout,
            path=repo.checkout_path,
            changed=[join("en-US", "c.ftl")],
            removed=[],
            renamed=[],
        )
        paths = find_paths(project, Checkouts(mock_checkout, mock_checkout))

        # Test
        assert sync_entities_from_repo(
            project, locale_map, mock_checkout, paths, now
        ) == (3, set(), set())
        res_c = project.resources.get(path="c.ftl")
        TranslatedResource.objects.get(resource=res_c)
        assert set(ent.key for ent in Entity.objects.filter(resource=res_c)) == {
            "key-1",
            "key-2",
            "key-3",
        }


@pytest.mark.django_db
def test_update_resource():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-up", locales=[locale], repositories=[repo]
        )
        res = {}
        for n in ("a", "b", "c"):
            res[n] = ResourceFactory.create(
                project=project, path=f"{n}.ftl", format="ftl", total_strings=3
            )
            TranslatedResourceFactory.create(locale=locale, resource=res[n])
            for i in (1, 2, 3):
                entity = EntityFactory.create(
                    resource=res[n],
                    key=f"key-{n}-{i}",
                    string=f"key-{n}-{i} = Message {i}\n",
                )
                TranslationFactory.create(
                    entity=entity,
                    locale=locale,
                    string=f"key-{n}-{i} = Translation {i}\n",
                    approved=True,
                )

        # Filesystem setup
        c_ftl = dedent(
            """
            key-c-2 = Message 2
            key-c-4 = Message 4
            """
        )
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.ftl": "", "b.ftl": "", "c.ftl": c_ftl},
                "fr-Test": {"a.ftl": "", "b.ftl": ""},
            },
        )

        # Paths setup
        mock_checkout = Mock(
            Checkout,
            path=repo.checkout_path,
            changed=[join("en-US", "c.ftl")],
            removed=[],
            renamed=[],
        )
        paths = find_paths(project, Checkouts(mock_checkout, mock_checkout))

        # Test sync
        assert sync_entities_from_repo(
            project, locale_map, mock_checkout, paths, now
        ) == (1, {"c.ftl"}, set())
        assert set(
            (ent.key, ent.obsolete) for ent in Entity.objects.filter(resource=res["c"])
        ) == {
            ("key-c-1", True),
            ("key-c-2", False),
            ("key-c-3", True),
            ("key-c-4", False),
        }

        # Test stats
        update_stats(project)
        project.refresh_from_db()
        assert (project.total_strings, project.approved_strings) == (8, 7)
