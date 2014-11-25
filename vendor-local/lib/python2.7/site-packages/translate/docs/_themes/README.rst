Bootstrap theme for Sphinx
==========================

This repository includes a Bootstrap-based Sphinx theme used for the
documentation of Translate's software.

Installation
------------

Add this repository contents as *_theme* into your docs folder. You can also
add it as a `git submodule <http://git-scm.com/book/en/Git-Tools-Submodules>`_,
which is probably the best idea. You need to run the following from the root of
your repository::

    git submodule add git://github.com/translate/sphinx-themes.git docs/_themes/

Adjust the necessary configuration options in *conf.py*::

    sys.path.insert(0, os.path.abspath('.'))
    html_theme_path = ['_themes']
    html_theme = 'sphinx-bootstrap'
