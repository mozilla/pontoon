from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


class ResourceQuerySet(models.QuerySet):
    def obsolete(self, now):
        from pontoon.base.models.entity import Entity

        self.update(obsolete=True, date_obsoleted=now)
        Entity.objects.filter(resource__in=self).obsolete(now)

    def current(self):
        return self.filter(obsolete=False)


class Resource(models.Model):
    project = models.ForeignKey("Project", models.CASCADE, related_name="resources")
    path = models.TextField()  # Path to localization file
    meta = ArrayField(ArrayField(models.TextField(), size=2), default=list)
    comment = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)
    """
    Index in the alphabetically sorted list of resources

    Sorting resources by path is a heavy operation, so we use this field
    to represent the alphabetic order of resources in the project.
    """

    total_strings = models.PositiveIntegerField(default=0)
    obsolete = models.BooleanField(default=False)

    date_created = models.DateTimeField(default=timezone.now)
    date_obsoleted = models.DateTimeField(null=True, blank=True)

    # Format
    class Format(models.TextChoices):
        ANDROID = "android", "android"
        DTD = "dtd", "dtd"
        FLUENT = "fluent", "fluent"
        GETTEXT = "gettext", "gettext"
        INI = "ini", "ini"
        PLAIN_JSON = "plain_json", "plain_json"
        PROPERTIES = "properties", "properties"
        WEBEXT = "webext", "webext"
        XCODE = "xcode", "xcode"
        XLIFF = "xliff", "xliff"

    format = models.CharField(
        "Format", max_length=20, blank=True, choices=Format.choices
    )

    deadline = models.DateField(blank=True, null=True)

    objects = ResourceQuerySet.as_manager()

    # Formats that allow empty translations
    EMPTY_TRANSLATION_FORMATS = {
        Format.DTD,
        Format.INI,
        Format.PROPERTIES,
    }

    class Meta:
        unique_together = (("project", "path"),)

    @property
    def allows_empty_translations(self):
        """Return True if this resource allows empty translations."""
        return self.format in self.EMPTY_TRANSLATION_FORMATS

    @property
    def name(self):
        return self.path

    def __str__(self):
        return "{project}: {resource}".format(
            project=self.project.name,
            resource=self.path,
        )
