from django.db import models

from pontoon.base.models import Translation


class FailedCheck(models.Model):
    """
    Store checks performed on translations if they failed.

    Severity of failed checks are expressed by subclasses of this model.
    """

    library = models.CharField(
        max_length=20,
        choices=(("p", "pontoon"), ("cl", "compare-locales"),),
        db_index=True,
    )
    message = models.TextField()

    class Meta:
        abstract = True

    def __repr__(self):
        return u"[{}] {}: {}".format(
            self.__class__.__name__, self.get_library_display(), self.message
        )


class Warning(FailedCheck):
    translation = models.ForeignKey(
        Translation, models.CASCADE, related_name="warnings"
    )

    class Meta(FailedCheck.Meta):
        unique_together = (("translation", "library", "message"),)


class Error(FailedCheck):
    translation = models.ForeignKey(Translation, models.CASCADE, related_name="errors")

    class Meta(FailedCheck.Meta):
        unique_together = (("translation", "library", "message"),)
