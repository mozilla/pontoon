from django.contrib.auth.models import Group
from django.db import connection

from pontoon.base.models import (
    Entity, Locale, Project, ProjectLocale, Resource,
    TranslatedResource, Translation)

from django.contrib.auth import get_user_model


class Environment(object):

    def setup(self):
        self.setup_collations()
        for i in range(0, 2):
            self.setup_translations(i)
        self.setup_x()
        self.setup_admin()

    def setup_collations(self):
        """Required for collation lookup tests

        At the moment this is only set up for Turkish

        cf: Bug 1440940
        """

        cursor = connection.cursor()
        cursor.execute("CREATE COLLATION tr_tr (LOCALE = 'tr_TR.utf8');")

    def setup_translations(self, i):
        translators_group = Group.objects.create(
            name='locale%s translators' % i,
        )
        managers_group = Group.objects.create(
            name='locale%s managers' % i,
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

    def setup_admin(self):
        admin0 = get_user_model().objects.create(
            username="admin0",
            email="admin0@user.email")
        admin0.is_superuser = True
        admin0.save()

    def setup_x(self):
        Locale.objects.create(code="localeX", name="LocaleX")
        Project.objects.create(slug="projectX", name="Project X")
        get_user_model().objects.create(
            username="userX",
            email="userX@user.email")
