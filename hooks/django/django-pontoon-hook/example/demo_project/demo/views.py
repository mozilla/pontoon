from django.utils.translation import ugettext as _
from django.http import HttpResponse
from demo.forms import DemoForm
from django.shortcuts import render_to_response
from django.template import RequestContext

def home(request):
    message = _("Hello, world")
    form = DemoForm()
    return render_to_response('home.html',
            {'message': message, 'form': form},
            context_instance=RequestContext(request))

