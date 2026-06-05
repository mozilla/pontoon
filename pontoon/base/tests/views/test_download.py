from os import makedirs
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from django.conf import settings
from django.test import RequestFactory

from pontoon.base.models import Project, Resource
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
from pontoon.sync.repositories import PullFromRepositoryException
from pontoon.sync.tests.test_checkouts import MockVersionControl
from pontoon.sync.tests.utils import build_file_tree


@pytest.mark.django_db
def test_download():
    with (
        TemporaryDirectory() as root,
        patch(
            "pontoon.sync.core.checkout.get_repo",
            return_value=MockVersionControl(),
        ),
    ):
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="de-Test")
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-dl",
            locales=[locale],
            repositories=[repo],
            visibility=Project.Visibility.PUBLIC,
        )
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.ftl": "key-0 = Message 0\n"},
                "de-Test": {"a.ftl": ""},
            },
        )
        res = ResourceFactory.create(
            project=project, path="a.ftl", format=Resource.Format.FLUENT
        )
        TranslatedResourceFactory.create(locale=locale, resource=res)
        entity = EntityFactory.create(
            resource=res, key=["key-0"], string="key-0 = Message 0\n"
        )
        TranslationFactory.create(
            entity=entity,
            locale=locale,
            string="key-0 = Übersetzung 0\n",
            active=True,
            approved=True,
        )

        request = RequestFactory().get(
            "/translations/?code=de-Test&slug=test-dl&part=a.ftl"
        )
        request.user = UserFactory()
        response = download_translations(request)
        assert response.status_code == 200
        assert response["Content-Type"] == "text/plain; charset=utf-8"
        assert response["Content-Disposition"] == 'attachment; filename="a.ftl"'
        assert response.content.decode("utf-8") == "key-0 = Übersetzung 0\n"


@pytest.mark.django_db
def test_download_missing_resource():
    with (
        TemporaryDirectory() as root,
        patch(
            "pontoon.sync.core.checkout.get_repo",
            return_value=MockVersionControl(),
        ),
    ):
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="de-Test")
        repo = RepositoryFactory(url="http://example.com/repo")
        ProjectFactory.create(
            name="test-dl-404",
            locales=[locale],
            repositories=[repo],
            visibility=Project.Visibility.PUBLIC,
        )
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {"en-US": {"a.ftl": ""}, "de-Test": {"a.ftl": ""}},
        )

        request = RequestFactory().get(
            "/translations/?code=de-Test&slug=test-dl-404&part=nope.ftl"
        )
        request.user = UserFactory()
        from django.http import Http404

        with pytest.raises(Http404):
            download_translations(request)


@pytest.mark.django_db
def test_download_repo_unavailable():
    locale = LocaleFactory.create(code="de-Test")
    repo = RepositoryFactory(url="http://example.com/repo")
    ProjectFactory.create(
        name="test-dl-503",
        locales=[locale],
        repositories=[repo],
        visibility=Project.Visibility.PUBLIC,
    )

    request = RequestFactory().get(
        "/translations/?code=de-Test&slug=test-dl-503&part=a.ftl"
    )
    request.user = UserFactory()
    with patch(
        "pontoon.sync.utils.serialize_locale",
        side_effect=PullFromRepositoryException("boom"),
    ):
        response = download_translations(request)
    assert response.status_code == 503
