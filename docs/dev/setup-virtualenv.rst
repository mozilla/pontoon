Developer Setup with virtualenv
===============================

The following describes how to set up an instance of the site on your
computer for development.

   .. Note::

    Installation with virtualenv is not recommended. If possible, please use
    Developer Setup with Docker, which is simpler and makes it easier for us
    to reproduce potential issues.

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

      sudo apt install git python-pip nodejs-legacy npm postgresql postgresql-server-dev-9.5 postgresql-contrib-9.5 libxml2-dev libxslt1-dev python-dev libmemcached-dev virtualenv

If you're on Ubuntu 17.04, you can install all the prerequisites using the following command:

   .. code-block:: bash

      sudo apt install git python-pip nodejs-legacy npm postgresql postgresql-server-dev-9.6 postgresql-contrib-9.6 libxml2-dev libxslt1-dev python-dev libmemcached-dev virtualenv

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

      git clone https://github.com/mozilla/pontoon.git
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

      pip install --require-hashes -r requirements/dev.txt -r requirements/test.txt

4. Create your database, using the following set of commands:

   .. code-block:: bash

      sudo -u postgres psql
      CREATE USER pontoon WITH PASSWORD 'asdf' SUPERUSER;
      CREATE DATABASE pontoon;
      GRANT ALL PRIVILEGES ON DATABASE pontoon to pontoon;
      \q

5. Create a ``.env`` file at the root of the repository to configure the
   settings for your development instance. It should look something like this:

   .. code-block:: ini

      SECRET_KEY=insert_random_key
      DJANGO_DEV=True
      DJANGO_DEBUG=True
      DATABASE_URL=postgres://pontoon:asdf@localhost/pontoon
      SESSION_COOKIE_SECURE=False
      SITE_URL=http://localhost:8000
      FXA_CLIENT_ID=2651b9211a44b7b2
      FXA_SECRET_KEY=a3cafccbafe39db54f2723f8a6f804c337e362950f197b5b33050d784129d570
      FXA_OAUTH_ENDPOINT=https://oauth-stable.dev.lcip.org/v1
      FXA_PROFILE_ENDPOINT=https://stable.dev.lcip.org/profile/v1


   Make sure to make the following modifications to the template above:

   - ``SECRET_KEY`` should be set to some random key you come up with,
     as it is used to secure the authentication data for your local
     instance.

   - ``DATABASE_URL`` should contain the connection data for connecting to
     your Postgres database. It takes the form
     ``postgres://username:password@server_addr/database_name``.

   - ``SITE_URL`` should be set to the URL you will use to connect to your
     local development site. Some people prefer to use
     ``http://127.0.0.1:8000`` instead of ``localhost``. However, should you
     decide to change the ``SITE_URL``, you also need to request_
     the new ``FXA_CLIENT_ID`` and ``FXA_SECRET_KEY``, and our in-context demo
     site ``http://localhost:8000/in-context/`` will require change of base url.

6. Initialize your database by running the migrations:

   .. code-block:: bash

      python manage.py migrate

7. Create a new superuser account:

   .. code-block:: bash

      python manage.py createsuperuser

   Make sure that the email address you use for the superuser account matches
   the email that you will log in with via Firefox Accounts.

8. Pull the latest strings from version control for the Pontoon Intro project
   (which is automatically created for you during the database migrations):

   .. code-block:: bash

      python manage.py sync_projects --projects=pontoon-intro --no-commit

9. After you've provided credentials for your django-allauth provider, you have to update them in database,
   because it's required by django-allauth. You will have to call this command after every change in your
   django-allauth settings (e.g. client key):

   .. code-block:: bash

      python manage.py update_auth_providers

10. Install the required Node libraries using ``npm``:

   .. code-block:: bash

      npm install

11. Run webpack:

   .. code-block:: bash

      ./node_modules/.bin/webpack -p

Once you've finished these steps, you should be able to start the site by
running:

.. code-block:: bash

   python manage.py runserver

The site should be available at http://localhost:8000.

.. _fork: http://help.github.com/fork-a-repo/
.. _issue: https://bugs.python.org/issue18378
.. _request: https://developer.mozilla.org/docs/Mozilla/Tech/Firefox_Accounts/Introduction

Extra settings
--------------
The following extra settings can be added to your ``.env`` file.

``GOOGLE_TRANSLATE_API_KEY``
   Set your `Google Cloud Translation API key`_ to use machine translation by Google.
``MICROSOFT_TRANSLATOR_API_KEY``
   Set your `Microsoft Translator API key`_ to use machine translation by Microsoft.
``GOOGLE_ANALYTICS_KEY``
   Set your `Google Analytics key`_ to use Google Analytics.
``MANUAL_SYNC``
   Enable Sync button in project Admin.

.. _Microsoft Translator API key: http://msdn.microsoft.com/en-us/library/hh454950
.. _Google Analytics key: https://www.google.com/analytics/
.. _Google Cloud Translation API key: https://cloud.google.com/translate/
