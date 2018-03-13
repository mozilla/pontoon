
from django.conf.urls import url

import views


urlpatterns = [

    url(r'^projects/(?P<project>[\w-]+)/tags/$',
        views.ProjectTagsView.as_view(),
        name='pontoon.project.tags'),

    url(r'^tags/ajax/(?P<project>[\w-]+)/$',
        views.ProjectTagsDashboardAjaxView.as_view(),
        name='pontoon.tags.ajax.project.tags'),

    # Project tag page
    url(r'^projects/(?P<project>[\w-]+)/tags/(?P<tag>[\w-]+)/$',
        views.ProjectTagView.as_view(),
        name='pontoon.tags.project.tag'),

    url(r'^tags/ajax/(?P<project>[\w-]+)/(?P<tag>[\w-]+)/$',
        views.ProjectTagDashboardAjaxView.as_view(),
        name='pontoon.tags.ajax.project.tag'),

]
