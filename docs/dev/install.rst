Developer Setup
===============
The following describes how to set up an instance of the site on your
computer for development.

Prerequisites
-------------
This guide assumes you have already installed and set up the following:

1. Git_
2. `Python 2.7`_, pip_, and virtualenv_
3. `Node.js`_ and npm_
4. `Postgres 9.4 or 9.5`_

These docs assume a Unix-like operating system, although the site should, in
theory, run on Windows as well. All the example commands given below are
intended to be run in a terminal.  If you're on Ubuntu 16.04, you can install
all the prerequisites using the following command:

   .. code-block:: bash

      sudo apt install git python-pip nodejs-legacy npm postgresql postgresql-server-dev-9.5 libxml2-dev libxslt1-dev python-dev libmemcached-dev

.. _Git: https://git-scm.com/
.. _Python 2.7: https://www.python.org/
.. _pip: https://pip.pypa.io/en/stable/
.. _virtualenv: https://virtualenv.pypa.io/en/latest/
.. _Node.js: https://nodejs.org/
.. _npm: https://www.npmjs.com/
.. _Postgres 9.4 or 9.5: http://www.postgresql.org/

Installation
------------
1. Clone this repository or your fork_:

   .. code-block:: bash

      git clone --recursive https://github.com/mozilla/pontoon.git
      cd pontoon

2. Create a virtualenv for Pontoon and activate it:

   .. code-block:: bash

      virtualenv venv
      source ./venv/bin/activate

   .. note::

      Whenever you want to work on Pontoon in a new terminal you'll have to
      re-activate the virtualenv. Read the virtualenv_ documentation to learn
      more about how virtualenv works.

3. Install the dependencies using the latest version of pip_:

   .. code-block:: bash

      pip install --require-hashes -r requirements.txt

4. Create a ``.env`` file at the root of the repository to configure the
   settings for your development instance. It should look something like this:

   .. code-block:: ini

      SECRET_KEY=insert_random_key
      DJANGO_DEV=True
      DJANGO_DEBUG=True
      DATABASE_URL=postgres://pontoon:asdf@localhost/pontoon
      SESSION_COOKIE_SECURE=False
      SITE_URL=http://localhost:8000

   Make sure to make the following modifications to the template above:

   - ``SECRET_KEY`` should be set to some random key you come up with,
     as it is used to secure the authentication data for your local
     instance.

   - ``DATABASE_URL`` should contain the connection data for connecting to
     your Postgres database. It takes the form
     ``postgres://username:password@server_addr/database_name``.

   - ``SITE_URL`` should be set to the URL you will use to connect to your
     local development site. Some people prefer to use
     ``http://127.0.0.1:8000`` instead of ``localhost``.

5. Initialize your database by running the migrations:

   .. code-block:: bash

      python manage.py migrate

6. Create a new superuser account:

   .. code-block:: bash

      python manage.py createsuperuser

   Make sure that the email address you use for the superuser account matches
   the email that you will log in with via Persona.

7. Pull the latest strings from version control for the Pontoon Intro project
   (which is automatically created for you during the database migrations):

   .. code-block:: bash

      python manage.py sync_projects --no-commit pontoon-intro

8. Install the required Node libraries using ``npm``:

   .. code-block:: bash

      npm install

Once you've finished these steps, you should be able to start the site by
running:

.. code-block:: bash

   python manage.py runserver

The site should be available at http://localhost:8000.

.. _pip: https://pip.pypa.io/en/stable/
.. _fork: http://help.github.com/fork-a-repo/
.. _issue: https://bugs.python.org/issue18378

Extra settings
--------------
The following extra settings can be added to your ``.env`` file.

``MICROSOFT_TRANSLATOR_API_KEY``
   Set your `Microsoft Translator API key`_ to use machine translation.
``GOOGLE_ANALYTICS_KEY``
   Set your `Google Analytics key`_ to use Google Analytics.
``MOZILLIANS_API_KEY``
   Set your `Mozillians API key`_ to grant permission to Mozilla localizers.

.. _Microsoft Translator API key: http://msdn.microsoft.com/en-us/library/hh454950
.. _Google Analytics key: https://www.google.com/analytics/
.. _Mozillians API key: https://wiki.mozilla.org/Mozillians/API-Specification
