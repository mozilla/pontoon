Developer Setup
===============

The following describes how to set up an instance of the site on your
computer for development with Docker.

   .. Warning::

    These installation steps are made for development only. It is not
    recommended to run Pontoon via Docker in production.

Prerequisites
-------------

1. Install `Docker <https://docs.docker.com/install/>`_.

2. Install `Node.js 14 and npm 7 or later <https://docs.npmjs.com/downloading-and-installing-node-js-and-npm>`_.

3. Install `make <https://www.gnu.org/software/make/>`_ using either your
   system's package manager (Linux) or Xcode command line developer tools (OSX).
   On Windows, you can use `MozillaBuild <https://wiki.mozilla.org/MozillaBuild>`_.

Quickstart
----------

1. Clone the `Pontoon repository <https://github.com/mozilla/pontoon>`_::

     $ git clone https://github.com/mozilla/pontoon.git

   .. Note::

        To contribute changes to the project, you will need to
        `fork <https://help.github.com/en/github/getting-started-with-github/fork-a-repo>`_
        the repository under your own GitHub account.


2. From the root of the repository, run::

     $ make build

   That will install Pontoon's JS dependencies,
   build the frontend packages, and build the server container.

   .. Note::

        If you want to share your development instance in your local network,
        set SITE_URL to bind the server to any address you like, e.g.
        ``make build SITE_URL="http://192.168.1.14:8000"``.


3. Run the webapp::

      $ make run

   .. Note::

        The first time you run this, the PostgreSQL container needs to do
        some work before it becomes available to the server container. Hence,
        the server might not be able to perform things like migrations.
        You can simply wait for the postgresql container to report that it's
        ready, then abort the process, then restart it. That should let the
        server do all its setup as expected.

        Alternatively, you can run ``docker-compose up postgresql`` and wait
        until it reports that the database is ready, then stop that and run
        ``make run``.


4. Finally, you need to run some setup steps, while the server is running::

      $ make setup

   This will ask you to create a superuser, and then will update your Firefox
   account settings.

The app should now be available at http://localhost:8000 or the custom SITE_URL.

And with that, you're ready to start :doc:`contributing`!

Installing Docker on Windows Pro/Enterprise/Education
-----------------------------------------------------

Install `Docker Desktop for Windows <https://docs.docker.com/desktop/install/windows-install/>`_.

Install tools (git, make, cygwin)
+++++++++++++++++++++++++++++++++

The easiest way is to use a package manager like
`Chocolatey <https://chocolatey.org/install>`_. Follow the installation
instructions for Windows Powershell (Admin), then run
``choco install make git cygwin`` to install all packages.

Follow the prompt requests allowing script execution. At the end, verify that
packages are available with ``make --version`` and ``git --version``, it should
return a version for each command.

At this point you need to disable the config ``core.autocrlf`` before cloning
the Pontoon repository, otherwise all files will use Windows line-endings
(CRLF), and docker images will fail to build. To do so, open a Powershell as
Admin (right click on the Start Menu, select *Windows Powershell (Admin)*), and
run::

   git config --system --unset core.autocrlf
   git config --global core.autocrlf false

You can use ``git config -l`` to verify that the value for ``core.autocrlf`` is
correctly set.

At this point, you can open the *Cygwin64 Terminal* and proceed with the
installation (the content of ``C:`` will be available in ``/cygdrive/c``). Once
the Docker image is running, Pontoon's instance will be available at
`http://localhost:8000`.
