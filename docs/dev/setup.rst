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

1. Clone your `fork <https://help.github.com/fork-a-repo/>` of Pontoon repository::

     $ git clone https://github.com/YOUR-USERNAME/pontoon.git


2. From the root of the repository, run::

     $ make build

   That will build the containers required for development: base and
   webapp.

   If you want to share your development instance in your local network, you set SITE_URL to bind
   the webapp to any address you like.::

     $ make build SITE_URL="https://192.168.1.14:8000"


3. Run the webapp::

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


4. Finally, you need to run some setup steps, while the webapp is running::

      $ make setup

   This will ask you to create a superuser, and then will update your Firefox
   account settings.

At that point, you're ready to start :doc:`contributing`! Access the webapp via this URL:
http://localhost:8000/ or the custom SITE_URL.
