Deployment
==========

Pontoon is designed to be deployed on Heroku. To deploy an instance of Pontoon
on Heroku, you must first create an app on your Heroku dashboard. The steps
below assume you've already created an app and have installed the
`Heroku Toolbelt`_.

For quick and easy deployment without leaving your web browser, click this button:

.. raw:: html

   <a class="reference external image-reference" href="https://heroku.com/deploy?template=https://github.com/mozilla/pontoon/tree/master">
      <img src="https://www.herokucdn.com/deploy/button.svg">
   </a>

.. _Heroku Toolbelt: https://toolbelt.heroku.com/

Buildpack
---------
Pontoon uses several buildpacks in a specific order. They are (in order):

1. `heroku-buildpack-apt`_ for installing Subversion.
2. `heroku-buildpack-ssh`_ for setting up the SSH keys necessary for committing
   to version control.
3. The official ``heroku/nodejs`` buildpack for installing Node.js programs for
   pre-processing frontend assets.
4. The official ``heroku/python`` buildpack as our primary buildpack.

You can set these buildpacks on your app with the following toolbelt commands:

.. code-block:: bash

   # Note that we use add and --index 1 to append to the top of the list.
   heroku buildpacks:set heroku/python
   heroku buildpacks:add --index 1 heroku/nodejs
   heroku buildpacks:add --index 1 https://github.com/Osmose/heroku-buildpack-ssh.git#v0.1
   heroku buildpacks:add --index 1 https://github.com/mozilla/heroku-buildpack-apt.git#v0.1

.. _heroku-buildpack-apt: https://github.com/mozilla/heroku-buildpack-apt
.. _heroku-buildpack-ssh: https://github.com/Osmose/heroku-buildpack-ssh

Environment Variables
---------------------
The following is a list of environment variables you'll want to set on the app
you create:

.. NOTE::

   Alternatively, you can put all variables below in a `dotenv
   <https://saurabh-kumar.com/python-dotenv/>`_ text file::

      VAR="value 1"
      OTHER_VAR="other value"

   If you do so, you will only have to give the path of this file to Pontoon
   through the ``DOTENV_PATH`` environment variable::

      DOTENV_PATH=/path/to/my/config.env


``ADMIN_EMAIL``
   Optional. Email address for the ``ADMINS`` setting.

``ADMIN_NAME``
   Optional. Name for the ``ADMINS`` setting.

``AUTHENTICATION_METHOD``
   The default value is `django`, which allows you to log in via accounts created using `manage.py shell`.
   Set to 'fxa' if you want to use 'Firefox Accounts' (corresponding FXA_* settings must be set).
   Set to 'github' if you want to use 'GitHub' (corresponding GITHUB_* settings must be set).
   Set to 'gitlab' if you want to use 'GitLab' (corresponding GITLAB_* settings must be set if required).
   Set to 'google' if you want to use 'Google' (corresponding GOOGLE_* settings must be set).

``CELERY_ALWAYS_EAGER``
   Controls whether asynchronous tasks (mainly used during sync) are sent to
   Celery or executed immediately and synchronously. Set this to ``False`` on
   production.

``CELERYD_MAX_TASKS_PER_CHILD``
   Maximum number of tasks a Celery worker process can execute before it’s
   replaced with a new one. Defaults to 20 tasks.

``DISABLE_COLLECTSTATIC``
   Disables running ``./manage.py collectstatic`` during the build. Should be
   set to ``1``.

   Heroku's Python buildpack has a bug that causes issues when running node
   binaries during the compile step of the buildpack. To get around this, we run
   the command in our post-compile step (see ``bin/post_compile``) when the
   issue doesn't occur.

``DJANGO_DEBUG``
   Controls ``DEBUG`` mode for the site. Should be set to `False` in
   production.

``DJANGO_DEV``
   Signifies whether this is a development server or not. Should be `False` in
   production.
   Adds some additional django apps that can be helpful during day to day development.

``EMAIL_HOST``
   SMTP host (default: ``'smtp.sendgrid.net'``)

``EMAIL_HOST_PASSWORD``
   Password for the SMTP connection.

``EMAIL_HOST_USER``
   Username for the SMTP connection (default: ``'apikey'``).

``EMAIL_PORT``
   SMTP port (default: ``587``)

``EMAIL_USE_TLS``
   Use TLS for the SMTP connection (default: ``True``)

``ENABLE_BUGS_TAB``
   Optional. Enables Bugs tab on team pages, which pulls team data from
   bugzilla.mozilla.org. Specific for Mozilla deployments.

``ENABLE_INSIGHTS_TAB``
   Optional. Enables Insights tab on team pages, which presents data that needs
   to be collected by the :ref:`collect-insights` scheduled job. It is advised
   to run the job at least once before enabling the tab, otherwise the content
   will be empty. See `the spec`_ for more information.

``ERROR_PAGE_URL``
   Optional. URL to the page displayed to your users when the application encounters
   a system error. See `Heroku Reference`_ for more information.

``GOOGLE_ANALYTICS_KEY``
   Optional. Set your `Google Analytics key`_ to use Google Analytics.

``GOOGLE_TRANSLATE_API_KEY``
   Optional. Set your `Google Cloud Translation API key`_ to use machine translation
   by Google.

``LOCALE_REQUEST_FROM_EMAIL``
   Optional. Requests for new project locales are sent from this email.

``MAINTENANCE_PAGE_URL``
   Optional. URL to the page displayed to your users when the application is placed
   in the maintenance state. See `Heroku Reference`_ for more information.

``MANUAL_SYNC``
   Optional. Enable Sync button in project Admin.

``MEDIA_ROOT``
   Optional. The absolute path of the "media" folder the projects will be
   cloned into (it is located next to the "pontoon" Python module by default).

``MICROSOFT_TRANSLATOR_API_KEY``
   Optional. Set your `Microsoft Translator API key`_ to use machine translation
   by Microsoft.

``NEW_RELIC_API_KEY``
   Optional. API key for accessing the New Relic REST API. Used to mark deploys
   on New Relic.

``NEW_RELIC_APP_NAME``
   Optional. Name to give to this app on New Relic. Required if you're using
   New Relic.

``PROJECT_MANAGERS``
   Optional. A list of project manager email addresses to send project requests to

``SECRET_KEY``
   Required. Secret key used for sessions, cryptographic signing, etc.

``SITE_URL``
   Controls the base URL for the site, including the protocol and port.
   Defaults to ``http://localhost:8000``, should always be set in production.

``SSH_CONFIG``
   Contents of the ``~/.ssh/config`` file used when Pontoon connects to VCS
   servers via SSH. Used for disabling strict key checking and setting the
   default user for SSH. For example::

      StrictHostKeyChecking=no

      Host hg.mozilla.org
      User pontoon@mozilla.com

      Host svn.mozilla.org
      User pontoon@mozilla.com

``SSH_KEY``
   SSH private key to use for authentication when Pontoon connects to VCS
   servers via SSH.

.. note:: Changing the ``SSH_CONFIG`` or ``SSH_KEY`` environment variables *requires*
   a rebuild of the site, as these settings are only used at build time. Simply
   changing them will not actually update the site until the next build.

   The `Heroku Repo`_ plugin includes a rebuild command that is handy for
   triggering builds without making code changes.

   .. _Heroku Repo: https://github.com/heroku/heroku-repo

.. note:: Some environment variables, such as the SSH-related ones, may contain
   newlines. The easiest way to set these is using the ``heroku`` command-line
   tool to pass the contents of an existing file to them:

   .. code-block:: bash

      heroku config:set SSH_KEY="`cat /path/to/key_rsa`"

``STATIC_HOST``
   Optional. Hostname to prepend to static resources paths. Useful for serving
   static files from a CDN. Example: ``//asdf.cloudfront.net``.

``SVN_LD_LIBRARY_PATH``
   Path to prepend to ``LD_LIBRARY_PATH`` when running SVN. This is necessary
   on Heroku because the Python buildpack alters the path in a way that breaks
   the built-in SVN command. Set this to ``/usr/lib/x86_64-linux-gnu/``.

``SYNC_TASK_TIMEOUT``
   Optional. Multiple sync tasks for the same project cannot run concurrently to
   prevent potential DB and VCS inconsistencies. We store the information about
   the running task in cache and clear it after the task completes. In case of
   an error, we might never clear the cache, so we use SYNC_TASK_TIMEOUT as the
   longest possible period after which the cache is cleared and the subsequent
   task can run. The value should exceed the longest sync task of the instance.
   The default value is 3600 seconds (1 hour).

``SYSTRAN_TRANSLATE_API_KEY``
   Optional. Set your `SYSTRAN Translate API key`_ to use machine translation
   by SYSTRAN.

``TZ``
   Timezone for the dynos that will run the app. Pontoon operates in UTC, so set
   this to ``UTC``.

``VCS_SYNC_NAME``
  Optional. Default committer's name used when committing translations to version control system.

``VCS_SYNC_EMAIL``
  Optional. Default committer's email used when committing translations to version control system.

.. _the spec: https://github.com/mozilla/pontoon/blob/master/specs/0108-community-health-dashboard.md
.. _Heroku Reference: https://devcenter.heroku.com/articles/error-pages#customize-pages
.. _Firefox Accounts: https://developer.mozilla.org/docs/Mozilla/Tech/Firefox_Accounts/Introduction
.. _Microsoft Translator API key: http://msdn.microsoft.com/en-us/library/hh454950
.. _Google Analytics key: https://www.google.com/analytics/
.. _Google Cloud Translation API key: https://cloud.google.com/translate/

Add-ons
-------
Pontoon is designed to run with the following add-ons enabled:

- Database: Heroku Postgres
- Log Management: Papertrail
- Error Tracking: Raygun.io
- Email: Sendgrid
- Scheduled Jobs: Heroku Scheduler
- Cache: Memcachier
- RabbitMQ: CloudAMQP

It's possible to run with the free tiers of all of these add-ons, but it is
recommended that, at a minimum, you run the "Standard 0" tier of Postgres.

SendGrid Add-on
~~~~~~~~~~~~~~~
Pontoon uses `SendGrid`_, which expects the following environment variable:

``SENDGRID_PASSWORD``
   Use SendGrid API key.

.. _SendGrid: https://devcenter.heroku.com/articles/sendgrid

Cache Add-on
~~~~~~~~~~~~
Pontoon uses `django-bmemcached`_, which expects the following environment
variables from the cache add-on:

``MEMCACHE_SERVERS``
   Semi-colon separated list of memcache server addresses.
``MEMCACHE_USERNAME``
   Username to use for authentication.
``MEMCACHE_PASSWORD``
   Password to use for authentication.

.. note::

   By default, the environment variables added by Memcachier are prefixed
   with ``MEMCACHIER`` instead of ``MEMCACHE``. You can "attach" the
   configuration variables with the correct prefix using the ``addons:attach``
   command:

   .. code-block:: bash

      heroku addons:attach resource_name --as MEMCACHE

   Replace ``resource_name`` with the name of the resource provided by the cache
   addon you wish to use, such as ``memcachier:100``. Use the
   ``heroku addons`` command to see a list of resource names that are available.

.. _django-bmemcached: https://github.com/jaysonsantos/python-binary-memcached

RabbitMQ Add-on
~~~~~~~~~~~~~~~
Similar to the cache add-ons, Pontoon expects environment variables from the
RabbitMQ add-on:

``RABBITMQ_URL``
   URL for connecting to the RabbitMQ server. This should be in the format for
   Celery's `BROKER_URL`_ setting.

.. note::

   Again, you must attach the resource for RabbitMQ as ``RABBITMQ``. See the
   note in the Cache Add-ons section for details.

.. _BROKER_URL: http://celery.readthedocs.io/en/latest/configuration.html#broker-url

Scheduled Jobs
--------------
Pontoon requires several scheduled jobs to run regularly.

Sync Projects
~~~~~~~~~~~~~
While internal Pontoon DB can be used for storing localizable strings, Pontoon
specializes in using version control systems for that purpose. If you choose
this option as well, you'll need to run the following scheduled job:

.. code-block:: bash

   ./manage.py sync_projects

It's recommended to run this job at least once an hour. It commits any string
changes in the database to the remote VCS servers associated with each project,
and pulls down the latest changes to keep the database in sync.

Send Deadline Notifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Pontoon allows you to set deadlines for projects. This job sends deadline
reminders to contributors of projects when they are due in 7 days. If 2 days
before the deadline project still isn't complete for the contributor's locale,
notifications are sent again. The command is designed to run daily.

.. code-block:: bash

   ./manage.py send_deadline_notifications

.. _collect-insights:

Collect Insights
~~~~~~~~~~~~~~~~
The Insights tab in the dashboards presents data that cannot be retrieved from
the existing data models efficiently upon each request. This job gathers all
the required data and stores it in a dedicated denormalized data model. The job
is designed to run in the beginning of the day, every day.

.. code-block:: bash

   ./manage.py collect_insights

Sync Log Retention
~~~~~~~~~~~~~~~~~~
You may also optionally run the ``clear_old_sync_logs`` management command on a
schedule to remove sync logs from the database that are over 90 days old:

.. code-block:: bash

   ./manage.py clear_old_sync_logs

Provisioning Workers
~~~~~~~~~~~~~~~~~~~~
Pontoon executes scheduled jobs using `Celery`_. These jobs are handled by
the ``worker`` process type. You'll need to manually provision workers based on
how many projects you plan to support and how complex they are. At a minimum,
you'll want to provision at least one ``worker`` dyno:

.. code-block:: bash

   heroku ps:scale worker=1

.. _Celery: http://www.celeryproject.org/

Database Migrations
-------------------
After deploying Pontoon for the first time, you must run the database
migrations. This can be done via the toolbelt:

.. code-block:: bash

   heroku run ./manage.py migrate

Creating an Admin User
----------------------
After deploying the site, you can create a superuser account using the
``createsuperuser`` management command:

.. code-block:: bash

   heroku run ./manage.py createsuperuser --user=admin --email=your@email.com

You'll then be prompted to set a password for your new user.

If you've already logged into the site with the email that you want to use,
you'll have to use the Django shell to mark your user account as an admin:

.. code-block:: bash

   heroku run ./manage.py shell
   # Connection and Python info...
   >>> from django.contrib.auth.models import User
   >>> user = User.objects.get(email='your@email.com')
   >>> user.is_staff = True
   >>> user.is_superuser = True
   >>> user.save()
   >>> exit()

And with that, you're ready to start :doc:`../user/localizing-your-projects`!
