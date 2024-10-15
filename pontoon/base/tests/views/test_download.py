from io import BytesIO
from os import makedirs
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest.mock import patch
from zipfile import ZipFile

import pytest

from django.conf import settings
from django.test import RequestFactory

from pontoon.base.models.project import Project
from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    RepositoryFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    TranslationFactory,
    UserFactory,
)
from pontoon.base.views import download_translations
from pontoon.sync.tests.test_checkouts import MockVersionControl
from pontoon.sync.tests.utils import build_file_tree


@pytest.mark.django_db
def test_download():
    mock_vcs = MockVersionControl(changes=None)
    with (
        TemporaryDirectory() as root,
        patch("pontoon.sync.core.checkout.get_repo", return_value=mock_vcs),
    ):
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="de-Test")
        repo_src = RepositoryFactory(
            url="http://example.com/src-repo", source_repo=True
        )
        repo_tgt = RepositoryFactory(url="http://example.com/tgt-repo")
        project = ProjectFactory.create(
            name="test-project",
            locales=[locale],
            repositories=[repo_src, repo_tgt],
            visibility=Project.Visibility.PUBLIC,
        )
        res_a = ResourceFactory.create(project=project, path="a.ftl", format="ftl")
        res_b = ResourceFactory.create(project=project, path="b.po", format="po")
        res_c = ResourceFactory.create(project=project, path="c.ftl", format="ftl")
        TranslatedResourceFactory.create(locale=locale, resource=res_a)
        TranslatedResourceFactory.create(locale=locale, resource=res_b)
        TranslatedResourceFactory.create(locale=locale, resource=res_c)
        for i in range(3):
            entity = EntityFactory.create(
                resource=res_c, key=f"key-{i}", string=f"key-{i} = Message {i}\n"
            )
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
            src_root, {"en-US": {"a.ftl": "", "b.pot": "", "c.ftl": c_ftl_src}}
        )

        tgt_root = repo_tgt.checkout_path
        c_ftl_de = dedent(
            """\
            key-0 = Translation de 0
            key-1 = Translation de 1
            key-2 = Translation de 2
            """
        )
        makedirs(tgt_root)
        build_file_tree(
            tgt_root, {"de-Test": {"a.ftl": "", "b.po": "", "c.ftl": c_ftl_de}}
        )

        # Test download
        request = RequestFactory().get("/translations/?code=de-Test&slug=test-project")
        request.user = UserFactory()
        response = download_translations(request)
        assert response.status_code == 200
        assert response.get("Content-Type") == "application/zip"
        zipfile = ZipFile(BytesIO(response.content), "r")
        assert set(zipfile.namelist()) == {"a.ftl", "b.po", "c.ftl"}
        assert (
            zipfile.read("c.ftl")
            == b"key-0 = New translation de 0\n# New entry comment\nkey-2 = New translation de 2\n"
        )
