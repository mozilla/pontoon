from os import makedirs
from os.path import join
from re import fullmatch
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest.mock import patch

import pytest

from django.conf import settings

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
from pontoon.sync.tasks import sync_project_task
from pontoon.sync.tests import SyncLogFactory
from pontoon.sync.tests.test_checkouts import MockVersionControl
from pontoon.sync.tests.utils import build_file_tree


@pytest.mark.django_db
def test_end_to_end():
    mock_vcs = MockVersionControl(changes=([join("en-US", "c.ftl")], []))
    with (
        TemporaryDirectory() as root,
        patch("pontoon.sync.core.checkout.get_repo", return_value=mock_vcs),
        patch("pontoon.sync.repositories.get_repo", return_value=mock_vcs),
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
        res_a = ResourceFactory.create(project=project, path="a.ftl", format="ftl")
        res_b = ResourceFactory.create(project=project, path="b.po", format="po")
        res_c = ResourceFactory.create(project=project, path="c.ftl", format="ftl")
        TranslatedResourceFactory.create(locale=locale_de, resource=res_a)
        TranslatedResourceFactory.create(locale=locale_de, resource=res_b)
        TranslatedResourceFactory.create(
            locale=locale_de, resource=res_c, total_strings=3
        )
        TranslatedResourceFactory.create(locale=locale_fr, resource=res_a)
        TranslatedResourceFactory.create(locale=locale_fr, resource=res_b)
        TranslatedResourceFactory.create(
            locale=locale_fr, resource=res_c, total_strings=3
        )
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
        commit_msg: str = mock_vcs._calls[-1][1][1]
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
        ]
        assert fullmatch(
            dedent(
                r"""
                Pontoon/test-project: Update Test German \(de-Test\), Test French \(fr-Test\)

                Co-authored-by: test\d+ <test\d+@example.com> \(de-Test\)
                Co-authored-by: test\d+ <test\d+@example.com> \(de-Test\)
                Co-authored-by: test\d+ <test\d+@example.com> \(fr-Test\)
                Co-authored-by: test\d+ <test\d+@example.com> \(fr-Test\)
                """
            ).strip(),
            commit_msg,
        )
