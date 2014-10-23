
import commonware.log
import datetime
import json

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.forms import ModelForm


log = commonware.log.getLogger('pontoon')


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    transifex_username = models.CharField(max_length=40, blank=True)
    transifex_password = models.CharField(max_length=128, blank=True)
    svn_username = models.CharField(max_length=40, blank=True)
    svn_password = models.CharField(max_length=128, blank=True)


class Locale(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=128)
    nplurals = models.SmallIntegerField(null=True, blank=True)
    plural_rule = models.CharField(max_length=128, blank=True)

    def __unicode__(self):
        return self.name

    def stringify(self):
        return json.dumps({
            'code': self.code,
            'name': self.name,
            'nplurals': self.nplurals,
            'plural_rule': self.plural_rule,
        })


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

    class Meta:
        permissions = (
            ("can_manage", "Can manage projects"),
            ("can_localize", "Can localize projects"),
        )

    def __unicode__(self):
        return self.name


class Subpage(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=128)
    url = models.URLField("URL", blank=True)  # Firefox OS Hack

    def __unicode__(self):
        return self.name


class Resource(models.Model):
    project = models.ForeignKey(Project)
    path = models.TextField()  # Path to localization file
    entity_count = models.PositiveIntegerField(default=0)

    # Format
    FORMAT_CHOICES = (
        ('po', 'po'),
        ('properties', 'properties'),
        ('dtd', 'dtd'),
        ('ini', 'ini'),
        ('lang', 'lang'),
    )
    format = models.CharField(
        "Format", max_length=20, blank=True, choices=FORMAT_CHOICES)

    def __unicode__(self):
        return '%s: %s' % (self.project.name, self.path)


class Entity(models.Model):
    resource = models.ForeignKey(Resource)
    string = models.TextField()
    string_plural = models.TextField(blank=True)
    key = models.TextField(blank=True)  # Needed for webL10n
    comment = models.TextField(blank=True)
    source = models.TextField(blank=True)  # Path to source code file
    obsolete = models.BooleanField(default=False)

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
            'original_plural': self.string_plural,
            'key': self.key,
            'path': self.resource.path,
            'format': self.resource.format,
            'comment': self.comment,
            'source': source,
            'obsolete': self.obsolete,
        }


class Translation(models.Model):
    entity = models.ForeignKey(Entity)
    locale = models.ForeignKey(Locale)
    user = models.ForeignKey(User, null=True, blank=True)
    string = models.TextField()
    # 0=zero, 1=one, 2=two, 3=few, 4=many, 5=other, null=no plural forms
    plural_form = models.SmallIntegerField(null=True, blank=True)
    date = models.DateTimeField()
    approved = models.BooleanField(default=False)
    fuzzy = models.BooleanField(default=False)

    def __unicode__(self):
        return self.string

    def save(self, stats=True, *args, **kwargs):
        super(Translation, self).save(*args, **kwargs)
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

    def clean(self):
        cleaned_data = super(ProjectForm, self).clean()
        repository_url = cleaned_data.get("repository_url")
        repository_type = cleaned_data.get("repository_type")
        transifex_project = cleaned_data.get("transifex_project")
        transifex_resource = cleaned_data.get("transifex_resource")

        if repository_type == 'Transifex':
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


def get_entities(project, locale, path=None):
    """Load project entities with locale translations."""

    resources = Resource.objects.filter(project=project)
    if path:
        resources = resources.filter(path=path)

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
    return entities_array


def get_translation(entity, locale, plural_form=None, fuzzy=None):
    """Get translation of a given entity to a given locale in a given form."""

    translations = Translation.objects.filter(
        entity=entity, locale=locale, plural_form=plural_form)

    if fuzzy is not None:
        translations = translations.filter(fuzzy=fuzzy)

    if len(translations) > 0:
        try:
            return translations.get(approved=True)
        except Translation.DoesNotExist:
            return translations.latest("date")
    else:
        return Translation()


def save_entity(resource, string, string_plural="", comment="",
                key="", source=""):
    """Add new or update existing entity."""

    # Update existing entity
    try:
        if key is "":
            e = Entity.objects.get(
                resource=resource, string=string,
                string_plural=string_plural)

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

    e.save()


def save_translation(entity, locale, string, plural_form=None, fuzzy=False):
    """Add new or update existing translation."""

    approved = not fuzzy
    translations = Translation.objects.filter(
        entity=entity, locale=locale, plural_form=plural_form)
    translations_equal = translations.filter(string=string)
    translations_equal_count = translations_equal.count()

    # Add new translation if it doesn's exist yet
    if translations_equal_count == 0:
        unset_approved(translations)
        t = Translation(
            entity=entity, locale=locale, plural_form=plural_form,
            string=string, date=datetime.datetime.now(),
            approved=approved, fuzzy=fuzzy)
        t.save(stats=False)

    # Update existing translations if fuzzy status changes
    elif translations_equal_count > 0:
        t = translations_equal[0]
        if translations_equal_count > 1:
            try:
                t = translations_equal.get(approved=True)
            except Translation.DoesNotExist:
                t = translations_equal.latest("date")

        if t.fuzzy != fuzzy:
            unset_approved(translations)
            t.date = datetime.datetime.now()
            t.approved = approved
            t.fuzzy = fuzzy
            t.save(stats=False)


def unset_approved(translations):
    """Unset approved attribute for given translations."""

    translations.update(approved=False)


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
    stats.translated_count = translated_entities.count() - approved - fuzzy
    stats.save()
