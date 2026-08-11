from io import BytesIO
from textwrap import dedent
from zipfile import ZipFile

import pytest

from django.test import RequestFactory

from pontoon.base.models import Project
from pontoon.base.views import download_translations
from pontoon.test.factories import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    SectionFactory,
    TranslatedResourceFactory,
    TranslationFactory,
    UserFactory,
)


@pytest.mark.django_db
def test_download_fluent():
    locale = LocaleFactory.create(code="de-Test")
    project = ProjectFactory.create(
        name="test-dl",
        locales=[locale],
        visibility=Project.Visibility.PUBLIC,
    )
    res = ResourceFactory.create(
        project=project, format="fluent", path="path/to/file.ftl"
    )
    TranslatedResourceFactory.create(locale=locale, resource=res)
    section = SectionFactory.create(resource=res, key=[], comment="Group")
    e1 = EntityFactory.create(resource=res, section=section, key=["e1"], value=["E1"])
    e2 = EntityFactory.create(
        resource=res,
        section=section,
        key=["e2"],
        value=[],
        properties={"attr": ["E2"]},
    )
    EntityFactory.create(resource=res, section=section, key=["e3"], value=["E3"])
    TranslationFactory.create(
        locale=locale, entity=e1, value=["T1"], active=True, approved=True
    )
    TranslationFactory.create(
        locale=locale,
        entity=e2,
        value=[],
        properties={"attr": ["T2"]},
        active=True,
        approved=True,
    )

    request = RequestFactory().get(
        "/translations/?code=de-Test&slug=test-dl&part=path/to/file.ftl"
    )
    request.user = UserFactory()
    response = download_translations(request)
    assert response.status_code == 200
    assert response["Content-Type"] == "application/zip"
    assert (
        response["Content-Disposition"]
        == "attachment; filename=de-Test_test-dl_path_to_file.zip"
    )
    bytes_io = BytesIO(response.content)
    with ZipFile(bytes_io, "r") as zipfile:
        assert zipfile.namelist() == ["de-Test_test-dl_path_to_file.ftl"]
        raw = zipfile.read("de-Test_test-dl_path_to_file.ftl")
    assert raw.decode("utf-8") == dedent("""\
        ## Group

        e1 = T1
        e2 =
            .attr = T2
        """)


@pytest.mark.django_db
def test_download_xliff():
    locale = LocaleFactory.create(code="de-Test")
    project = ProjectFactory.create(
        name="test-dlx",
        locales=[locale],
        visibility=Project.Visibility.PUBLIC,
    )
    res = ResourceFactory.create(project=project, format="xliff", path="file.xlf")
    TranslatedResourceFactory.create(locale=locale, resource=res)
    section = SectionFactory.create(resource=res, key=["file.foo"], comment="Group")
    e1 = EntityFactory.create(
        resource=res, section=section, key=["file.foo", "e1"], value=["E1"]
    )
    e2 = EntityFactory.create(
        resource=res, section=section, key=["file.foo", "e2"], value=["E2"]
    )
    EntityFactory.create(
        resource=res, section=section, key=["file.foo", "e3"], value=["E3"]
    )
    TranslationFactory.create(
        locale=locale, entity=e1, value=["T1"], active=True, approved=True
    )
    TranslationFactory.create(
        locale=locale, entity=e2, value=["T2"], active=True, approved=True
    )

    request = RequestFactory().get(
        "/translations/?code=de-Test&slug=test-dlx&part=file.xlf"
    )
    request.user = UserFactory()
    response = download_translations(request)
    assert response.status_code == 200
    assert response["Content-Type"] == "application/zip"
    assert (
        response["Content-Disposition"]
        == "attachment; filename=de-Test_test-dlx_file.zip"
    )
    bytes_io = BytesIO(response.content)
    with ZipFile(bytes_io, "r") as zipfile:
        assert zipfile.namelist() == ["de-Test_test-dlx_file.xlf"]
        raw = zipfile.read("de-Test_test-dlx_file.xlf")
    assert raw.decode("utf-8") == dedent("""\
        <?xml version="1.0" encoding="utf-8"?>
        <xliff>
          <file original="file.foo">
            <!-- Group -->
            <body>
              <trans-unit id="e1">
                <source>E1</source>
                <target>T1</target>
              </trans-unit>
              <trans-unit id="e2">
                <source>E2</source>
                <target>T2</target>
              </trans-unit>
              <trans-unit id="e3">
                <source>E3</source>
              </trans-unit>
            </body>
          </file>
        </xliff>
        """)
