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
from pontoon.sync.checkouts import Checkout, Checkouts
from pontoon.sync.paths import get_paths
from pontoon.sync.sync_translations_from_repo import sync_translations_from_repo
from pontoon.sync.tests.utils import build_file_tree


now = timezone.now()


@pytest.mark.django_db
def test_add_ftl_translation():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(
            code="fr-Test", total_strings=100, approved_strings=99
        )
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-add-ftl",
            locales=[locale],
            repositories=[repo],
            total_strings=10,
            approved_strings=9,
        )
        res_a = ResourceFactory.create(project=project, path="a.ftl", format="ftl")
        res_b = ResourceFactory.create(project=project, path="b.po", format="po")
        res_c = ResourceFactory.create(
            project=project, path="c.ftl", format="ftl", total_strings=3
        )
        TranslatedResourceFactory.create(locale=locale, resource=res_a)
        TranslatedResourceFactory.create(locale=locale, resource=res_b)
        TranslatedResourceFactory.create(
            locale=locale, resource=res_c, total_strings=3, approved_strings=2
        )
        for i in range(3):
            entity = EntityFactory.create(
                resource=res_c, string=f"key-{i} = Message {i}\n", key=f"key-{i}"
            )
            if i != 2:
                TranslationFactory.create(
                    entity=entity,
                    locale=locale,
                    string=f"key-{i} = Translation {i}\n",
                    approved=True,
                )

        # Filesystem setup
        c_ftl = dedent(
            """
            key-0 = Translation 0
            key-1 = Translation 1
            key-2 = Translation 2
            """
        )
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.ftl": "", "b.pot": "", "c.ftl": ""},
                "fr-Test": {"a.ftl": "", "b.po": "", "c.ftl": c_ftl},
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
        paths = get_paths(project, checkouts)

        # Test
        sync_translations_from_repo(project, locale_map, checkouts, paths, [], now)
        assert set(
            trans.entity.key
            for trans in Translation.objects.filter(
                entity__resource=res_c, locale=locale
            )
        ) == {"key-0", "key-1", "key-2"}
        project.refresh_from_db()
        locale.refresh_from_db()
        assert project.approved_strings == 10
        assert locale.approved_strings == 100
        tm = TranslationMemoryEntry.objects.filter(
            entity__resource=res_c, translation__isnull=False
        )
        assert len(tm) == 3


@pytest.mark.django_db
def test_remove_po_target_resource():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(
            code="fr-Test", total_strings=100, approved_strings=99
        )
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-rm-po",
            locales=[locale],
            repositories=[repo],
            total_strings=10,
            approved_strings=7,
        )
        res_a = ResourceFactory.create(project=project, path="a.ftl", format="ftl")
        res_b = ResourceFactory.create(
            project=project, path="b.po", format="po", total_strings=3
        )
        res_c = ResourceFactory.create(project=project, path="c.ftl", format="ftl")
        TranslatedResourceFactory.create(locale=locale, resource=res_a)
        TranslatedResourceFactory.create(locale=locale, resource=res_b, total_strings=3)
        TranslatedResourceFactory.create(locale=locale, resource=res_c)
        for i in range(3):
            entity = EntityFactory.create(
                resource=res_b, key=f"key-{i}", string=f"Message {i}"
            )
            TranslationFactory.create(
                entity=entity, locale=locale, string=f"Translation {i}", approved=True
            )
        project.refresh_from_db()
        assert project.approved_strings == 10

        # Filesystem setup
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.ftl": "", "b.pot": "", "c.ftl": ""},
                "fr-Test": {"a.ftl": "", "c.ftl": ""},
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
        paths = get_paths(project, checkouts)

        # Test
        sync_translations_from_repo(project, locale_map, checkouts, paths, [], now)
        assert not TranslatedResource.objects.filter(locale=locale, resource=res_b)
        assert not Translation.objects.filter(entity__resource=res_b, locale=locale)
        project.refresh_from_db()
        assert project.total_strings == 10
        assert project.approved_strings == 7
        tm = TranslationMemoryEntry.objects.filter(
            entity__resource=res_b, translation__isnull=True
        )
        assert len(tm) == 3
