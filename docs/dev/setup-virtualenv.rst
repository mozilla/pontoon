Developer Setup with virtualenv
===============================

The following document describes how to set up an instance of the site on your
computer for development.

   .. Note::

    Installation with virtualenv is not recommended. If possible, please use
    Developer Setup with Docker, which is simpler and makes it easier to
    reproduce potential issues.

Prerequisites
-------------
This guide assumes you have already installed and set up the following:

1. `Git <https://git-scm.com>`__
2. `Python 3.11 <https://www.python.org>`__
3. `uv <https://docs.astral.sh/uv/getting-started/installation/#standalone-installer>`_
4. `Node.js <https://nodejs.org>`__ and `npm <https://www.npmjs.com>`__
5. `PostgreSQL 15 <http://www.postgresql.org>`__

These docs assume a Unix-like operating system, although the site should, in
theory, run on Windows as well. All the example commands given below are
intended to be run in a terminal.

If you're on Ubuntu 24.04 LTS, you can install all the prerequisites using the
following commands:

   .. code-block:: bash

      # These steps are required to install PostgreSQL 15 (default is 16)
      sudo apt install -y dirmngr ca-certificates software-properties-common apt-transport-https lsb-release curl
      curl -fSsL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | sudo tee /usr/share/keyrings/postgresql.gpg > /dev/null
      echo deb [arch=amd64,arm64,ppc64el signed-by=/usr/share/keyrings/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main | sudo tee /etc/apt/sources.list.d/postgresql.list
      sudo apt update

      sudo apt install -y git python3-dev python-is-python3 virtualenv postgresql-client-15 postgresql-15 libxml2-dev libxslt1-dev libmemcached-dev libpq-dev nodejs npm
      # Set Python 3.11 as default
      update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

      # Install uv
      curl -LsSf https://astral.sh/uv/install.sh | sh
      source $HOME/.cargo/env

      # Start PostgreSQL server
      /etc/init.d/postgresql start

Installation
------------
1. Clone this repository_ or your fork_:

   .. code-block:: bash

      git clone https://github.com/mozilla/pontoon.git
      cd pontoon

2. Create a virtualenv for Pontoon with Python 3.11 and activate it:

   .. code-block:: bash

      uv python install 3.11
      uv venv --python 3.11
      # Activate virtualenv
      source .venv/bin/activate

   .. note::

      Whenever you want to work on Pontoon in a new terminal you'll have to
      re-activate the virtualenv.

3. Install the dependencies:

   .. code-block:: bash

      uv pip install -r requirements/default.txt -r requirements/dev.txt -r requirements/test.txt

4. Create your database, using the following set of commands.

   First connect to Postgres:

   .. code-block:: bash

      sudo -u postgres psql

   Then run the following commands in the console:

   .. code-block:: bash

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

   - ``SITE_URL`` should be set to the URL you will use to connect to your local development site.
     Some people prefer to use ``http://127.0.0.1:8000`` instead of ``localhost``.
     However, should you decide to change the ``SITE_URL``,
     you also need to request_ the new ``FXA_CLIENT_ID`` and ``FXA_SECRET_KEY``.

6. Initialize your database by running the migrations:

   .. code-block:: bash

      python manage.py migrate

7. Create a new superuser account:

   .. code-block:: bash

      python manage.py createsuperuser

   Make sure that the email address you use for the superuser account matches
   the email that you will log in with via Firefox Accounts.

9.

10. After you've provided credentials for your django-allauth provider, you have to update them in database,
   because it's required by django-allauth. You will have to call this command after every change in your
   django-allauth settings (e.g. client key):

   .. code-block:: bash

      python manage.py update_auth_providers

11. Install the required Node libraries using ``npm``:

   .. code-block:: bash

      npm install

12. Build the client:

   .. code-block:: bash

      npm run build

Once you've finished these steps, you should be able to start the site by
running:

.. code-block:: bash

   python manage.py runserver

The site should be available at http://localhost:8000.

.. _repository: https://github.com/mozilla/pontoon
.. _fork: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo
.. _request: https://mozilla.github.io/ecosystem-platform/

Extra settings
--------------
The following extra settings can be added to your ``.env`` file.

``GOOGLE_TRANSLATE_API_KEY``
   Set your `Google Cloud Translation API`_ key to use generic machine translation
   engine by Google.
``GOOGLE_AUTOML_PROJECT_ID``
   Set your `Google Cloud AutoML Translation`_ model ID to use custom machine
   translation engine by Google.
``MICROSOFT_TRANSLATOR_API_KEY``
   Set your `Microsoft Translator API`_ key to use machine translation by Microsoft.
``GOOGLE_ANALYTICS_KEY``
   Set your `Google Analytics key`_ to use Google Analytics.
``MANUAL_SYNC``
   Enable Sync button in project Admin.

.. _Microsoft Translator API: http://msdn.microsoft.com/en-us/library/hh454950
.. _Google Analytics key: https://www.google.com/analytics/
.. _Google Cloud Translation API: https://cloud.google.com/translate/
.. _Google Cloud AutoML Translation: https://cloud.google.com/translate/
