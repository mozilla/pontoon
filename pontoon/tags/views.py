import json
from collections import OrderedDict

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView, View

from pontoon.base.models import Project
from pontoon.base.templatetags.helpers import provider_login_url
from pontoon.base.utils import DjangoJSONMultiEncoder
from pontoon.base.views import AjaxDetailView

from .models import Tag
from .utils import TagsTool, TagLocalesEncoder, ProjectTagsEncoder

# from dj.debug import debug, debug_sql


class Tabs(object):
    tabs = ()

    def __init__(self, view):
        self.view = view


class ProjectTabs(Tabs):

    @property
    def project(self):
        return self.view.project

    @property
    def tabs(self):
        teams = self.project.project_locale.count()
        return [
            dict(label='teams',
                 count=teams,
                 href=reverse(
                     'pontoon.projects.project',
                     kwargs=dict(slug=self.project.slug))),
            dict(label='tags',
                 count=len(self.view.tags),
                 active=True, href=''),
            dict(label='contributors',
                 href=reverse(
                     'pontoon.projects.contributors',
                     kwargs=dict(slug=self.project.slug))),
            dict(label='info',
                 href=reverse(
                     'pontoon.projects.info',
                     kwargs=dict(slug=self.project.slug))),
            dict(label='notifications',
                 href=reverse(
                     'pontoon.projects.notifications',
                     kwargs=dict(slug=self.project.slug)))]


class TagTabs(Tabs):

    @property
    def tabs(self):
        teams = 3
        return [
            dict(label='teams',
                 count=teams,
                 active=True,
                 href='')]


class DashboardEncoder(DjangoJSONEncoder):

    def default(self, obj):
        if isinstance(obj, Dashboard):
            return dict(
                context=obj.context,
                toolbar=obj.toolbar,
                tabs=obj.tabs)
        if isinstance(obj, Tabs):
            return obj.tabs
        if isinstance(obj, Toolbar):
            return dict(
                logo=obj.logo,
                links=obj.links,
                menus=obj.menus,
                notifications=obj.notifications,
                user=obj.user_profile)
        return super(DashboardEncoder, self).default(obj)


class ProjectTagsViewEncoder(DjangoJSONMultiEncoder):
    encoders = (DashboardEncoder, ProjectTagsEncoder)


class TagLocalesEncoder(DjangoJSONMultiEncoder):
    encoders = (DashboardEncoder, TagLocalesEncoder)


class Toolbar(object):

    def __init__(self, view):
        self.view = view
        self.request = view.request
        self.user = self.request.user

    @property
    def links(self):
        return [
            dict(href='/teams', label='Teams'),
            dict(href='/projects', label='Projects'),
            dict(href='/contributors', label='Contributors'),
            dict(href='/machinery', label='Machinery')]

    @property
    def logo(self):
        return dict(src="/static/img/logo.svg", href="/")

    @property
    def general_menu(self):
        return [
            dict(href="/terms/",
                 icon='legal',
                 text='Terms of use'),
            dict(href=("https://mozilla-l10n.github.io/"
                       "localizer-documentation/tools/pontoon/"),
                 icon='life-ring',
                 text='Help')]

    @property
    def menus(self):
        return OrderedDict(
            (('general', self.general_menu),
             ('user', self.user_menu)))

    def get_actor(self, actor):
        _actor = {}
        if hasattr(actor, 'slug'):
            _actor['url'] = reverse(
                'pontoon.projects.project',
                kwargs=dict(slug=actor.slug))
            _actor['anchor'] = str(actor)
        elif hasattr(actor, 'email'):
            _actor['url'] = reverse(
                'pontoon.contributors.contributor.username',
                actor.username)
            _actor['anchor'] = actor.name_or_email
        return _actor

    @property
    def notifications(self):
        if self.user.is_anonymous:
            return []
        return list(
            dict(id=notification.id,
                 level=notification.level,
                 unread=notification.unread,
                 actor=self.get_actor(notification.actor),
                 verb=notification.verb,
                 target=notification.target,
                 ago=notification.timesince(),
                 description=notification.description)
            for notification in self.user.menu_notifications)

    @property
    def user_menu(self):
        if self.user.is_anonymous:
            return [
                dict(href=provider_login_url(self.request),
                     icon='sign-in',
                     text='Sign in')]
        menu = []
        if self.user.is_superuser:
            menu += [
                dict(href='/admin',
                     icon='wrench',
                     text='Admin'),
                dict(href='/admin',
                     icon='wrench',
                     text='Admin - Current project')]
        return menu + [
            dict(href='/settings',
                 icon='cog',
                 text='Settings')]

    @property
    def user_profile(self):
        if self.user.is_anonymous:
            return dict(username=None)
        return dict(
            username=self.user.username,
            email=self.user.email,
            avatar=self.user.gravatar_url(''))


class Dashboard(object):
    tabs_class = Tabs
    toolbar_class = Toolbar
    info = None

    def __init__(self, view):
        self.view = view

    @property
    def toolbar(self):
        return self.toolbar_class(self.view)

    @property
    def tabs(self):
        return self.tabs_class(self.view)


class ProjectDashboard(Dashboard):
    tabs_class = ProjectTabs

    @property
    def project(self):
        return self.view.project

    @property
    def context(self):
        return dict(
            title=self.title,
            subtitle=self.subtitle,
            priority=self.project.priority,
            deadline=self.project.deadline,
            repository=self.project.repositories.first().website,
            stats=self.stats,
            user=(
                dict(
                    name=self.project.contact.name_or_email,
                    url=self.project.contact.profile_url)
                if self.project.contact
                else {}))

    @property
    def stats(self):
        return dict(
            missing_strings=self.project.missing_strings,
            total_strings=self.project.total_strings,
            translated_strings=self.project.translated_strings,
            fuzzy_strings=self.project.fuzzy_strings,
            approved_strings=self.project.approved_strings)

    @property
    def title(self):
        return self.project.name

    @property
    def subtitle(self):
        return ''


class TagDashboard(ProjectDashboard):

    @property
    def tabs_class(self):
        return TagTabs

    @property
    def tag(self):
        return self.view.tag

    @property
    def subtitle(self):
        return self.tag.name


class ProjectTagView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        tag = get_object_or_404(
            Tag.objects.select_related('project', 'project__contact'),
            slug=self.kwargs['tag'],
            project__slug=self.kwargs['project'])
        self.project = tag.project
        context = super(ProjectTagView, self).get_context_data()
        context['bundle'] = 'project_tag_dashboard'
        context['api'] = reverse(
            'pontoon.tags.ajax.project.tag',
            kwargs=dict(
                project=self.kwargs['project'],
                tag=self.kwargs['tag']))
        data = {}
        data['dashboard'] = self.dashboard
        data['tag'] = self.tag
        context['data'] = json.dumps(data, cls=self.encoder)
        return context

    @cached_property
    def tags(self):
        return TagsTool(projects=[self.project], priority=True)

    @cached_property
    def tag(self):
        return self.tags.get(self.kwargs['tag'])

    @property
    def dashboard(self):
        return TagDashboard(self)

    @property
    def encoder(self):
        return TagLocalesEncoder


class ProjectTagsView(TemplateView):
    template_name = 'dashboard.html'
    encoder = ProjectTagsViewEncoder

    @cached_property
    def tags(self):
        return TagsTool(projects=[self.project], priority=True)

    @property
    def dashboard(self):
        return ProjectDashboard(self)

    def get_context_data(self, **kwargs):
        self.project = get_object_or_404(Project, slug=self.kwargs['project'])
        context = super(ProjectTagsView, self).get_context_data()
        context['bundle'] = 'project_tags_dashboard'
        context['api'] = reverse(
            'pontoon.tags.ajax.project.tags',
            kwargs=dict(project=self.kwargs['project']))
        data = {}
        data['dashboard'] = self.dashboard
        data['tags'] = self.tags
        context['data'] = json.dumps(data, cls=self.encoder)
        return context


class AjaxView(View):
    pass


class ProjectAjaxView(AjaxDetailView):
    slug_url_kwarg = 'project'
    model = Project

    @property
    def project(self):
        return self.object


class ProjectDashboardAjaxView(ProjectAjaxView):

    @cached_property
    def tags(self):
        return TagsTool(projects=[self.project], priority=True)

    @property
    def dashboard(self):
        return ProjectDashboard(self)

    def get_context_data(self, *args, **kwargs):
        data = {}
        data['dashboard'] = self.dashboard
        return data


class ProjectTagDashboardAjaxView(ProjectDashboardAjaxView):

    @property
    def tag(self):
        return self.tags.get(self.kwargs['tag'])

    @property
    def dashboard(self):
        return TagDashboard(self)

    @property
    def encoder(self):
        return TagLocalesEncoder

    def get_context_data(self, **kwargs):
        data = super(
            ProjectTagDashboardAjaxView,
            self).get_context_data(**kwargs)
        data['tag'] = self.tag
        return data


class ProjectTagsDashboardAjaxView(ProjectDashboardAjaxView):
    encoder = ProjectTagsViewEncoder

    def get_context_data(self, **kwargs):
        data = super(
            ProjectTagsDashboardAjaxView,
            self).get_context_data(**kwargs)
        data['tags'] = self.tags
        return data
