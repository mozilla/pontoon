
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from pontoon.base.models import Project
from pontoon.base.utils import require_AJAX

from .utils import TagsTool

from django.views.generic import DetailView


class ProjectTagView(DetailView):
    """This view provides both the html view and the JSON view for
    retrieving results in the /projects/$project/tags/$tag view
    """
    model = Project
    slug_url_kwarg = 'project'
    template_name = 'tags/tag.html'

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.get_AJAX(request, *args, **kwargs)
        return super(ProjectTagView, self).get(request, *args, **kwargs)

    def get_AJAX(self, request, *args, **kwargs):
        self.template_name = 'projects/includes/teams.html'
        return super(ProjectTagView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        try:
            tag = TagsTool(
                projects=[self.object],
                priority=True).get()
        except IndexError:
            raise Http404
        if self.request.is_ajax():
            return dict(project=self.object, locales=list(tag.iter_locales()))
        return dict(project=self.object, tag=tag)


@require_AJAX
def ajax_tags(request, slug=None):
    """This view provides JSON view for retrieving results in the
    /projects/$project/tags view
    """
    project = get_object_or_404(Project, slug=slug)
    if project.tags_enabled:
        project = [project]
    else:
        raise Http404
    tags_tool = TagsTool(
        projects=project,
        priority=True)
    return render(
        request, 'projects/includes/tags.html', {
            'project': project,
            'tags': list(tags_tool)})
