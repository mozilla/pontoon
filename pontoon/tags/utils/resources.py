from django.db.models import Q

from pontoon.tags.exceptions import InvalidProjectError

from .base import TagsDataTool


class TagsResourcesTool(TagsDataTool):
    """ Find, link and unlink Resources for Tags
    """

    filter_methods = ("locales", "projects", "slug", "path")

    @property
    def data_manager(self):
        return self.resource_manager

    @property
    def filtered_data(self):
        return super(TagsResourcesTool, self).filtered_data.distinct()

    def filter_locales(self, resources):
        return (
            resources.filter(translatedresources__locale__in=self.locales)
            if self.locales
            else resources
        )

    def filter_path(self, resources):
        return resources.filter(path__contains=self.path) if self.path else resources

    def filter_projects(self, resources):
        return (
            resources.filter(project__in=self.projects) if self.projects else resources
        )

    def filter_slug(self, resources):
        return (
            resources.filter(tag__slug__contains=self.slug) if self.slug else resources
        )

    def find(self, search_path=None, include=None, exclude=None):
        """ Find filtered resources by their path, and optionally
        include/exclude resources linked to given tags.
        Return all resources by default.
        """

        if include:
            resources = self.resource_manager.filter(tag__slug=include)
        elif exclude:
            resources = self.resource_manager.exclude(tag__slug=exclude)
        else:
            resources = self.resource_manager

        if self.projects:
            resources = resources.filter(project__in=self.projects)

        if search_path:
            return resources.filter(path__contains=search_path)
        else:
            return resources.all()

    def get(self, tag):
        return self.filtered_data.filter(tag__slug=tag).distinct()

    def get_linkable_resources(self, slug):
        """ Return `values` of resources that can be linked to a given tag,
        but are not already
        """

        return self.find(exclude=slug).values("path", "project")

    def get_linked_resources(self, slug):
        """ Return `values` of resources that are already linked to a given tag
        """
        return self.get(slug).values("path", "project")

    def link(self, tag, resources):
        """ Associate Resources with a Tag. The Resources can be selected
        either by passing a search query to match, or by passing a list
        of Resource paths
        """
        query = Q(project__in=self.projects) if self.projects else Q()
        tag = self.tag_manager.filter(query).get(slug=tag)
        if resources is not None:
            _resources = self.resource_manager.none()
            for resource in resources:
                self._validate_resource(tag, resource["project"])
                _resources |= self.resource_manager.filter(
                    project=resource["project"], path=resource["path"]
                )
            tag.resources.add(*list(_resources))

    def unlink(self, tag, resources):
        """
        Unassociate Resources from a Tag.

        The Resources can be selected by passing a list of Resource paths.
        """
        query = Q(project__in=self.projects) if self.projects else Q()
        if resources is not None:
            _resources = self.resource_manager.none()
            for resource in resources:
                _resources |= self.resource_manager.filter(
                    project=resource["project"], path=resource["path"]
                )
            self.tag_manager.filter(query).get(slug=tag).resources.remove(
                *list(_resources)
            )

    def _validate_resource(self, tag, resource_project):
        if tag.project_id and resource_project != tag.project_id:
            raise InvalidProjectError(
                "Cannot add Resource from Project (%s) to Tag (%s)"
                % (resource_project, self.slug)
            )
