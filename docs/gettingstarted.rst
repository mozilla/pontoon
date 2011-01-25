Getting started
===============

Requirements
------------

You need Python 2.6.

To check out playdoh, run::

    git clone --recursive git://github.com/mozilla/playdoh.git

This project is set up to use a vendor library, i.e. a subdirectory ``vendor``
that contains all pure Python libraries required by this project. The recursive
checkout will also clone these requirements.

In addition, there are compiled libraries (such as Jinja2) that you will need
to build yourself, either by installing them from ``pypi`` or by using your
favorite package manager for your OS.

For development, you can run this in a `virtualenv environment`_::

    easy_install pip
    pip install -r requirements/compiled.txt

For more information on vendor libraries, read :ref:`packages`.

.. _virtualenv environment: http://pypi.python.org/pypi/virtualenv


Starting a project based on playdoh
-----------------------------------
The default branch of playdoh is ``base``. To start a new project, you fork
playdoh and start working on your app in ``master`` (branched from base). If
you start adding pieces that should go back into playdoh, you can apply the
patch to base and move it upstream.

Eventually you'll probably diverge enough that you'll want to delete the base
branch.
