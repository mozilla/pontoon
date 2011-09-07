import os
import sys

sys.path.append('../silme/lib')

import mozilla.l10n.paths
import silme.io
import silme.format
import silme.core

ioc = silme.io.Manager.get('file')

def get_app_package(project_repo_path,
                    l10n_repo_path,
                    app='browser',
                    locale='en-US'):
    pack = silme.core.Package(id=None)

    modules = mozilla.l10n.paths.get_modules(project_repo_path, app)
    locales_path = mozilla.l10n.paths.get_locales_path(locale)

    if locale == 'en-US':
        repo_path = project_repo_path
    else:
        repo_path = os.path.join(l10n_repo_path, locale)

    for module in modules:
        path = os.path.join(repo_path, module, locales_path)
        if os.path.exists(path):
            subpack = ioc.get_package(path, object_type='structure')
            p = os.path.split(module)
            subpack.id = p[1]
            pack.add_package(subpack, path=p[0])
    return pack
