from os import makedirs
from os.path import dirname, exists, join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest.mock import Mock

import pytest

from django.conf import settings
from django.utils import timezone

from pontoon.base.models import ChangedEntityLocale
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
from pontoon.sync.core.translations_to_repo import sync_translations_to_repo
from pontoon.sync.tests.utils import build_file_tree


now = timezone.now()


@pytest.mark.django_db
def test_remove_resource():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-rm-res",
            locales=[locale],
            repositories=[repo],
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
        )
        checkouts = Checkouts(mock_checkout, mock_checkout)
        paths = find_paths(project, checkouts)

        # Test
        sync_translations_to_repo(
            project, False, locale_map, checkouts, paths, [], set(), {"c.ftl"}, now
        )
        assert exists(join(repo.checkout_path, "fr-Test", "b.po"))
        assert not exists(join(repo.checkout_path, "fr-Test", "c.ftl"))


@pytest.mark.django_db
def test_remove_entity():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-rm-ent",
            locales=[locale],
            repositories=[repo],
        )
        res_a = ResourceFactory.create(project=project, path="a.ftl", format="ftl")
        res_b = ResourceFactory.create(project=project, path="b.po", format="po")
        res_c = ResourceFactory.create(project=project, path="c.ftl", format="ftl")
        TranslatedResourceFactory.create(locale=locale, resource=res_a)
        TranslatedResourceFactory.create(locale=locale, resource=res_b)
        TranslatedResourceFactory.create(locale=locale, resource=res_c, total_strings=3)
        for i in range(3):
            if i != 1:
                entity = EntityFactory.create(
                    resource=res_c, key=f"key-{i}", string=f"key-{i} = Message {i}\n"
                )
                TranslationFactory.create(
                    entity=entity,
                    locale=locale,
                    string=f"key-{i} = Translation {i}\n",
                    active=True,
                    approved=True,
                )

        # Filesystem setup
        c_ftl_src = dedent(
            """\
            key-0 = Message 0
            key-2 = Message 2
            """
        )
        c_ftl_tgt = dedent(
            """\
            key-0 = Translation 0
            key-1 = Translation 1
            key-2 = Translation 2
            """
        )
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.ftl": "", "b.pot": "", "c.ftl": c_ftl_src},
                "fr-Test": {"a.ftl": "", "b.po": "", "c.ftl": c_ftl_tgt},
            },
        )

        # Paths setup
        mock_checkout = Mock(
            Checkout,
            path=repo.checkout_path,
            changed=[join("en-US", "c.ftl")],
            removed=[],
        )
        checkouts = Checkouts(mock_checkout, mock_checkout)
        paths = find_paths(project, checkouts)

        # Test
        sync_translations_to_repo(
            project, False, locale_map, checkouts, paths, [], {"c.ftl"}, set(), now
        )
        with open(join(repo.checkout_path, "fr-Test", "c.ftl")) as file:
            assert file.read() == dedent(
                """\
                key-0 = Translation 0
                key-2 = Translation 2
                """
            )


@pytest.mark.django_db
def test_add_translation():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-add-trans",
            locales=[locale],
            repositories=[repo],
        )
        res_a = ResourceFactory.create(project=project, path="a.ftl", format="ftl")
        res_b = ResourceFactory.create(project=project, path="b.po", format="po")
        res_c = ResourceFactory.create(project=project, path="c.ftl", format="ftl")
        TranslatedResourceFactory.create(locale=locale, resource=res_a)
        TranslatedResourceFactory.create(locale=locale, resource=res_b)
        TranslatedResourceFactory.create(locale=locale, resource=res_c, total_strings=3)
        ent_0 = EntityFactory.create(
            resource=res_c, key="key-0", string="key-0 = Message 0\n"
        )
        TranslationFactory.create(
            entity=ent_0,
            locale=locale,
            string="key-0 = Translation 0\n",
            active=True,
            approved=True,
        )
        ent_1 = EntityFactory.create(
            resource=res_c, key="key-1", string="key-1 = Message 1\n"
        )
        TranslationFactory.create(
            entity=ent_1,
            locale=locale,
            string="key-1 = Translation 1\n",
            active=True,
            approved=True,
        )
        ent_2 = EntityFactory.create(
            resource=res_c, key="key-2", string="key-2 =\n    .attr = Message 2\n"
        )
        TranslationFactory.create(
            entity=ent_2,
            locale=locale,
            string="key-2 =\n    .attr = Translation 2\n",
            active=True,
            approved=True,
        )
        ent_3 = EntityFactory.create(
            resource=res_c, key="-term-3", string="-term-3 = Term 3\n"
        )
        TranslationFactory.create(
            entity=ent_3,
            locale=locale,
            string="-term-3 = Translation 3\n    .attr = Term attribute\n",
            active=True,
            approved=True,
        )

        # Filesystem setup
        c_ftl_src = dedent(
            """\
            key-0 = Message 0
            key-1 = Message 1
            key-2 =
                .attr = Message 2
            -term-3 = Term 3
            """
        )
        c_ftl_tgt = dedent(
            """\
            key-0 = Translation 0
            """
        )
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.ftl": "", "b.pot": "", "c.ftl": c_ftl_src},
                "fr-Test": {"a.ftl": "", "b.po": "", "c.ftl": c_ftl_tgt},
            },
        )

        # Paths setup
        mock_checkout = Mock(
            Checkout,
            path=repo.checkout_path,
            changed=[join("en-US", "c.ftl")],
            removed=[],
        )
        checkouts = Checkouts(mock_checkout, mock_checkout)
        paths = find_paths(project, checkouts)

        # Test
        db_changes = ChangedEntityLocale.objects.filter(
            entity__resource__project=project
        )
        assert len(db_changes) == 4
        sync_translations_to_repo(
            project, False, locale_map, checkouts, paths, db_changes, set(), set(), now
        )
        with open(join(repo.checkout_path, "fr-Test", "c.ftl")) as file:
            assert file.read() == dedent(
                """\
                key-0 = Translation 0
                key-1 = Translation 1
                key-2 =
                    .attr = Translation 2
                -term-3 = Translation 3
                    .attr = Term attribute
                """
            )


@pytest.mark.django_db
def test_directory_creation_on_translation_update():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-dir-update",
            locales=[locale],
            repositories=[repo],
        )
        res_c = ResourceFactory.create(
            project=project, path="nested_dir/deeper_dir/c.ftl", format="ftl"
        )
        TranslatedResourceFactory.create(locale=locale, resource=res_c, total_strings=1)
        entity = EntityFactory.create(
            resource=res_c, key="key-0", string="key-0 = Message 0\n"
        )
        TranslationFactory.create(
            entity=entity,
            locale=locale,
            string="key-0 = Translation 0\n",
            active=True,
            approved=True,
        )

        # Filesystem setup
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {
                    "nested_dir": {"deeper_dir": {"c.ftl": "key-0 = Message 0\n"}}
                },
                "fr-Test": {},
            },
        )

        # Paths setup
        mock_checkout = Mock(
            Checkout,
            path=repo.checkout_path,
            changed=[join("en-US", "nested_dir", "deeper_dir", "c.ftl")],
            removed=[],
        )
        checkouts = Checkouts(mock_checkout, mock_checkout)
        paths = find_paths(project, checkouts)

        # Test
        sync_translations_to_repo(
            project,
            False,
            locale_map,
            checkouts,
            paths,
            [],
            {"nested_dir/deeper_dir/c.ftl"},
            set(),
            now,
        )
        target_path = join(
            repo.checkout_path, "fr-Test", "nested_dir", "deeper_dir", "c.ftl"
        )
        assert exists(dirname(target_path)), (
            "Expected nested directories to be created."
        )
        assert exists(target_path), (
            "Expected translated file to be created in nested directories."
        )
