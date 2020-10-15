from django.http import Http404

from .utils import TagsTool
from pontoon.base.models import Project

from django.views.generic import DetailView


class ProjectTagView(DetailView):
    """This view provides both the html view and the JSON view for
    retrieving results in the /projects/$project/tags/$tag view
    """

    model = Project
    slug_url_kwarg = "project"
    template_name = "tags/tag.html"

    def get_queryset(self):
        return super().get_queryset().visible_for(self.request.user)

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.get_AJAX(request, *args, **kwargs)
        return super(ProjectTagView, self).get(request, *args, **kwargs)

    def get_AJAX(self, request, *args, **kwargs):
        self.template_name = "projects/includes/teams.html"
        return super(ProjectTagView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        try:
            tag = TagsTool(projects=[self.object], priority=True,)[
                self.kwargs["tag"]
            ].get()
        except IndexError:
            raise Http404

        if self.request.is_ajax():
            return dict(project=self.object, locales=list(tag.iter_locales()), tag=tag,)

        return dict(project=self.object, tag=tag)
