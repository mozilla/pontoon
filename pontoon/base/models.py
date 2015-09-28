import hashlib
import json
import logging
import os.path
import urllib
from urlparse import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, Prefetch, F, Q, Case, When
from django.db.models.signals import post_save
from django.templatetags.static import static
from django.utils import timezone

from dirtyfields import DirtyFieldsMixin
from jsonfield import JSONField

from pontoon.administration.vcs import commit_to_vcs, get_revision, update_from_vcs
from pontoon.base import utils


log = logging.getLogger('pontoon')


class UserTranslationsManager(models.Manager):
    """
    Provides various method to interact with larger sets of translations and their stats for user.
    """

    def _changed_translations_count(self, *args):
        """
        Helper method, returns expression object which allows us to annotate querysets
        with counts of translations.
        """
        translation_query = (
            ~Q(translation__string=F('translation__entity__string'))
            & ~Q(translation__string=F('translation__entity__string_plural'))
            & Q(translation__user__isnull=False)
        )
        for arg in args:
            translation_query &= arg

        # For each translation that matches the filter, return 1. Aggregate
        # the sum of all those results to count the number of matching
        # translations.
        return Sum(
            Case(
                When(translation_query, then=1), output_field=models.IntegerField(), default=0))

    def with_translation_counts(self, start_date=None, limit=100):
        """
        Returns contributors list, sorted by count of their translations.
        Every user instance has added following properties:
        * translations_count
        * translations_approved_count
        * translations_unapproved_count
        * translations_needs_work_count
        Method has been created mainly to improve performance and to optimize
        count of sql queries during generation of metrics.
        All counts will be returned from start_date to now().
        :param date start_date: start date for translations.
        """
        def translations_count(query=None):
            """Short helper to avoid duplication of passing dates."""
            query = query or Q()
            if start_date:
                query &= Q(translation__date__gte=start_date)
            return self._changed_translations_count(query)
        return (
            self
            .exclude(email__in=settings.EXCLUDE)
            .annotate(translations_count=translations_count(),
                      translations_approved_count=translations_count(Q(translation__approved=True)),
                      translations_unapproved_count=translations_count(Q(translation__approved=False, translation__fuzzy=False)),
                      translations_needs_work_count=translations_count(Q(translation__fuzzy=True)))
            .exclude(translations_count=0)
            .distinct().order_by('-translations_count')[:limit]
        )


# User class extensions
@property
def user_display_name(self):
    name = self.first_name or self.email.split('@')[0]
    return u'{name} <{email}>'.format(name=name, email=self.email)

User.add_to_class('display_name', user_display_name)
User.add_to_class('translators', UserTranslationsManager())


def user_gravatar_url(self, size):
    email = hashlib.md5(self.email.lower()).hexdigest()
    data = {'s': str(size)}

    if not settings.DEBUG:
        append = '_big' if size > 44 else ''
        data['d'] = settings.SITE_URL + static('img/anonymous' + append + '.jpg')

    return '//www.gravatar.com/avatar/{email}?{data}'.format(
        email=email, data=urllib.urlencode(data))
User.add_to_class('gravatar_url', user_gravatar_url)


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

    team_description = models.TextField(blank=True)

    def cldr_plurals_list(self):
        if self.cldr_plurals == '':
            return [1]
        else:
            return map(int, self.cldr_plurals.split(','))

    @classmethod
    def cldr_plural_to_id(self, cldr_plural):
        for i in self.CLDR_PLURALS:
            if i[1] == cldr_plural:
                return i[0]

    @property
    def nplurals(self):
        return len(self.cldr_plurals_list())

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

    class Meta:
        ordering = ['name', 'code']

    def latest_activity(self, project=None):
        """Get latest activity for locale and project if provided."""
        translations = Translation.objects.filter(locale=self)
        if project:
            translations = translations.filter(entity__resource__project=project)

        return translations.latest_activity()


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
        return utils.first(
            self.repositories.all(),
            lambda r: r.can_commit
        ) is not None

    @property
    def checkout_path(self):
        """Path where this project's VCS checkouts are located."""
        return os.path.join(settings.MEDIA_ROOT, 'projects', self.slug)

    # For compatibility with the old sync, these properties refer to the
    # first repository by ID.
    def _repo_compat_attr(self, attribute):
        repo = self.repositories.first()
        return getattr(repo, attribute) if repo is not None else None

    @property
    def repository_type(self):
        return self._repo_compat_attr('type')

    @property
    def repository_url(self):
        return self._repo_compat_attr('url')

    @property
    def repository_path(self):
        return self._repo_compat_attr('checkout_path')

    def repository_for_path(self, path):
        """
        Return the repository instance whose checkout contains the given
        path. If no matching repo is found, raise a ValueError.
        """
        repo = utils.first(
            self.repositories.all(),
            lambda r: path.startswith(r.checkout_path)
        )

        if repo is None:
            raise ValueError('Could not find repo matching path {path}.'.format(path=path))
        else:
            return repo

    def latest_activity(self, locale=None):
        """Get latest activity for project and locale if provided."""
        translations = Translation.objects.filter(entity__resource__project=self)
        if locale:
            translations = translations.filter(locale=locale)

        return translations.latest_activity()

    @property
    def locales_parts_stats(self):
        """Get project locales with their pages/paths and stats."""
        def get_details(stats):
            return stats.order_by('resource__path').values(
                'resource__path',
                'resource__entity_count',
                'translated_count',
                'approved_count',
            )

        pages = self.subpage_set.all()
        resources = self.active_resources
        details = {}

        for locale in self.locales.all():
            stats = Stats.objects.filter(resource__in=resources, locale=locale)
            locale_details = []

            # Is subpages aren't defined and project uses more than one
            # resource, return resource paths with corresponding resource stats
            if len(pages) == 0 and len(resources) > 1:
                locale_details = get_details(stats)

            # If project has defined subpages, return their names with
            # corresponding project stats. If subpages have defined resources,
            # only include stats for page resources.
            elif len(pages) > 0:
                # Each subpage must have resources defined
                if pages[0].resources.exists():
                    locale_details = get_details(
                        # List only subpages, whose resources are available for locale
                        pages.filter(resources__stats__locale=locale).annotate(
                            resource__path=F('name'),
                            resource__entity_count=F('resources__entity_count'),
                            translated_count=F('resources__stats__translated_count'),
                            approved_count=F('resources__stats__approved_count')
                        )
                    )

                else:
                    locale_details = get_details(
                        pages.annotate(
                            resource__path=F('name'),
                            resource__entity_count=F('project__resource__entity_count'),
                            translated_count=F('project__resource__stats__translated_count'),
                            approved_count=F('project__resource__stats__approved_count')
                        )
                    )

            details[locale.code.lower()] = list(locale_details)

        return details

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


class Repository(models.Model):
    """
    A remote VCS repository that stores resource files for a project.
    """
    FILE = 'file'
    GIT = 'git'
    HG = 'hg'
    SVN = 'svn'
    TRANSIFEX = 'transifex'
    TYPE_CHOICES = (
        (FILE, 'File'),
        (GIT, 'Git'),
        (HG, 'HG'),
        (SVN, 'SVN'),
        (TRANSIFEX, 'Transifex'),
    )

    project = models.ForeignKey(Project, related_name='repositories')
    type = models.CharField(
        max_length=255,
        blank=False,
        default='file',
        choices=TYPE_CHOICES
    )
    url = models.CharField("URL", max_length=2000, blank=True)

    """
    Mapping of locale codes to VCS revisions of each repo at the last
    sync. If this isn't a multi-locale repo, the mapping has a single
    key named "single_locale" with the revision.
    """
    last_synced_revisions = JSONField(blank=True, default=dict)

    source_repo = models.BooleanField(default=False, help_text="""
        If true, this repo contains the source strings directly in the
        root of the repo. Checkouts of this repo will have "templates"
        appended to the end of their path so that they are detected as
        source directories.
    """)
    multi_locale = models.BooleanField(default=False, help_text="""
        If true, this repo corresponds to multiple locale-specific repos. The
        URL should have the string "{locale_code}" in it, which will be replaced
        by the locale codes of all enabled locales for the project during pulls
        and and commits.
    """)

    @property
    def checkout_path(self):
        """
        Path where the checkout for this repo is located. Does not
        include a trailing path separator.
        """
        path_components = [self.project.checkout_path]

        # Include path components from the URL in case it has locale
        # information, like https://hg.mozilla.org/gaia-l10n/fr/.
        # No worry about overlap between repos, any overlap of locale
        # directories is an error already.
        path_components += urlparse(self.url).path.split('/')
        if self.multi_locale:
            path_components = [c for c in path_components if c != '{locale_code}']

        if self.source_repo:
            path_components.append('templates')

        # Remove trailing separator for consistency.
        return os.path.join(*path_components).rstrip(os.sep)

    @property
    def can_commit(self):
        """True if we can commit strings back to this repo."""
        return self.type in ('svn', 'git', 'hg')

    def locale_checkout_path(self, locale):
        """
        Path where the checkout for the given locale for this repo is
        located. If this repo is not a multi-locale repo, a ValueError
        is raised.
        """
        if not self.multi_locale:
            raise ValueError('Cannot get locale_checkout_path for non-multi-locale repos.')

        return os.path.join(self.checkout_path, locale.code)

    def locale_url(self, locale):
        """
        URL for the repo for the given locale. If this repo is not a
        multi-locale repo, a ValueError is raised.
        """
        if not self.multi_locale:
            raise ValueError('Cannot get locale_url for non-multi-locale repos.')

        return self.url.format(locale_code=locale.code)

    def url_for_path(self, path):
        """
        Determine the locale-specific repo URL for the given path.

        If this is not a multi-locale repo, raise a ValueError. If no
        repo is found for the given path, also raise a ValueError.
        """
        for locale in self.project.locales.all():
            if path.startswith(self.locale_checkout_path(locale)):
                return self.locale_url(locale)

        raise ValueError('No repo found for path: {0}'.format(path))

    def pull(self):
        """
        Pull changes from VCS. Returns the revision(s) of the repo after
        pulling.
        """
        if not self.multi_locale:
            update_from_vcs(self.type, self.url, self.checkout_path)
            return {
                'single_locale': get_revision(self.type, self.checkout_path)
            }
        else:
            current_revisions = {}
            for locale in self.project.locales.all():
                checkout_path = self.locale_checkout_path(locale)
                update_from_vcs(
                    self.type,
                    self.locale_url(locale),
                    checkout_path
                )
                current_revisions[locale.code] = get_revision(self.type, checkout_path)

            return current_revisions

    def commit(self, message, author, path):
        """Commit changes to VCS."""
        # For multi-locale repos, figure out which sub-repo corresponds
        # to the given path.
        url = self.url
        if self.multi_locale:
            url = self.url_for_path(path)

        return commit_to_vcs(self.type, path, message, author, url)

    class Meta:
        unique_together = ('project', 'url')
        ordering = ['id']


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

    SOURCE_EXTENSIONS = ['pot']  # Extensions of source-only formats.
    ALLOWED_EXTENSIONS = [f[0] for f in FORMAT_CHOICES] + SOURCE_EXTENSIONS

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
    resources = models.ManyToManyField(Resource, blank=True)

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
            translation.approved_date = timezone.now()

        translation.save()

    def get_translation(self, plural_form=None):
        """Get fetched translation of a given entity."""
        translations = self.fetched_translations

        if plural_form is not None:
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
                'string': None,
                'approved': False,
                'pk': None
            }

    @classmethod
    def for_project_locale(self, project, locale, paths=None):
        """Get project entities with locale translations."""
        entities = self.objects.filter(
            resource__project=project,
            resource__stats__locale=locale,
            obsolete=False
        )

        if paths:
            try:
                subpage = Subpage.objects.get(project=project, name__in=paths)
                paths = subpage.resources.values_list("path")
            except Subpage.DoesNotExist:
                pass
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
    when = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('entity', 'locale')


class TranslationQuerySet(models.QuerySet):
    def latest_activity(self):
        """Find latest activity in given translations."""
        if not self.exists():
            return None

        latest_translation = self.order_by('-date')[0]
        latest_approval = self.order_by('-approved_date')[0]

        if latest_approval.approved_date and latest_translation.date < latest_approval.approved_date:
            return {
                'date': latest_approval.date,
                'user': latest_approval.approved_user
            }

        else:
            return {
                'date': latest_translation.date,
                'user': latest_translation.user
            }


class TranslationManager(models.Manager):
    def get_queryset(self):
        return (TranslationQuerySet(self.model, using=self._db)
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
    date = models.DateTimeField(default=timezone.now)
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


def get_locales_with_stats():
    """Add chart data to locales."""

    locales = Locale.objects.filter(stats__isnull=False).distinct()

    for locale in locales:
        stats = Stats.objects.filter(
            resource__entity__obsolete=False,
            locale=locale).distinct()

        locale.chart = get_chart_data(stats)

    return locales


def get_locales_with_project_stats(project):
    """Add chart data to locales for specified project."""

    locales = Locale.objects.all()

    for locale in locales:
        if locale in project.locales.all():

            stats = Stats.objects.filter(
                resource__project=project,
                resource__entity__obsolete=False,
                locale=locale).distinct()

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
    now = timezone.now()
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
