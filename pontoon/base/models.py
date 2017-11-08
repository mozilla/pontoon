from __future__ import unicode_literals
from __future__ import division

import hashlib
import json
import logging
import math
import operator
import os.path
import re

from collections import defaultdict
from dirtyfields import DirtyFieldsMixin
from six.moves import reduce
from six.moves.urllib.parse import (urlencode, urlparse)

from django.conf import settings
from django.contrib.auth.models import User, Group, UserManager
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.db import models
from django.db.models import Count, F, Prefetch, Q, Sum
from django.templatetags.static import static
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
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
from pontoon.db import IContainsCollate  # noqa
from pontoon.sync import KEY_SEPARATOR


log = logging.getLogger(__name__)


def combine_entity_filters(entities, filter_choices, filters, *args):
    """Return a combination of filters to apply to an Entity object.

    The content for each filter is defined in the EntityQuerySet helper class, using methods
    that have the same name as the filter. Each subset of filters is combined with the others
    with the OR operator.

    :arg EntityQuerySet entities: an Entity query set object with predefined filters
    :arg list filter_choices: list of valid choices, used to sanitize the content of `filters`
    :arg list filters: the filters to get and combine
    :arg *args: arguments that will be passed to the filter methods of the EntityQuerySet class

    :returns: a combination of django ORM Q() objects containing all the required filters

    """
    # We first sanitize the list sent by the user and restrict it to only values we accept.
    sanitized_filters = filter(lambda s: s in filter_choices, filters)

    filters = [Q()]
    for filter_name in sanitized_filters:
        filters.append(getattr(entities, filter_name.replace('-', '_'))(*args))

    # Combine all generated filters with an OR operator.
    # `operator.ior` is the pipe (|) Python operator, which turns into a logical OR
    # when used between django ORM query objects.
    return reduce(operator.ior, filters)


class UserTranslationsManager(UserManager):
    def with_translation_counts(self, start_date=None, query_filters=None, limit=100):
        """
        Returns contributors list, sorted by count of their translations. Every user instance has
        the following properties:
        * translations_count
        * translations_approved_count
        * translations_unapproved_count
        * translations_needs_work_count
        * user_role

        All counts will be returned from start_date to now().
        :param date start_date: start date for translations.
        :param django.db.models.Q query_filters: filters contributors by given query_filters.
        :param int limit: limit results to this number.
        """

        # Collect data for faster user stats calculation.
        user_stats = {}
        translations = Translation.objects.exclude(user=None)

        if start_date:
            translations = translations.filter(date__gte=start_date)
        if query_filters:
            translations = translations.filter(query_filters)

        translations = (
            translations
            .values('user', 'approved', 'fuzzy')
            .annotate(count=Count('user'))
        )

        for translation in translations:
            count = translation['count']
            user = translation['user']

            if translation['approved']:
                status = 'approved'
            elif translation['fuzzy']:
                status = 'fuzzy'
            else:
                status = 'suggested'

            if user not in user_stats:
                user_stats[user] = {
                    'total': 0,
                    'approved': 0,
                    'suggested': 0,
                    'fuzzy': 0,
                }

            user_stats[user]['total'] += count
            user_stats[user][status] += count

        # Collect data for faster user role detection.
        managers = defaultdict(set)
        translators = defaultdict(set)

        locales = Locale.objects.prefetch_related(
            Prefetch(
                'managers_group__user_set',
                to_attr='fetched_managers'
            ),
            Prefetch(
                'translators_group__user_set',
                to_attr='fetched_translators'
            )
        )

        for locale in locales:
            for user in locale.managers_group.fetched_managers:
                managers[user].add(locale.code)
            for user in locale.translators_group.fetched_translators:
                translators[user].add(locale.code)

        # Assign properties to user objects.
        contributors = self.filter(pk__in=user_stats.keys())

        for contributor in contributors:
            user = user_stats[contributor.pk]
            contributor.translations_count = user['total']
            contributor.translations_approved_count = user['approved']
            contributor.translations_unapproved_count = user['suggested']
            contributor.translations_needs_work_count = user['fuzzy']
            contributor.user_role = contributor.role(managers, translators)

        return sorted(contributors, key=lambda x: -x.translations_count)[:100]


class UserCustomManager(UserManager):
    """
    Django migrations is able to migrate managers, and throws an error if we directly call
    UserManager.from_queryset(): Please note that you need to inherit from managers you dynamically
    generated with 'from_queryset()'.
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
            example = daily.order_by('-pk').first()

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
    return reverse('pontoon.contributors.contributor.username', kwargs={
        'username': self.username
    })


def user_gravatar_url(self, size):
    email = hashlib.md5(self.email.lower()).hexdigest()
    data = {'s': str(size)}

    if not settings.DEBUG:
        append = '_big' if size > 44 else ''
        data['d'] = settings.SITE_URL + static('img/anon' + append + '.jpg')

    return '//www.gravatar.com/avatar/{email}?{data}'.format(
        email=email, data=urlencode(data))


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
    return Translation.objects.filter(user=self)


@property
def top_contributed_locale(self):
    """Locale the user has made the most contributions to."""
    try:
        return (
            self.translation_set
                .values('locale__code')
                .annotate(total=Count('locale__code'))
                .distinct()
                .order_by('-total')
                .first()['locale__code']
        )
    except TypeError:
        # This error is raised if `top_contribution` is null. That happens if the user
        # has never contributed to any locales.
        return None


def can_translate(self, locale, project):
    """Check if user has suitable permissions to translate in given locale or project/locale."""

    # Locale managers can translate all projects
    if locale.code in self.managed_locales:
        return True

    project_locale = ProjectLocale.objects.get(project=project, locale=locale)
    if project_locale.has_custom_translators:
        return self.has_perm('base.can_translate_project_locale', project_locale)

    return self.has_perm('base.can_translate_locale', locale)


@property
def menu_notifications(self):
    """A list of notifications to display in the notifications menu."""
    unread_count = self.notifications.unread().count()
    count = settings.NOTIFICATIONS_MAX_COUNT

    if unread_count > count:
        count = unread_count

    return self.notifications.prefetch_related('actor', 'target')[:count]


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
User.add_to_class('top_contributed_locale', top_contributed_locale)
User.add_to_class('can_translate', can_translate)
User.add_to_class('menu_notifications', menu_notifications)


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User, related_name='profile')
    # Other fields here.
    quality_checks = models.BooleanField(default=True)
    force_suggestions = models.BooleanField(default=False)

    # Used to redirect a user to a custom team page.
    custom_homepage = models.CharField(max_length=10, blank=True, null=True)

    # Defines the order of locales displayed in locale tab.
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

    @classmethod
    def get_stats_sum(cls, qs):
        """
        Get sum of stats for all items in the queryset.
        """
        return cls(
            total_strings=sum(x.total_strings for x in qs),
            approved_strings=sum(x.approved_strings for x in qs),
            translated_strings=sum(x.translated_strings for x in qs),
            fuzzy_strings=sum(x.fuzzy_strings for x in qs),
        )

    @classmethod
    def get_top_instances(cls, qs):
        """
        Get top instances in the queryset.
        """
        return {
            'most_strings': sorted(qs, key=lambda x: x.total_strings)[-1],
            'most_translations': sorted(qs, key=lambda x: x.approved_strings)[-1],
            'most_suggestions': sorted(qs, key=lambda x: x.translated_strings)[-1],
            'most_missing': sorted(
                qs,
                key=lambda x:
                    x.total_strings - x.approved_strings - x.translated_strings - x.fuzzy_strings
            )[-1],
        }

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

    @property
    def missing_strings(self):
        return (
            self.total_strings - self.translated_strings -
            self.approved_strings - self.fuzzy_strings
        )

    @property
    def complete(self):
        return self.total_strings == self.approved_strings


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
        return self.filter(pk__in=TranslatedResource.objects.values_list('locale', flat=True))

    def prefetch_project_locale(self, project):
        """
        Prefetch ProjectLocale and latest translation data for given project.
        """
        return self.prefetch_related(
            Prefetch(
                'project_locale',
                queryset=(
                    ProjectLocale.objects.filter(project=project)
                    .prefetch_related('latest_translation__user')
                ),
                to_attr='fetched_project_locale'
            )
        )

    def get_stats_sum(self):
        """
        Get sum of stats for all items in the queryset.
        """
        return AggregatedStats.get_stats_sum(self)

    def get_top_instances(self):
        """
        Get top instances in the queryset.
        """
        return AggregatedStats.get_top_instances(self)


@python_2_unicode_compatible
class Locale(AggregatedStats):
    code = models.CharField(max_length=20, unique=True)

    # Codes related to Microsoft products.
    ms_translator_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="""
        Microsoft Translator maintains its own list of
        <a href="https://msdn.microsoft.com/en-us/library/hh456380.aspx">supported locales</a>.
        Choose a locale from that list that's is the closest match or leave it blank to disable
        support for Microsoft Translator.
        """
    )
    ms_terminology_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="""
        Microsoft Terminology uses language codes that include both the language and
        the country/region. Chose a matching locale from the list or leave blank to disable support
        for Microsoft terminology:

        af-za, am-et, ar-dz, ar-eg, ar-sa, as-in, az-latn-az, be-by, bg-bg, bn-bd, bn-in,
        bs-cyrl-ba, bs-latn-ba, ca-es, ca-es-valencia, chr-cher-us, cs-cz, cy-gb, da-dk, de-at,
        de-ch, de-de, el-gr, en-au, en-ca, en-gb, en-hk, en-ie, en-in, en-my, en-ng, en-nz, en-ph,
        en-pk, en-sg, en-tt, en-us, en-za, es-ar, es-bo, es-cl, es-co, es-cr, es-do, es-ec, es-es,
        es-gt, es-hn, es-mx, es-ni, es-pa, es-pe, es-pr, es-py, es-sv, es-us, es-uy, es-ve, et-ee,
        eu-es, fa-ir, fi-fi, fil-ph, fo-fo, fr-be, fr-ca, fr-ch, fr-dz, fr-fr, fr-ma, fr-tn,
        fuc-latn-sn, ga-ie, gd-gb, gl-es, gu-in, guc-ve, ha-latn-ng, he-il, hi-in, hr-hr, hu-hu,
        hy-am, id-id, ig-ng, is-is, it-ch, it-it, iu-latn-ca, ja-jp, ka-ge, kk-kz, km-kh, kn-in,
        ko-kr, kok-in, ku-arab-iq, ky-kg, lb-lu, lo-la, lt-lt, lv-lv, mi-nz, mk-mk, ml-in, mn-mn,
        mr-in, ms-bn, ms-my, mt-mt, my-mm, nb-no, ne-np, nl-be, nl-nl, nn-no, nso-za, or-in,
        pa-arab-pk, pa-in, pl-pl, prs-af, ps-af, pt-br, pt-pt, quc-latn-gt, quz-pe, ro-md, ro-ro,
        ru-kz, ru-ru, rw-rw, sd-arab-pk, si-lk, sk-sk, sl-si, sp-xl, sq-al, sr-cyrl-ba, sr-cyrl-rs,
        sr-latn-me, sr-latn-rs, sv-se, sw-ke, ta-in, te-in, tg-cyrl-tj, th-th, ti-et, tk-tm, tl-ph,
        tn-za, tr-tr, tt-ru, ug-cn, uk-ua, ur-pk, uz-cyrl-uz, uz-latn-uz, vi-vn, wo-sn, xh-za,
        yo-ng, zh-cn, zh-hk, zh-sg, zh-tw, zu-za
        """
    )

    transvision = models.BooleanField(default=False, help_text="""
        Enable Machinery suggestions from <a href="https://transvision.mozfr.org/">Transvision</a>.
        Only useful for locales that don't translate all projects on Pontoon.
    """)

    db_collation = models.CharField(
        max_length=20,
        blank=True,
        help_text="""
        Some of locales require to use different database collation than default ('en_US').

        <strong>Use with caution, because it may brake the search for this locale.</strong>
        """,
    )

    name = models.CharField(max_length=128)
    plural_rule = models.CharField(
        max_length=128,
        blank=True,
        help_text="""
        Plural rule is part of the plurals header in
        <a href="https://www.gnu.org/software/gettext/manual/gettext.html#Plural-forms">
        Gettext PO files
        </a>,
        that follows the <i>plural=</i> string, without the trailing semicolon.
        E.g. (n != 1)
        """
    )

    # Locale contains references to user groups that translate or manage them.
    # Groups store respective permissions for users.
    translators_group = models.ForeignKey(
        Group,
        related_name='translated_locales',
        null=True,
        on_delete=models.SET_NULL
    )
    managers_group = models.ForeignKey(
        Group,
        related_name='managed_locales',
        null=True,
        on_delete=models.SET_NULL
    )

    # CLDR Plurals
    CLDR_PLURALS = (
        (0, 'zero'),
        (1, 'one'),
        (2, 'two'),
        (3, 'few'),
        (4, 'many'),
        (5, 'other'),
    )

    cldr_plurals = models.CharField(
        "CLDR Plurals",
        blank=True,
        max_length=11,
        validators=[validate_cldr],
        help_text="""
        A comma separated list of
        <a href="http://www.unicode.org/cldr/charts/dev/supplemental/language_plural_rules.html">
        CLDR plural rules</a>, where 0 represents zero, 1 one, 2 two, 3 few, 4 many, and 5 other.
        E.g. 1,5
        """
    )

    script = models.CharField(
        max_length=128,
        default='Latin',
        help_text="""
        The script used by this locale. Find it in
        <a
        href="http://www.unicode.org/cldr/charts/latest/supplemental/languages_and_scripts.html">
        CLDR Languages and Scripts</a>.
        """
    )

    # Writing direction
    DIRECTION = (
        ('ltr', 'left-to-right'),
        ('rtl', 'right-to-left'),
    )
    direction = models.CharField(
        max_length=3,
        default='ltr',
        choices=DIRECTION,
        help_text="""
        Writing direction of the script. Set to "right-to-left" if "rtl" value
        for the locale script is set to "YES" in
        <a href="https://github.com/unicode-cldr/cldr-core/blob/master/scriptMetadata.json">
        CLDR scriptMetadata.json</a>.
        """
    )

    population = models.PositiveIntegerField(
        default=0,
        help_text="""
        Number of native speakers. Find locale code in CLDR territoryInfo.json:
        https://github.com/unicode-cldr/cldr-core/blob/master/supplemental/territoryInfo.json
        and multiply its "_populationPercent" with the territory "_population".
        Repeat if multiple occurrences of locale code exist and sum products.
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

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            'code': self.code,
            'name': self.name,
            'nplurals': self.nplurals,
            'plural_rule': self.plural_rule,
            'cldr_plurals': self.cldr_id_list(),
            'direction': self.direction,
            'script': self.script,
            'ms_translator_code': self.ms_translator_code,
            'ms_terminology_code': self.ms_terminology_code,
            'transvision': json.dumps(self.transvision),
        }

    def cldr_id_list(self):
        if self.cldr_plurals == '':
            return [1]
        else:
            return map(int, self.cldr_plurals.split(','))

    def cldr_plurals_list(self):
        return ', '.join(
            map(Locale.cldr_id_to_plural, self.cldr_id_list())
        )

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
        return len(self.cldr_id_list())

    @property
    def projects_permissions(self):
        """
        List of tuples that contain informations required by the locale permissions view.

        A row contains:
            id  - id of project locale
            slug - slug of the project
            name - name of the project
            all_users - (id, first_name, email) users that aren't translators of given project
                locale.
            translators - (id, first_name, email) translators assigned to a project locale.
            contributors - (id, first_name, email) people who contributed for a project in
                current locale.
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
            (
                User.objects
                .filter(groups__pk__in=[
                    project_locale['translators_group__pk']
                    for project_locale in project_locales
                ])
                .exclude(email='')
                .prefetch_related('groups')
                .values('id', 'first_name', 'email', 'groups__pk')
                .distinct()
            ),
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
        ) + ['all-projects']

    def get_plural_index(self, cldr_plural):
        """Returns plural index for given cldr name."""
        cldr_id = Locale.cldr_plural_to_id(cldr_plural)
        return self.cldr_id_list().index(cldr_id)

    def get_relative_cldr_plural(self, plural_id):
        """
        Every locale supports a subset (a list) of The CLDR Plurals forms.
        In code, we store their relative position.
        """
        return Locale.cldr_id_to_plural(self.cldr_id_list()[plural_id])

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

        if project.slug != 'all-projects':
            pages = project.subpage_set.all()
        else:
            pages = Subpage.objects.filter(project__in=self.project_set.all())

        translatedresources = TranslatedResource.objects.filter(
            resource__entities__obsolete=False,
            locale=self
        )
        if project.slug != 'all-projects':
            translatedresources = translatedresources.filter(resource__project=project)
        translatedresources = translatedresources.distinct()

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
            if pages[0].resources.exists() or project.slug == 'all-projects':
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
                        translated_strings=F(
                            'project__resources__translatedresources__translated_strings'
                        ),
                        approved_strings=F(
                            'project__resources__translatedresources__approved_strings'
                        )
                    )
                )

            # List resources not bound to subpages as regular resources
            bound_resources = locale_pages.values_list('resources', flat=True)
            unbound_tr = translatedresources.exclude(resource__pk__in=bound_resources)
            unbound_details = get_details(unbound_tr.annotate(
                title=F('resource__path'),
                url=F('resource__project__url')
            ))

        if project.slug != 'all-projects':
            stats = ProjectLocale.objects.get(project=project, locale=self)
        else:
            stats = self

        all_paths = translatedresources.values_list("resource__path", flat=True)

        details_list = list(details) + list(unbound_details)
        details_list.append({
            'title': 'all-resources',
            'resource__path': list(all_paths),
            'resource__total_strings': stats.total_strings,
            'fuzzy_strings': stats.fuzzy_strings,
            'translated_strings': stats.translated_strings,
            'approved_strings': stats.approved_strings,
        })

        return details_list


class ProjectQuerySet(models.QuerySet):
    def available(self):
        """
        Available projects are not disabled and have at least one
        resource defined.
        """
        return self.filter(disabled=False, resources__isnull=False).distinct()

    def prefetch_project_locale(self, locale):
        """
        Prefetch ProjectLocale and latest translation data for given locale.
        """
        return self.prefetch_related(
            Prefetch(
                'project_locale',
                queryset=(
                    ProjectLocale.objects.filter(locale=locale)
                    .prefetch_related('latest_translation__user')
                ),
                to_attr='fetched_project_locale'
            )
        )

    def get_stats_sum(self):
        """
        Get sum of stats for all items in the queryset.
        """
        return AggregatedStats.get_stats_sum(self)

    def get_top_instances(self):
        """
        Get top instances in the queryset.
        """
        return AggregatedStats.get_top_instances(self)


PRIORITY_CHOICES = (
    (1, 'Lowest'),
    (2, 'Low'),
    (3, 'Normal'),
    (4, 'High'),
    (5, 'Highest'),
)


@python_2_unicode_compatible
class Project(AggregatedStats):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True)
    locales = models.ManyToManyField(Locale, through='ProjectLocale')

    can_be_requested = models.BooleanField(default=True, help_text="""
        Allow localizers to request the project for their team.
    """)

    disabled = models.BooleanField(default=False, help_text="""
        Hide project from the UI and only keep it accessible from the admin.
        Disable the project instead of deleting it to keep translation memory
        and attributions.
    """)

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

    # Project info
    info = models.TextField("Project info", blank=True)
    deadline = models.DateField(blank=True, null=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=1)
    contact = models.ForeignKey(User, null=True, blank=True, related_name="contact_for", help_text="""
        L10n driver in charge of the project
    """)
    admin_notes = models.TextField(blank=True, help_text="""
        Notes only visible in Administration
    """)

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
            ("can_manage_project", "Can manage project"),
        )

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            'pk': self.pk,
            'name': self.name,
            'slug': self.slug,
            'info': self.info,
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

    def changed_resources(self, now):
        """
        Returns a map of resource paths and their locales
        that where changed from the last sync.
        """
        resources = defaultdict(set)
        changes = (
            ChangedEntityLocale.objects
            .filter(entity__resource__project=self, when__lte=now)
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


@python_2_unicode_compatible
class ExternalResource(models.Model):
    """
    Represents links to external project resources like staging websites,
    production websites, development builds, production builds, screenshots,
    langpacks, etc. or team resources like style guides, dictionaries,
    glossaries, etc.
    Has no relation to the Resource class.
    """
    locale = models.ForeignKey(Locale, blank=True, null=True)
    project = models.ForeignKey(Project, blank=True, null=True)
    name = models.CharField(max_length=32)
    url = models.URLField("URL", blank=True)

    def __str__(self):
        return self.name


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

        if getattr(self, 'fetched_project_locale', None):
            if self.fetched_project_locale:
                latest_translation = self.fetched_project_locale[0].latest_translation

        elif extra is None:
            latest_translation = self.latest_translation

        else:
            project = self if isinstance(self, Project) else extra
            locale = self if isinstance(self, Locale) else extra
            project_locale = utils.get_object_or_none(
                ProjectLocale, project=project, locale=locale
            )

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

        if getattr(self, 'fetched_project_locale', None):
            if self.fetched_project_locale:
                chart = cls.get_chart_dict(self.fetched_project_locale[0])

        elif extra is None:
            chart = cls.get_chart_dict(self)

        else:
            project = self if isinstance(self, Project) else extra
            locale = self if isinstance(self, Locale) else extra
            project_locale = utils.get_object_or_none(
                ProjectLocale, project=project, locale=locale
            )

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
                'approved_percent': int(
                    math.floor(obj.approved_strings / obj.total_strings * 100)
                ),
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

    website = models.URLField("Public Repository Website", blank=True, max_length=2000)

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

    @cached_property
    def api_config(self):
        """
        Repository API configuration consists of:
        - Endpoint: A URL pattern to get repository metadata from. Used during sync for faster
          retrieval of latest commit hashes in combination with the Key.
          Supports {locale_code} wildcard.
        - Key: A string used to retrieve the latest commit hash from the JSON response.
        """
        url = self.url

        if url.startswith('ssh://hg.mozilla.org/'):
            parsed_url = urlparse(url)
            endpoint = (
                'https://{netloc}/{path}/json-rev/default'
                .format(netloc=parsed_url.netloc, path=parsed_url.path.strip('/'))
            )
            return {
                'endpoint': endpoint,
                'get_key': lambda x: x['node'],
            }

        if url.startswith('ssh://hg@bitbucket.org/'):
            parsed_url = urlparse(url)
            endpoint = (
                'https://api.bitbucket.org/2.0/repositories/{path}/commit/default'
                .format(path=parsed_url.path.strip('/'))
            )
            return {
                'endpoint': endpoint,
                'get_key': lambda x: x['hash'],
            }

        return None

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

    def pull(self, locales=None):
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
            locales = locales or self.project.locales.all()

            for locale in locales:
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


@python_2_unicode_compatible
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
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)

    SOURCE_EXTENSIONS = ['pot']  # Extensions of source-only formats.
    ALLOWED_EXTENSIONS = [f[0] for f in FORMAT_CHOICES] + SOURCE_EXTENSIONS

    ASYMMETRIC_FORMATS = ('dtd', 'properties', 'ini', 'inc', 'ftl')

    objects = ResourceQuerySet.as_manager()

    @property
    def is_asymmetric(self):
        """Return True if this resource is in an asymmetric format."""
        return self.format in self.ASYMMETRIC_FORMATS

    def __str__(self):
        return '%s: %s' % (self.project.name, self.path)

    def save(self, *args, **kwargs):
        super(Resource, self).save(*args, **kwargs)

        if self.deadline and self.project.deadline:
            if self.deadline < self.project.deadline:
                self.project.deadline = self.deadline
                self.project.save()

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


@python_2_unicode_compatible
class Subpage(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=128)
    url = models.URLField("URL", blank=True)
    resources = models.ManyToManyField(Resource, blank=True)

    def __str__(self):
        return self.name


class EntityQuerySet(models.QuerySet):
    def get_filtered_entities(self, locale, query, rule, match_all=True):
        """Return a QuerySet of values of entity PKs matching the locale, query and rule.

        Filter entities that match the given filter provided by the `locale` and `query`
        parameters. For performance reasons the `rule` parameter is also provided to filter
        entities in python instead of the DB.

        :arg Locale locale: a Locale object to get translations for
        :arg Q query: a django ORM Q() object describing translations to filter
        :arg function rule: a lambda function implementing the `query` logic
        :arg boolean match_all: if true, all plural forms must match the rule.
            Otherwise, only one matching is enough

        :returns: a QuerySet of values of entity PKs

        """
        # First of find all translations that match the criteria.
        translations = Translation.objects.filter(locale=locale).filter(query)

        plural_pks = []

        if locale.nplurals:
            # Then we want to find the active translation of each plural form of each
            # entity that has plurals.
            # So we query all those entities, with for each a list of translations ordered
            # so that the first one for each plural form will be the active one.
            plural_candidates = (
                self
                .exclude(string_plural='')
                .prefetch_related(Prefetch(
                    'translation_set',
                    queryset=translations.order_by('approved', 'fuzzy', '-date'),
                    to_attr='fetched_translations'
                ))
            )

            # Now that we have all those translations, we'll want to extract just the
            # active one and then make sure it matches the `rule`. If it does, we store
            # it to be retrieved in the final query.
            for candidate in plural_candidates:
                # Walk through the plural forms one by one.
                count = 0
                for i in range(locale.nplurals):
                    candidate_translations = filter(
                        lambda x: x.plural_form == i,
                        candidate.fetched_translations
                    )
                    if len(candidate_translations) and rule(candidate_translations[0]):
                        count += 1

                        # No point going on if we don't care about matching all.
                        if not match_all:
                            continue

                # If `match_all` is True, we want all plural forms to have a match.
                # Otherwise, just one of them matching is enough.
                if (match_all and count == locale.nplurals) or (not match_all and count):
                    plural_pks.append(candidate.pk)

        # Finally, we return a query that returns both the matching entities with no
        # plurals and the entities with plurals that were stored earlier.
        return (
            Translation.objects
            .filter(locale=locale)
            .filter(
                Q(Q(entity__string_plural='') & query) |
                Q(entity_id__in=plural_pks)
            )
            .values('entity')
        )

    def missing(self, locale):
        """Return a filter to be used to select entities marked as "missing".

        An entity is marked as "missing" if at least one of its plural forms has
        zero translations.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        have_translations = self.filter(translation__locale=locale)

        have_missing_plural_forms = []
        if locale.nplurals:
            plural_candidates = (
                self
                .exclude(string_plural='')
                .prefetch_translations(locale)
            )

            for candidate in plural_candidates:
                candidate_translations = set(
                    x.plural_form for x in candidate.fetched_translations
                )
                if len(candidate_translations) < locale.nplurals:
                    have_missing_plural_forms.append(candidate.pk)

        return ~Q(pk__in=have_translations) | Q(pk__in=have_missing_plural_forms)

    def fuzzy(self, locale):
        """Return a filter to be used to select entities marked as "fuzzy".

        An entity is marked as "fuzzy" if all of its plural forms have a fuzzy
        translation. Note that a fuzzy translation is always the active one.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(fuzzy=True),
                lambda x: x.fuzzy
            )
        )

    def suggested(self, locale):
        """Return a filter to be used to select entities marked as "suggested".

        An entity is marked as "suggested" if at least one of its plural forms has
        translations none of which are either fuzzy or approved.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        # First, we only care about entities that actually have translations.
        have_translations = self.filter(translation__locale=locale)

        # We can remove all entities that have approved or fuzzy translations.
        approved_or_fuzzy = (
            Translation.objects
            .filter(locale=locale)
            .filter(Q(approved=True) | Q(fuzzy=True))
            .values('entity')
        )

        # And we can remove all entities with plurals that have a number of
        # approved + fuzzy translations equal to the number of plural forms.
        approved_or_fuzzy_plurals_forms = []
        if locale.nplurals:
            plural_candidates = (
                self
                .exclude(string_plural='')
                .prefetch_translations(locale)
            )

            for candidate in plural_candidates:
                approved_or_fuzzy_plurals = set(
                    x.plural_form
                    for x in candidate.fetched_translations
                    if x.approved or x.fuzzy
                )
                if len(approved_or_fuzzy_plurals) == locale.nplurals:
                    approved_or_fuzzy_plurals_forms.append(candidate.pk)

        return (
            Q(pk__in=have_translations) &
            ~Q(pk__in=approved_or_fuzzy, string_plural='') &
            ~Q(pk__in=approved_or_fuzzy_plurals_forms)
        )

    def translated(self, locale):
        """Return a filter to be used to select entities marked as "approved".

        An entity is marked as "approved" if all of its plural forms have an approved
        translation. Note that an approved translation is always the active one.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(approved=True),
                lambda x: x.approved
            )
        )

    def has_suggestions(self, locale):
        """Return a filter to be used to select entities with suggested translations.

        An entity is said to have suggestions if at least one of its plural forms
        has at least one unreviewed suggestion (not fuzzy, not approved, not rejected).

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(approved=False, rejected=False, fuzzy=False),
                lambda x: not x.approved and not x.rejected and not x.fuzzy,
                match_all=False,
            )
        )

    def rejected(self, locale):
        """Return a filter to be used to select entities with rejected translations.

        This filter will return all entities that have a rejected translation, whether
        they have approved or fuzzy translations or not.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(rejected=True),
                lambda x: x.rejected,
                match_all=False,
            )
        )

    def unchanged(self, locale):
        """Return a filter to be used to select entities that have unchanged translations.

        An entity is marked as "unchanged" if all of its plural forms have translations
        equal to the source string.

        :arg Locale locale: a Locale object to get translations for

        :returns: a django ORM Q object to use as a filter

        """
        return Q(
            pk__in=self.get_filtered_entities(
                locale,
                Q(Q(string=F('entity__string')) | Q(string=F('entity__string_plural'))),
                lambda x: x.string == x.entity.string,
                match_all=False,
            )
        )

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

    def prefetch_translations(self, locale):
        """
        Prefetch translations for given locale.
        """
        return self.prefetch_related(
            Prefetch(
                'translation_set',
                queryset=Translation.objects.filter(locale=locale),
                to_attr='fetched_translations'
            )
        )


@python_2_unicode_compatible
class Entity(DirtyFieldsMixin, models.Model):
    resource = models.ForeignKey(Resource, related_name='entities')
    string = models.TextField()
    string_plural = models.TextField(blank=True)
    key = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    date_created = models.DateTimeField(default=timezone.now)
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

    class Meta:
        index_together = (
            ('resource', 'obsolete', 'string_plural'),
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

    def __str__(self):
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
            translation = sorted(
                translations,
                key=lambda k: (k.approved, not k.rejected, k.date),
                reverse=True
            )[0]
            return translation.serialize()

        return {
            'fuzzy': False,
            'string': None,
            'approved': False,
            'pk': None,
        }

    @classmethod
    def for_project_locale(
        self, project, locale, paths=None, status=None,
        search=None, exclude_entities=None, extra=None, time=None, author=None,
    ):
        """Get project entities with locale translations."""

        # Time & author filters have to be applied before the aggregation
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

        if author:
            pre_filters.append(Entity.objects.authored_by(locale, author.split(',')))

        if pre_filters:
            entities = Entity.objects.filter(pk__in=Entity.objects.filter(Q(*pre_filters)))
        else:
            entities = Entity.objects.all()

        entities = entities.filter(
            resource__translatedresources__locale=locale,
            obsolete=False
        )

        if project.slug != 'all-projects':
            entities = entities.filter(resource__project=project)

        # Filter by path
        if paths:
            paths = project.parts_to_paths(paths)
            entities = entities.filter(resource__path__in=paths)

        if status:
            # Apply a combination of filters based on the list of statuses the user sent.
            status_filter_choices = ('missing', 'fuzzy', 'suggested', 'translated')
            post_filters.append(
                combine_entity_filters(
                    entities,
                    status_filter_choices,
                    status.split(','),
                    locale
                )
            )

        if extra:
            # Apply a combination of filters based on the list of extras the user sent.
            extra_filter_choices = ('has-suggestions', 'rejected', 'unchanged')
            post_filters.append(
                combine_entity_filters(
                    entities,
                    extra_filter_choices,
                    extra.split(','),
                    locale
                )
            )

        if post_filters:
            entities = entities.filter(Q(*post_filters))

        # Filter by search parameters
        if search:
            # https://docs.djangoproject.com/en/dev/topics/db/queries/#spanning-multi-valued-relationships
            search_query = (search, locale.db_collation)
            translation_matches = (
                entities.filter(
                    translation__string__icontains_collate=search_query,
                    translation__locale=locale,
                )
                .values_list('id', flat=True)
            )
            entity_matches = (
                entities.filter(
                    Q(string__icontains=search) |
                    Q(string_plural__icontains=search) |
                    Q(comment__icontains=search) |
                    Q(key__icontains=search)
                )
                .values_list('id', flat=True)
            )
            entities = Entity.objects.filter(
                pk__in=set(list(translation_matches) + list(entity_matches))
            )

        entities = entities.prefetch_related('resource').prefetch_translations(locale)

        if exclude_entities:
            entities = entities.exclude(pk__in=exclude_entities)

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
                'visible': (
                    False if entity.pk not in visible_entities or not visible_entities
                    else True
                ),
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
        """
        :return: A tuple
            - a queryset of old translations (to be changed)
            - a list of newly created translations
        """
        translations = self.filter(string__contains=find)

        if translations.count() == 0:
            return translations, []

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
        changed_translations = Translation.objects.bulk_create(translations_to_create)
        return translations, changed_translations

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


@python_2_unicode_compatible
class Translation(DirtyFieldsMixin, models.Model):
    entity = models.ForeignKey(Entity)
    locale = models.ForeignKey(Locale)
    user = models.ForeignKey(User, null=True, blank=True)
    string = models.TextField()
    # 0=zero, 1=one, 2=two, 3=few, 4=many, 5=other, null=no plural forms
    plural_form = models.SmallIntegerField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    fuzzy = models.BooleanField(default=False)

    approved = models.BooleanField(default=False)
    approved_user = models.ForeignKey(
        User, related_name='approved_translations', null=True, blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)

    unapproved_user = models.ForeignKey(
        User, related_name='unapproved_translations', null=True, blank=True)
    unapproved_date = models.DateTimeField(null=True, blank=True)

    rejected = models.BooleanField(default=False)
    rejected_user = models.ForeignKey(
        User, related_name='rejected_translations', null=True, blank=True)
    rejected_date = models.DateTimeField(null=True, blank=True)

    unrejected_user = models.ForeignKey(
        User, related_name='unrejected_translations', null=True, blank=True)
    unrejected_date = models.DateTimeField(null=True, blank=True)

    # Field contains a concatenated state of the  entity for faster search lookups.
    # Due to the nature of sql queries, it's faster to perform `icontains` filter on the same table
    # than OR condition for The Entity and The Translation class joined together.
    entity_document = models.TextField(blank=True)

    objects = TranslationQuerySet.as_manager()
    NotAllowed = TranslationNotAllowed

    # extra stores data that we want to save for the specific format
    # this translation is stored in, but that we otherwise don't care
    # about.
    extra = JSONField(default=extra_default)

    class Meta:
        index_together = (
            ('entity', 'locale', 'approved'),
            ('entity', 'locale', 'fuzzy'),
        )

    @classmethod
    def for_locale_project_paths(self, locale, project, paths):
        """
        Return Translation QuerySet for given locale, project and paths.
        """
        translations = Translation.objects.filter(
            entity__obsolete=False,
            locale=locale
        )

        if project.slug != 'all-projects':
            translations = translations.filter(entity__resource__project=project)

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
            return {
                'translation': self,
                'date': self.approved_date,
                'user': self.approved_user,
                'type': 'approved',
            }
        else:
            return {
                'translation': self,
                'date': self.date,
                'user': self.user,
                'type': 'submitted',
            }

    def __str__(self):
        return self.string

    def save(self, imported=False, *args, **kwargs):
        super(Translation, self).save(*args, **kwargs)

        # Only one translation can be approved at a time for any
        # Entity/Locale.
        if self.approved:
            (
                Translation.objects
                .filter(
                    entity=self.entity,
                    locale=self.locale,
                    plural_form=self.plural_form,
                    rejected=False,
                )
                .exclude(pk=self.pk)
                .update(
                    approved=False,
                    approved_user=None,
                    approved_date=None,
                    rejected=True,
                    rejected_user=self.approved_user,
                    rejected_date=self.approved_date,
                    fuzzy=False,
                )
            )

            if not self.memory_entries.exists():
                TranslationMemoryEntry.objects.create(
                    source=self.entity.string,
                    target=self.string,
                    entity=self.entity,
                    translation=self,
                    locale=self.locale,
                    project=self.entity.resource.project,
                )

        if not imported:
            # Update stats AFTER changing approval status.
            translatedresource, _ = TranslatedResource.objects.get_or_create(
                resource=self.entity.resource, locale=self.locale
            )
            translatedresource.calculate_stats()

            # Whenever a translation changes, mark the entity as having
            # changed in the appropriate locale. We could be smarter about
            # this but for now this is fine.
            if self.approved:
                self.entity.mark_changed(self.locale)

            # Update latest translation where necessary
            self.update_latest_translation()

    def update_latest_translation(self):
        """
        Set `latest_translation` to this translation if its more recent than
        the currently stored translation. Do this for all affected models.
        """
        resource = self.entity.resource
        project = resource.project
        locale = self.locale
        translatedresource = TranslatedResource.objects.get(resource=resource, locale=locale)

        instances = [project, locale, translatedresource]

        project_locale = utils.get_object_or_none(ProjectLocale, project=project, locale=locale)
        if project_locale:
            instances.append(project_locale)

        for instance in instances:
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

        if stats:
            TranslatedResource.objects.get(
                resource=self.entity.resource,
                locale=self.locale
            ).calculate_stats()

        TranslationMemoryEntry.objects.filter(translation=self).delete()
        self.entity.mark_changed(self.locale)

    def unreject(self, user):
        """
        Unreject translation.
        """
        self.rejected = False
        self.unrejected_user = user
        self.unrejected_date = timezone.now()
        self.save()

    def serialize(self):
        return {
            'pk': self.pk,
            'string': self.string,
            'approved': self.approved,
            'rejected': self.rejected,
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
            where=[
                '(CHAR_LENGTH(source) BETWEEN %s AND %s)',
                levenshtein_ratio_equation + ' > %s'
            ],
            params=(min_dist, max_dist, text, text, text, min_quality),
            select={'quality': levenshtein_ratio_equation + '* 100'},
            select_params=(text, text, text)
        )
        return entries


class TranslationMemoryEntry(models.Model):
    source = models.TextField()
    target = models.TextField()

    entity = models.ForeignKey(Entity, null=True, on_delete=models.SET_NULL,
                               related_name='memory_entries')
    translation = models.ForeignKey(Translation, null=True, on_delete=models.SET_NULL,
                                    related_name='memory_entries')
    locale = models.ForeignKey(Locale)
    project = models.ForeignKey(Project, null=True, related_name='memory_entries')

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
        translated_resources = self.filter(
            locale=locale
        )

        if project.slug != 'all-projects':
            translated_resources = translated_resources.filter(
                resource__project=project,
                resource__path__in=paths
            )

        return translated_resources.aggregated_stats()


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
