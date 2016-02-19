from __future__ import division

import hashlib
import logging
import math
import os.path
import urllib
from urlparse import urlparse

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, Prefetch, F, Q, Case, When
from django.templatetags.static import static
from django.utils import timezone
from django.utils.functional import cached_property

from dirtyfields import DirtyFieldsMixin
from guardian.shortcuts import get_objects_for_user
from jsonfield import JSONField

from pontoon.sync.vcs.repositories import commit_to_vcs, get_revision, update_from_vcs
from pontoon.base import utils
from pontoon.sync import KEY_SEPARATOR


log = logging.getLogger('pontoon')


# User class extensions
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

    def with_translation_counts(self, start_date=None, query_filters=None, limit=100):
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
        :param django.db.models.Q query_filters: filters contributors by given query_filters.
        :param int limit: limit results to this number.
        """
        def translations_count(query=None):
            """Short helper to avoid duplication of passing dates."""
            query = query or Q()
            if start_date:
                query &= Q(translation__date__gte=start_date)

            if query_filters:
                query &= query_filters

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


@property
def user_translated_locales(self):
    locales = get_objects_for_user(
        self, 'base.can_translate_locale', accept_global_perms=False)

    return [locale.code for locale in locales]


@property
def user_name_or_email(self):
    return self.first_name or self.email


@property
def user_display_name(self):
    return self.first_name or self.email.split('@')[0]


@property
def user_display_name_and_email(self):
    name = self.display_name
    return u'{name} <{email}>'.format(name=name, email=self.email)


def user_gravatar_url(self, size):
    email = hashlib.md5(self.email.lower()).hexdigest()
    data = {'s': str(size)}

    if not settings.DEBUG:
        append = '_big' if size > 44 else ''
        data['d'] = settings.SITE_URL + static('img/anon' + append + '.jpg')

    return '//www.gravatar.com/avatar/{email}?{data}'.format(
        email=email, data=urllib.urlencode(data))

User.add_to_class('gravatar_url', user_gravatar_url)
User.add_to_class('name_or_email', user_name_or_email)
User.add_to_class('display_name', user_display_name)
User.add_to_class('display_name_and_email', user_display_name_and_email)
User.add_to_class('translated_locales', user_translated_locales)
User.add_to_class('translators', UserTranslationsManager())


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User, related_name='profile')

    # Other fields here
    quality_checks = models.BooleanField(default=True)
    force_suggestions = models.BooleanField(default=False)


class AggregatedStats(models.Model):
    total_strings = models.PositiveIntegerField(default=0)
    approved_strings = models.PositiveIntegerField(default=0)
    translated_strings = models.PositiveIntegerField(default=0)
    fuzzy_strings = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def adjust_stats(self, approved_strings_diff, fuzzy_strings_diff, translated_strings_diff):
        self.approved_strings = F('approved_strings') + approved_strings_diff
        self.fuzzy_strings = F('fuzzy_strings') + fuzzy_strings_diff
        self.translated_strings = F('translated_strings') + translated_strings_diff
        self.save(update_fields=['approved_strings', 'fuzzy_strings', 'translated_strings'])


def validate_cldr(value):
    for item in value.split(','):
        try:
            number = int(item.strip())
        except ValueError:
            return
        if number < 0 or number >= len(Locale.CLDR_PLURALS):
            raise ValidationError(
                '%s must be a list of integers between 0 and 5' % value)


class LocaleQuerySet(models.QuerySet):
    def available(self):
        """
        Available locales have at least one stats defined.
        """
        return self.filter(translatedresources__isnull=False).distinct()

    def prefetch_latest_translation(self, project):
        """
        Prefetch latest translation data for given project.
        """
        return self.prefetch_related(
            Prefetch(
                'project_locale',
                queryset=(
                    ProjectLocale.objects.filter(project=project)
                    .select_related('latest_translation__user')
                ),
                to_attr='fetched_latest_translation'
            )
        )


class Locale(AggregatedStats):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=128)
    plural_rule = models.CharField(max_length=128, blank=True)

    # Locale contains references to user groups who translate or manage them.
    # Groups also store respective permissions for users.
    translators_group = models.ForeignKey(Group, related_name='translated_locales', null=True,
        on_delete=models.SET_NULL)
    managers_group = models.ForeignKey(Group, related_name='managed_locales', null=True,
        on_delete=models.SET_NULL)

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

    #: Most recent translation approved or created for this locale.
    latest_translation = models.ForeignKey(
        'Translation',
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    objects = LocaleQuerySet.as_manager()

    class Meta:
        ordering = ['name', 'code']
        permissions = (
            ('can_translate_locale', 'Can add translations'),
            ('can_manage_locale', 'Can manage locale')
        )

    def __unicode__(self):
        return self.name

    def serialize(self):
        return {
            'code': self.code,
            'name': self.name,
            'nplurals': self.nplurals,
            'plural_rule': self.plural_rule,
            'cldr_plurals': self.cldr_plurals_list(),
        }

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

    @classmethod
    def cldr_id_to_plural(self, cldr_id):
        for i in self.CLDR_PLURALS:
            if i[0] == cldr_id:
                return i[1]

    @property
    def nplurals(self):
        return len(self.cldr_plurals_list())

    def available_projects_list(self):
        """Get a list of available project slugs."""
        return list(
            self.project_set.available().values_list('slug', flat=True)
        )

    def get_plural_index(self, cldr_plural):
        """Returns plural index for given cldr name."""
        cldr_id = Locale.cldr_plural_to_id(cldr_plural)
        return self.cldr_plurals_list().index(cldr_id)

    def get_relative_cldr_plural(self, plural_id):
        """
        Every locale supports a subset (a list) of The CLDR Plurals forms.
        In code, we store their relative position.
        """
        return Locale.cldr_id_to_plural(self.cldr_plurals_list()[plural_id])

    def get_latest_activity(self, project=None):
        return ProjectLocale.get_latest_activity(self, project)

    def get_chart(self, project=None):
        return ProjectLocale.get_chart(self, project)

    def aggregate_stats(self):
        TranslatedResource.objects.filter(
            resource__project__disabled=False,
            resource__entities__obsolete=False,
            locale=self
        ).distinct().aggregate_stats(self)

    def parts_stats(self, project):
        """Get locale-project pages/paths with stats."""
        def get_details(translatedresources):
            return translatedresources.order_by('resource__path').values(
                'url',
                'resource__path',
                'resource__total_strings',
                'fuzzy_strings',
                'translated_strings',
                'approved_strings',
            )

        pages = project.subpage_set.all()
        translatedresources = TranslatedResource.objects.filter(
            resource__project=project,
            resource__entities__obsolete=False,
            locale=self
        ).distinct()
        details = []

        # If subpages aren't defined,
        # return resource paths with corresponding stats
        if len(pages) == 0:
            details = get_details(translatedresources.annotate(url=F('resource__project__url')))

        # If project has defined subpages, return their names with
        # corresponding project stats. If subpages have defined resources,
        # only include stats for page resources.
        elif len(pages) > 0:
            # Each subpage must have resources defined
            if pages[0].resources.exists():
                details = get_details(
                    # List only subpages, whose resources are available for locale
                    pages.filter(resources__translatedresources__locale=self).annotate(
                        resource__path=F('name'),
                        resource__total_strings=F('resources__total_strings'),
                        fuzzy_strings=F('resources__translatedresources__fuzzy_strings'),
                        translated_strings=F('resources__translatedresources__translated_strings'),
                        approved_strings=F('resources__translatedresources__approved_strings')
                    )
                )

            else:
                details = get_details(
                    pages.annotate(
                        resource__path=F('name'),
                        resource__total_strings=F('project__resources__total_strings'),
                        fuzzy_strings=F('project__resources__translatedresources__fuzzy_strings'),
                        translated_strings=F('project__resources__translatedresources__translated_strings'),
                        approved_strings=F('project__resources__translatedresources__approved_strings')
                    )
                )

        return list(details)


class ProjectQuerySet(models.QuerySet):
    def available(self):
        """
        Available projects are not disabled and have at least one
        resource defined.
        """
        return self.filter(disabled=False, resources__isnull=False).distinct()


class Project(AggregatedStats):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True)
    locales = models.ManyToManyField(Locale, through='ProjectLocale')

    # Project info
    info_brief = models.TextField("Project info", blank=True)

    # Website for in place localization
    url = models.URLField("URL", blank=True)
    width = models.PositiveIntegerField(
        "Default website (iframe) width in pixels. If set, \
        sidebar will be opened by default.", null=True, blank=True)
    links = models.BooleanField(
        'Keep links on the project website clickable', default=False)

    # Disable project instead of deleting to keep translation memory & attributions
    disabled = models.BooleanField(default=False)

    # Whether this project has changed since the last sync.
    has_changed = models.BooleanField(default=False)

    # Most recent translation approved or created for this project.
    latest_translation = models.ForeignKey(
        'Translation',
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    objects = ProjectQuerySet.as_manager()

    class Meta:
        permissions = (
            ("can_manage", "Can manage projects"),
        )

    def __unicode__(self):
        return self.name

    def serialize(self):
        return {
            'pk': self.pk,
            'name': self.name,
            'slug': self.slug,
            'info': self.info_brief,
            'url': self.url,
            'width': self.width or '',
            'links': self.links or '',
        }

    def save(self, *args, **kwargs):
        """
        When project disabled status changes, update denormalized stats
        for all project locales.
        """
        disabled_changed = False
        if self.pk is not None:
            try:
                original = Project.objects.get(pk=self.pk)
                if self.disabled != original.disabled:
                    disabled_changed = True
            except Project.DoesNotExist:
                pass

        super(Project, self).save(*args, **kwargs)

        if disabled_changed:
            for locale in self.locales.all():
                locale.aggregate_stats()

    @property
    def needs_sync(self):
        """
        True if the project has changed since the last sync such that
        another sync is required.
        """
        changes = ChangedEntityLocale.objects.filter(entity__resource__project=self)
        return self.has_changed or changes.exists()

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

    def get_latest_activity(self, locale=None):
        return ProjectLocale.get_latest_activity(self, locale)

    def get_chart(self, locale=None):
        return ProjectLocale.get_chart(self, locale)

    def aggregate_stats(self):
        TranslatedResource.objects.filter(
            resource__project=self,
            resource__entities__obsolete=False
        ).distinct().aggregate_stats(self)


class ProjectLocale(AggregatedStats):
    """Link between a project and a locale that is active for it."""
    project = models.ForeignKey(Project, related_name='project_locale')
    locale = models.ForeignKey(Locale, related_name='project_locale')

    #: Most recent translation approved or created for this project in
    #: this locale.
    latest_translation = models.ForeignKey(
        'Translation',
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = ('project', 'locale')

    @classmethod
    def get_latest_activity(cls, self, extra=None):
        """
        Get the latest activity within project, locale
        or combination of both.

        :param self: object to get data for,
            instance of Projet or Locale
        :param extra: extra filter to be used,
            instance of Projet or Locale
        """
        latest_translation = None

        if extra is None:
            if self.latest_translation is not None:
                latest_translation = self.latest_translation

        else:
            if hasattr(self, 'fetched_project_locales'):
                if self.fetched_project_locales:
                    latest_translation = self.fetched_project_locales[0].latest_translation

            else:
                project = self if isinstance(self, Project) else extra
                locale = self if isinstance(self, Locale) else extra
                project_locale = utils.get_object_or_none(ProjectLocale, project=project, locale=locale)

                if project_locale is not None and project_locale.latest_translation is not None:
                    latest_translation = project_locale.latest_translation

        return latest_translation.latest_activity if latest_translation else None

    @classmethod
    def get_chart(cls, self, extra=None):
        """
        Get chart for project, locale or combination of both.

        :param self: object to get data for,
            instance of Projet or Locale
        :param extra: extra filter to be used,
            instance of Projet or Locale
        """
        chart = None

        if extra is None:
            chart = cls.get_chart_dict(self)

        else:
            project = self if isinstance(self, Project) else extra
            locale = self if isinstance(self, Locale) else extra
            project_locale = utils.get_object_or_none(ProjectLocale, project=project, locale=locale)

            if project_locale is not None:
                chart = cls.get_chart_dict(project_locale)

        return chart

    @classmethod
    def get_chart_dict(cls, obj):
        """Get chart data dictionary"""
        if obj.total_strings:
            return {
                'total_strings': obj.total_strings,
                'approved_strings': obj.approved_strings,
                'translated_strings': obj.translated_strings,
                'fuzzy_strings': obj.fuzzy_strings,
                'approved_share': round(obj.approved_strings / obj.total_strings * 100, 2),
                'translated_share': round(obj.translated_strings / obj.total_strings * 100, 2),
                'fuzzy_share': round(obj.fuzzy_strings / obj.total_strings * 100, 2),
                'approved_percent': int(math.floor(obj.approved_strings / obj.total_strings * 100)),
            }


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
    Prefix of the resource URL, used for direct downloads. To form a full
    URL, relative path must be appended.
    """
    permalink_prefix = models.CharField("Permalink prefix", max_length=2000, blank=True)

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

    @property
    def multi_locale(self):
        """
        Checks if url contains locale code variable. System will replace
        this variable by the locale codes of all enabled locales for the
        project during pulls and commits.
        """
        return '{locale_code}' in self.url

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

    @cached_property
    def locales(self):
        """
        Yield an iterable of Locales whose strings are stored within
        this repo.
        """
        from pontoon.sync.utils import locale_directory_path

        locales = []  # Use list since we're caching the result.
        for locale in self.project.locales.all():
            try:
                locale_directory_path(self.checkout_path, locale.code)
                locales.append(locale)
            except IOError:
                pass  # Directory missing, not in this repo.

        return locales

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
    project = models.ForeignKey(Project, related_name='resources')
    path = models.TextField()  # Path to localization file
    total_strings = models.PositiveIntegerField(default=0)

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

    deadline = models.DateField(blank=True, null=True)

    PRIORITY_CHOICES = (
        (1, 'Lowest'),
        (2, 'Low'),
        (3, 'Normal'),
        (4, 'High'),
        (5, 'Highest'),
    )
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)

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
    resource = models.ForeignKey(Resource, related_name='entities')
    string = models.TextField()
    string_plural = models.TextField(blank=True)
    key = models.TextField(blank=True)
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

    @property
    def cleaned_key(self):
        """
        Get cleaned key, without the source string and Translate Toolkit
        separator.
        """
        key = self.key.split(KEY_SEPARATOR)[0]
        if key == self.string:
            key = ''

        return key

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

    def get_translation(self, plural_form=None):
        """Get fetched translation of a given entity."""
        translations = self.fetched_translations

        if plural_form is not None:
            translations = [t for t in translations if t.plural_form == plural_form]

        if translations:
            translation = sorted(translations, key=lambda k: (k.approved, k.date), reverse=True)[0]
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
    def for_project_locale(self, project, locale, paths=None, search=None):
        """Get project entities with locale translations."""
        entities = self.objects.filter(
            resource__project=project,
            resource__translatedresources__locale=locale,
            obsolete=False
        )

        # Filter by search parameters
        if search:
            keyword = search.get('keyword', None)
            i = '' if search.get('casesensitive', None) else 'i'

            entity_query = Q()  # Empty object
            if search.get('sources', None):
                entity_query |= Q(**{'string__%scontains' % i: keyword}) | Q(**{'string_plural__%scontains' % i: keyword})

            if search.get('translations', None):
                entity_query |= Q(**{'translation__string__%scontains' % i: keyword})

            if search.get('comments', None):
                entity_query |= Q(**{'comment__%scontains' % i: keyword})

            if search.get('keys', None):
                entity_query |= Q(**{'key__%scontains' % i: keyword})

            entities = entities.filter(entity_query).distinct()

        # Filter by path
        elif paths:
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
            has_suggestions = False

            if entity.string_plural == "":
                translation_array.append(entity.get_translation())
                if len(entity.fetched_translations) > 1:
                    has_suggestions = True

            else:
                for plural_form in range(0, locale.nplurals or 1):
                    translation_array.append(entity.get_translation(plural_form))
                    if len([t for t in entity.fetched_translations if t.plural_form == plural_form]) > 1:
                        has_suggestions = True

            entities_array.append({
                'pk': entity.pk,
                'original': entity.string,
                'marked': entity.marked,
                'original_plural': entity.string_plural,
                'marked_plural': entity.marked_plural,
                'key': entity.cleaned_key,
                'path': entity.resource.path,
                'format': entity.resource.format,
                'comment': entity.comment,
                'order': entity.order,
                'source': entity.source,
                'obsolete': entity.obsolete,
                'translation': translation_array,
                'has_suggestions': has_suggestions,
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

    # extra stores data that we want to save for the specific format
    # this translation is stored in, but that we otherwise don't care
    # about.
    extra = JSONField(default=extra_default)

    @property
    def latest_activity(self):
        """
        Return the date and user associated with the latest activity on
        this translation.
        """
        if self.approved_date is not None and self.approved_date > self.date:
            return {'date': self.approved_date, 'user': self.approved_user}
        else:
            return {'date': self.date, 'user': self.user}

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

            if not self.memory_entries.exists():
                TranslationMemoryEntry.objects.create(
                    source=self.entity.string,
                    target=self.string,
                    entity=self.entity,
                    translation=self,
                    locale=self.locale
                )

        if not imported:
            # Update stats AFTER changing approval status.
            translatedresource, _ = TranslatedResource.objects.get_or_create(resource=self.entity.resource, locale=self.locale)
            translatedresource.calculate_stats()

            # Whenever a translation changes, mark the entity as having
            # changed in the appropriate locale. We could be smarter about
            # this but for now this is fine.
            if self.approved:
                self.entity.mark_changed(self.locale)

            # Check and update the latest translation where necessary.
            self.check_latest_translation(self.entity.resource.project)
            self.check_latest_translation(self.locale)
            self.check_latest_translation(translatedresource)

            project_locale = utils.get_object_or_none(
                ProjectLocale,
                project=self.entity.resource.project,
                locale=self.locale
            )
            if project_locale:
                self.check_latest_translation(project_locale)

    def check_latest_translation(self, instance):
        """
        Check if the given model instance has a `latest_activity`
        attribute and, if it does, see if this translation is more
        recent than it. If so, replace it and save.
        """
        latest = instance.latest_translation
        if latest is None or self.latest_activity['date'] > latest.latest_activity['date']:
            instance.latest_translation = self
            instance.save(update_fields=['latest_translation'])

    def delete(self, stats=True, *args, **kwargs):
        super(Translation, self).delete(*args, **kwargs)
        if stats:
            TranslatedResource.objects.get(resource=self.entity.resource, locale=self.locale).calculate_stats()

        # Mark entity as changed before deleting. This is skipped during
        # bulk delete operations, but we shouldn't be bulk-deleting
        # translations anyway.
        if self.approved:
            self.entity.mark_changed(self.locale)

    def serialize(self):
        return {
            'pk': self.pk,
            'string': self.string,
            'approved': self.approved,
            'fuzzy': self.fuzzy,
        }


class TranslationMemoryEntryManager(models.Manager):
    def minimum_levenshtein_ratio(self, text, min_quality=0.7):
        """
        Returns entries that match minimal levenshtein_ratio
        """
        length = len(text)
        min_dist = math.ceil(max(length * min_quality, 2))
        max_dist = math.floor(min(length / min_quality, 1000))
        levenshtein_ratio_equation = """(
            (char_length(source) + char_length(%s) - levenshtein(source, %s, 1, 2, 2))::float /
            (char_length(source) + char_length(%s))
        )"""

        # Only check entities with similar length
        entries = self.extra(
            where=['(CHAR_LENGTH(source) BETWEEN %s AND %s)',
                  levenshtein_ratio_equation + ' > %s'],
            params=(min_dist, max_dist, text, text, text, min_quality),
            select={'quality': levenshtein_ratio_equation + '* 100'},
            select_params=(text, text, text)
        )
        return entries


class TranslationMemoryEntry(models.Model):
    source = models.TextField()
    target = models.TextField()

    entity = models.ForeignKey(Entity, null=True, on_delete=models.SET_NULL)
    translation = models.ForeignKey(Translation, null=True, on_delete=models.SET_NULL,
                                    related_name="memory_entries")
    locale = models.ForeignKey(Locale)

    objects = TranslationMemoryEntryManager()


class TranslatedResourceQuerySet(models.QuerySet):
    def aggregate_stats(self, instance):
        aggregated_stats = self.aggregate(
            total=Sum('resource__total_strings'),
            approved=Sum('approved_strings'),
            translated=Sum('translated_strings'),
            fuzzy=Sum('fuzzy_strings')
        )

        instance.total_strings = aggregated_stats['total'] or 0
        instance.approved_strings = aggregated_stats['approved'] or 0
        instance.translated_strings = aggregated_stats['translated'] or 0
        instance.fuzzy_strings = aggregated_stats['fuzzy'] or 0

        instance.save()


class TranslatedResource(AggregatedStats):
    """
    Resource representation for a specific locale.
    """
    resource = models.ForeignKey(Resource, related_name='translatedresources')
    locale = models.ForeignKey(Locale, related_name='translatedresources')

    #: Most recent translation approved or created for this translated
    #: resource.
    latest_translation = models.ForeignKey(
        'Translation',
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    objects = TranslatedResourceQuerySet.as_manager()

    def __unicode__(self):
        translated = float(self.translated_strings + self.approved_strings)
        percent = 0
        if self.resource.total_strings > 0:
            percent = translated * 100 / self.resource.total_strings
        return str(int(round(percent)))

    def calculate_stats(self):
        """Update stats, including denormalized ones."""
        resource = self.resource
        locale = self.locale

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

        translated = max(translated_entities.count() - approved - fuzzy, 0)

        # Calculate diffs to reduce DB queries
        approved_strings_diff = approved - self.approved_strings
        fuzzy_strings_diff = fuzzy - self.fuzzy_strings
        translated_strings_diff = translated - self.translated_strings

        # Translated Resource
        self.adjust_stats(approved_strings_diff, fuzzy_strings_diff, translated_strings_diff)

        # Project
        project = resource.project
        project.adjust_stats(approved_strings_diff, fuzzy_strings_diff, translated_strings_diff)

        # Locale
        locale.adjust_stats(approved_strings_diff, fuzzy_strings_diff, translated_strings_diff)

        # ProjectLocale
        project_locale = utils.get_object_or_none(
            ProjectLocale,
            project=project,
            locale=locale
        )
        if project_locale:
            project_locale.adjust_stats(approved_strings_diff, fuzzy_strings_diff, translated_strings_diff)
