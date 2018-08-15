from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_sameorigin


@xframe_options_sameorigin
def intro(request):
    return render(request, 'intro.html')
