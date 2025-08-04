import re

from contextlib import contextmanager
from os import makedirs
from os.path import isfile, join
from tempfile import TemporaryDirectory
from textwrap import dedent
from typing import cast
from unittest import TestCase
from unittest.mock import patch

import pytest

from django.conf import settings

from pontoon.base.models import (
    ChangedEntityLocale,
    Entity,
    Locale,
    Repository,
    TranslatedResource,
    Translation,
)
from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ProjectLocaleFactory,
    RepositoryFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    TranslationFactory,
)
from pontoon.sync.models import Sync
from pontoon.sync.tasks import sync_project_task
from pontoon.sync.tests.test_checkouts import MockVersionControl
from pontoon.sync.tests.utils import build_file_tree


@contextmanager
def mock_setup(mock_vcs=None):
    if mock_vcs is None:
        mock_vcs = MockVersionControl()
    with (
        TemporaryDirectory() as root,
        patch("pontoon.sync.core.checkout.get_repo", return_value=mock_vcs),
        patch("pontoon.sync.core.translations_to_repo.get_repo", return_value=mock_vcs),
    ):
        settings.MEDIA_ROOT = root
        repo = cast(Repository, RepositoryFactory.create(url="http://example.com/repo"))
        locale = cast(Locale, LocaleFactory.create(code="de-Test", name="Test German"))
        yield repo, locale


@pytest.mark.django_db
def test_kitchen_sink():
    mock_vcs = MockVersionControl(changed=[join("en-US", "c.ftl")])
    with mock_setup(mock_vcs) as (_, locale_de):
        # Database setup
        locale_fr = LocaleFactory.create(code="fr-Test", name="Test French")
        repo_src = RepositoryFactory(
            url="http://example.com/src-repo", source_repo=True
        )
        repo_tgt = RepositoryFactory(url="http://example.com/tgt-repo")
        project = ProjectFactory.create(
            name="test-project",
            locales=[locale_de, locale_fr],
            repositories=[repo_src, repo_tgt],
        )
        ResourceFactory.create(project=project, path="a.ftl", format="fluent")
        ResourceFactory.create(project=project, path="b.po", format="gettext")
        res_c = ResourceFactory.create(project=project, path="c.ftl", format="fluent")
        for i in range(3):
            entity = EntityFactory.create(
                resource=res_c,
                key=[f"key-{i}"],
                string=f"key-{i} = Message {i}\n",
            )
            for locale in [locale_de, locale_fr]:
                TranslationFactory.create(
                    entity=entity,
                    locale=locale,
                    string=f"key-{i} = New translation {locale.code[:2]} {i}\n",
                    active=True,
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
        sync_project_task(project.pk)
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
            ("update", ("http://example.com/src-repo", src_root, "", False)),
            ("revision", (src_root,)),
            ("update", ("http://example.com/tgt-repo", tgt_root, "", False)),
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
        assert re.fullmatch(
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
        assert Sync.objects.get(project=project).status == Sync.Status.DONE


@pytest.mark.django_db
def test_add_resources():
    with mock_setup() as (repo, locale):
        # Database setup
        project = ProjectFactory.create(
            name="add-resources", locales=[locale], repositories=[repo]
        )

        # Filesystem setup
        makedirs(repo.checkout_path)
        file_pot = dedent("""
            #
            msgid ""
            msgstr ""

            msgid "source"
            msgstr "source"
        """)
        file_xliff = dedent("""\
            <xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
              <file original="file.txt" source-language="en-US" target-language="en-US" datatype="plaintext">
                <body>
                  <trans-unit id="key">
                    <source>source</source>
                    <target>source</target>
                  </trans-unit>
                </body>
              </file>
            </xliff>
        """)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {
                    "file.ftl": "key = Message\n",
                    "file.pot": file_pot,
                    "file.xliff": file_xliff,
                },
                "de-Test": {},
            },
        )

        # Sync with no translations
        sync_project_task(project.pk)

        # Test that entities are generated, translations are not, and FTL & XLIFF are localizable
        assert {
            (ent.resource.path, *ent.key)
            for ent in Entity.objects.filter(resource__project=project)
        } == {
            ("file.ftl", "key"),
            ("file.po", "source"),
            ("file.xliff", "file.txt", "key"),
        }
        assert (
            Translation.objects.filter(entity__resource__project=project).count() == 0
        )
        assert {
            (tr.resource.path, tr.locale.code)
            for tr in TranslatedResource.objects.filter(resource__project=project)
        } == {("file.ftl", "de-Test"), ("file.xliff", "de-Test")}

        # Add an XLIFF translation
        TranslationFactory.create(
            entity=Entity.objects.get(
                resource__project=project, resource__path="file.xliff"
            ),
            locale=locale,
            string="xliff translation",
            active=True,
            approved=True,
        )
        sync_project_task(project.pk)

        # Test that gettext is not written, while XLIFF is
        tgt_po_path = join(repo.checkout_path, "de-Test", "file.po")
        tgt_xliff_path = join(repo.checkout_path, "de-Test", "file.xliff")
        assert not isfile(tgt_po_path)
        with open(tgt_xliff_path) as file:
            assert file.read() == dedent("""\
                <?xml version="1.0" encoding="utf-8"?>
                <xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
                  <file original="file.txt" source-language="en-US" target-language="de-Test" datatype="plaintext">
                    <body>
                      <trans-unit id="key">
                        <source>source</source>
                        <target>xliff translation</target>
                      </trans-unit>
                    </body>
                  </file>
                </xliff>
            """)

        # Add an empty target gettext file
        with open(tgt_po_path, "x") as file:
            file.write("\n")
        sync_project_task(project.pk)

        # Test that the gettext file is now localizable
        assert {
            (tr.resource.path, tr.locale.code)
            for tr in TranslatedResource.objects.filter(resource__project=project)
        } == {
            ("file.ftl", "de-Test"),
            ("file.po", "de-Test"),
            ("file.xliff", "de-Test"),
        }
        with open(tgt_po_path) as file:
            assert file.read() == dedent("""\
                #
                msgid ""
                msgstr ""
                "Language: de_Test\\n"
                "Plural-Forms: nplurals=1; plural=0;\\n"
                "Generated-By: Pontoon\\n"

                msgid "source"
                msgstr ""
            """)


@pytest.mark.django_db
def test_translation_before_source():
    mock_vcs = MockVersionControl(changed=[join("de-Test", "a.ftl")])
    with mock_setup(mock_vcs) as (repo, locale):
        # Database setup
        project = ProjectFactory.create(
            name="trans-before-source", locales=[locale], repositories=[repo]
        )
        res_a = ResourceFactory.create(project=project, path="a.ftl", format="fluent")
        TranslationFactory.create(
            entity=EntityFactory.create(
                resource=res_a, key=["a0"], string="a0 = Message 0\n"
            ),
            locale=locale,
            string="a0 = Translation 0\n",
            active=True,
            approved=True,
        )

        res_b = ResourceFactory.create(project=project, path="b.ftl", format="fluent")
        TranslationFactory.create(
            entity=EntityFactory.create(
                resource=res_b, key=["b0"], string="b0 = Message 0\n"
            ),
            locale=locale,
            string="b0 = Translation 0\n",
            active=True,
            approved=True,
        )

        ChangedEntityLocale.objects.filter(entity__resource__project=project).delete()

        # Filesystem setup
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {
                    "a.ftl": "a0 = Message 0\n",
                    "b.ftl": "b0 = Message 0\n",
                },
                "de-Test": {
                    "a.ftl": ("a0 = New translation 0\na1 = New translation 1\n"),
                    "b.ftl": "b0 = Translation 0\n",
                },
            },
        )

        sync_project_task(project.pk)

        # Test -- New a0 translation is picked up, added a1 is dropped
        with open(join(repo.checkout_path, "de-Test", "a.ftl")) as file:
            assert file.read() == "a0 = New translation 0\n"


@pytest.mark.django_db
def test_android():
    with mock_setup() as (repo, locale):
        # Database setup
        project = ProjectFactory.create(
            name="test-android", locales=[locale], repositories=[repo]
        )
        res = ResourceFactory.create(
            project=project, path="strings.xml", format="android"
        )

        entity = EntityFactory.create(
            resource=res, key=["quotes"], string="Prev quotes"
        )
        TranslationFactory.create(
            entity=entity,
            locale=locale,
            string="'Hello' \"translation\"",
            active=True,
            approved=True,
        )

        entity = EntityFactory.create(
            resource=res, key=["newline"], string="Prev newline"
        )
        TranslationFactory.create(
            entity=entity,
            locale=locale,
            string="translated \n escaped \\n newlines",
            active=True,
            approved=True,
        )

        # Filesystem setup
        src_xml = """<?xml version="1.0" ?>
            <resources xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">
                <string name="quotes">\\'Hello\\' \\"source\\"</string>
                <string name="newline">literal \n escaped \\n newlines</string>
            </resources>"""
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {"en-US": {"strings.xml": src_xml}, "de-Test": {}},
        )

        # Test
        sync_project_task(project.pk)
        assert set(ent.string for ent in Entity.objects.filter(resource=res)) == {
            "'Hello' \"source\"",
            "literal escaped \\n\nnewlines",
        }
        with open(join(repo.checkout_path, "de-Test", "strings.xml")) as file:
            assert file.read() == dedent("""\
                <?xml version="1.0" encoding="utf-8"?>
                <resources>
                  <string name="quotes">\\'Hello\\' \\"translation\\"</string>
                  <string name="newline">translated escaped \\nnewlines</string>
                </resources>
                """)


@pytest.mark.django_db
def test_gettext_fuzzy():
    mock_vcs = MockVersionControl(
        changed=[join("en-US", "res.pot"), join("de-test", "res.po")]
    )
    with mock_setup(mock_vcs) as (repo, locale):
        # Database setup
        project = ProjectFactory.create(
            name="test-write-fuzzy", locales=[locale], repositories=[repo]
        )
        res = ResourceFactory.create(project=project, path="res.po", format="gettext")
        TranslatedResourceFactory.create(locale=locale, resource=res)
        for i in range(5):
            string = f"Message {i}\n"
            fuzzy = i < 3
            entity = EntityFactory.create(resource=res, key=[f"key-{i}"], string=string)
            TranslationFactory.create(
                entity=entity,
                locale=locale,
                string=string.replace("Message", "Fuzzy" if fuzzy else "Translation"),
                active=True,
                approved=not fuzzy,
                fuzzy=fuzzy,
            )
        ChangedEntityLocale.objects.filter(entity__resource__project=project).delete()

        # Filesystem setup
        res_src = dedent(
            """
            #, fuzzy
            msgid "key-0"
            msgstr ""

            #, fuzzy
            msgid "key-1"
            msgstr ""

            msgid "key-2"
            msgstr ""

            msgid "key-3"
            msgstr ""

            #, fuzzy
            msgid "key-4"
            msgstr ""
            """
        )
        res_tgt = dedent(
            """
            #, fuzzy
            msgid "key-0"
            msgstr "Fuzzy 0"

            #, fuzzy
            msgid "key-1"
            msgstr "Fuzzy Changed 1"

            msgid "key-2"
            msgstr "Not Fuzzy 2"

            msgid "key-3"
            msgstr "Translation 3"

            #, fuzzy
            msgid "key-4"
            msgstr "Made Fuzzy 4"
            """
        )
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {"en-US": {"res.pot": res_src}, "de-Test": {"res.po": res_tgt}},
        )

        sync_project_task(project.pk)

        # Test
        trans = Translation.objects.filter(
            entity__resource=res, locale=locale, active=True
        ).values_list("string", flat=True)
        assert set(trans) == {
            "Fuzzy 0",
            "Fuzzy Changed 1",
            "Not Fuzzy 2",
            "Translation 3",
            "Made Fuzzy 4",
        }
        assert set(trans.filter(fuzzy=True)) == {
            "Fuzzy 0",
            "Fuzzy Changed 1",
            "Made Fuzzy 4",
        }
        assert set(trans.filter(approved=True)) == {
            "Not Fuzzy 2",
            "Translation 3",
        }
        with open(join(repo.checkout_path, "de-Test", "res.po")) as file:
            assert re.sub(r'^".*"\n', "", file.read(), flags=re.MULTILINE) == dedent(
                """\
                #
                msgid ""
                msgstr ""

                #, fuzzy
                msgid "key-0"
                msgstr "Fuzzy 0"

                #, fuzzy
                msgid "key-1"
                msgstr "Fuzzy Changed 1"

                msgid "key-2"
                msgstr "Not Fuzzy 2"

                msgid "key-3"
                msgstr "Translation 3"

                #, fuzzy
                msgid "key-4"
                msgstr "Made Fuzzy 4"
                """
            )


class TestEndToEnd(TestCase):
    @pytest.mark.django_db
    def test_plain_json(self):
        with mock_setup() as (repo, locale):
            # Database setup
            project = ProjectFactory.create(
                name="test-plain-json", locales=[locale], repositories=[repo]
            )
            res = ResourceFactory.create(
                project=project, path="old-file.json", format="plain_json"
            )

            entity = EntityFactory.create(resource=res, key=["o1"], string="Entity 1")
            TranslationFactory.create(
                entity=entity,
                locale=locale,
                string="Translation 1",
                active=True,
                approved=True,
            )

            # Filesystem setup
            makedirs(repo.checkout_path)
            build_file_tree(
                repo.checkout_path,
                {
                    "en-US": {
                        "bad-file.json": '{ "b1": "Entity 1", "b2": "Entity 2", }',  # trailing comma
                        "new-file.json": '{ "n1": "Entity 1", "n2": "Entity 2" }',
                        "old-file.json": '{ "o1": "Entity 1", "o2": "Entity 2" }',
                    },
                    "de-Test": {
                        "new-file.json": '{ "n1": "Entity 1", "n2": "Entity 2" }',
                        "old-file.json": "{}",
                    },
                },
            )

            # Test
            with self.assertLogs("pontoon.sync.core.entities", level="ERROR") as cm:
                sync_project_task(project.pk)
            (bad_json_error,) = cm.output
            assert "Resource format detection failed" in bad_json_error
            with open(join(repo.checkout_path, "de-Test", "old-file.json")) as file:
                assert file.read() == dedent("""\
            {
              "o1": "Translation 1"
            }
            """)
            assert {
                (ent.resource.path, ent.resource.format, *ent.key)
                for ent in Entity.objects.filter(resource__project=project)
            } == {
                ("new-file.json", "plain_json", "n1"),
                ("new-file.json", "plain_json", "n2"),
                ("old-file.json", "plain_json", "o1"),
                ("old-file.json", "plain_json", "o2"),
            }

    @pytest.mark.django_db
    def test_unsupported_formats(self):
        with mock_setup() as (repo, locale):
            project = ProjectFactory.create(
                name="test-unsupported-formats", locales=[locale], repositories=[repo]
            )

            makedirs(repo.checkout_path)
            build_file_tree(
                repo.checkout_path,
                {
                    "en-US": {
                        "file.inc": "#define inc unsupported\n",
                        "file.json": '{ "json": "valid src" }',
                        "file.lang": "",
                    },
                    "de-Test": {},
                },
            )

            with self.assertLogs("pontoon.sync.core.entities", level="ERROR") as cm:
                sync_project_task(project.pk)
            bad_inc_error = next(msg for msg in cm.output if ":file.inc]" in msg)
            assert "Skipping resource with unsupported format: inc" in bad_inc_error
            bad_lang_error = next(msg for msg in cm.output if ":file.lang]" in msg)
            assert "Resource format detection failed" in bad_lang_error
            assert len(cm.output) == 2
            assert {
                (ent.resource.path, ent.resource.format, *ent.key)
                for ent in Entity.objects.filter(resource__project=project)
            } == {("file.json", "plain_json", "json")}


@pytest.mark.django_db
def test_webext():
    with mock_setup() as (repo, locale):
        # Database setup
        project = ProjectFactory.create(
            name="test-webext",
            locales=[locale],
            repositories=[repo],
        )
        res = ResourceFactory.create(
            project=project, path="messages.json", format="android"
        )

        entity = EntityFactory.create(resource=res, key=["plain"], string="Entity")
        TranslationFactory.create(
            entity=entity,
            locale=locale,
            string="Translation",
            active=True,
            approved=True,
        )

        entity = EntityFactory.create(
            resource=res, key=["number"], string="Entity for $1"
        )
        TranslationFactory.create(
            entity=entity,
            locale=locale,
            string="Translation for $1",
            active=True,
            approved=True,
        )

        ph = '{"ORIGIN": {"content": "$1", "example": "developer.mozilla.org"}}'
        entity = EntityFactory.create(
            resource=res,
            key=["name"],
            string="Entity for $ORIGIN$",
            meta=[["placeholders", ph]],
        )
        TranslationFactory.create(
            entity=entity,
            locale=locale,
            string="Translation for $ORIGIN$",
            active=True,
            approved=True,
        )

        # Filesystem setup
        src_messages_json = dedent("""\
          {
            "plain": { "message": "Entity" },
            "number": { "message": "Entity for $1" },
            "name": {
              "message": "Entity for $ORIGIN$",
              "placeholders": {
                "origin": {
                  "content": "$1",
                  "example": "developer.mozilla.org"
                }
              }
            }
          }""")
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"messages.json": src_messages_json},
                "de-Test": {"messages.json": "{}"},
            },
        )

        # Test
        sync_project_task(project.pk)
        with open(join(repo.checkout_path, "de-Test", "messages.json")) as file:
            assert file.read() == dedent("""\
            {
              "plain": {
                "message": "Translation"
              },
              "number": {
                "message": "Translation for $1"
              },
              "name": {
                "message": "Translation for $ORIGIN$",
                "placeholders": {
                  "ORIGIN": {
                    "content": "$1",
                    "example": "developer.mozilla.org"
                  }
                }
              }
            }
            """)


@pytest.mark.django_db
def test_add_project_locale():
    mock_vcs = MockVersionControl(changed=[])
    with mock_setup(mock_vcs) as (repo, locale_de):
        # Database setup
        project = ProjectFactory.create(
            name="test-mod-locale",
            locales=[locale_de],
            repositories=[repo],
            system_project=False,
        )

        # Filesystem setup
        makedirs(repo.checkout_path)
        build_file_tree(
            repo.checkout_path,
            {
                "en-US": {"messages.json": '{ "key": { "message": "Entity" } }'},
                "de-Test": {"messages.json": "{}"},
            },
        )

        # First sync...
        sync_project_task(project.pk)

        # Then add a project-locale...
        locale_fr = LocaleFactory.create(code="fr-Test", name="Test French")
        ProjectLocaleFactory.create(project=project, locale=locale_fr)

        # After which the next sync should update the new locale's translated resources.
        sync_project_task(project.pk)

        assert {
            tr.locale.code: tr.total_strings
            for tr in TranslatedResource.objects.filter(resource__project=project)
        } == {"fr-Test": 1, "de-Test": 1}
