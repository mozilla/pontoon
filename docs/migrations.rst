.. _migrations:

===================
Database Migrations
===================

For database migrations, we use a strikingly simple tool called `schematic
<https://github.com/jbalogh/schematic>`_.

It runs numbered SQL files on top of your existing database. In a table
named ``schema_version``, it remembers what migration number your database
is currently on. If the table does not exist, it considers the database
to be at migration 0 and creates the table.

By default, migrations live in the ``migrations/`` directory. Run schematic
like this::

    schematic migrations/

    # or, when using the vendor library:
    ./vendor/src/schematic/schematic migrations/


Schematic vs. syncdb
--------------------

To create a DB from scratch, Django users run ``./manage.py syncdb``. It
analyzes the models and generates SQL accordingly.

Unfortunately, as the schema evolves, the output of *syncdb* will conflict
with the *schematic* migrations you might have added to evolve older DBs.
To circumvent this, consider the following:

When done creating the first set of models, capture their syncdb-created SQL
output as a baseline migration (number 1)::

    # edit some models in apps/foo/models.py
    ./manage.py sqlall foo > migrations/01-base.sql

Then, as the schema evolves, add incremental migrations as ``02-...sql``, etc.

When setting up a copy of the codebase from scratch in the future, forgo
*syncdb* altogether and after setting your empty database's credentials
correctly in ``settings_local.py``, just run ``schematic migrations/``. It will
run your base migration, followed by incremental updates, and result in a
database that's up to date with your latest existing databases.
