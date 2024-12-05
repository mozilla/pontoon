from os import makedirs
from os.path import join
from re import fullmatch
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest.mock import patch

import pytest

from django.conf import settings

from pontoon.base.models import ChangedEntityLocale
from pontoon.base.models.translated_resource import TranslatedResource
from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    RepositoryFactory,
    ResourceFactory,
    TranslationFactory,
)
from pontoon.sync.tasks import sync_project_task
from pontoon.sync.tests import SyncLogFactory
from pontoon.sync.tests.test_checkouts import MockVersionControl
from pontoon.sync.tests.utils import build_file_tree


@pytest.mark.django_db
def test_end_to_end():
    mock_vcs = MockVersionControl(changes=([join("en-US", "c.ftl")], [], []))
    with (
        TemporaryDirectory() as root,
        patch("pontoon.sync.core.checkout.get_repo", return_value=mock_vcs),
        patch("pontoon.sync.core.translations_to_repo.get_repo", return_value=mock_vcs),
    ):
        # Database setup
        settings.MEDIA_ROOT = root
        synclog = SyncLogFactory.create()
        locale_de = LocaleFactory.create(
            code="de-Test", name="Test German", total_strings=100
        )
        locale_fr = LocaleFactory.create(
            code="fr-Test", name="Test French", total_strings=100
        )
        repo_src = RepositoryFactory(
            url="http://example.com/src-repo", source_repo=True
        )
        repo_tgt = RepositoryFactory(url="http://example.com/tgt-repo")
        project = ProjectFactory.create(
            name="test-project",
            locales=[locale_de, locale_fr],
            repositories=[repo_src, repo_tgt],
            total_strings=10,
        )
        ResourceFactory.create(project=project, path="a.ftl", format="ftl")
        ResourceFactory.create(project=project, path="b.po", format="po")
        res_c = ResourceFactory.create(project=project, path="c.ftl", format="ftl")
        for i in range(3):
            entity = EntityFactory.create(
                resource=res_c, key=f"key-{i}", string=f"key-{i} = Message {i}\n"
            )
            for locale in [locale_de, locale_fr]:
                TranslationFactory.create(
                    entity=entity,
                    locale=locale,
                    string=f"key-{i} = New translation {locale.code[:2]} {i}\n",
                    approved=True,
                )

        # Filesystem setup
        src_root = repo_src.checkout_path
        c_ftl_src = dedent(
            """\
            key-0 = Message 0
            # New entry comment
            key-2 = Message 2
            key-3 = Message 3
            """
        )
        makedirs(src_root)
        build_file_tree(
            src_root,
            {"en-US": {"a.ftl": "", "b.pot": "", "c.ftl": c_ftl_src}},
        )

        tgt_root = repo_tgt.checkout_path
        c_ftl_de = dedent(
            """\
            key-0 = Translation de 0
            key-1 = Translation de 1
            key-2 = Translation de 2
            """
        )
        c_ftl_fr = dedent(
            """\
            key-0 = Translation fr 0
            key-1 = Translation fr 1
            """
        )
        makedirs(tgt_root)
        build_file_tree(
            tgt_root,
            {
                "de-Test": {"a.ftl": "", "b.po": "", "c.ftl": c_ftl_de},
                "fr-Test": {"a.ftl": "", "b.po": "", "c.ftl": c_ftl_fr},
            },
        )

        # Test
        assert len(ChangedEntityLocale.objects.filter(entity__resource=res_c)) == 6
        sync_project_task(project.id, synclog.id)
        assert len(ChangedEntityLocale.objects.filter(entity__resource=res_c)) == 0
        with open(join(repo_tgt.checkout_path, "de-Test", "c.ftl")) as file:
            assert (
                file.read()
                == "key-0 = New translation de 0\n# New entry comment\nkey-2 = New translation de 2\n"
            )
        with open(join(repo_tgt.checkout_path, "fr-Test", "c.ftl")) as file:
            assert (
                file.read()
                == "key-0 = New translation fr 0\n# New entry comment\nkey-2 = New translation fr 2\n"
            )
        commit_msg: str = mock_vcs._calls[4][1][1]
        assert mock_vcs._calls == [
            ("update", ("http://example.com/src-repo", src_root, "")),
            ("revision", (src_root,)),
            ("update", ("http://example.com/tgt-repo", tgt_root, "")),
            ("revision", (tgt_root,)),
            (
                "commit",
                (
                    tgt_root,
                    commit_msg,
                    f"{settings.VCS_SYNC_NAME} <{settings.VCS_SYNC_EMAIL}>",
                    "",
                    "http://example.com/tgt-repo",
                ),
            ),
            ("revision", (tgt_root,)),
        ]
        assert fullmatch(
            dedent(
                r"""
                Pontoon/test-project: Update Test (German|French) \((de|fr)-Test\), Test (German|French) \((de|fr)-Test\)

                Co-authored-by: test\d+ <test\d+@example.com> \((de|fr)-Test\)
                Co-authored-by: test\d+ <test\d+@example.com> \((de|fr)-Test\)
                Co-authored-by: test\d+ <test\d+@example.com> \((de|fr)-Test\)
                Co-authored-by: test\d+ <test\d+@example.com> \((de|fr)-Test\)
                """
            ).strip(),
            commit_msg,
        )
        assert TranslatedResource.objects.filter(resource__project=project).count() == 6


@pytest.mark.django_db
def test_translation_before_source():
    with TemporaryDirectory() as root:
        # Database setup
        settings.MEDIA_ROOT = root
        synclog = SyncLogFactory.create()
        locale_de = LocaleFactory.create(code="de-Test", name="Test German")
        repo_src = RepositoryFactory(
            url="http://example.com/src-repo", source_repo=True
        )
        repo_tgt = RepositoryFactory(url="http://example.com/tgt-repo")
        project = ProjectFactory.create(
            name="trans-before-source",
            locales=[locale_de],
            repositories=[repo_src, repo_tgt],
        )
        res_a = ResourceFactory.create(project=project, path="a.ftl", format="ftl")
        TranslationFactory.create(
            entity=EntityFactory.create(
                resource=res_a, key="a0", string="a0 = Message 0\n"
            ),
            locale=locale_de,
            string="a0 = Translation 0\n",
            approved=True,
        )

        res_b = ResourceFactory.create(project=project, path="b.ftl", format="ftl")
        TranslationFactory.create(
            entity=EntityFactory.create(
                resource=res_b, key="b0", string="b0 = Message 0\n"
            ),
            locale=locale_de,
            string="b0 = Translation 0\n",
            approved=True,
        )

        ChangedEntityLocale.objects.filter(entity__resource__project=project).delete()

        # Filesystem setup
        src_root = repo_src.checkout_path
        makedirs(src_root)
        build_file_tree(
            src_root,
            {
                "en-US": {
                    "a.ftl": "a0 = Message 0\n",
                    "b.ftl": "b0 = Message 0\n",
                }
            },
        )

        tgt_root = repo_tgt.checkout_path
        makedirs(tgt_root)
        build_file_tree(
            tgt_root,
            {
                "de-Test": {
                    "a.ftl": ("a0 = New translation 0\n" "a1 = New translation 1\n"),
                    "b.ftl": "b0 = Translation 0\n",
                }
            },
        )

        # Sync
        mock_vcs = MockVersionControl(changes=([join("de-Test", "a.ftl")], [], []))
        with (
            patch("pontoon.sync.core.checkout.get_repo", return_value=mock_vcs),
            patch(
                "pontoon.sync.core.translations_to_repo.get_repo",
                return_value=mock_vcs,
            ),
        ):
            sync_project_task(project.id, synclog.id)

        # Test -- New a0 translation is picked up, added a1 is dropped
        with open(join(repo_tgt.checkout_path, "de-Test", "a.ftl")) as file:
            assert file.read() == "a0 = New translation 0\n"
