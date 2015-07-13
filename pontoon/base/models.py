import datetime
import json
import logging

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.forms import ModelForm

from pontoon.base import utils


log = logging.getLogger('pontoon')


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
    last_committed = models.DateTimeField(null=True)

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

    def __unicode__(self):
        return '%s: %s' % (self.project.name, self.path)


class Subpage(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=128)
    url = models.URLField("URL", blank=True)  # Firefox OS Hack
    resource = models.ManyToManyField(Resource, blank=True)

    def __unicode__(self):
        return self.name


class Entity(models.Model):
    resource = models.ForeignKey(Resource)
    string = models.TextField()
    string_plural = models.TextField(blank=True)
    key = models.TextField(blank=True)  # Needed for webL10n
    comment = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    source = models.TextField(blank=True)  # Path to source code file
    obsolete = models.BooleanField(default=False)

    @property
    def marked(self):
        return utils.mark_placeables(self.string)

    @property
    def marked_plural(self):
        return utils.mark_placeables(self.string_plural)

    def __unicode__(self):
        return self.string

    def serialize(self):
        try:
            source = eval(self.source)
        except SyntaxError:
            source = self.source

        return {
            'pk': self.pk,
            'original': self.string,
            'marked': self.marked,
            'original_plural': self.string_plural,
            'marked_plural': self.marked_plural,
            'key': self.key,
            'path': self.resource.path,
            'format': self.resource.format,
            'comment': self.comment,
            'order': self.order,
            'source': source,
            'obsolete': self.obsolete,
        }

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


class Translation(models.Model):
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

    def __unicode__(self):
        return self.string

    def save(self, stats=True, *args, **kwargs):
        super(Translation, self).save(*args, **kwargs)

        # Only one translation can be approved at a time for any
        # Entity/Locale.
        if self.approved:
            (Translation.objects
                .filter(entity=self.entity, locale=self.locale, plural_form=self.plural_form)
                .exclude(pk=self.pk)
                .update(approved=False, approved_user=None, approved_date=None))

        # Update stats AFTER changing approval status.
        if stats:
            update_stats(self.entity.resource, self.locale)


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


def get_entities(project, locale, paths=None):
    """Load project entities with locale translations."""

    resources = Resource.objects.filter(project=project)
    if paths:
        resource_with_paths = resources.filter(path__in=paths)
        resources = resource_with_paths or resources

    entities = Entity.objects.filter(resource__in=resources, obsolete=False)
    entities_array = []

    for e in entities:
        translation_array = []

        # Entities without plurals
        if e.string_plural == "":
            translation = get_translation(entity=e, locale=locale)
            translation_array.append(translation.serialize())

        # Pluralized entities
        else:
            for i in range(0, locale.nplurals or 1):
                translation = get_translation(
                    entity=e, locale=locale, plural_form=i)
                translation_array.append(translation.serialize())

        obj = e.serialize()
        obj["translation"] = translation_array

        entities_array.append(obj)
    return sorted(entities_array, key=lambda k: k['order'])


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

    if len(translations) > 0:
        try:
            return translations.filter(approved=True).latest("date")
        except Translation.DoesNotExist as e:
            return translations.latest("date")
    else:
        return Translation()


def save_entity(resource, string, string_plural="", comment="",
                order=0, key="", source=""):
    """Add new or update existing entity."""

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
        t.save(stats=False)

    # Update existing translations
    elif translations_equal_count > 0:
        t = translations_equal[0]
        if translations_equal_count > 1:
            try:
                t = translations_equal.filter(approved=True).latest("date")
                t.approved_date = now
            except Translation.DoesNotExist as e:
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
            t.save(stats=False)


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
