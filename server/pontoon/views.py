from django.shortcuts import render_to_response
from django.http import HttpResponse
from utils import generate_po, compile_po, normalize_project_name
from models import Project

import os

def stats(request):
    return render_to_response('pontoon/stats.html', {
    });

def push(request):
    if request.method == 'OPTIONS':
        response = HttpResponse('')
        response['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']
        response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response['Access-Control-Max-Age'] = 1728000  
        return response
    if request.method == 'GET':
        return HttpResponse('GET is not allowed here')
    lang = request.POST.get('locale', '')
    project = request.POST.get('project', '')
    project = normalize_project_name(project)
    try:
        po = Project.objects.get(name=project)
    except:
        return HttpResponse('Project "%s" not registered' % project)
    project_path = './po/%s' % project
    po_path = '%s/LC_MESSAGES' % lang
    path = os.path.join(project_path, po_path)
    ids = request.POST.getlist('id')
    values = request.POST.getlist('value')

    generate_po(ids, values, path)
    compile_po(path)
    response = HttpResponse('OK')
    return response
