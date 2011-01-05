"""Example views. Feel free to delete this app."""

from django import http

import jingo


def home(request):
    data = {}
    return jingo.render(request, 'examples/home.html', data)
