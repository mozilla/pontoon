
import codecs
import commonware.log
import configparser
import datetime
import fnmatch
import os
import polib
import silme.core
import silme.format.properties
import urllib2

from django.conf import settings
from pontoon.administration.utils.vcs import update_from_vcs

from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    ProjectForm,
    Subpage,
    Translation,
    UserProfile,
)

log = commonware.log.getLogger('pontoon')


def get_locale_paths(source_paths, source_directory, locale_code):
    """Get paths to locale files."""

    locale_paths = []
    for sp in source_paths:

        # Also include paths to source files
        if source_directory == locale_code:
            path = sp
            locale_paths.append(path)

        else:
            path = sp.replace('/' + source_directory + '/',
                              '/' + locale_code + '/', 1).rstrip("t")

            # Only include if path exists
            if os.path.exists(path):
                locale_paths.append(path)

            # Also check for locale variants with underscore, e.g. de_AT
            elif locale_code.find('-') != -1:
                path = path.replace(
                    '/' + locale_code + '/',
                    '/' + locale_code.replace('-', '_') + '/', 1
                )

                if os.path.exists(path):
                    locale_paths.append(path)

    return locale_paths


def detect_format(path):
    """Detect file format based on file extensions."""
    log.debug("Detect file format based on file extensions.")

    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden files and folders
        filenames = [f for f in filenames if not f[0] == '.']
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        for extension in ('pot', 'po', 'properties', 'ini', 'lang'):
            for filename in fnmatch.filter(filenames, '*.' + extension):
                return 'po' if extension == 'pot' else extension


def get_source_paths(path):
    """Get paths to source files."""
    log.debug("Get paths to source files.")

    source_paths = []
    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden files and folders
        filenames = [f for f in filenames if not f[0] == '.']
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        for extension in ('pot', 'po', 'properties', 'ini', 'lang'):
            for filename in fnmatch.filter(filenames, '*.' + extension):
                source_paths.append(os.path.join(root, filename))

    return source_paths


def get_source_directory(path):
    """Get name and path of the directory with source strings."""
    log.debug("Get name and path of the directory with source strings.")

    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden files and folders
        filenames = [f for f in filenames if not f[0] == '.']
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        for directory in ('templates', 'en-US', 'en-GB', 'en'):
            for dirname in fnmatch.filter(dirnames, directory):
                return {
                    'name': dirname,
                    'path': os.path.join(root, dirname),
                }

    # INI Format
    return {
        'name': '',
        'path': path,
    }


def is_one_locale_repository(repository_url, repository_path_master):
    """Check if repository contains one or multiple locales."""

    one_locale = repository_url_master = False
    repository_path = repository_path_master
    last = os.path.basename(os.path.normpath(repository_url))

    if last in ('templates', 'en-US', 'en-GB', 'en'):
        one_locale = True
        repository_url_master = repository_url.rsplit(last, 1)[0]
        repository_path = os.path.join(repository_path_master, last)

    return one_locale, repository_url_master, repository_path


def get_repository_path_master(project):
    """Get path to master project folder containing repository data."""
    log.debug("Get path to master project folder containing repository data.")

    return os.path.join(
        settings.MEDIA_ROOT, project.repository_type, project.slug)


def _save_entity(project, string, string_plural="",
                 comment="", key="", source=""):
    """Admin interface: save new or update existing entity in DB."""

    # Update existing entity
    try:
        if key is "":
            e = Entity.objects.get(
                project=project, string=string, string_plural=string_plural)

        else:
            e = Entity.objects.get(project=project, key=key, source=source)
            e.string = string
            e.string_plural = string_plural

        # Set obsolete attribute for all entities to False
        e.obsolete = False

    # Add new entity
    except Entity.DoesNotExist:
        e = Entity(project=project, string=string, string_plural=string_plural,
                   key=key, source=source)

    if len(comment) > 0:
        e.comment = comment

    e.save()


def _save_translation(entity, locale, string, plural_form=None, fuzzy=False):
    """Admin interface: save new or update existing translation in DB."""

    approved = not fuzzy

    # Update existing translation if different from repository
    try:
        t = Translation.objects.get(entity=entity, locale=locale,
                                    plural_form=plural_form, approved=True)
        if t.string != string or t.fuzzy != fuzzy:
            t.string = string
            t.user = None
            t.date = datetime.datetime.now()
            t.approved = approved
            t.fuzzy = fuzzy
            t.save()

    # Save new translation if it doesn's exist yet
    except Translation.DoesNotExist:
        t = Translation(
            entity=entity, locale=locale, string=string,
            plural_form=plural_form, date=datetime.datetime.now(),
            approved=approved, fuzzy=fuzzy)
        t.save()


def _parse_lang(path):
    """Parse a dotlang file and return a dict of translations."""
    trans = {}

    if not os.path.exists(path):
        return trans

    with codecs.open(path, 'r', 'utf-8', errors='replace') as lines:
        source = None
        comment = ''

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line[0] == '#' and line[1] != '#':
                comment = line.lstrip('#').strip()
                continue

            if line[0] == ';':
                source = line[1:]

            elif source:
                for tag in ('{ok}', '{l10n-extra}'):
                    if line.lower().endswith(tag):
                        line = line[:-len(tag)]
                line = line.strip()
                trans[source] = [comment, line]
                comment = ''

    return trans


def _extract_po(project, locale, paths, source_locale, translations=True):
    """Extract .po (gettext) files from paths and save or update in DB."""

    for path in paths:
        try:
            log.debug(path)
            po = polib.pofile(path)
            escape = polib.escape

            if locale.code == source_locale:
                for entry in po:
                    if not entry.obsolete:
                        _save_entity(project=project,
                                     string=escape(entry.msgid),
                                     string_plural=escape(entry.msgid_plural),
                                     comment=entry.comment,
                                     source=entry.occurrences)
            elif translations:
                for entry in (po.translated_entries() + po.fuzzy_entries()):
                    if not entry.obsolete:

                        # Entities without plurals
                        if len(escape(entry.msgstr)) > 0:
                            try:
                                e = Entity.objects.get(
                                    project=project,
                                    string=escape(entry.msgid))
                                _save_translation(
                                    entity=e,
                                    locale=locale,
                                    string=escape(entry.msgstr),
                                    fuzzy='fuzzy' in entry.flags)

                            except Entity.DoesNotExist:
                                continue

                        # Pluralized entities
                        elif len(entry.msgstr_plural) > 0:
                            try:
                                e = Entity.objects.get(
                                    project=project,
                                    string=escape(entry.msgid))
                                for k in entry.msgstr_plural:
                                    _save_translation(
                                        entity=e,
                                        locale=locale,
                                        string=escape(entry.msgstr_plural[k]),
                                        plural_form=k,
                                        fuzzy='fuzzy' in entry.flags)

                            except Entity.DoesNotExist:
                                continue

            log.debug("[" + locale.code + "]: saved to DB.")
        except Exception as e:
            log.critical('PoExtractError for %s: %s' % (path, e))


def _extract_properties(project, locale, paths,
                        source_locale, translations=True):
    """Extract .properties files from paths and save or update in DB."""

    for path in paths:
        try:
            f = open(path)
            structure = silme.format.properties \
                .PropertiesFormatParser.get_structure(f.read())

            locale_code = locale.code
            if 'templates' in path:
                locale_code = 'templates'
            short_path = '/' + path.split('/' + locale_code + '/')[-1]

            for obj in structure:
                if isinstance(obj, silme.core.entity.Entity):
                    if locale.code == source_locale:
                        _save_entity(project=project, string=obj.value,
                                     key=obj.id, source=short_path)
                    elif translations:
                        try:
                            e = Entity.objects.get(
                                project=project,
                                key=obj.id,
                                source=short_path)
                            _save_translation(
                                entity=e,
                                locale=locale,
                                string=obj.value)
                        except Entity.DoesNotExist:
                            continue
            log.debug("[" + locale.code + "]: " + path + " saved to DB.")
            f.close()
        except IOError:
            log.debug("[" + locale.code + "]: " +
                      path + " doesn't exist. Skipping.")


def _extract_lang(project, locale, paths, source_locale, translations=True):
    """Extract .lang files from paths and save or update in DB."""

    for path in paths:
        lang = _parse_lang(path)

        if locale.code == source_locale:
            for key, value in lang.items():
                _save_entity(project=project, string=key, comment=value[0])
        elif translations:
            for key, value in lang.items():
                if key != value[1]:
                    try:
                        e = Entity.objects.get(project=project, string=key)
                        _save_translation(
                            entity=e, locale=locale, string=value[1])
                    except Entity.DoesNotExist:
                        continue

        log.debug("[" + locale.code + "]: saved to DB.")


def _extract_ini(project, path):
    """Extract .ini file from path and save or update in DB."""

    config = configparser.ConfigParser()
    with codecs.open(path, 'r', 'utf-8') as f:
        try:
            config.read_file(f)
        except Exception as e:
            log.debug("INI configparser: " + str(e))

    sections = config.sections()

    source_locale = None
    for s in ('templates', 'en-US', 'en-GB', 'en'):
        if s in sections:
            source_locale = s
            break
    if source_locale is None:
        log.error("Unable to detect source locale")
        raise Exception("error")

    # Move source locale on top, so we save entities first, then translations
    sections.insert(0, sections.pop(sections.index(source_locale)))

    for section in sections:
        for item in config.items(section):
            if section == source_locale:
                _save_entity(project=project, string=item[1],
                             key=item[0], source=path)
            else:
                try:
                    l = Locale.objects.get(code=section)
                except Locale.DoesNotExist:
                    log.debug("Locale not supported: " + section)
                    break
                try:
                    e = Entity.objects.get(
                        project=project, key=item[0], source=path)
                    _save_translation(
                        entity=e, locale=l, string=item[1])
                except Entity.DoesNotExist:
                    log.debug("[" + section + "]: line ID " +
                              item[0] + " is obsolete.")
                    continue
        log.debug("[" + section + "]: saved to DB.")


def extract_to_database(project, locales=None):
    """Extract data from project files and save or update in DB."""
    log.debug("Extract data from project files and save or update in DB.")

    repository_path_master = get_repository_path_master(project)
    source_directory = get_source_directory(repository_path_master)

    source_locale = 'en-US'
    if not source_directory['name'] in ('', 'templates'):
        source_locale = source_directory['name']

    if not locales:
        # Mark all existing project entities as obsolete
        Entity.objects.filter(project=project).update(obsolete=True)

        locales = [Locale.objects.get(code=source_locale)]
        locales.extend(project.locales.all())

    isVCS = project.repository_type != 'file'
    source_paths = get_source_paths(source_directory['path'])

    if project.format == 'ini':
        try:
            _extract_ini(project, source_paths[0])
            return
        except Exception as e:
            if not isVCS:
                os.remove(file_path)

    for index, locale in enumerate(locales):
        locale_code = source_directory['name'] if index == 0 else locale.code
        locale_paths = get_locale_paths(
            source_paths, source_directory['name'], locale_code)
        globals()['_extract_%s' % project.format](
            project, locale, locale_paths, source_locale, isVCS)


def update_from_repository(project, locales=None):
    """Update project files from remote repository."""
    log.debug("Update project files from remote repository.")

    repository_type = project.repository_type
    repository_url = project.repository_url
    repository_path_master = get_repository_path_master(project)

    # Update repository path if one-locale repository
    one_locale, repository_url_master, repository_path = \
        is_one_locale_repository(repository_url, repository_path_master)

    if repository_type == 'file':

        # Save file to server
        u = urllib2.urlopen(repository_url)
        file_name = repository_url.rstrip('/').rsplit('/', 1)[1]
        file_path = os.path.join(repository_path_master, file_name)

        if not os.path.exists(repository_path_master):
            os.makedirs(repository_path_master)

        try:
            with open(file_path, 'w') as f:
                f.write(u.read().decode("utf-8-sig").encode("utf-8"))
        except IOError as e:
            log.debug("IOError: " + str(e))

        # Detect format
        temp, file_extension = os.path.splitext(file_name)
        format = file_extension[1:].lower()
        format = 'po' if format == 'pot' else format

    else:

        # Save files to server
        if not locales or not one_locale:
            locales = project.locales.all()
            update_from_vcs(repository_type, repository_url, repository_path)

        if one_locale:
            for l in locales:
                update_from_vcs(
                    repository_type,
                    os.path.join(repository_url_master, l.code),
                    os.path.join(repository_path_master, l.code))

        # Detect format
        source_directory = get_source_directory(repository_path_master)
        format = detect_format(source_directory['path'])

    # Store project format and repository_path
    project.format = format
    project.repository_path = repository_path
    project.save()
