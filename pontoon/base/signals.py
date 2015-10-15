from django.db.models.signals import post_save
from django.dispatch import receiver

from pontoon.base.models import ProjectLocale


@receiver(post_save, sender=ProjectLocale)
def project_locale_added(sender, **kwargs):
    """
    When a new locale is added to a project, mark the project as
    changed.
    """
    created = kwargs.get('created', False)
    raw = kwargs.get('raw', False)
    project_locale = kwargs.get('instance', None)
    if created and not raw and project_locale is not None:
        project = project_locale.project
        project.has_changed = True
        project.save(update_fields=['has_changed'])
