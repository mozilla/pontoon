from django.http import Http404
from django.views.generic import DetailView
from pontoon.base.models import Project
from pontoon.base.utils import is_ajax
from pontoon.tags.utils import Tags


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
        if is_ajax(request):
            return self.get_AJAX(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_AJAX(self, request, *args, **kwargs):
        self.template_name = "projects/includes/teams.html"
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        tags = Tags(project=self.object, slug=self.kwargs["tag"])
        tag = tags.get_tag_locales()

        if not tag:
            raise Http404

        if is_ajax(self.request):
            return dict(
                project=self.object,
                locales=tag.locales,
                tag=tag,
            )

        return dict(project=self.object, tag=tag)
