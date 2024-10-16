from os import makedirs
from os.path import join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest.mock import Mock

import pytest

from django.conf import settings
from django.utils import timezone

from pontoon.base.models import TranslatedResource, Translation, TranslationMemoryEntry
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
from pontoon.sync.core.paths import find_paths
from pontoon.sync.core.stats import update_stats
from pontoon.sync.core.translations_from_repo import sync_translations_from_repo
from pontoon.sync.tests.utils import build_file_tree


now = timezone.now()


@pytest.mark.django_db
def test_add_ftl_translation():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-add-ftl",
            locales=[locale],
            repositories=[repo],
            total_strings=9,
        )
        res = {}
        for id in ["a", "b", "c"]:
            res[id] = ResourceFactory.create(
                project=project, path=f"{id}.ftl", format="ftl", total_strings=3
            )
            TranslatedResourceFactory.create(
                locale=locale, resource=res[id], total_strings=3
            )
            for i in range(3):
                key = f"key-{id}-{i}"
                string = f"{key} = Message {id} {i}\n"
                entity = EntityFactory.create(resource=res[id], string=string, key=key)
                if id != "c" or i != 2:
                    TranslationFactory.create(
                        entity=entity,
                        locale=locale,
                        string=string.replace("Message", "Translation"),
                        approved=True,
                    )

        project.refresh_from_db()
        assert project.total_strings == 9
        assert project.approved_strings == 8

        # Filesystem setup
        c_ftl = dedent(
            """
            key-c-0 = Translation c 0
            key-c-1 = Translation c 1
            key-c-2 = Translation c 2
            """
        )
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.ftl": "", "b.ftl": "", "c.ftl": ""},
                "fr-Test": {"a.ftl": "", "b.ftl": "", "c.ftl": c_ftl},
            },
        )

        # Paths setup
        mock_checkout = Mock(
            Checkout,
            path=repo.checkout_path,
            changed=[join("fr-Test", "c.ftl")],
            removed=[],
        )
        checkouts = Checkouts(mock_checkout, mock_checkout)
        paths = find_paths(project, checkouts)

        # Test sync
        sync_translations_from_repo(project, locale_map, checkouts, paths, [], now)
        assert set(
            trans.entity.key
            for trans in Translation.objects.filter(
                entity__resource=res["c"], locale=locale
            )
        ) == {"key-c-0", "key-c-1", "key-c-2"}

        # Test stats
        update_stats(project)
        project.refresh_from_db()
        assert project.total_strings == 9
        assert project.approved_strings == 9
        tm = TranslationMemoryEntry.objects.filter(
            entity__resource=res["c"], translation__isnull=False
        )
        assert len(tm) == 3


@pytest.mark.django_db
def test_remove_po_target_resource():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-rm-po", locales=[locale], repositories=[repo]
        )
        res = {}
        for id in ["a", "b", "c"]:
            res[id] = ResourceFactory.create(
                project=project, path=f"{id}.po", format="po", total_strings=3
            )
            TranslatedResourceFactory.create(locale=locale, resource=res[id])
            for i in range(3):
                key = f"key-{id}-{i}"
                string = f"Message {id} {i}"
                entity = EntityFactory.create(resource=res[id], string=string, key=key)
                TranslationFactory.create(
                    entity=entity,
                    locale=locale,
                    string=string.replace("Message", "Translation"),
                    approved=True,
                )

        # Filesystem setup
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.pot": "", "b.pot": "", "c.pot": ""},
                "fr-Test": {"a.po": "", "c.po": ""},
            },
        )

        # Paths setup
        mock_checkout = Mock(
            Checkout,
            path=repo.checkout_path,
            changed=[],
            removed=[join("fr-Test", "b.po")],
        )
        checkouts = Checkouts(mock_checkout, mock_checkout)
        paths = find_paths(project, checkouts)

        # Test sync
        sync_translations_from_repo(project, locale_map, checkouts, paths, [], now)
        assert not TranslatedResource.objects.filter(locale=locale, resource=res["b"])
        assert not Translation.objects.filter(entity__resource=res["b"], locale=locale)
        tm = TranslationMemoryEntry.objects.filter(
            entity__resource=res["b"], translation__isnull=True
        )
        assert len(tm) == 3

        # Test stats
        update_stats(project)
        project.refresh_from_db()
        assert (project.total_strings, project.approved_strings) == (9, 6)
