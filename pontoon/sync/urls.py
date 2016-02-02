from django.conf.urls import url

from pontoon.sync import views


urlpatterns = [
    url(r'^sync/log/$', views.sync_log_list, name='pontoon.sync.logs.list'),

    url(r'^sync/log/(?P<sync_log_pk>\d+)/', views.sync_log_details,
        name='pontoon.sync.logs.details'),
]
