============
Contributing
============

Source code
===========

Pontoon source code is available via GitHub:

https://github.com/mozilla/pontoon


Bugs
====

All bugs are tracked in `<https://bugzilla.mozilla.org/>`_.

Write up a new bug:

https://bugzilla.mozilla.org/enter_bug.cgi?product=Webtools&component=Pontoon


Docker
======

Everything runs in a Docker container. Thus Pontoon requires fewer things to get
started and you're guaranteed to have the same setup as everyone else and it
solves some other problems, too.

If you're not familiar with `Docker <https://docs.docker.com/>`_ and
`docker-compose <https://docs.docker.com/compose/overview/>`_, it's worth
reading up on.


Database
========

By default, you will have default data loaded for only the Pontoon Intro project.
If you have a database dump, you can load it into your PostgreSQL database.

Make sure you backup your existing database first:

.. code-block:: shell

    $ make dumpdb

And then load the dump:

.. code-block:: shell

    $ make loaddb DB_DUMP_FILE=path/to/my/dump

Note that your database container needs to be running while you do that. You
can start just the postgresql container by running:

.. code-block:: shell

    $ docker-compose run postgresql -d


Interactive shell
=================

If you need to run specific commands, that are not covered by our `Makefile`,
you can start an interactive shell inside a Pontoon container:

.. code-block:: shell

    $ make shell


Browser Support
===============

The list of browsers supported by Pontoon is defined in the `"browserslist"` entry of the root package.json, and contains by default:

.. code-block:: bash

    Firefox >= 78
    Chrome >= 80
    Edge >= 91
    Safari >= 13.1


Code style
==========

We use code formatters so that we do not have to fight over code style.
You are free to write code however you like, because in the end the formatter is the one
that will format it. We thus don't need to pay attention to style during
code reviews, and are free from those never-ending code style discussions.

To format the Python and the JavaScript code at once you can use:

.. code-block:: shell

    $ make format

Code formatting is explained in more detail in the following sections.


Python code conventions
=======================

Our Python code is automatically formatted using `black <https://black.readthedocs.io/en/stable/>`_.
We enforce that in our Continuous Integration, so you will need to run
black on your code before sending it for review.

You can run black locally either as an
`add-on in your code editor <https://black.readthedocs.io/en/stable/editor_integration.html>`_,
or as a `git pre-hook commit <https://black.readthedocs.io/en/stable/version_control_integration.html>`_.
Alternatively, you can format your code using:

.. code-block:: shell

    $ make black

Additionally, we use a linter to verify that imports are correct. You can run it with:

.. code-block:: shell

    $ make flake8

In the rare case when you cannot fix a flake8 error, use ``# noqa`` to make the linter
ignore that error. Note that in most cases, it is better to fix the issues than ignoring them.


Javascript code conventions
===========================

Our Javascript code is automatically formatted using `Prettier <https://prettier.io/docs/en/index.html>_`.
We enforce that in our Continuous Integration, so you will need to run
prettier on your code before sending it for review.

You can run prettier locally either as an
`add-on in your code editor <https://prettier.io/docs/en/editors.html>`_,
or as a `git pre-hook commit <https://prettier.io/docs/en/precommit.html>`_.
Alternatively, you can format your code using:

.. code-block:: shell

    $ make prettier 

Additionally, there are linting rules that are defined in our
``.eslintrc.js`` file. To run the linter, do:

.. code-block:: shell

    $ make eslint

In the rare case when you cannot fix an eslint error, use ``// eslint-disable`` to make the linter
ignore that error. Note that in most cases, it is better to fix the issues than ignore them.

For more specifics about the ```frontend`` folder, look at the README.md file there.


Git conventions
===============

The first line is a summary of the commit. It should start with one of the following::

    Fix bug XXXXXXX

or::

    Bug XXXXXXX


The first, when it lands, will cause the bug to be closed. The second one does not.

After that, the commit should explain *why* the changes are being made and any
notes that future readers should know for context or be aware of.

We follow `The seven rules of a great Git commit message <https://chris.beams.io/posts/git-commit/#seven-rules>`_:

1. Separate subject from body with a blank line
2. Limit the subject line to 50 characters
3. Capitalize the subject line
4. Do not end the subject line with a period
5. Use the imperative mood in the subject line
6. Wrap the body at 72 characters
7. Use the body to explain what and why vs. how


Pull requests
=============

Pull request summary should indicate the bug the pull request addresses.

Pull request descriptions should cover at least some of the following:

1. what is the issue the pull request is addressing?
2. why does this pull request fix the issue?
3. how should a reviewer review the pull request?
4. what did you do to test the changes?
5. any steps-to-reproduce for the reviewer to use to test the changes


Code reviews
============

Pull requests should be reviewed before merging.

Style nits should be covered by linting as much as possible.

Code reviews should review the changes in the context of the rest of the system.


Dependencies
============

Direct dependencies for Pontoon are distributed across three files:

1. ``requirements/default.in``: Running Pontoon in production
2. ``requirements/dev.in``: Development
3. ``requirements/test.in``: Testing
4. ``requirements/lint.in``:  Linting

In order to pin and hash the direct and indirect dependencies, we use `pip-compile <https://pypi.org/project/pip-tools/>`_,
which yields corresponding ``*.txt`` files. These ``*.txt`` files contain all direct and indirect dependencies,
and can be used for installation with ``pip``. After any change to the ``*.in`` files,
you should run the following command to update all ``requirements/*.txt`` files.

.. code-block:: shell

    $ make requirements

When adding a new requirement, add it to the appropriate ``requirements/*.in`` file.
For example, to add the development dependency ``foobar`` version 5, add ``foobar==5`` to ``requirements/dev.in``,
and then run the command from above.

Once you are done adding, removing or updating requirements, rebuild your docker environment:

.. code-block:: shell

    $ make build

If there are problems, it'll tell you.

To upgrade existing dependencies within the given constraints of the input
files, you can pass options through to the ``pip-compile`` invocations, i.e.

.. code-block:: shell

    $ make requirements opts=--upgrade

Documentation
=============

Documentation for Pontoon is built with `Sphinx
<http://www.sphinx-doc.org/en/stable/>`_ and is available on ReadTheDocs.

Building docs is not covered with docker yet, so you will have to do it on your host. To make
a virtualenv to build docs, do this:

.. code-block:: shell

    $ cd docs/
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install --require-hashes -r requirements.txt

Then, to build the docs, run this:

.. code-block:: shell

    $ make html

The HTML documentation will be in `docs/_build/html/`. Try to open `docs/_build/html/index.html`
for example.

.. note:: Pontoon uses `GraphViz`_ as part of the documentation generation, so
   you'll need to install it to generate graphs that use it. Most package
   managers, including `Homebrew`_, have a package available for install.

.. _GraphViz: http://www.graphviz.org/
.. _Homebrew: http://brew.sh/


Running tests
=============

To run the entire test suite, do:

.. code-block:: shell

    $ make test


To run only the ``frontend`` tests:

.. code-block:: shell

    $ make jest


To run only the Python tests:

.. code-block:: shell

    $ make pytest


To run specific tests or specify arguments, you'll want to start a shell in the
test container:

.. code-block:: shell

    $ make shell


Then you can run tests as you like.

Running all the unittests (make sure you run ``./manage.py collectstatic`` first):

.. code-block:: shell

    app@...:/app$ pytest


Running a directory of tests:

.. code-block:: shell

    app@...:/app$ pytest pontoon/base/


Running a file of tests:

.. code-block:: shell

    app@...:/app$ pytest pontoon/base/tests/test_views.py


Writing tests
=============

Put your tests in the ``tests/`` directory of the appropriate app in
``pontoon/``.


Mock usage
----------

`Mock <http://www.voidspace.org.uk/python/mock/>`_ is a python library for mocks
objects. This allows us to write isolated tests by simulating services besides
using the real ones. Best examples are existing tests which admittedly do mocking
different depending on the context.

Tip! Try to mock in limited context so that individual tests don't affect other
tests. Use context managers instead of monkey patching imported modules.


Updating Your Local Instance
============================

When changes are merged into the main Pontoon repository, you'll want to update
your local development instance to reflect the latest version of the site. You
can use Git as normal to pull the latest changes, but if the changes add any new
dependencies or alter the database, you'll want to install any new libraries and
run any new migrations.

If you're unsure what needs to be run, it's safe to just perform all of these
steps, as they don't affect your setup if nothing has changed:

.. code-block:: shell

   # Pull the latest code (assuming you've already checked out master).
   git pull origin master

   # Install new dependencies or update existing ones.
   pip install -U --force --require-hashes -r requirements/default.txt

   # Run database migrations.
   python manage.py migrate


Building front-end resources
============================

We use webpack to build our JavaScript files for some pages. While `make build` will build
those files for you, you might want to rebuild them while programming on the front. To build
the files just once, run:

.. code-block:: shell

    $ make build-frontend

If you want to have those files be built automatically when you make changes, you can run:

.. code-block:: shell

    $ make build-frontend-w
