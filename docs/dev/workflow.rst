Workflow
========
The following is a list of things you'll probably need to do at some point while
working on Pontoon.

Running Tests
-------------
You can run the automated test suite with the following command:

.. code-block:: bash

   python manage.py test

Updating Your Local Instance
----------------------------
When changes are merged to the main Pontoon repository, you'll want to update
your local development instance to reflect the latest version of the site. You
can use Git as normal to pull the latest changes, but if the changes add any new
dependencies or alter the database, you'll want to install any new libraries and
run any new migrations.

If you're unsure what needs to be run, it's safe to just perform all of these
steps, as they don't affect your setup if nothing has changed:

.. code-block:: bash

   # Pull latest code (assuming you've already checked out master).
   git pull origin master

   # Install new dependencies or update existing ones.
   pip install -U --force --require-hashes -r requirements.txt

   # Run database migrations.
   python manage.py migrate

Building the Documentation
--------------------------

Before you can build the documentation, you will need to install a few
dependencies. It is recommended to do that in a Python virtual environment:

.. code-block:: bash

    cd docs
    virtualenv venv
    source venv/bin/activate
    pip install --require-hashes -r requirements.txt

You can build the documentation with the following command:

.. code-block:: bash

   # From the docs/ subdirectory
   make html

After running this command, the documentation should be available at
``docs/_build/html/index.html``.

.. note:: Pontoon uses `GraphViz`_ as part of the documentation generation, so
   you'll need to install it to generate graphs that use it. Most package
   managers, including `Homebrew`_, have a package available for install.

.. _GraphViz: http://www.graphviz.org/
.. _Homebrew: http://brew.sh/

Adding New Dependencies
-----------------------

Pontoon uses pip_ to install dependencies, and since version 8, that tool
checks downloaded packages to ensure they haven't been tampered with.

Because of this, adding a new library to ``requirements.txt`` is a bit more work
as you need to add hashes for each library you want to install. To help make
this easier, you can use the hashin_ tool to add new dependencies to the
requirements file.

.. _pip: https://pip.pypa.io/
.. _hashin: https://github.com/peterbe/hashin/
