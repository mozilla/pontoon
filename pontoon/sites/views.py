import logging
from urlparse import urljoin
import urllib2

from django.shortcuts import render

from django.http import HttpResponseBadRequest

log = logging.getLogger('pontoon')


def sites_snippet_page(request, template, repository_url, default_filename):
    """Downloads snippets file from given repository_url and passes it to given template."""
    try:
        snippets_file = request.GET.get('file', default_filename)
        snippets_contents = urllib2.urlopen(urljoin(repository_url, snippets_file)).read()
        snippets = [s[1:].decode('utf-8') for s in snippets_contents.splitlines() if s.startswith(';')]
    except IOError:
        log.error('Sites download error: %s', urljoin(repository_url, snippets_file))
        return HttpResponseBadRequest("Couldn't download or find file: %s" % urljoin(repository_url, snippets_file))

    try:
        # Previous php version starts from indexes from 1.
        snippet_index = int(request.GET.get('snippet', 1))-1
        if len(snippets) <= snippet_index: raise ValueError()
    except ValueError:
        return HttpResponseBadRequest("Snippet index is invalid")

    return render(request, "sites/{}".format(template), dict(snippets=snippets,
        snippet_index=snippet_index))