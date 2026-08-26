from os import makedirs
from os.path import join
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest.mock import patch

import pytest

from django.conf import settings

from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    RepositoryFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    TranslationFactory,
)
from pontoon.sync.tests.test_checkouts import MockVersionControl
from pontoon.sync.tests.utils import build_file_tree
from pontoon.sync.utils import serialize_locale


@pytest.mark.django_db
def test_serialize_locale():
    with (
        TemporaryDirectory() as root,
        patch(
            "pontoon.sync.core.checkout.get_repo",
            return_value=MockVersionControl(),
        ),
    ):
        # Database setup
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-serialize", locales=[locale], repositories=[repo]
        )
        res_ftl = ResourceFactory.create(project=project, path="a.ftl", format="fluent")
        res_po = ResourceFactory.create(project=project, path="b.po", format="gettext")
        TranslatedResourceFactory.create(locale=locale, resource=res_ftl)
        TranslatedResourceFactory.create(locale=locale, resource=res_po)
        entity_ftl = EntityFactory.create(
            resource=res_ftl, key=["key-0"], string="key-0 = Message 0\n"
        )
        TranslationFactory.create(
            entity=entity_ftl,
            locale=locale,
            string="key-0 = Traduction 0\n",
            active=True,
            approved=True,
        )
        entity_po = EntityFactory.create(
            resource=res_po, key=["source"], string="source"
        )
        TranslationFactory.create(
            entity=entity_po,
            locale=locale,
            string="traduction",
            active=True,
            approved=True,
        )

        # Filesystem setup: reference files only; no translated files needed
        b_pot = dedent("""\
            #
            msgid ""
            msgstr ""

            msgid "source"
            msgstr ""
        """)
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.ftl": "key-0 = Message 0\n", "b.pot": b_pot},
                "fr-Test": {"a.ftl": "", "b.po": ""},
            },
        )

        # Test: all resources
        files = dict(serialize_locale(project, locale))
        assert set(files.keys()) == {"fr-Test/a.ftl", "fr-Test/b.po"}
        assert files["fr-Test/a.ftl"] == "key-0 = Traduction 0\n"
        assert 'msgid "source"' in files["fr-Test/b.po"]
        assert 'msgstr "traduction"' in files["fr-Test/b.po"]
        assert "Generated-By: Pontoon" in files["fr-Test/b.po"]

        # Test: single resource filter
        only_ftl = dict(serialize_locale(project, locale, "a.ftl"))
        assert set(only_ftl.keys()) == {"fr-Test/a.ftl"}

        # Test: unknown resource filter yields nothing
        assert dict(serialize_locale(project, locale, "nope.ftl")) == {}


@pytest.mark.django_db
def test_serialize_locale_no_translations():
    with (
        TemporaryDirectory() as root,
        patch(
            "pontoon.sync.core.checkout.get_repo",
            return_value=MockVersionControl(),
        ),
    ):
        # Database setup: resources exist but have no translations
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-serialize-empty", locales=[locale], repositories=[repo]
        )
        res_ftl = ResourceFactory.create(project=project, path="a.ftl", format="fluent")
        res_po = ResourceFactory.create(project=project, path="b.po", format="gettext")
        TranslatedResourceFactory.create(locale=locale, resource=res_ftl)
        TranslatedResourceFactory.create(locale=locale, resource=res_po)
        EntityFactory.create(
            resource=res_ftl, key=["key-0"], string="key-0 = Message 0\n"
        )
        EntityFactory.create(resource=res_po, key=["source"], string="source")

        # Filesystem setup
        b_pot = dedent("""\
            #
            msgid ""
            msgstr ""

            msgid "source"
            msgstr ""
        """)
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"a.ftl": "key-0 = Message 0\n", "b.pot": b_pot},
                "fr-Test": {"a.ftl": "", "b.po": ""},
            },
        )

        # Untranslated resources are still yielded: gettext as a valid file
        # with empty msgstrs, fluent with all entries pruned (empty content).
        files = dict(serialize_locale(project, locale))
        assert set(files.keys()) == {"fr-Test/a.ftl", "fr-Test/b.po"}
        assert files["fr-Test/a.ftl"] == ""
        assert 'msgid "source"' in files["fr-Test/b.po"]
        assert 'msgstr ""' in files["fr-Test/b.po"]


@pytest.mark.django_db
def test_serialize_locale_rejects_path_traversal():
    with (
        TemporaryDirectory() as root,
        patch(
            "pontoon.sync.core.checkout.get_repo",
            return_value=MockVersionControl(),
        ),
    ):
        settings.MEDIA_ROOT = root
        locale = LocaleFactory.create(code="fr-Test")
        repo = RepositoryFactory(url="http://example.com/repo")
        project = ProjectFactory.create(
            name="test-traversal", locales=[locale], repositories=[repo]
        )
        res_ok = ResourceFactory.create(project=project, path="a.ftl", format="fluent")
        TranslatedResourceFactory.create(locale=locale, resource=res_ok)

        # A secret file outside the reference root, pointed at by a Resource
        # whose (unrestricted) path escapes it.
        secret = join(root, "secret.ftl")
        with open(secret, "w", encoding="utf-8") as f:
            f.write("leaked = TOP-SECRET\n")
        res_evil = ResourceFactory.create(project=project, path=secret, format="fluent")
        TranslatedResourceFactory.create(locale=locale, resource=res_evil)

        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {"en-US": {"a.ftl": "key-0 = Message 0\n"}, "fr-Test": {"a.ftl": ""}},
        )

        files = dict(serialize_locale(project, locale))
        # The escaping resource is skipped; its contents never leak.
        assert all("TOP-SECRET" not in content for content in files.values())
        assert all("secret.ftl" not in path for path in files)


# import_uploaded_file used to raise a bare "Upload failed." for three very
# different situations: an unparseable file, a file whose keys match no source
# string, and a file that is simply already in sync. The message has to say
# which one it is, or the upload looks broken for no reason.


def _upload(project, locale, res_path, body):
    from django.core.files.base import ContentFile

    from pontoon.base.tests import UserFactory
    from pontoon.sync.utils import import_uploaded_file

    return import_uploaded_file(
        project,
        locale,
        res_path,
        ContentFile(body.encode("utf-8"), name=res_path),
        UserFactory.create(),
    )


@pytest.fixture
def upload_project():
    locale = LocaleFactory.create(code="fr-Upload")
    project = ProjectFactory.create(
        name="test-upload", locales=[locale], repositories=[]
    )
    resource = ResourceFactory.create(
        project=project, path="messages.json", format="plain_json"
    )
    entity = EntityFactory.create(resource=resource, string="Hello", key=["greeting"])
    return project, locale, entity


@pytest.mark.django_db
def test_import_uploaded_file_creates_translation(upload_project):
    project, locale, entity = upload_project

    _upload(project, locale, "messages.json", '{"greeting": "Bonjour"}')

    assert entity.translation_set.filter(locale=locale, string="Bonjour").exists()


@pytest.mark.django_db
def test_import_uploaded_file_reports_parse_error(upload_project):
    project, locale, _ = upload_project

    with pytest.raises(Exception) as error:
        _upload(project, locale, "messages.json", "{ not json")

    assert "Could not parse messages.json" in str(error.value)


@pytest.mark.django_db
def test_import_uploaded_file_reports_unmatched_keys(upload_project):
    """Source strings come from the repository; uploading new keys cannot add
    them, and the old message never said so."""
    project, locale, _ = upload_project

    with pytest.raises(Exception) as error:
        _upload(project, locale, "messages.json", '{"brand_new_key": "Nouveau"}')

    assert "None of the translations in the uploaded file match" in str(error.value)


@pytest.mark.django_db
def test_import_uploaded_file_reports_nothing_new(upload_project):
    project, locale, entity = upload_project
    TranslationFactory.create(
        entity=entity, locale=locale, string="Bonjour", approved=True, active=True
    )

    with pytest.raises(Exception) as error:
        _upload(project, locale, "messages.json", '{"greeting": "Bonjour"}')

    assert "No new translations found" in str(error.value)
