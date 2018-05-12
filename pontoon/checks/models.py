from django.db import models as m

from pontoon.base.models import Translation


class Check(m.Model):
    """
    Store checks performed on translations if they failed.

    Severity of failed checks are expressed by subclasses of this model.
    """
    library = m.CharField(
        max_length=20,
        choices=(
            ('p', 'pontoon'),
            ('tt', 'translate-toolkit'),
            ('cl', 'compare-locales'),
        ),
        db_index=True
    )
    message = m.TextField()

    class Meta:
        abstract = True
        ordering = ('library', 'message')


class Warning(Check):
    translation = m.ForeignKey(Translation, related_name='warnings')

    class Meta(Check.Meta):
        unique_together = (('translation', 'library', 'message'),)


class Error(Check):
    translation = m.ForeignKey(Translation, related_name='errors')

    class Meta(Check.Meta):
        unique_together = (('translation', 'library', 'message'),)
