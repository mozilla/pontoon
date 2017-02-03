from __future__ import division

import hashlib
import logging
import math
import os.path
import re
import urllib

from collections import defaultdict
from dirtyfields import DirtyFieldsMixin

from django.conf import settings
from django.contrib.auth.models import User, Group, UserManager
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.db import models
from django.db.models import Case, Count, F, Prefetch, Q, Sum, When
from django.templatetags.static import static
from django.utils import timezone
from django.utils.functional import cached_property

from guardian.shortcuts import get_objects_for_user
from jsonfield import JSONField

from pontoon.sync.vcs.repositories import (
    commit_to_vcs,
    get_revision,
    update_from_vcs,
    PullFromRepositoryException,
)
from pontoon.base import utils
from pontoon.sync import KEY_SEPARATOR

from urlparse import urlparse


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

        def extract_locale(name):
            """Extract locale code from group name."""
            name = name.split(' ')[0]
            if '/' in name:
                name = name.split('/')[1]
            return name

        def with_roles(self):
            """Add user roles."""
            managers = defaultdict(set)
            manager_groups = Group.objects.filter(name__endswith='managers').prefetch_related('user_set')

            for group in manager_groups:
                for user in group.user_set.all():
                    managers[user].add(extract_locale(group.name))

            translators = defaultdict(set)
            translator_groups = Group.objects.filter(name__endswith='translators').prefetch_related('user_set')
            for group in translator_groups:
                for user in group.user_set.all():
                    translators[user].add(extract_locale(group.name))

            for contributor in self:
                contributor.user_role = contributor.role(managers, translators)

            return self

        return with_roles(
            self
            .exclude(email__in=settings.EXCLUDE)
            .annotate(translations_count=translations_count(),
                      translations_approved_count=translations_count(Q(translation__approved=True)),
                      translations_unapproved_count=translations_count(Q(translation__approved=False, translation__fuzzy=False)),
                      translations_needs_work_count=translations_count(Q(translation__fuzzy=True)))
            .exclude(translations_count=0)
            .distinct().order_by('-translations_count')[:limit]
        )


class UserCustomManager(UserManager):
    """
    Django migrations is able to migrate managers, and throws an error if we directly call UserManager.from_queryset():
        Please note that you need to inherit from managers you dynamically generated with 'from_queryset()'.
    """
    use_in_migrations = False

    def map_translations_to_events(cls, days, translations):
        """
        Map translations into events (jsonable dictionaries).
        :param QuerySet[Translation] events: a QuerySet with translastions.
        :rtype: list[dict]
        :return: A list of dicts with mapped fields.
        """
        timeline = []
        for day in days:
            daily = translations.filter(date__startswith=day['day'])
            daily.prefetch_related('entity__resource__project')
            example = daily.first()

            timeline.append({
                'date': example.date,
                'type': 'translation',
                'count': day['count'],
                'project': example.entity.resource.project,
                'translation': example,
            })

        return timeline


class UserQuerySet(models.QuerySet):
    def serialize(self):
        users = []

        for user in self:
            users.append({
                'email': user.email,
                'display_name': user.name_or_email,
                'id': user.id,
                'gravatar_url': user.gravatar_url(44),
                'translation_count': user.translation_count,
                'role': user.role()
            })

        return users


@property
def user_profile_url(self):
    return reverse('pontoon.contributor.username', kwargs={
        'username': self.username
    })


def user_gravatar_url(self, size):
    email = hashlib.md5(self.email.lower()).hexdigest()
    data = {'s': str(size)}

    if not settings.DEBUG:
        append = '_big' if size > 44 else ''
        data['d'] = settings.SITE_URL + static('img/anon' + append + '.jpg')

    return '//www.gravatar.com/avatar/{email}?{data}'.format(
        email=email, data=urllib.urlencode(data))


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


@classmethod
def user_display_name_or_blank(cls, user):
    """Shorcut function that displays user info if user isn't none."""
    return (user.name_or_email if user else "")


@property
def user_translated_locales(self):
    locales = get_objects_for_user(
        self, 'base.can_translate_locale', accept_global_perms=False)

    return locales.values_list('code', flat=True)


@property
def user_translated_projects(self):
    """
    Returns a map of permission for every user
    :param self:
    :return:
    """
    user_project_locales = (
        get_objects_for_user(self, 'base.can_translate_project_locale', accept_global_perms=False)
    ).values_list('pk', flat=True)

    project_locales = (
        ProjectLocale.objects.filter(
            has_custom_translators=True
        ).values_list('pk', 'locale__code', 'project__slug')
    )
    permission_map = {
        '{}-{}'.format(locale, project): (pk in user_project_locales)
        for pk, locale, project in project_locales
    }
    return permission_map


@property
def user_managed_locales(self):
    locales = get_objects_for_user(
        self, 'base.can_manage_locale', accept_global_perms=False)

    return locales.values_list('code', flat=True)


def user_role(self, managers=None, translators=None):
    """
    Prefetched managers and translators dicts help reduce the number of queries
    on pages that contain a lot of users, like the Top Contributors page.
    """
    if self.is_superuser:
        return 'Admin'

    if managers is not None:
        if self in managers:
            return 'Manager for ' + ', '.join(managers[self])
    else:
        if self.managed_locales:
            return 'Manager for ' + ', '.join(self.managed_locales)

    if translators is not None:
        if self in translators:
            return 'Translator for ' + ', '.join(translators[self])
    else:
        if self.translated_locales:
            return 'Translator for ' + ', '.join(self.translated_locales)

    return 'Contributor'


def user_locale_role(self, locale):
    if self in locale.managers_group.user_set.all():
        return 'manager'
    if self in locale.translators_group.user_set.all():
        return 'translator'
    else:
        return 'contributor'


@property
def contributed_translations(self):
    """Filtered contributions provided by user."""
    translations = (
        Translation.objects.filter(user=self)
            .exclude(string=F('entity__string'))
            .exclude(string=F('entity__string_plural'))
    )
    return translations


def can_translate(self, locale, project):
    """Check if user has suitable permissions to translate in given locale or project/locale."""

    # Locale managers can translate all projects
    if locale.code in self.managed_locales:
        return True

    project_locale = ProjectLocale.objects.get(project=project, locale=locale)
    if project_locale.has_custom_translators:
        return self.has_perm('base.can_translate_project_locale', project_locale)

    return self.has_perm('base.can_translate_locale', locale)


User.add_to_class('profile_url', user_profile_url)
User.add_to_class('gravatar_url', user_gravatar_url)
User.add_to_class('name_or_email', user_name_or_email)
User.add_to_class('display_name', user_display_name)
User.add_to_class('display_name_and_email', user_display_name_and_email)
User.add_to_class('display_name_or_blank', user_display_name_or_blank)
User.add_to_class('translated_locales', user_translated_locales)
User.add_to_class('translated_projects', user_translated_projects)
User.add_to_class('managed_locales', user_managed_locales)
User.add_to_class('role', user_role)
User.add_to_class('locale_role', user_locale_role)
User.add_to_class('translators', UserTranslationsManager())
User.add_to_class('objects', UserCustomManager.from_queryset(UserQuerySet)())
User.add_to_class('contributed_translations', contributed_translations)
User.add_to_class('can_translate', can_translate)


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User, related_name='profile')
    # Other fields here
    quality_checks = models.BooleanField(default=True)
    force_suggestions = models.BooleanField(default=False)

    """Defines the order of locales displayed in locale tab."""
    locales_order = ArrayField(
        models.PositiveIntegerField(),
        default=list,
        blank=True,
    )

    @property
    def sorted_locales(self):
        locales = Locale.objects.filter(pk__in=self.locales_order)
        return sorted(locales, key=lambda locale: self.locales_order.index(locale.pk))

    @property
    def sorted_locales_codes(self):
        """Return the codes of locales that contributor set in his preferences."""
        return [l.code for l in self.sorted_locales]


class AggregatedStats(models.Model):
    total_strings = models.PositiveIntegerField(default=0)
    approved_strings = models.PositiveIntegerField(default=0)
    translated_strings = models.PositiveIntegerField(default=0)
    fuzzy_strings = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def adjust_stats(self, total_strings_diff, approved_strings_diff,
                     fuzzy_strings_diff, translated_strings_diff):
        self.total_strings = F('total_strings') + total_strings_diff
        self.approved_strings = F('approved_strings') + approved_strings_diff
        self.fuzzy_strings = F('fuzzy_strings') + fuzzy_strings_diff
        self.translated_strings = F('translated_strings') + translated_strings_diff

        self.save(update_fields=[
            'total_strings', 'approved_strings',
            'fuzzy_strings', 'translated_strings'
        ])


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
    def unsynced(self):
        """
        Filter unsynchronized locales.
        """
        return self.filter(translatedresources__isnull=True).distinct()

    def available(self):
        """
        Available locales have at least one TranslatedResource defined.
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
    plural_rule = models.CharField(
        max_length=128,
        blank=True,
        help_text="""
        Plural rule is part of the plurals header in
        <a href="https://www.gnu.org/software/gettext/manual/gettext.html#Plural-forms">Gettext PO files</a>,
        that follows the <i>plural=</i> string, without the trailing semicolon.
        E.g. (n != 1)
        """
    )

    # Locale contains references to user groups that translate or manage them.
    # Groups store respective permissions for users.
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
        "CLDR Plurals",
        blank=True,
        max_length=11,
        validators=[validate_cldr],
        help_text="""
        A comma separated list of <a href="http://www.unicode.org/cldr/charts/dev/supplemental/language_plural_rules.html">CLDR plural rules</a>,
        where 0 represents zero, 1 one, 2 two, 3 few, 4 many, and 5 other.
        E.g. 1,5
        """
    )

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

    @property
    def projects_permissions(self):
        """
        List of tuples that contain informations required by the locale permissions view.

        A row contains:
            id  - id of project locale
            slug - slug of the project
            name - name of the project
            all_users - (id, first_name, email) users that aren't translators of given project locale.
            translators - (id, first_name, email) translators assigned to a project locale.
            contributors - (id, first_name, email) people who contributed for a project in current locale.
            has_custom_translators - Flag if locale has a translators group for the project.
        """
        locale_projects = []

        def create_users_map(qs, keyfield):
            """
            Creates a map from query set
            """
            user_map = defaultdict(list)
            for row in qs:
                key = row.pop(keyfield)
                user_map[key].append(row)
            return user_map

        project_locales = list(
            self.project_locale.available()
                .prefetch_related('project', 'translators_group')
                .order_by('project__name')
                .values(
                    'id',
                    'project__pk',
                    'project__name',
                    'project__slug',
                    'translators_group__pk',
                    'has_custom_translators'
                )
        )

        projects_translators = create_users_map(
            User.objects
                .filter(groups__pk__in=[project_locale['translators_group__pk'] for project_locale in project_locales])
                .exclude(email='')
                .prefetch_related('groups')
                .values('id', 'first_name', 'email', 'groups__pk')
                .distinct(),
            'groups__pk'
        )

        projects_all_users = defaultdict(set)

        for project_locale in project_locales:
            projects_all_users[project_locale['translators_group__pk']] = list(
                User.objects
                    .exclude(email='')
                    .exclude(groups__projectlocales__pk=project_locale['id'])
                    .values('id', 'first_name', 'email')
                    .distinct()
            )

        for project_locale in project_locales:
            group_pk = project_locale['translators_group__pk']
            locale_projects.append((
                project_locale['id'],
                project_locale['project__slug'],
                project_locale['project__name'],
                projects_all_users[group_pk],
                projects_translators[group_pk],
                project_locale['has_custom_translators']
            ))

        return locale_projects

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
        def get_details(parts):
            return parts.order_by('title').values(
                'url',
                'title',
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
        unbound_details = []

        # If subpages aren't defined,
        # return resource paths with corresponding stats
        if len(pages) == 0:
            details = get_details(translatedresources.annotate(
                title=F('resource__path'),
                url=F('resource__project__url')
            ))

        # If project has defined subpages, return their names with
        # corresponding project stats. If subpages have defined resources,
        # only include stats for page resources.
        elif len(pages) > 0:
            # Each subpage must have resources defined
            if pages[0].resources.exists():
                locale_pages = pages.filter(resources__translatedresources__locale=self)
                details = get_details(
                    # List only subpages, whose resources are available for locale
                    locale_pages.annotate(
                        title=F('name'),
                        resource__path=F('resources__path'),
                        resource__total_strings=F('resources__total_strings'),
                        fuzzy_strings=F('resources__translatedresources__fuzzy_strings'),
                        translated_strings=F('resources__translatedresources__translated_strings'),
                        approved_strings=F('resources__translatedresources__approved_strings')
                    )
                )

            else:
                locale_pages = (
                    pages
                        .filter(project__resources__translatedresources__locale=self)
                        .exclude(project__resources__total_strings=0)
                )
                details = get_details(
                    locale_pages.annotate(
                        title=F('name'),
                        resource__path=F('project__resources__path'),
                        resource__total_strings=F('project__resources__total_strings'),
                        fuzzy_strings=F('project__resources__translatedresources__fuzzy_strings'),
                        translated_strings=F('project__resources__translatedresources__translated_strings'),
                        approved_strings=F('project__resources__translatedresources__approved_strings')
                    )
                )

            # List resources not bound to subpages as regular resources
            bound_resources = locale_pages.values_list('resources', flat=True)
            unbound_tr = translatedresources.exclude(resource__pk__in=bound_resources)
            unbound_details = get_details(unbound_tr.annotate(
                title=F('resource__path'),
                url=F('resource__project__url')
            ))

        all_resources = ProjectLocale.objects.get(project=project, locale=self)
        all_paths = (
            TranslatedResource.objects
            .filter(resource__project=project, locale=self)
            .values_list("resource__path", flat=True)
        )

        details_list = list(details) + list(unbound_details)
        details_list.append({
            'title': 'all-resources',
            'resource__path': list(all_paths),
            'resource__total_strings': all_resources.total_strings,
            'fuzzy_strings': all_resources.fuzzy_strings,
            'translated_strings': all_resources.translated_strings,
            'approved_strings': all_resources.approved_strings,
        })

        return details_list


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
    width = models.PositiveIntegerField(null=True, blank=True, help_text="""
        Default website (iframe) width in pixels.
        If set, sidebar will be opened by default.
    """)
    links = models.BooleanField(
        'Keep links on the project website clickable', default=False)

    langpack_url = models.URLField('Language pack URL', blank=True, null=True, help_text="""
        URL pattern for downloading language packs. Leave empty if language packs
        not available for the project. Supports {locale_code} wildcard.
    """)

    # Disable project instead of deleting to keep translation memory & attributions
    disabled = models.BooleanField(default=False)

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
            'langpack_url': self.langpack_url or '',
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
    def changed_resources(self):
        """
        Returns a map of resource paths and their locales
        that where changed from the last sync.
        """
        resources = defaultdict(set)
        changes = (
            ChangedEntityLocale.objects
                .filter(entity__resource__project=self)
                .prefetch_related('locale', 'entity__resource')
        )

        for change in changes:
            resources[change.entity.resource.path].add(change.locale)

        return resources

    @cached_property
    def unsynced_locales(self):
        """
        Project Locales that haven't been synchronized yet.
        """
        return list(
            set(self.locales.all()) - set(Locale.objects.filter(
                translatedresources__resource__project=self)
            )
        )

    @property
    def needs_sync(self):
        """
        True if the project has changed since the last sync such that
        another sync is required.
        """
        changes = ChangedEntityLocale.objects.filter(entity__resource__project=self)
        return changes.exists() or self.unsynced_locales

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

    @property
    def has_multi_locale_repositories(self):
        for repo in self.repositories.all():
            if repo.multi_locale:
                return True

        return False

    @property
    def has_single_repo(self):
        return self.repositories.count() == 1

    @cached_property
    def source_repository(self):
        """
        Returns an instance of repository which contains the path to source files.
        """
        if not self.has_single_repo:
            from pontoon.sync.vcs.models import VCSProject
            source_directories = VCSProject.SOURCE_DIR_SCORES.keys()

            for repo in self.repositories.all():
                last_directory = os.path.basename(os.path.normpath(urlparse(repo.url).path))
                if repo.source_repo or last_directory in source_directories:
                    return repo

        return self.repositories.first()

    def translation_repositories(self):
        """
        Returns a list of project repositories containing translations.
        """
        pks = [repo.pk for repo in self.repositories.all() if repo.is_translation_repository]
        return Repository.objects.filter(pk__in=pks)

    def get_latest_activity(self, locale=None):
        return ProjectLocale.get_latest_activity(self, locale)

    def get_chart(self, locale=None):
        return ProjectLocale.get_chart(self, locale)

    def aggregate_stats(self):
        TranslatedResource.objects.filter(
            resource__project=self,
            resource__entities__obsolete=False
        ).distinct().aggregate_stats(self)

    def parts_to_paths(self, paths):
        try:
            subpage = Subpage.objects.get(project=self, name__in=paths)
            return subpage.resources.values_list("path")
        except Subpage.DoesNotExist:
            return paths


class ProjectLocaleQuerySet(models.QuerySet):
    def available(self):
        """
        Available project locales belong to available projects.
        """
        return self.filter(project__disabled=False, project__resources__isnull=False).distinct()


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

    # ProjectLocale contains references to user groups that translate them.
    # Groups store respective permissions for users.
    translators_group = models.ForeignKey(
        Group,
        related_name='projectlocales',
        null=True,
        on_delete=models.SET_NULL
    )

    # Defines if locale has a translators group for the specific project.
    has_custom_translators = models.BooleanField(
        default=False,
    )

    objects = ProjectLocaleQuerySet.as_manager()

    class Meta:
        unique_together = ('project', 'locale')
        permissions = (
            ('can_translate_project_locale', 'Can add translations'),
        )

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
            latest_translation = self.latest_translation

        else:
            project = self if isinstance(self, Project) else extra
            locale = self if isinstance(self, Locale) else extra
            project_locale = utils.get_object_or_none(ProjectLocale, project=project, locale=locale)

            if project_locale is not None:
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
                'approved_share': round(obj.approved_strings / obj.total_strings * 100),
                'translated_share': round(obj.translated_strings / obj.total_strings * 100),
                'fuzzy_share': round(obj.fuzzy_strings / obj.total_strings * 100),
                'approved_percent': int(math.floor(obj.approved_strings / obj.total_strings * 100)),
            }

    def aggregate_stats(self):
        TranslatedResource.objects.filter(
            resource__project=self.project,
            resource__project__disabled=False,
            resource__entities__obsolete=False,
            locale=self.locale
        ).distinct().aggregate_stats(self)


class Repository(models.Model):
    """
    A remote VCS repository that stores resource files for a project.
    """
    TYPE_CHOICES = (
        ('git', 'Git'),
        ('hg', 'HG'),
        ('svn', 'SVN'),
    )

    project = models.ForeignKey(Project, related_name='repositories')
    type = models.CharField(
        max_length=255,
        default='git',
        choices=TYPE_CHOICES
    )
    url = models.CharField("URL", max_length=2000)
    branch = models.CharField("Branch", blank=True, max_length=2000)

    # TODO: We should be able to remove this once we have persistent storage
    permalink_prefix = models.CharField("Download prefix", max_length=2000, help_text="""
        A URL prefix for downloading localized files. For GitHub repositories,
        select any localized file on GitHub, click Raw and replace locale code
        and the following bits in the URL with `{locale_code}`.
    """)

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

    def __repr__(self):
        repo_kind = 'Repository'
        if self.source_repo:
            repo_kind = 'SourceRepository'
        return "<{}[{}:{}:{}]".format(repo_kind, self.pk, self.type, self.url)

    @property
    def multi_locale(self):
        """
        Checks if url contains locale code variable. System will replace
        this variable by the locale codes of all enabled locales for the
        project during pulls and commits.
        """
        return '{locale_code}' in self.url

    @property
    def is_source_repository(self):
        """
        Returns true if repository contains source strings.
        """
        return self == self.project.source_repository

    @property
    def is_translation_repository(self):
        """
        Returns true if repository contains translations.
        """
        return self.project.has_single_repo or not self.is_source_repository

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

    def pull(self, skip_locales=None):
        """
        Pull changes from VCS. Returns the revision(s) of the repo after
        pulling.
        """
        if not self.multi_locale:
            update_from_vcs(self.type, self.url, self.checkout_path, self.branch)
            return {
                'single_locale': get_revision(self.type, self.checkout_path)
            }
        else:
            current_revisions = {}
            skip_locales = skip_locales or []
            for locale in self.project.locales.exclude(code__in=skip_locales):
                repo_type = self.type
                url = self.locale_url(locale)
                checkout_path = self.locale_checkout_path(locale)
                repo_branch = self.branch

                try:
                    update_from_vcs(repo_type, url, checkout_path, repo_branch)
                    current_revisions[locale.code] = get_revision(repo_type, checkout_path)
                except PullFromRepositoryException as e:
                    log.error('%s Pull Error for %s: %s' % (repo_type.upper(), url, e))

            return current_revisions

    def commit(self, message, author, path):
        """Commit changes to VCS."""
        # For multi-locale repos, figure out which sub-repo corresponds
        # to the given path.
        url = self.url
        if self.multi_locale:
            url = self.url_for_path(path)

        return commit_to_vcs(self.type, path, message, author, self.branch, url)

    """
    Set last_synced_revisions to a dictionary of revisions
    that are currently downloaded on the disk.
    """
    def set_last_synced_revisions(self, locales=None):
        current_revisions = {}

        if self.multi_locale:
            for locale in self.project.locales.all():
                if locales is not None and locale not in locales:
                    revision = self.last_synced_revisions.get(locale.code)
                else:
                    revision = get_revision(
                        self.type,
                        self.locale_checkout_path(locale)
                    )

                if revision:
                    current_revisions[locale.code] = revision

        else:
            current_revisions['single_locale'] = get_revision(
                self.type,
                self.checkout_path
            )

        self.last_synced_revisions = current_revisions
        self.save(update_fields=['last_synced_revisions'])

    """
    Get revision from the last_synced_revisions dictionary if exists.
    """
    def get_last_synced_revisions(self, locale=None):
        if self.last_synced_revisions:
            key = locale or 'single_locale'
            return self.last_synced_revisions.get(key)
        else:
            return None

    class Meta:
        unique_together = ('project', 'url')
        ordering = ['id']


class ResourceQuerySet(models.QuerySet):
    def asymmetric(self):
        return self.filter(format__in=Resource.ASYMMETRIC_FORMATS)

    """
    List of paths to remove translations of obsolete entities from
    """
    def obsolete_entities_paths(self, obsolete_vcs_entities):
        return self.filter(
            entities__pk__in=obsolete_vcs_entities
        ).asymmetric().values_list('path', flat=True).distinct()


class Resource(models.Model):
    project = models.ForeignKey(Project, related_name='resources')
    path = models.TextField()  # Path to localization file
    total_strings = models.PositiveIntegerField(default=0)

    # Format
    FORMAT_CHOICES = (
        ('po', 'po'),
        ('xliff', 'xliff'),
        ('xlf', 'xliff'),
        ('properties', 'properties'),
        ('dtd', 'dtd'),
        ('inc', 'inc'),
        ('ini', 'ini'),
        ('lang', 'lang'),
        ('ftl', 'ftl'),
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

    ASYMMETRIC_FORMATS = ('dtd', 'properties', 'ini', 'inc', 'ftl')

    objects = ResourceQuerySet.as_manager()

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
        if path_format == 'pot':
            return 'po'
        elif path_format == 'xlf':
            return 'xliff'
        else:
            return path_format


class Subpage(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=128)
    url = models.URLField("URL", blank=True)  # Firefox OS Hack
    resources = models.ManyToManyField(Resource, blank=True)

    def __unicode__(self):
        return self.name


class EntityQuerySet(models.QuerySet):
    """
    Queryset provides a set of additional methods that should allow us to filter entities.
    """
    user_entity_filters = ('missing', 'fuzzy', 'suggested', 'translated')
    user_extra_filters = ('has-suggestions', 'unchanged')

    def filter_statuses(self, locale, statuses):
        sanitized_statuses = filter(lambda s: s in self.user_entity_filters, statuses)
        if sanitized_statuses:
            return reduce(lambda x, y: x | y, [getattr(Entity.objects, s)() for s in sanitized_statuses])
        return Q()

    def filter_extra(self, locale, extra):
        sanitized_extras = filter(lambda f: f in self.user_extra_filters, extra)

        if sanitized_extras:
            return reduce(lambda x, y: x | y, [getattr(Entity.objects, s.replace('-', '_'))() for s in sanitized_extras])
        return Q()

    def with_status_counts(self, locale):
        """
        Helper method that returns a set with annotation of following fields:
            * approved_count - a number of approved translations in the entity.
            * fuzzy_count - a number of fuzzy translations in the antity
            * suggested_count - a number of translations assigned do the entity.
            * expected_count - a number of translations that should cover entity.
            * unchanged_count - a number of translations that have the same string as the entity.
        """
        return self.annotate(
            approved_count=Sum(
                Case(
                    When(
                        Q(translation__approved=True, translation__fuzzy=False, translation__locale=locale), then=1
                    ), output_field=models.IntegerField(), default=0
                )
            ),
            fuzzy_count=Sum(
                Case(
                    When(
                        Q(translation__fuzzy=True, translation__approved=False, translation__locale=locale), then=1
                    ), output_field=models.IntegerField(), default=0
                )
            ),
            suggested_count=Sum(
                Case(
                    When(
                        Q(translation__locale=locale, translation__approved=False, translation__fuzzy=False), then=1
                    ), output_field=models.IntegerField(), default=0
                )
            ),
            expected_count=Case(
                When(
                    Q(string_plural__isnull=True) | Q(string_plural=""), then=1
                ), output_field=models.IntegerField(), default=locale.nplurals
            ),
            unchanged_count=Sum(
                Case(
                    When(
                    Q(translation__locale=locale, translation__string=F('string')) |\
                    Q(translation__locale=locale, translation__plural_form__gt=-1,
                        translation__plural_form__isnull=False, translation__string=F('string_plural')), then=1
                    ), output_field=models.IntegerField(), default=0
                )
            )
        )

    def missing(self):
        return Q(approved_count__lt=F('expected_count')) & Q(fuzzy_count__lt=F('expected_count')) & Q(suggested_count__lt=F('expected_count'))

    def fuzzy(self):
        return Q(fuzzy_count=F('expected_count')) & ~Q(approved_count=F('expected_count'))

    def suggested(self):
        return Q(suggested_count__gt=0) & ~Q(fuzzy_count=F('expected_count')) & ~Q(approved_count=F('expected_count'))

    def translated(self):
        return Q(approved_count=F('expected_count'))

    def has_suggestions(self):
        return Q(suggested_count__gt=0)

    def unchanged(self):
        return Q(unchanged_count=F('expected_count'))

    def authored_by(self, locale, emails):
        def is_email(email):
            """
            Validate if user passed a real email.
            """
            try:
                validate_email(email)
                return True
            except ValidationError:
                return False

        sanitized_emails = filter(is_email, emails)
        if sanitized_emails:
            return Q(translation__locale=locale, translation__user__email__in=sanitized_emails)
        return Q()

    def between_time_interval(self, locale, start, end):
        return Q(translation__locale=locale, translation__date__range=(start, end))

    def prefetch_resources_translations(self, locale):
        """
        Prefetch resources and translations for given locale.
        """
        return self.prefetch_related(
            'resource',
            Prefetch(
                'translation_set',
                queryset=Translation.objects.filter(locale=locale),
                to_attr='fetched_translations'
            )
        )


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
    objects = EntityQuerySet.as_manager()

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
    def for_project_locale(self, project, locale, paths=None, statuses=None,
        search=None, exclude=None, extra=None, time=None, authors=None):
        """Get project entities with locale translations."""

        # Time & authors filters have to be applied before the aggregation
        # (with_status_counts) and the status & extra filters to avoid
        # unnecessary joins causing performance and logic issues.
        pre_filters = []
        post_filters = []

        if time:
            if re.match('^[0-9]{12}-[0-9]{12}$', time):
                start, end = utils.parse_time_interval(time)
                pre_filters.append(Entity.objects.between_time_interval(locale, start, end))
            else:
                raise ValueError(time)

        if authors:
            pre_filters.append(Entity.objects.authored_by(locale, authors.split(',')))

        if pre_filters:
            entities = Entity.objects.filter(pk__in=Entity.objects.filter(Q(*pre_filters)))
        else:
            entities = Entity.objects.all()

        if statuses:
            post_filters.append(Entity.objects.filter_statuses(locale, statuses.split(',')))

        if extra:
            post_filters.append(Entity.objects.filter_extra(locale, extra.split(',')))

        if post_filters:
            entities = entities.with_status_counts(locale).filter(Q(*post_filters))

        entities = entities.filter(
            resource__project=project,
            resource__translatedresources__locale=locale,
            obsolete=False
        )

        # Filter by path
        if paths:
            paths = project.parts_to_paths(paths)
            entities = entities.filter(resource__path__in=paths)

        # Filter by search parameters
        if search:
            search_query = Q(**{'string__icontains': search})
            search_query |= Q(**{'string_plural__icontains': search})
            search_query |= Q(**{'translation__string__icontains': search, 'translation__locale': locale})
            search_query |= Q(**{'comment__icontains': search})
            search_query |= Q(**{'key__icontains': search})
            # https://docs.djangoproject.com/en/dev/topics/db/queries/#spanning-multi-valued-relationships
            entities = Entity.objects.filter(search_query, pk__in=entities).distinct()

        entities = entities.prefetch_resources_translations(locale)

        if exclude:
            entities = entities.exclude(pk__in=exclude)

        return entities.distinct().order_by('resource__path', 'order')

    @classmethod
    def map_entities(cls, locale, entities, visible_entities=None):
        entities_array = []
        visible_entities = visible_entities or []

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
                'key': entity.cleaned_key,
                'path': entity.resource.path,
                'format': entity.resource.format,
                'comment': entity.comment,
                'order': entity.order,
                'source': entity.source,
                'obsolete': entity.obsolete,
                'translation': translation_array,
                'visible': False if entity.pk not in visible_entities or not visible_entities
                                 else True
            })

        return entities_array


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


class TranslationNotAllowed(Exception):
    """Raised when submitted Translation cannot be saved."""


class TranslationQuerySet(models.QuerySet):
    def translated_resources(self, locale):
        return TranslatedResource.objects.filter(
            resource__entities__translation__in=self,
            locale=locale
        ).distinct()

    def find_and_replace(self, find, replace, user):
        # Find translations
        translations = self.filter(string__contains=find)

        if translations.count() == 0:
            return translations

        # Empty translations produced by replace might not be always allowed
        forbidden = (
            translations.filter(string=find)
            .exclude(entity__resource__format__in=Resource.ASYMMETRIC_FORMATS)
        )
        if not replace and forbidden.exists():
            raise Translation.NotAllowed

        # Create translations' clones and replace strings
        now = timezone.now()
        translations_to_create = []
        for translation in translations:
            translation.pk = None  # Create new translation
            translation.string = translation.string.replace(find, replace)
            translation.user = translation.approved_user = user
            translation.date = translation.approved_date = now
            translation.approved = True
            translation.fuzzy = False
            translations_to_create.append(translation)

        # Unapprove old translations
        translations.update(approved=False, approved_user=None, approved_date=None)

        # Create new translations
        Translation.objects.bulk_create(translations_to_create)
        return translations

    def authors(self):
        """
        Return a QuerySet of translation authors.
        """
        return (
            User.objects
                .filter(translation__in=self)
                .annotate(translation_count=Count('id'))
                .order_by('translation_count')
        )

    def counts_per_minute(self):
        """
        Return a dictionary of translation counts per minute.
        """
        translations = (
            self
            .extra({'minute': "date_trunc('minute', date)"})
            .order_by('minute')
            .values('minute')
            .annotate(count=Count('id'))
        )

        data = []
        for period in translations:
            data.append([
                utils.convert_to_unix_time(period['minute']),
                period['count']
            ])
        return data


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
        User, related_name='approved_translations', null=True, blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)

    unapproved_user = models.ForeignKey(
        User, related_name='unapproved_translations', null=True, blank=True)
    unapproved_date = models.DateTimeField(null=True, blank=True)
    fuzzy = models.BooleanField(default=False)

    objects = TranslationQuerySet.as_manager()
    NotAllowed = TranslationNotAllowed

    # extra stores data that we want to save for the specific format
    # this translation is stored in, but that we otherwise don't care
    # about.
    extra = JSONField(default=extra_default)

    @classmethod
    def for_locale_project_paths(self, locale, project, paths):
        """
        Return Translation QuerySet for given locale, project and paths.
        """
        translations = Translation.objects.filter(
            entity__resource__project=project,
            entity__obsolete=False,
            locale=locale
        )

        if paths:
            paths = project.parts_to_paths(paths)
            translations = translations.filter(entity__resource__path__in=paths)

        return translations

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

    def unapprove(self, user, stats=True):
        """
        Unapprove translation.
        """
        self.approved = False
        self.unapproved_user = user
        self.unapproved_date = timezone.now()
        self.save()

        TranslatedResource.objects.get(resource=self.entity.resource, locale=self.locale).calculate_stats()
        TranslationMemoryEntry.objects.filter(translation=self).delete()
        self.entity.mark_changed(self.locale)

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
    def aggregated_stats(self):
        return self.aggregate(
            total=Sum('resource__total_strings'),
            approved=Sum('approved_strings'),
            translated=Sum('translated_strings'),
            fuzzy=Sum('fuzzy_strings')
        )

    def aggregate_stats(self, instance):
        aggregated_stats = self.aggregated_stats()

        instance.total_strings = aggregated_stats['total'] or 0
        instance.approved_strings = aggregated_stats['approved'] or 0
        instance.translated_strings = aggregated_stats['translated'] or 0
        instance.fuzzy_strings = aggregated_stats['fuzzy'] or 0

        instance.save(update_fields=[
            'total_strings', 'approved_strings',
            'fuzzy_strings', 'translated_strings'
        ])

    def stats(self, project, paths, locale):
        """
        Returns statistics for the given project, paths and locale.
        """
        return self.filter(
            resource__project=project,
            resource__path__in=paths,
            locale=locale).aggregated_stats()


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

    def calculate_stats(self, save=True):
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
        missing = 0
        for e in translated_entities.exclude(string_plural=''):
            translations = Translation.objects.filter(entity=e, locale=locale)
            plural_approved_count = translations.filter(approved=True).count()
            plural_fuzzy_count = translations.filter(fuzzy=True).count()
            plural_translated_count = translations.values('plural_form').distinct().count()

            if plural_approved_count == nplurals:
                approved += 1
            elif plural_fuzzy_count == nplurals:
                fuzzy += 1
            elif plural_translated_count < nplurals:
                missing += 1

        translated = max(translated_entities.count() - approved - fuzzy - missing, 0)

        if not save:
            self.total_strings = resource.total_strings
            self.approved_strings = approved
            self.fuzzy_strings = fuzzy
            self.translated_strings = translated

            return False

        # Calculate diffs to reduce DB queries
        total_strings_diff = resource.total_strings - self.total_strings
        approved_strings_diff = approved - self.approved_strings
        fuzzy_strings_diff = fuzzy - self.fuzzy_strings
        translated_strings_diff = translated - self.translated_strings

        # Translated Resource
        self.adjust_stats(
            total_strings_diff, approved_strings_diff,
            fuzzy_strings_diff, translated_strings_diff
        )

        # Project
        project = resource.project
        project.adjust_stats(
            total_strings_diff, approved_strings_diff,
            fuzzy_strings_diff, translated_strings_diff
        )

        # Locale
        locale.adjust_stats(
            total_strings_diff, approved_strings_diff,
            fuzzy_strings_diff, translated_strings_diff
        )

        # ProjectLocale
        project_locale = utils.get_object_or_none(
            ProjectLocale,
            project=project,
            locale=locale
        )
        if project_locale:
            project_locale.adjust_stats(
                total_strings_diff, approved_strings_diff,
                fuzzy_strings_diff, translated_strings_diff
            )
