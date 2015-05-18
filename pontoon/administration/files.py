import codecs
import configparser
import datetime
import fnmatch
import logging
import operator
import os
import polib
import shutil
import silme.core
import silme.format.properties
import silme.format.dtd
import StringIO
import urllib2
import zipfile

from django.conf import settings
from pontoon.administration.vcs import update_from_vcs
from translate.storage import xliff

from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    Resource,
    Stats,
    Translation,
    save_entity,
    save_translation,
    update_entity_count,
    update_stats,
)

log = logging.getLogger('pontoon')


""" Start monkeypatching """
from silme.core.structure import Structure, Comment
from silme.format.properties.parser import PropertiesParser


@classmethod
def split_comments_mine(
        cls, text, object, code='default', pointer=0, end=None):
    pattern = cls.patterns['comment']
    if end:
        match = pattern.search(text, pointer, end)
    else:
        match = pattern.search(text, pointer)
    while match:
        st0 = match.start(0)
        if st0 > pointer:
            cls.split_entities(
                text, object, code=code, pointer=pointer, end=st0)
        groups = match.groups()
        comment = silme.core.structure.Comment(
            match.group(0)[1:].replace('\n#', '\n'))
        object.append(comment)
        pointer = match.end(0)
        if end:
            match = pattern.search(text, pointer, end)
        else:
            match = pattern.search(text, pointer)
    if (not end or (end > pointer)) and len(text) > pointer:
        cls.split_entities(text, object, code=code, pointer=pointer)

PropertiesParser.split_comments = split_comments_mine


def __repr__mine(self):
        string = ''
        for i in self:
            string += str(i)
        return string

Comment.__repr__ = __repr__mine


def modify_entity_mine(self, id, value, code=None):
    """
    modifies entity value; supports duplicate keys
    code - if given modified the value for given locale code
    """
    found = False
    for item in self:
        if isinstance(item, silme.core.entity.Entity) and item.id == id:
            item.set_value(value, code)
            found = True

    if found:
        return True
    else:
        raise KeyError('No such entity')

Structure.modify_entity = modify_entity_mine
""" End monkeypatching """


def get_locale_paths(project, locale):
    """Get paths to locale files."""

    locale_paths = []
    path = get_locale_directory(project, locale)["path"]
    formats = Resource.objects.filter(project=project).values_list(
        'format', flat=True).distinct()

    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden files
        filenames = [f for f in filenames if not f[0] == '.']

        for format in formats:
            for filename in fnmatch.filter(filenames, '*.' + format):
                locale_paths.append(os.path.join(root, filename))

    return locale_paths


def get_locale_directory(project, locale):
    """
    Get path to the directory with locale files.

    Args:
        project: Project instance
        locale: Locale instance
    Returns:
        Dict with directory name and path as keys.
    """

    path = get_repository_path_master(project)

    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden folders
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        for dirname in fnmatch.filter(dirnames, locale.code):
            return {
                'name': dirname,
                'path': os.path.join(root, dirname),
            }

        # Also check for locale variants with underscore, e.g. de_AT
        for dirname in fnmatch.filter(dirnames, locale.code.replace('-', '_')):
            return {
                'name': dirname,
                'path': os.path.join(root, dirname),
            }

    # Projects not using locale directories (.ini, file)
    formats = Resource.objects.filter(project=project).values_list(
        'format', flat=True).distinct()
    if 'ini' in formats or project.repository_type == 'file':
        return {
            'name': '',
            'path': path,
        }

    error = "Directory for locale %s not found." % locale.code
    log.error(error)
    raise Exception(error)


def detect_format(path):
    """Detect file format from source directory path."""

    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden files
        filenames = [f for f in filenames if not f[0] == '.']

        for extension in ['pot'] + [i[0] for i in Resource.FORMAT_CHOICES]:
            for filename in fnmatch.filter(filenames, '*.' + extension):
                return 'po' if extension == 'pot' else extension


def get_format(path):
    """Get file format from file path based on extension."""

    return os.path.splitext(path)[1][1:].lower()


def get_source_paths(path):
    """Get paths to source files."""

    source_paths = []

    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden files
        filenames = [f for f in filenames if not f[0] == '.']

        for extension in ['pot'] + [i[0] for i in Resource.FORMAT_CHOICES]:
            for filename in fnmatch.filter(filenames, '*.' + extension):
                source_paths.append(os.path.join(root, filename))

    return source_paths


def get_source_directory(path):
    """Get name and path of the directory with source files."""

    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden folders
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        for directory in ('templates', 'en-US', 'en-GB', 'en'):
            for dirname in fnmatch.filter(dirnames, directory):
                source_directory_path = os.path.join(root, dirname)
                if detect_format(source_directory_path):
                    return {
                        'name': dirname,
                        'path': source_directory_path,
                    }

    # Projects not using locale directories (.ini, file)
    return {
        'name': '',
        'path': path,
    }


def get_repository_path_master(project):
    """Get path to master project folder containing repository files."""

    return os.path.join(
        settings.MEDIA_ROOT, project.repository_type, project.slug)


def get_relative_path(path, locale):
    """Get relative path to repository file."""

    locale_directory = locale.code
    if 'templates' in path:
        locale_directory = 'templates'

    # Also check for locale variants with underscore, e.g. de_AT
    underscore = locale.code.replace('-', '_')
    if '/' + underscore + '/' in path:
        locale_directory = underscore

    return path.split('/' + locale_directory + '/')[-1]


def parse_lang(path):
    """Parse a dotlang file and return a dict of translations."""
    trans = {}

    if not os.path.exists(path):
        return trans

    with codecs.open(path, 'r', 'utf-8', errors='replace') as lines:
        source = None
        comment = ''
        tags = []
        counter = 0

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
                        tags.append(tag)
                line = line.strip()
                trans[source] = [counter, comment, line, tags]
                comment = ''
                tags = []
                counter += 1

    # Sort by counter
    trans = sorted(trans.iteritems(), key=operator.itemgetter(1))
    return trans


def extract_po(project, locale, path, entities=False):
    """Extract .po (gettext) file with path and save or update in DB."""

    try:
        po = polib.pofile(path)

        relative_path = get_relative_path(path, locale)
        if relative_path[-1] == 't':
            relative_path = relative_path[:-1]

        resource, created = Resource.objects.get_or_create(
            project=project, path=relative_path, format='po')

        if entities:
            for order, entry in enumerate(po):
                if not entry.obsolete:
                    save_entity(resource=resource,
                                string=entry.msgid,
                                string_plural=entry.msgid_plural,
                                comment=entry.comment,
                                order=order,
                                source=entry.occurrences)

            update_entity_count(resource)

        else:
            for entry in (po.translated_entries() + po.fuzzy_entries()):
                if not entry.obsolete:

                    # Entities without plurals
                    if len(entry.msgstr) > 0:
                        try:
                            e = Entity.objects.get(
                                resource=resource,
                                string=entry.msgid)
                            save_translation(
                                entity=e,
                                locale=locale,
                                string=entry.msgstr,
                                fuzzy='fuzzy' in entry.flags)

                        except Entity.DoesNotExist:
                            continue

                    # Pluralized entities
                    elif len(entry.msgstr_plural) > 0:
                        try:
                            e = Entity.objects.get(
                                resource=resource,
                                string=entry.msgid)
                            for k in entry.msgstr_plural:
                                save_translation(
                                    entity=e,
                                    locale=locale,
                                    string=entry.msgstr_plural[k],
                                    plural_form=k,
                                    fuzzy='fuzzy' in entry.flags)

                        except Entity.DoesNotExist:
                            continue

            update_stats(resource, locale)

        log.debug("[" + locale.code + "]: " + path + " saved to DB.")
    except Exception as e:
        log.critical('PoExtractError for %s: %s' % (path, e))


def extract_xliff(project, locale, path, entities=False):
    """Extract .xliff file with path and save or update in DB."""

    with open(path) as f:
        xf = xliff.xlifffile(f)

        relative_path = get_relative_path(path, locale)
        resource, created = Resource.objects.get_or_create(
            project=project, path=relative_path, format='xliff')

        if entities:
            for order, unit in enumerate(xf.units):
                save_entity(
                    resource=resource,
                    string=unicode(unit.get_rich_source()[0]),
                    key=unit.getid(),
                    comment=unit.getnotes(),
                    order=order)

            update_entity_count(resource)

        else:
            for unit in xf.units:
                translation = unicode(unit.get_rich_target()[0])
                if translation:
                    try:
                        e = Entity.objects.get(
                            resource=resource, key=unit.getid())
                        save_translation(
                            entity=e, locale=locale, string=translation)

                    except Entity.DoesNotExist:
                        continue

            update_stats(resource, locale)

        log.debug("[" + locale.code + "]: " + path + " saved to DB.")


def extract_silme(parser, project, locale, path, entities=False):
    """Extract file with path using silme and save or update in DB."""

    try:
        f = open(path)
        structure = parser.get_structure(f.read())
        format = str(parser).split('.')[-1].split('Format')[0].lower()

        comment = ""
        order = 0
        relative_path = get_relative_path(path, locale)
        resource, created = Resource.objects.get_or_create(
            project=project, path=relative_path, format=format)

        for obj in structure:
            if isinstance(obj, silme.core.entity.Entity):
                if entities:
                    save_entity(resource=resource, string=obj.value,
                                key=obj.id, comment=comment, order=order)
                    comment = ""
                    order += 1
                else:
                    try:
                        e = Entity.objects.get(resource=resource, key=obj.id)
                        save_translation(
                            entity=e,
                            locale=locale,
                            string=obj.value)

                    except Entity.DoesNotExist:
                        continue

            elif isinstance(obj, silme.core.structure.Comment):
                if entities:
                    comment = str(obj)

        if entities:
            update_entity_count(resource)
        else:
            update_stats(resource, locale)

        log.debug("[" + locale.code + "]: " + path + " saved to DB.")
        f.close()
    except IOError:
        log.debug("[" + locale.code + "]: " +
                  path + " doesn't exist. Skipping.")


def extract_properties(project, locale, path, entities=False):
    """Extract .properties file with path and save or update in DB."""

    parser = silme.format.properties.PropertiesFormatParser
    extract_silme(parser, project, locale, path, entities)


def extract_dtd(project, locale, path, entities=False):
    """Extract .dtd file with path and save or update in DB."""

    parser = silme.format.dtd.DTDFormatParser
    extract_silme(parser, project, locale, path, entities)


def extract_lang(project, locale, path, entities=False):
    """Extract .lang file with path and save or update in DB."""

    lang = parse_lang(path)
    relative_path = get_relative_path(path, locale)

    resource, created = Resource.objects.get_or_create(
        project=project, path=relative_path, format='lang')

    if entities:
        for order, (key, value) in enumerate(lang):
            save_entity(
                resource=resource, string=key, comment=value[1], order=order)

        update_entity_count(resource)

    else:
        for key, value in lang:
            if key != value[2] or '{ok}' in value[3]:
                try:
                    e = Entity.objects.get(resource=resource, string=key)
                    save_translation(
                        entity=e, locale=locale, string=value[2])

                except Entity.DoesNotExist:
                    continue

        update_stats(resource, locale)

    log.debug("[" + locale.code + "]: " + path + " saved to DB.")


def extract_ini(project, path):
    """Extract .ini file with path and save or update in DB."""

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

    resource, created = Resource.objects.get_or_create(
        project=project, path=path, format='ini')

    for section in sections:
        try:
            locale = Locale.objects.get(code__iexact=section)
        except Locale.DoesNotExist:
            log.debug("Locale not supported: " + section)
            break

        order = 0
        for item in config.items(section):
            if section == source_locale:
                save_entity(resource=resource, string=item[1],
                            key=item[0], order=order)
                order += 1
            else:
                try:
                    e = Entity.objects.get(
                        resource=resource, key=item[0])
                    save_translation(
                        entity=e, locale=locale, string=item[1])
                except Entity.DoesNotExist:
                    log.debug("[" + section + "]: line ID " +
                              item[0] + " is obsolete.")
                    continue

        if section == source_locale:
            update_entity_count(resource)
        else:
            update_stats(resource, locale)

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
        resources = Resource.objects.filter(project=project)
        Entity.objects.filter(resource__in=resources).update(obsolete=True)

        # Remove Stats for removed locales
        project_locales = project.locales.all()
        Stats.objects.filter(resource__in=resources).exclude(
            locale__in=project_locales).delete()

        locales = [Locale.objects.get(code__iexact=source_locale)]
        locales.extend(project_locales)

    isFile = project.repository_type == 'file'
    source_paths = get_source_paths(source_directory['path'])
    format = detect_format(source_directory['path'])

    if format == 'ini':
        try:
            extract_ini(project, source_paths[0])
        except Exception as e:
            if isFile:
                os.remove(source_paths[0])
        return

    for index, locale in enumerate(locales):
        if locale.code == source_locale:
            paths = source_paths
            entities = True
        else:
            paths = get_locale_paths(project, locale)
            entities = isFile

        for path in paths:
            format = get_format(path)
            format = 'po' if format == 'pot' else format
            globals()['extract_%s' % format](project, locale, path, entities)


def update_from_repository(project, locales=None):
    """
    Update project files from remote repository.

    Args:
        project: Project instance
        locales: List of Locale instances
    """
    log.debug("Update project files from remote repository.")

    repository_type = project.repository_type
    repository_url = project.repository_url
    repository_path = repository_path_master = \
        get_repository_path_master(project)

    # If one-locale repo, set repository_url_master and update repository_path
    repository_url_master = False
    ending = os.path.basename(os.path.normpath(repository_url))

    if ending in ('templates', 'en-US', 'en-GB', 'en'):
        repository_url_master = repository_url.rsplit(ending, 1)[0]
        repository_path = os.path.join(repository_path_master, ending)

    # Save file to server
    if repository_type == 'file':

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

    # Save files to server
    else:

        if not locales:
            update_from_vcs(repository_type, repository_url, repository_path)

        if repository_url_master:  # One-locale repo
            if not locales:
                locales = project.locales.all()
            for l in locales:
                update_from_vcs(
                    repository_type,
                    os.path.join(repository_url_master, l.code),
                    os.path.join(repository_path_master, l.code))

        elif locales:
            if repository_type == 'svn':
                for l in locales:
                    path = get_locale_directory(project, l)["path"]
                    update_from_vcs(repository_type, repository_url, path)

            else:
                update_from_vcs(
                    repository_type, repository_url, repository_path)

    # Store project repository_path
    project.repository_path = repository_path
    project.save()


def dump_po(project, locale, relative_path):
    """Dump .po (gettext) file with relative path from database."""

    locale_directory_path = get_locale_directory(project, locale)["path"]
    path = os.path.join(locale_directory_path, relative_path)
    po = polib.pofile(path)
    date = datetime.datetime(1, 1, 1)
    newest = Translation()
    resource = Resource.objects.filter(project=project, path=relative_path)
    entities = Entity.objects.filter(resource=resource, obsolete=False)

    for entity in entities:
        entry = po.find(entity.string)
        if entry:
            if not entry.msgid_plural:
                try:
                    translation = Translation.objects.filter(
                        entity=entity, locale=locale, approved=True) \
                        .latest('date')
                    entry.msgstr = translation.string

                    if translation.date > date:
                        date = translation.date
                        newest = translation
                    if 'fuzzy' in entry.flags:
                        entry.flags.remove('fuzzy')

                except Translation.DoesNotExist as e:
                    pass

            else:
                for i in range(0, 6):
                    if i < (locale.nplurals or 1):
                        try:
                            translation = Translation.objects.filter(
                                entity=entity, locale=locale,
                                plural_form=i, approved=True).latest('date')
                            entry.msgstr_plural[i] = translation.string

                            if translation.date > date:
                                date = translation.date
                                newest = translation
                            if 'fuzzy' in entry.flags:
                                entry.flags.remove('fuzzy')

                        except Translation.DoesNotExist as e:
                            pass

                    # Remove obsolete plural forms if exist
                    else:
                        if i in entry.msgstr_plural:
                            del entry.msgstr_plural[i]

    # Update PO metadata
    if newest.id:
        if newest.user:
            po.metadata['PO-Revision-Date'] = newest.date
            po.metadata['Last-Translator'] = '%s <%s>' \
                % (newest.user.first_name, newest.user.email)
    po.metadata['Language'] = locale.code
    po.metadata['X-Generator'] = 'Pontoon'

    if locale.nplurals:
        po.metadata['Plural-Forms'] = 'nplurals=%s; plural=%s;' \
            % (str(locale.nplurals), locale.plural_rule)

    po.save()
    log.debug("File updated: " + path)


def dump_xliff(project, locale, relative_path):
    """Dump .xliff file with relative path from database."""

    locale_directory_path = get_locale_directory(project, locale)["path"]
    path = os.path.join(locale_directory_path, relative_path)
    resource = Resource.objects.filter(project=project, path=relative_path)
    entities = Entity.objects.filter(resource=resource, obsolete=False)

    with open(path, 'r+') as f:
        xf = xliff.xlifffile(f)

        for unit in xf.units:
            key = unit.getid()

            try:
                entity = Entity.objects.get(resource=resource, key=key)

            except Entity.DoesNotExist as e:
                log.error('%s: Entity "%s" does not exist' % (path, original))
                continue

            try:
                translation = Translation.objects.filter(
                    entity=entity, locale=locale, approved=True) \
                    .latest('date').string
                unit.settarget(translation)

            except Translation.DoesNotExist as e:
                # Remove "approved" attribute
                try:
                    del unit.xmlelement.attrib['approved']
                except KeyError:
                    pass

                # Remove "target" element
                target = unit.xmlelement.find(unit.namespaced("target"))
                if target:
                    unit.xmlelement.remove(target)

        # Erase file and then write, otherwise content gets appended
        f.seek(0)
        f.truncate()
        f.writelines(xf.__str__())
        log.debug("File updated: " + path)


def dump_silme(parser, project, locale, relative_path):
    """Dump file with relative path from database using silme. Generate files
    from source files, but only ones with translated strings."""

    locale_directory_path = get_locale_directory(project, locale)["path"]
    path = os.path.join(locale_directory_path, relative_path)

    # Create folders and copy files from source
    basedir = os.path.dirname(path)
    source_directory = get_source_directory(project.repository_path)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    try:
        shutil.copy(
            os.path.join(source_directory['path'], relative_path), path)
    # Obsolete files
    except Exception as e:
        log.debug(e)
        return

    with codecs.open(path, 'r+', 'utf-8') as f:
        structure = parser.get_structure(f.read())
        resource = Resource.objects.filter(project=project, path=relative_path)
        entities_with_path = Entity.objects.filter(
            resource=resource, obsolete=False)

        for entity in entities_with_path:
            key = entity.key

            try:
                try:
                    # Modify translated entities
                    translation = Translation.objects.filter(
                        entity=entity, locale=locale, approved=True) \
                        .latest('date')
                    structure.modify_entity(key, translation.string)

                except Translation.DoesNotExist as e:
                    # Remove untranslated and following newline
                    pos = structure.entity_pos(key)
                    structure.remove_entity(key)
                    line = structure[pos]

                    if type(line) == unicode and line.startswith('\n'):
                        line = line[len('\n'):]
                        structure[pos] = line
                        if len(line) is 0:
                            structure.remove_element(pos)

            # Obsolete entities
            except KeyError as e:
                pass

        # Erase file and then write, otherwise content gets appended
        f.seek(0)
        f.truncate()
        content = parser.dump_structure(structure)
        f.write(content)

    log.debug("File updated: " + path)


def dump_properties(project, locale, relative_path):
    """Dump .properties file with relative path from database."""

    parser = silme.format.properties.PropertiesFormatParser
    dump_silme(parser, project, locale, relative_path)


def dump_dtd(project, locale, relative_path):
    """Dump .dtd file with relative path from database."""

    parser = silme.format.dtd.DTDFormatParser
    dump_silme(parser, project, locale, relative_path)


def dump_lang(project, locale, relative_path):
    """Dump .lang file with relative path from database."""

    locale_directory_path = get_locale_directory(project, locale)["path"]
    path = os.path.join(locale_directory_path, relative_path)

    if not os.path.exists(path):
        log.info("File does not exist: " + path)
        return

    try:
        resource = Resource.objects.get(project=project, path=relative_path)
    except Resource.DoesNotExist as e:
        log.info("Resource does not exist")
        return

    with codecs.open(path, 'r+', 'utf-8', errors='replace') as lines:
        content = []
        translation = None

        for line in lines:
            if translation:
                # Keep newlines in line if present
                trans_line = line.replace(line.rstrip('\r\n'), translation)
                content.append(trans_line)
                translation = None
                continue

            content.append(line)
            line = line.strip()

            if not line:
                continue

            if line[0] == ';':
                original = line[1:].strip()

                try:
                    entity = Entity.objects.get(
                        resource=resource, string=original)
                except Entity.DoesNotExist as e:
                    log.error('%s: Entity "%s" does not exist' %
                              (path, original))
                    continue

                try:
                    translation = Translation.objects.filter(
                        entity=entity, locale=locale, approved=True) \
                        .latest('date').string

                    if translation == original:
                        translation += ' {ok}'

                except Translation.DoesNotExist as e:
                    translation = original

        # Erase file and then write, otherwise content gets appended
        lines.seek(0)
        lines.truncate()
        lines.writelines(content)
        log.debug("File updated: " + path)


def dump_ini(project, locale):
    """Dump .ini files from database."""

    path = get_locale_directory(project, locale)["path"]
    source_path = get_source_paths(path)[0]
    resource = Resource.objects.get(project=project, path=source_path)
    entities = Entity.objects.filter(resource=resource, obsolete=False)
    config = configparser.ConfigParser()

    with codecs.open(source_path, 'r+', 'utf-8', errors='replace') as f:
        try:
            config.read_file(f)
            if config.has_section(locale.code):

                for entity in entities:
                    key = entity.key

                    try:
                        translation = Translation.objects.filter(
                            entity=entity, locale=locale, approved=True) \
                            .latest('date').string
                        config.set(locale.code, key, translation)

                    except Translation.DoesNotExist as e:
                        pass

                # Erase and then write, otherwise content gets appended
                f.seek(0)
                f.truncate()
                config.write(f)
                log.debug("File updated: " + source_path)

            else:
                log.debug("Locale not available in the source file")
                raise Exception("error")

        except Exception as e:
            log.debug("INI configparser: " + str(e))


def dump_from_database(project, locale):
    """Dump project files from database."""
    log.debug("Dump project files from database.")

    # Check if locale directory even exist
    locale_directory_path = get_locale_directory(project, locale)["path"]
    if not locale_directory_path:
        return False

    formats = Resource.objects.filter(project=project).values_list(
        'format', flat=True).distinct()

    if 'ini' in formats:
        dump_ini(project, locale)

    else:
        # Get relative paths to translated files only
        stats = Stats.objects.filter(locale=locale).exclude(approved_count=0) \
            .values("resource")
        resources = Resource.objects.filter(project=project, id__in=stats)
        relative_paths = resources.values_list('path', flat=True).distinct()

        # Asymmetric formats: Remove files and folders from locale repository
        if 'dtd' in formats or 'properties' in formats:
            items = os.listdir(locale_directory_path)
            items = [i for i in items if not i[0] == '.']

            for item in items:
                path = os.path.join(locale_directory_path, item)
                try:
                    shutil.rmtree(path)
                except OSError:
                    if get_format(path) in ('dtd', 'properties'):
                        os.remove(path)
                except Exception as e:
                    log.error(e)

            # If directory empty, make sure Git and Mercurial don't remove it
            if len(os.listdir(locale_directory_path)) == 0:
                open(os.path.join(locale_directory_path, '.keep'), 'a').close()

        # Dump files based on format
        for path in relative_paths:
            format = get_format(path)
            format = 'po' if format == 'pot' else format
            globals()['dump_%s' % format](project, locale, path)

    return locale_directory_path


def generate_zip(project, locale):
    """
    Generate .zip of all project files for the specified locale.

    Args:
        project: Project instance
        locale: Locale code
    Returns:
        A string for generated ZIP content.
    """
    log.debug("Generate .zip of all project files for the specified locale.")

    try:
        locale = Locale.objects.get(code__iexact=locale)
    except Locale.DoesNotExist as e:
        log.error(e)

    path = dump_from_database(project, locale)
    if not path:
        return False

    s = StringIO.StringIO()
    zf = zipfile.ZipFile(s, "w")

    # ZIP empty root directory to avoid corrupt archive if no file translated
    root = os.path.split(path)[-1]
    zf.write(path, root)

    for root, dirs, filenames in os.walk(path):
        for f in filenames:
            file_path = os.path.join(root, f)
            zip_path = os.path.relpath(file_path, os.path.join(path, '..'))
            zf.write(file_path, zip_path)

    zf.close()
    return s.getvalue()
