import collections
import datetime
import json
import logging
import os.path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, Prefetch
from django.db.models.signals import post_save
from django.forms import ModelForm
from django.utils import timezone

from dirtyfields import DirtyFieldsMixin
from jsonfield import JSONField

from pontoon.base import MOZILLA_REPOS, utils


log = logging.getLogger('pontoon')


# User class extensions
@property
def user_display_name(self):
    name = self.first_name or self.email.split('@')[0]
    return u'{name} <{email}>'.format(name=name, email=self.email)
User.add_to_class('display_name', user_display_name)


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User, related_name='profile')

    # Other fields here
    transifex_username = models.CharField(max_length=40, blank=True)
    transifex_password = models.CharField(max_length=128, blank=True)
    svn_username = models.CharField(max_length=40, blank=True)
    svn_password = models.CharField(max_length=128, blank=True)
    quality_checks = models.BooleanField(default=True)


def validate_cldr(value):
    for item in value.split(','):
        try:
            number = int(item.strip())
        except ValueError:
            return
        if number < 0 or number >= len(Locale.CLDR_PLURALS):
            raise ValidationError(
                '%s must be a list of integers between 0 and 5' % value)


class Locale(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=128)
    nplurals = models.SmallIntegerField(null=True, blank=True)
    plural_rule = models.CharField(max_length=128, blank=True)

    # CLDR Plurals
    CLDR_PLURALS = (
        (0, 'zero'),
        (1, 'one'),
        (2, 'two'),
        (3, 'few'),
        (4, 'many'),
        (5, 'other'),
    )

    cldr_plurals = models.CommaSeparatedIntegerField(
        "CLDR Plurals", blank=True, max_length=11, validators=[validate_cldr])

    def cldr_plurals_list(self):
        if self.cldr_plurals == '':
            return [1]
        else:
            return map(int, self.cldr_plurals.split(','))

    def __unicode__(self):
        return self.name

    def stringify(self):
        return json.dumps({
            'code': self.code,
            'name': self.name,
            'nplurals': self.nplurals,
            'plural_rule': self.plural_rule,
            'cldr_plurals': self.cldr_plurals_list(),
        })

    @classmethod
    def cldr_plural_to_id(self, cldr_plural):
        for i in self.CLDR_PLURALS:
            if i[1] == cldr_plural:
                return i[0]

    class Meta:
        ordering = ['name']


class ProjectQuerySet(models.QuerySet):
    def available(self):
        """
        Available projects are not disabled and have at least one
        resource defined.
        """
        return self.filter(disabled=False, resource__isnull=False)


class Project(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True)
    locales = models.ManyToManyField(Locale)

    # Repositories
    REPOSITORY_TYPE_CHOICES = (
        ('file', 'File'),
        ('git', 'Git'),
        ('hg', 'HG'),
        ('svn', 'SVN'),
        ('transifex', 'Transifex'),
    )

    repository_type = models.CharField(
        "Type", max_length=20, blank=False, default='File',
        choices=REPOSITORY_TYPE_CHOICES)

    # URLField does not take git@github.com:user/project.git URLs
    repository_url = models.CharField("URL", max_length=2000, blank=True)

    # Includes source directory in one-locale repositories
    repository_path = models.TextField(blank=True)

    transifex_project = models.CharField(
        "Project", max_length=128, blank=True)
    transifex_resource = models.CharField(
        "Resource", max_length=128, blank=True)

    # Project info
    info_brief = models.TextField("Project info", blank=True)

    # Website for in place localization
    url = models.URLField("URL", blank=True)
    width = models.PositiveIntegerField(
        "Default website (iframe) width in pixels. If set, \
        sidebar will be opened by default.", null=True, blank=True)
    links = models.BooleanField(
        "Keep links on the project website clickable")

    # Disable project instead of deleting to keep translation memory & stats
    disabled = models.BooleanField(default=False)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        permissions = (
            ("can_manage", "Can manage projects"),
            ("can_localize", "Can localize projects"),
        )

    @property
    def can_commit(self):
        """
        True if we can commit strings back to the repository this
        project is hosted in, False otherwise.
        """
        return self.repository_type in ('git', 'hg', 'svn')

    @property
    def checkout_path(self):
        """Path that this project's VCS checkout is located."""
        return os.path.join(settings.MEDIA_ROOT, self.repository_type, self.slug)

    def source_directory_path(self):
        """Path to the directory where source strings are stored."""
        for root, dirnames, filenames in os.walk(self.checkout_path):
            for dirname in dirnames:
                if dirname in ('templates', 'en-US', 'en'):
                    return os.path.join(root, dirname)

        raise Exception('No source directory found for project {0}'.format(self.slug))

    def locale_directory_path(self, locale_code=None):
        """
        Path to the directory where strings for the given locale are
        stored.

        If locale_code is None, return the path to the directory where
        source strings are stored.
        """
        path = self.checkout_path
        locale_code = locale_code or self.source_directory_name()
        if locale_code is not None:
            for root, dirnames, filenames in os.walk(path):
                if locale_code in dirnames:
                    return os.path.join(root, locale_code)

                locale_variant = locale_code.replace('-', '_')
                if locale_variant in dirnames:
                    return os.path.join(root, locale_variant)

        raise Exception('Directory for locale `{0}` not found'.format(
                        locale_code or 'source'))

    def relative_resource_paths(self):
        """
        List of paths relative to the locale directories returned by
        self.locale_directory_path() for each resource in this project.
        """
        path = self.source_directory_path()
        for absolute_path in self.resources_for_path(path):
            yield os.path.relpath(absolute_path, path)

    def resources_for_path(self, path):
        """
        List of paths for all supported resources found within the given
        path.
        """
        for root, dirnames, filenames in os.walk(path):
            # Ignore certain files in Mozilla repositories.
            if self.repository_url in MOZILLA_REPOS:
                filenames = [f for f in filenames if f.endswith('region.properties')]

            for filename in filenames:
                base, extension = os.path.splitext(filename)
                if extension[1:].lower() in Resource.ALLOWED_EXTENSIONS:
                    yield os.path.join(root, filename)

    def __unicode__(self):
        return self.name

    def serialize(self):
        return {
            'pk': self.pk,
            'name': self.name,
            'slug': self.slug,
            'url': self.url,
        }

    def as_json(self):
        return json.dumps(self.serialize())


class Resource(models.Model):
    project = models.ForeignKey(Project)
    path = models.TextField()  # Path to localization file
    entity_count = models.PositiveIntegerField(default=0)

    # Format
    FORMAT_CHOICES = (
        ('po', 'po'),
        ('xliff', 'xliff'),
        ('properties', 'properties'),
        ('dtd', 'dtd'),
        ('inc', 'inc'),
        ('ini', 'ini'),
        ('lang', 'lang'),
        ('l20n', 'l20n'),
    )
    format = models.CharField(
        "Format", max_length=20, blank=True, choices=FORMAT_CHOICES)

    ALLOWED_EXTENSIONS = [f[0] for f in FORMAT_CHOICES] + ['pot']

    ASYMMETRIC_FORMATS = ('dtd', 'properties', 'ini', 'inc', 'l20n')

    @property
    def is_asymmetric(self):
        """Return True if this resource is in an asymmetric format."""
        return self.format in self.ASYMMETRIC_FORMATS

    def __unicode__(self):
        return '%s: %s' % (self.project.name, self.path)

    @classmethod
    def get_path_format(self, path):
        filename, extension = os.path.splitext(path)
        path_format = extension[1:].lower()

        # Special case: pot files are considered the po format
        return 'po' if path_format == 'pot' else path_format


class Subpage(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=128)
    url = models.URLField("URL", blank=True)  # Firefox OS Hack
    resource = models.ManyToManyField(Resource, blank=True)

    def __unicode__(self):
        return self.name


class Entity(DirtyFieldsMixin, models.Model):
    resource = models.ForeignKey(Resource)
    string = models.TextField()
    string_plural = models.TextField(blank=True)
    key = models.TextField(blank=True)  # Needed for webL10n
    comment = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    source = JSONField(blank=True, default=list)  # List of paths to source code files
    obsolete = models.BooleanField(default=False)

    changed_locales = models.ManyToManyField(
        Locale,
        through='ChangedEntityLocale',
        help_text='List of locales in which translations for this entity have '
                  'changed since the last sync.'
    )

    @property
    def marked(self):
        return utils.mark_placeables(self.string)

    @property
    def marked_plural(self):
        return utils.mark_placeables(self.string_plural)

    def __unicode__(self):
        return self.string

    def has_changed(self, locale):
        """
        Check if translations in the given locale have changed since the
        last sync.
        """
        return locale in self.changed_locales.all()

    def mark_changed(self, locale):
        """
        Mark the given locale as having changed translations since the
        last sync.
        """
        ChangedEntityLocale.objects.get_or_create(entity=self, locale=locale)

    def add_translation(self, string, locale, user):
        """
        Add a new translation for this entity. If a matching translation
        already exists, mark it as unfuzzy, and if the given user is a
        translator, approve it.
        """
        try:
            translation = self.translation_set.get(locale=locale, string=string)
        except Translation.DoesNotExist:
            translation = Translation(entity=self, locale=locale, user=user, string=string,
                                      fuzzy=True)

        if translation.pk:
            translation.fuzzy = False

        if user.has_perm('base.can_localize') and not translation.approved:
            translation.approved = True
            translation.approved_user = user
            translation.approved_date = datetime.datetime.now()

        translation.save()

    def get_translation(self, plural_form=None):
        """Get fetched translation of a given entity."""
        translations = self.fetched_translations

        if plural_form:
            translations = [t for t in translations if t.plural_form == plural_form]

        if translations:
            translation = sorted(translations, key=lambda k: (not k.approved, k.date))[0]
            return {
                'fuzzy': translation.fuzzy,
                'string': translation.string,
                'approved': translation.approved,
                'pk': translation.pk
            }

        else:
            return {
                'fuzzy': False,
                'string': u'',
                'approved': False,
                'pk': None
            }

    @classmethod
    def for_project_locale(self, project, locale, paths=None):
        """Get project entities with locale translations."""
        entities = self.objects.filter(resource__project=project, obsolete=False)

        if paths:
            entities = entities.filter(resource__path__in=paths) or entities

        entities = entities.prefetch_related(
            'resource',
            Prefetch(
                'translation_set',
                queryset=Translation.objects.filter(locale=locale),
                to_attr='fetched_translations'
            )
        )

        entities_array = []

        for entity in entities:
            translation_array = []

            if entity.string_plural == "":
                translation_array.append(entity.get_translation())

            else:
                for plural_form in range(0, locale.nplurals or 1):
                    translation_array.append(entity.get_translation(plural_form))

            entities_array.append({
                'pk': entity.pk,
                'original': entity.string,
                'marked': entity.marked,
                'original_plural': entity.string_plural,
                'marked_plural': entity.marked_plural,
                'key': entity.key,
                'path': entity.resource.path,
                'format': entity.resource.format,
                'comment': entity.comment,
                'order': entity.order,
                'source': entity.source,
                'obsolete': entity.obsolete,
                'translation': translation_array,
            })

        return sorted(entities_array, key=lambda k: k['order'])


class ChangedEntityLocale(models.Model):
    """
    ManyToMany model for storing what locales have changed translations for a
    specific entity since the last sync.
    """
    entity = models.ForeignKey(Entity)
    locale = models.ForeignKey(Locale)

    class Meta:
        unique_together = ('entity', 'locale')


class TranslationManager(models.Manager):
    def get_queryset(self):
        return (super(TranslationManager, self).get_queryset()
                .filter(deleted__isnull=True))


class DeletedTranslationManager(models.Manager):
    def get_queryset(self):
        return (super(DeletedTranslationManager, self).get_queryset()
                .filter(deleted__isnull=False))


def extra_default():
    """Default value for the Translation.extra field."""
    return {}


class Translation(DirtyFieldsMixin, models.Model):
    entity = models.ForeignKey(Entity)
    locale = models.ForeignKey(Locale)
    user = models.ForeignKey(User, null=True, blank=True)
    string = models.TextField()
    # 0=zero, 1=one, 2=two, 3=few, 4=many, 5=other, null=no plural forms
    plural_form = models.SmallIntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approved_user = models.ForeignKey(
        User, related_name='approvers', null=True, blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    fuzzy = models.BooleanField(default=False)
    deleted = models.DateTimeField(default=None, null=True)

    # extra stores data that we want to save for the specific format
    # this translation is stored in, but that we otherwise don't care
    # about.
    extra = JSONField(default=extra_default)

    # Due to https://code.djangoproject.com/ticket/14891,
    # TranslationManager will be used for the reverse FK from entities,
    # e.g. entity.translation_set. Deleted translations cannot be
    # accessed via that relation.
    objects = TranslationManager()
    deleted_objects = DeletedTranslationManager()

    def __unicode__(self):
        return self.string

    def save(self, imported=False, *args, **kwargs):
        super(Translation, self).save(*args, **kwargs)

        # Only one translation can be approved at a time for any
        # Entity/Locale.
        if self.approved:
            (Translation.objects
                .filter(entity=self.entity, locale=self.locale, plural_form=self.plural_form)
                .exclude(pk=self.pk)
                .update(approved=False, approved_user=None, approved_date=None))

        if not imported:
            # Update stats AFTER changing approval status.
            update_stats(self.entity.resource, self.locale)

            # Whenever a translation changes, mark the entity as having
            # changed in the appropriate locale. We could be smarter about
            # this but for now this is fine.
            self.entity.mark_changed(self.locale)

    def mark_for_deletion(self):
        self.deleted = timezone.now()
        self.save()

    def delete(self, stats=True, *args, **kwargs):
        super(Translation, self).delete(*args, **kwargs)
        if stats:
            update_stats(self.entity.resource, self.locale)

    def serialize(self):
        return {
            'pk': self.pk,
            'string': self.string,
            'approved': self.approved,
            'fuzzy': self.fuzzy,
        }


class Stats(models.Model):
    resource = models.ForeignKey(Resource)
    locale = models.ForeignKey(Locale)
    translated_count = models.PositiveIntegerField(default=0)
    approved_count = models.PositiveIntegerField(default=0)
    fuzzy_count = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        translated = float(self.translated_count + self.approved_count)
        percent = 0
        if self.resource.entity_count > 0:
            percent = translated * 100 / self.resource.entity_count
        return str(int(round(percent)))


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'slug', 'locales', 'repository_type',
                  'repository_url', 'repository_path', 'transifex_project',
                  'transifex_resource', 'info_brief', 'url', 'width',
                  'links', 'disabled')

    def clean(self):
        cleaned_data = super(ProjectForm, self).clean()
        repository_url = cleaned_data.get("repository_url")
        repository_type = cleaned_data.get("repository_type")
        transifex_project = cleaned_data.get("transifex_project")
        transifex_resource = cleaned_data.get("transifex_resource")

        if repository_type == 'transifex':
            if not transifex_project:
                self._errors["repository_url"] = self.error_class(
                    [u"You need to provide Transifex project and resource."])
                del cleaned_data["transifex_resource"]

            if not transifex_resource:
                self._errors["repository_url"] = self.error_class(
                    [u"You need to provide Transifex project and resource."])
                del cleaned_data["transifex_project"]

        elif not repository_url:
            self._errors["repository_url"] = self.error_class(
                [u"You need to provide a valid URL."])

        return cleaned_data


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# For every newly created user
post_save.connect(create_user_profile, sender=User)


def get_chart_data(stats):
    """Get chart data for stats."""

    return stats.aggregate(
        total=Sum('resource__entity_count'),
        approved=Sum('approved_count'),
        translated=Sum('translated_count'),
        fuzzy=Sum('fuzzy_count')
    )


def get_locales_with_stats(project):
    """Add chart data to locales for specified project."""

    locales = Locale.objects.all()

    for locale in locales:
        if locale in project.locales.all():
            r = Entity.objects.filter(obsolete=False).values('resource')
            resources = Resource.objects.filter(project=project, pk__in=r)
            stats = Stats.objects.filter(resource__in=resources, locale=locale)

            locale.chart = get_chart_data(stats)

    return locales


def get_projects_with_stats(projects, locale=None):
    """Add chart data to projects (for specified locale)."""

    for project in projects:
        r = Entity.objects.filter(obsolete=False).values('resource')
        resources = Resource.objects.filter(project=project, pk__in=r)
        locales = project.locales.all()
        stats = Stats.objects.filter(
            resource__in=resources, locale__in=locales)

        if locale:
            stats = stats.filter(locale=locale)

        project.chart = get_chart_data(stats)

    return projects


def get_translation(entity, locale, plural_form=None, fuzzy=None):
    """Get translation of a given entity to a given locale in a given form."""

    translations = Translation.objects.filter(
        entity=entity, locale=locale, plural_form=plural_form)

    if fuzzy is not None:
        translations = translations.filter(fuzzy=fuzzy)

    if translations.exists():
        try:
            return translations.filter(approved=True).latest("date")
        except Translation.DoesNotExist:
            return translations.latest("date")
    else:
        return Translation()


def save_entity(resource, string, string_plural="", comment="",
                order=0, key="", source=None):
    """Add new or update existing entity."""
    source = source or []

    # Update existing entity
    try:
        if key is "":
            e = Entity.objects.get(
                resource=resource, string=string, string_plural=string_plural)

        else:
            e = Entity.objects.get(resource=resource, key=key)
            e.string = string
            e.string_plural = string_plural

        e.source = source

        # Set obsolete attribute for all updated entities to False
        e.obsolete = False

    # Add new entity
    except Entity.DoesNotExist:
        e = Entity(resource=resource, string=string,
                   string_plural=string_plural, key=key, source=source)

    if len(comment) > 0:
        e.comment = comment

    e.order = order
    e.save()


def save_translation(entity, locale, string, plural_form=None, fuzzy=False):
    """Add new or update existing translation."""

    approved = not fuzzy
    now = datetime.datetime.now()
    translations = Translation.objects.filter(
        entity=entity, locale=locale, plural_form=plural_form)
    translations_equal = translations.filter(string=string)
    translations_equal_count = translations_equal.count()

    # Add new translation if it doesn's exist yet
    if translations_equal_count == 0:
        unapprove(translations)
        unfuzzy(translations)
        t = Translation(
            entity=entity, locale=locale, plural_form=plural_form,
            string=string, date=now,
            approved=approved, fuzzy=fuzzy)
        if approved:
            t.approved_date = now
        t.save(imported=True)

    # Update existing translations
    elif translations_equal_count > 0:
        t = translations_equal[0]
        if translations_equal_count > 1:
            try:
                t = translations_equal.filter(approved=True).latest("date")
                t.approved_date = now
            except Translation.DoesNotExist:
                t = translations_equal.latest("date")

        # If fuzzy status changes
        if t.fuzzy != fuzzy:
            # Only if fuzzy flag removed
            if not fuzzy:
                unapprove(translations)

            unfuzzy(translations)

            if fuzzy and get_translation(
                    entity=entity, locale=locale,
                    plural_form=plural_form) == t:
                t.fuzzy = fuzzy

            t.date = now
            t.approved = approved
            t.save(imported=True)


def unapprove(translations):
    """Set approved attribute for given translations to False."""

    translations.update(approved=False, approved_user=None, approved_date=None)


def unfuzzy(translations):
    """Set fuzzy attribute for given translations to False."""

    translations.update(fuzzy=False)


def update_entity_count(resource):
    """Save number of non-obsolete entities for a given resource."""

    count = Entity.objects.filter(resource=resource, obsolete=False).count()
    resource.entity_count = count
    resource.save()

    # Asymmetric formats:
    # Make sure Stats object exists, so resources are listed in the menu
    if resource.format in ('dtd', 'properties'):
        for locale in resource.project.locales.all():
            stats, created = Stats.objects.get_or_create(
                resource=resource, locale=locale)

            # Existing stats were set to 0 beforehand and need to be restored
            if not created:
                update_stats(resource, locale)


def update_stats(resource, locale):
    """Save stats for given resource and locale."""

    stats, c = Stats.objects.get_or_create(resource=resource, locale=locale)
    entity_ids = Translation.objects.filter(locale=locale).values('entity')
    translated_entities = Entity.objects.filter(
        pk__in=entity_ids, resource=resource, obsolete=False)

    # Singular
    translations = Translation.objects.filter(
        entity__in=translated_entities.filter(string_plural=''), locale=locale)
    approved = translations.filter(approved=True).count()
    fuzzy = translations.filter(fuzzy=True).count()

    # Plural
    nplurals = locale.nplurals or 1
    for e in translated_entities.exclude(string_plural=''):
        translations = Translation.objects.filter(entity=e, locale=locale)
        if translations.filter(approved=True).count() == nplurals:
            approved += 1
        elif translations.filter(fuzzy=True).count() == nplurals:
            fuzzy += 1

    stats.approved_count = approved
    stats.fuzzy_count = fuzzy
    stats.translated_count = max(translated_entities.count() - approved - fuzzy, 0)
    stats.save()
