from django.conf.urls import url
import views

urlpatterns = [
    # Sites pages
    url(r'^tiles/$', views.sites_snippet_page,
        kwargs=dict(template="tiles.html",
                    repository_url="https://svn.mozilla.org/projects/l10n-misc/trunk/firefoxtiles/en-US/",
                    default_filename="tiles.lang"),
        name='sites-tiles'),
    url(r'^snippets/$', views.sites_snippet_page,
        kwargs=dict(template="snippets.html",
                    repository_url="https://svn.mozilla.org/projects/l10n-misc/trunk/snippets/en-US/",
                    default_filename="jan2014.lang"),
        name='sites-snippets'),
    url(r'^updater/$', views.sites_snippet_page,
        kwargs=dict(template="updater.html",
                    repository_url="https://svn.mozilla.org/projects/l10n-misc/trunk/firefoxupdater/en-US/",
                    default_filename="updater.lang"),
        name='sites-updater'),
]
