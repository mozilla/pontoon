Developer Setup with Docker
===========================

The following describes how to set up an instance of the site on your
computer for development with Docker and docker-compose.

   .. Warning::

    These installation steps are made for development only. It is not
    recommended to run Pontoon via Docker in production.

   .. Note::

    Installation via Docker is still a fresh feature. Problems might happen,
    bugs might be met. If you have any troubles with it, please
    `file a bug <https://bugzilla.mozilla.org/enter_bug.cgi?product=Webtools&component=Pontoon>`_
    or `propose a patch <https://github.com/mozilla/pontoon>`_!

Prerequisites
-------------

1. Install `Docker <https://docs.docker.com/engine/installation/>`_.

2. Install `docker-compose <https://docs.docker.com/compose/install/>`_. You need
   1.10 or higher.

3. Install `make <https://www.gnu.org/software/make/>`_ using either your
   system's package manager (Linux) or homebrew (OSX) or FIXME (Windows).

Quickstart
----------

1. From the root of this repository, run::

     $ make dockerbuild

   That will build the containers required for development: base and
   webapp.

2. Then run the webapp::

      $ make dockerrun

   .. Note::

        The first time you run this, the PostgreSQL container needs to do
        some work before it becomes available to the webapp container. Hence,
        the webapp might not be able to perform things like migrations.
        You can simply wait for the postgresql container to report that it's
        ready, then abort the process, then restart it. That should let the
        webapp do all its setup as expected.

3. Finally you need to run some setup steps, while the webapp is running::

      $ make dockersetup

   This will ask you to create a superuser, and then will update your Firefox
   account settings.

At that point, you're good to go. Access the webapp via this URL: http://localhost:8000/
