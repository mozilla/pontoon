from os import makedirs
from os.path import join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest.mock import Mock

import pytest

from django.conf import settings
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import (
    Entity,
    TranslatedResource,
    Translation,
    TranslationMemoryEntry,
)
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
def test_update_ftl_translations():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-update-trans",
            locales=[locale],
            repositories=[repo],
            visibility="public",
        )
        res = {}
        for id in ["a", "b", "c"]:
            res[id] = ResourceFactory.create(
                project=project, path=f"{id}.ftl", format="ftl", total_strings=3
            )
            TranslatedResourceFactory.create(
                locale=locale, resource=res[id], total_strings=3
            )
            for i in [0, 1, 2]:
                key = f"key-{id}-{i}"
                string = f"{key} = Message {id} {i}\n"
                entity = EntityFactory.create(resource=res[id], string=string, key=key)
                if not (id == "c" and i == 2):
                    TranslationFactory.create(
                        entity=entity,
                        locale=locale,
                        string=string.replace(" Message", "Translation"),
                        active=True,
                        approved=True,
                    )
        TranslationFactory.create(
            entity=Entity.objects.get(resource=res["c"], key="key-c-1"),
            locale=locale,
            string="key-c-1 = New translation c 1\n",
        )

        project.refresh_from_db()
        assert project.total_strings == 9
        assert project.approved_strings == 8

        # Filesystem setup
        c_ftl = dedent(
            """
            # key-c-0 = Translation c 0

            key-c-1 = New translation c 1
            key-c-2 = New translation c 2
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
        removed_resources, updated_translations = sync_translations_from_repo(
            project, locale_map, checkouts, paths, [], now
        )
        assert (removed_resources, updated_translations) == (0, 3)
        translations = Translation.objects.filter(
            entity__resource=res["c"], locale=locale
        )
        assert set((trans.entity.key, trans.approved) for trans in translations) == {
            ("key-c-0", False),
            ("key-c-1", False),
            ("key-c-1", True),
            ("key-c-2", True),
        }
        tr_c2 = next(trans for trans in translations if trans.entity.key == "key-c-2")
        assert not tr_c2.user

        # Test actions
        assert {
            (action.translation.string, action.action_type)
            for action in ActionLog.objects.filter(translation__in=translations)
        } == {
            ("key-c-0 =Translation c 0\n", "translation:rejected"),
            ("key-c-1 =Translation c 1\n", "translation:rejected"),
            ("key-c-1 = New translation c 1\n", "translation:approved"),
            ("key-c-2 = New translation c 2\n", "translation:created"),
        }

        # Test stats
        update_stats(project)
        project.refresh_from_db()
        assert project.total_strings == 9
        assert project.approved_strings == 8
        tm = TranslationMemoryEntry.objects.filter(
            entity__resource=res["c"], translation__isnull=False
        ).values_list("target", flat=True)
        assert set(tm) == {
            "Translation c 0",
            "Translation c 1",
            "New translation c 1",
            "New translation c 2",
        }


@pytest.mark.django_db
def test_remove_po_target_resource():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        locale_map = {locale.code: locale}
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-rm-po",
            locales=[locale],
            repositories=[repo],
            visibility="public",
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
                    active=True,
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
        removed_resources, updated_translations = sync_translations_from_repo(
            project, locale_map, checkouts, paths, [], now
        )
        assert (removed_resources, updated_translations) == (1, 0)
        assert not TranslatedResource.objects.filter(locale=locale, resource=res["b"])
        assert not Translation.objects.filter(entity__resource=res["b"], locale=locale)
        tm = TranslationMemoryEntry.objects.filter(
            entity__resource=res["b"], translation__isnull=True
        )
        assert len(tm) == 3

        # Test stats
        update_stats(project)
        project.refresh_from_db()
        assert (project.total_strings, project.approved_strings) == (6, 6)
