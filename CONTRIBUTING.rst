============
Contributing
============

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


Python code conventions
=======================

Python code should follow PEP-8.

Max line length is 100 characters.

4-space indentation.

To run the linter, do::

  $ pylama pontoon


If you hit issues, use ``# noqa`` to make the linter ignore that error. Note that in most cases,
it is better to fix the issues than ignoring them.


Javascript code conventions
===========================

2-space indentation.


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

Dependencies for production Pontoon are in ``requirements.txt``. Development dependencies are in
``requirements-dev.txt``. They need to be pinned and hashed, and we use `hashin <https://pypi.python.org/pypi/hashin>`_ for that.

Note that we use a specific format for our dependencies, in order to make them more maintainable. When adding a new requirement, you should add it to the appropriate section and group it with its sub-dependencies if applicable.

For example, to add ``foobar`` version 5::

  $ hashin -r requirements.txt foobar==5

Then open ``requirements.txt`` and move the added dependencies to:
* the first section if it has no other requirements
* the second section if it has sub-dependencies, and add all its dependencies there as well.

That format is documented more extensively inside the ``requirements.txt`` file.

Once you are done adding or updating requirements, rebuild your docker environment::

  $ make dockerbuild

If there are problems, it'll tell you.


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

To run the tests, do::

  $ make dockertest


To run specific tests or specify arguments, you'll want to start a shell in the
test container::

  $ make dockershell


Then you can run tests as you like.

Running all the unittests (make sure you run ``./manage.py collectstatic`` first)::

  app@...:/app$ ./manage.py test


Running a directory of tests::

  app@...:/app$ ./manage.py test pontoon/base/


Running a file of tests::

  app@...:/app$ ./manage.py test pontoon/base/tests/test_views.py


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
   pip install -U --force --require-hashes -r requirements.txt

   # Run database migrations.
   python manage.py migrate


Integration with fluent
=======================

Pontoon is able to synchronize translations produced by libraries provided by
`Project Fluent <http://projectfluent.io/>`_ and provides an advanced editor for translators.

Because of our very close integration, we'll need to compile the fresh versions of
javascript/python libraries in order to provide new features.

It's important to remember to update both packages:

* python-fluent (responsible for e.g. server-side sync process)
* fluent-syntax (required by the fluent editor)

How to build the fresh version of fluent-syntax.js
--------------------------------------------------

.. code-block:: shell

    npm install fluent-syntax
    cp node_modules/fluent-syntax/compat.js pontoon/base/static/js/lib/fluent-syntax.js
