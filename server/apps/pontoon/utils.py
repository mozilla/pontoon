import os
import commands

try:
    import sys
    sys.path.append('/Users/zbraniecki/projects/silme/lib')
    import silme.core
    import silme.format
    import silme.io
    silme.format.Manager.register('gettext')
except:
    raise


def generate_po(ids, values, path):
    elist = silme.core.EntityList()
    elist.id = 'messages.po'
    for i,id in enumerate(ids):
        entity = silme.core.Entity(id.replace('"','\\"'))
        entity.value = values[i].replace('"','\\"')
        elist.add_entity(entity)
    if not os.path.isdir(path):
        os.makedirs(path)
    ioc = silme.io.Manager.get('file')
    ioc.write_entitylist(elist, path=path,encoding='utf8')

def localize_html(ids, values, path):
    pass

def compile_po(path):
    commands.getstatusoutput('msgfmt %s -o %s' % (os.path.join(path, 'messages.po'),
                                                  os.path.join(path, 'messages.mo')))

def normalize_project_name(name):
    '''
    extracts the project name from the URL path, for example:
    http://foo.tld/projects/boo/ -> boo
    http://foo.tld/ -> foo.tld
    etc.
    '''
    if name[-1]=='/': # remove trailing slash
        name = name[:-1]
    sl = name.rfind('/')
    if name.rfind('.', sl)!=-1: # if there's a file name at the end like: foo.php
        name = name[:name.rfind('.', sl)]
    name = name[name.rfind('/')+1:]
    return name
