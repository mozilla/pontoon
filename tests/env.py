from django.contrib.auth.models import Group

from pontoon.base.models import (
    Entity, Locale, Project, ProjectLocale, Resource,
    TranslatedResource, Translation)

from django.contrib.auth import get_user_model


class Environment(object):

    def setup(self):
        for i in range(0, 2):
            self.setup_translations(i)
        self.setup_x()

    def setup_translations(self, i):
        translators_group = Group.objects.create(
            name='locale%s translators' % i,
        )
        managers_group = Group.objects.create(
            name='local%s managers' % i,
        )
        locale = Locale.objects.create(
            code="locale%s" % i,
            name="Locale %s" % i,
            translators_group=translators_group,
            managers_group=managers_group
        )
        project = Project.objects.create(
            slug="project%s" % i, name="Project %s" % i)
        ProjectLocale.objects.create(project=project, locale=locale)
        user = get_user_model().objects.create(
            username="user%s" % i,
            email="user%s@user.email" % i)
        resource = Resource.objects.create(
            project=project, path="resource%s.po" % i, format="po")
        TranslatedResource.objects.create(
            resource=resource, locale=locale)
        entity = Entity.objects.create(
            resource=resource, string="entity%s" % i)
        resource.total_strings = 1
        resource.save()
        Translation.objects.create(
            entity=entity,
            string="Translation for entity%s" % i,
            locale=locale,
            user=user)

    def setup_x(self):
        Locale.objects.create(code="localeX", name="LocaleX")
        Project.objects.create(slug="projectX", name="Project X")
        get_user_model().objects.create(
            username="userX",
            email="userX@user.email")
