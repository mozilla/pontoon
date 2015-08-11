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
   ./bin/peep.py install -r requirements.txt

   # Run database migrations.
   python manage.py migrate

Building the Documentation
--------------------------
You can build the documentation with the following command:

.. code-block:: bash

   # Enter the docs/ subdirectory
   cd docs
   make html

After running this command, the documentation should be available at
``docs/_build/html/index.html``.

Adding New Dependencies
-----------------------
Pontoon uses peep_ to install dependencies. Peep is a wrapper around pip that
checks downloaded packages to ensure they haven't been tampered with.

Because of this, adding a new library to ``requirements.txt`` is a bit more work
as you need to add hashes for each library you want to install. To help make
this easier, you can use the peepin_ tool to add new dependencies to the
requirements file.

.. _peep: https://github.com/erikrose/peep/
.. _peepin: https://github.com/peterbe/peepin/
