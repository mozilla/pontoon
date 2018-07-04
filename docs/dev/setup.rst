Developer Setup
===============

The following describes how to set up an instance of the site on your
computer for development with Docker and docker-compose.

   .. Warning::

    These installation steps are made for development only. It is not
    recommended to run Pontoon via Docker in production.

Prerequisites
-------------

1. Install `Docker <https://docs.docker.com/engine/installation/>`_.

2. Install `docker-compose <https://docs.docker.com/compose/install/>`_. You need
   1.10 or higher.

3. Install `make <https://www.gnu.org/software/make/>`_ using either your
   system's package manager (Linux) or Xcode command line developer tools (OSX).
   On Windows, you can use `MozillaBuild <https://wiki.mozilla.org/MozillaBuild>`_.

Quickstart
----------

Make sure to clone the repository using the ``--recursive`` option, or
initialize submodules with ``git submodule update --init --recursive``.

1. From the root of the repository, run::

     $ make build

   That will build the containers required for development: base and
   webapp.

   If you want to share your development instance in your local network, you set SITE_URL to bind
   the webapp to any address you like.

     $ make build SITE_URL="https://192.168.1.14:8000"


2. Then run the webapp::

      $ make run

   .. Note::

        The first time you run this, the PostgreSQL container needs to do
        some work before it becomes available to the webapp container. Hence,
        the webapp might not be able to perform things like migrations.
        You can simply wait for the postgresql container to report that it's
        ready, then abort the process, then restart it. That should let the
        webapp do all its setup as expected.

        Alternatively, you can run ``docker-compose up postgresql`` and wait
        until it reports that the database is ready, then stop that and run
        ``make dockerrun``.

3. Finally you need to run some setup steps, while the webapp is running::

      $ make setup

   This will ask you to create a superuser, and then will update your Firefox
   account settings.

At that point, you're good to go. Access the webapp via this URL: http://localhost:8000/ or the custom SITE_URL.


Database
--------

By default, you will have default data loaded for only the Pontoon Intro project.
If you have a database dump, you can load it into your PostgreSQL database by running::

    $ make loaddb DB_DUMP_FILE=path/to/my/dump

Note that your database container needs to be running while you do that. You
can start just the postgresql container by runnin::

    $ docker-compose run postgresql

Running tests
-------------

To run the entire test suite, simply run::

    $ make test

If you want to run only some unit tests, or want to avoid rebuilding the
docker container every time you run tests, you can start a shell that will
allow to run your own commands. To do that, run::

    $ make shell
    app@675af05d66ae:/app$ python manage.py test

Building front-end resources
----------------------------

We use webpack to build our JavaScript files for some pages. While `make build` will build
those files for you, you might want to rebuild them while programming on the front. To build
the files just once, run::

   $ make build-frontend

If you want to have those files be built automatically when you make changes, you can run::

   $ make build-frontend-w
