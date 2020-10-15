from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from pontoon.base.views import AjaxFormPostView
from pontoon.base.models import Project
from pontoon.base.utils import require_AJAX, permission_required

from .forms import LinkTagResourcesAdminForm


class ProjectTagAdminAjaxView(AjaxFormPostView):
    form_class = LinkTagResourcesAdminForm

    @method_decorator(require_AJAX)
    @method_decorator(permission_required("base.can_manage_project"))
    def post(self, *args, **kwargs):
        self.project = get_object_or_404(
            Project.objects.visible_for(self.request.user), slug=kwargs["project"]
        )
        self.tag = kwargs["tag"]
        return super(ProjectTagAdminAjaxView, self).post(*args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        kwargs = super(ProjectTagAdminAjaxView, self).get_form_kwargs(**kwargs)
        kwargs["project"] = self.project
        kwargs["data"] = kwargs["data"].copy()
        kwargs["data"]["tag"] = self.tag
        return kwargs
