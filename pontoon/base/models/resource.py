from django.db import models
from django.utils import timezone


class Resource(models.Model):
    project = models.ForeignKey("Project", models.CASCADE, related_name="resources")
    path = models.TextField()  # Path to localization file

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
        DTD = "dtd", "dtd"
        FTL = "ftl", "ftl"
        INC = "inc", "inc"
        INI = "ini", "ini"
        JSON = "json", "json"
        PO = "po", "po"
        PROPERTIES = "properties", "properties"
        XLF = "xlf", "xliff"
        XLIFF = "xliff", "xliff"
        XML = "xml", "xml"

    format = models.CharField(
        "Format", max_length=20, blank=True, choices=Format.choices
    )

    deadline = models.DateField(blank=True, null=True)

    # Formats that allow empty translations
    EMPTY_TRANSLATION_FORMATS = {
        Format.DTD,
        Format.INC,
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
