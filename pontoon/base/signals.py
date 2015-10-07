from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from pontoon.base.models import Project


@receiver(m2m_changed, sender=Project.locales.through)
def project_locale_added(sender, **kwargs):
    """When a new locale is added to a project, mark the project as changed."""
    action = kwargs.get('action', None)
    project = kwargs.get('instance', None)
    if action == 'post_add' and project is not None:
        project.has_changed = True
        project.save(update_fields=['has_changed'])
