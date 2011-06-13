"""Example views. Feel free to delete this app."""

from django import http
from django.views.decorators.csrf import csrf_exempt

import bleach
import jingo


def home(request):
    """Main example view."""
    data = {}  # You'd add data here that you're sending to the template.
    return jingo.render(request, 'examples/home.html', data)


@csrf_exempt
def bleach_test(request):
    """A view outlining bleach's input sanitization."""
    allowed_tags = ('strong', 'em')

    data = {}

    if request.method == 'POST':
        bleachme = request.POST.get('bleachme', None)
        data['bleachme'] = bleachme
        if bleachme:
            data['bleached'] = bleach.clean(bleachme, tags=allowed_tags)

    return jingo.render(request, 'examples/bleach.html', data)
