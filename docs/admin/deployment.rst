Deployment
==========

Pontoon is designed to be deployed on Heroku. To deploy an instance of Pontoon
on Heroku, you must first create an app on your Heroku dashboard. The steps
below assume you've already created an app and have installed the
`Heroku CLI`_.

For quick and easy deployment without leaving your web browser, click this button:

.. raw:: html

   <a class="reference external image-reference" href="https://heroku.com/deploy?template=https://github.com/mozilla/pontoon/tree/main">
      <img src="https://www.herokucdn.com/deploy/button.svg">
   </a>

.. _Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

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
   Set to 'fxa' if you want to use 'Mozilla Accounts' (corresponding FXA_* settings must be set).
   Set to 'github' if you want to use 'GitHub' (corresponding GITHUB_* settings must be set).
   Set to 'gitlab' if you want to use 'GitLab' (corresponding GITLAB_* settings must be set if required).
   Set to 'google' if you want to use 'Google' (corresponding GOOGLE_* settings must be set).

``BADGES_PROMOTION_THRESHOLDS``
   Optional. A comma-separated list of numeric thresholds for different levels of the 
   Community Builder badge.

``BADGES_START_DATE``
   Optional. Specifies the start date from which user activities count towards badge achievements. 
   This variable should be in YYYY-MM-DD format.

``BADGES_TRANSLATION_THRESHOLDS``
   Optional. A comma-separated list of numeric thresholds for different levels of the 
   Review Master and Translation Champion badges.

``BLOCKED_IPS``
   A comma-separated list of IP addresses or IP ranges (expressed using the
   `CIDR notation`_, e.g. `192.168.1.0/24`) to be blocked from accessing the app, for
   example because they are DDoS'ing the server.

   .. _CIDR notation: https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing#CIDR_notation

``CELERY_ALWAYS_EAGER``
   Controls whether asynchronous tasks (mainly used during sync) are sent to
   Celery or executed immediately and synchronously. Set this to ``False`` on
   production.

``CELERYD_MAX_TASKS_PER_CHILD``
   Maximum number of tasks a Celery worker process can execute before it’s
   replaced with a new one. Defaults to 20 tasks.

``DEFAULT_FROM_EMAIL``
   Optional. Default email address to send emails from. Default value:
   ``Pontoon <pontoon@hostname>``.

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
   SMTP host (default: ``'smtp.sendgrid.net'``).

``EMAIL_HOST_PASSWORD``
   Password for the SMTP connection.

``EMAIL_HOST_USER``
   Username for the SMTP connection (default: ``'apikey'``).

``EMAIL_PORT``
   SMTP port (default: ``587``).

``EMAIL_USE_TLS``
   Use explicit TLS for the SMTP connection (default: ``True``).

``EMAIL_USE_SSL``
   Use implicit TLS for the SMTP connection (default: ``False``).

``EMAIL_CONSENT_ENABLED``
   Optional. Enables Email consent page (default: ``False``).

``EMAIL_CONSENT_TITLE``
   Optional, unless ``EMAIL_CONSENT_ENABLED`` is ``True``.
   Title of the Email consent page.

``EMAIL_CONSENT_MAIN_TEXT``
   Optional, unless ``EMAIL_CONSENT_ENABLED`` is ``True``.
   Main text of the Email consent page. You can use that to explain what type
   of communication to expect among other things.

``EMAIL_CONSENT_PRIVACY_NOTICE``
   Optional. Privacy notice on the Email consent page. It's possible to use HTML and
   link to external privacy notice page.

``EMAIL_COMMUNICATIONS_HELP_TEXT``
   Optional. Help text to use under the Email communications checkbox in user settings.
   It allows to explain what type of communication to expect and to link to
   deployment-specific privacy notices among other things.

``EMAIL_COMMUNICATIONS_FOOTER_PRE_TEXT``
   Optional. Text to be shown in the footer of the non-transactional emails sent
   using the Messaging Center, just above the unsubscribe text.

``+EMAIL_MONTHLY_ACTIVITY_SUMMARY_INTRO``
   Optional. Custom text to be shown in the Monthly activity summary emails after the
   greeting and before the stats.

``ENABLE_BUGS_TAB``
   Optional. Enables Bugs tab on team pages, which pulls team data from
   bugzilla.mozilla.org. Specific for Mozilla deployments.

``ENABLE_INSIGHTS``
   Optional. Enables Insights pages, which present data that needs
   to be collected by the :ref:`collect-insights` scheduled job. It is advised
   to run the job at least once before enabling the tab, otherwise the content
   will be empty. See `the spec`_ for more information.

``ERROR_PAGE_URL``
   Optional. URL to the page displayed to your users when the application encounters
   a system error. See `Heroku Reference`_ for more information.

``GOOGLE_ANALYTICS_KEY``
   Optional. Set your `Google Analytics key`_ to use Google Analytics.

``GOOGLE_TRANSLATE_API_KEY``
   Optional. Set your `Google Cloud Translation API`_ key to use generic machine
   translation engine by Google.

``GOOGLE_AUTOML_PROJECT_ID``
   Optional. Set your `Google Cloud AutoML Translation`_ model ID to use custom machine
   translation engine by Google.

``INACTIVE_CONTRIBUTOR_PERIOD``
   Optional. Number of days in which the contributor needs to log in in order not to
   receive the inactive account email. The default value is 180 (6 months).

``INACTIVE_TRANSLATOR_PERIOD``
   Optional. Number of days in which the locale translator needs to submit or review at
   least one translations in order not to receive the inactive account email.
   The default value is 60 (2 months).

``INACTIVE_MANAGER_PERIOD``
   Optional. Number of days in which the locale manager needs to submit or review at
   least one translations in order not to receive the inactive account email.
   The default value is 60 (2 months).

``LOG_TO_FILE``
   Optional. Enables logging to a file (default: ``False``).
   This is useful for retaining log data for later analysis or troubleshooting.

``MAINTENANCE_PAGE_URL``
   Optional. URL to the page displayed to your users when the application is placed
   in the maintenance state. See `Heroku Reference`_ for more information.

``MANUAL_SYNC``
   Optional. Enable Sync button in project Admin.

``MEDIA_ROOT``
   Optional. The absolute path of the "media" folder the projects will be
   cloned into (it is located next to the "pontoon" Python module by default).

``MICROSOFT_TRANSLATOR_API_KEY``
   Optional. Set your `Microsoft Translator API`_ key to use machine translation
   by Microsoft.

``MONTHLY_ACTIVITY_SUMMARY_DAY``
   Optional. Integer representing a day of the month on which the Monthly
   activity summary emails will be sent. 1 represents the first day of the month.
   The default value is 1.

``NEW_RELIC_API_KEY``
   Optional. API key for accessing the New Relic REST API. Used to mark deploys
   on New Relic.

``NEW_RELIC_APP_NAME``
   Optional. Name to give to this app on New Relic. Required if you're using
   New Relic.

``NOTIFICATION_DIGEST_DAY``
   Optional. Integer representing a day of the week on which the weekly notification
   digest email will be sent. 0 represents Monday, 6 represents Sunday. The default
   value is 4 (Friday).

``ONBOARDING_EMAIL_2_DELAY``
   Optional. The number of days to wait after user registration before sending the
   2nd onboarding email. The default value is 2.

``ONBOARDING_EMAIL_3_DELAY``
   Optional. The number of days to wait after user registration before sending the
   3rd onboarding email. The default value is 7.

``OPENAI_API_KEY``
   Optional. Set your `OpenAI API` key to add the ability to refine machine
   translations using ChatGPT.

``PROJECT_MANAGERS``
   Optional. A list of project manager email addresses to send project requests to

``PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION``
   Required. Must be set to ``python``. Needed for Google AutoML Translation.
   Learn more on `Protocol Buffers Homepage`_.

``SECRET_KEY``
   Required. Secret key used for sessions, cryptographic signing, etc.

``SITE_URL``
   Controls the base URL for the site, including the protocol and port.
   Defaults to ``http://localhost:8000``, should always be set in production.

``ALLOWED_HOSTS``
   A list of strings representing the host/domain names the site can serve.
   Defaults to ``.localhost, 127.0.0.1, [::1]``, should always be set in production.

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

``SUGGESTION_NOTIFICATIONS_DAY``
   Optional. Integer representing a day of the week on which the
   `send_suggestion_notifications` management command will run. 0 represents
   Monday, 6 represents Sunday. The default value is 4 (Friday).

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
   Optional. Set your `SYSTRAN Translate API key` to use machine translation
   by SYSTRAN.

``TBX_DESCRIPTION``
   Optional. Description to be used in the header of the Terminology (.TBX) files.

``TBX_TITLE``
   Optional. Title to be used in the header of the Terminology (.TBX) files.

``THROTTLE_ENABLED``
   Optional. Enables traffic throttling based on IP address (default: ``False``).

``THROTTLE_MAX_COUNT``
   Optional. Maximum number of requests allowed in ``THROTTLE_OBSERVATION_PERIOD``
   (default: ``300``).

``THROTTLE_OBSERVATION_PERIOD``
   Optional. A period (in seconds) in which ``THROTTLE_MAX_COUNT`` requests are
   allowed. (default: ``60``). If longer than ``THROTTLE_BLOCK_DURATION``,
   ``THROTTLE_BLOCK_DURATION`` will be used.

``THROTTLE_BLOCK_DURATION``
   Optional. A duration (in seconds) for which IPs are blocked (default: ``600``).

``TZ``
   Timezone for the dynos that will run the app. Pontoon operates in UTC, so set
   this to ``UTC``.

``VCS_SYNC_NAME``
  Optional. Default committer's name used when committing translations to version control system.

``VCS_SYNC_EMAIL``
  Optional. Default committer's email used when committing translations to version control system.

.. _the spec: https://github.com/mozilla/pontoon/blob/HEAD/specs/0108-community-health-dashboard.md
.. _Heroku Reference: https://devcenter.heroku.com/articles/error-pages#customize-pages
.. _Microsoft Translator API: http://msdn.microsoft.com/en-us/library/hh454950
.. _Google Analytics key: https://www.google.com/analytics/
.. _Google Cloud Translation API: https://cloud.google.com/translate/
.. _Google Cloud AutoML Translation: https://cloud.google.com/translate/
.. _Protocol Buffers Homepage: https://developers.google.com/protocol-buffers/docs/news/2022-05-06#python-updates

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

.. _BROKER_URL: https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-url

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

Send Suggestion Notifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This job sends notifications about newly created unreviewed suggestions that
were submitted, unapproved or unrejected in the last 7 days. Recipients of
notifications are users with permission to review them, as well as authors of
any previous translations or comments of the same string. The command is
designed to run on a weekly basis.

.. code-block:: bash

   ./manage.py send_suggestion_notifications

Send Review Notifications
~~~~~~~~~~~~~~~~~~~~~~~~~
This job sends notifications about newly reviewed (approved or rejected)
suggestions to the authors of those suggestions. The command is designed to
run on a daily basis.

.. code-block:: bash

   ./manage.py send_review_notifications

Send Notification Emails
~~~~~~~~~~~~~~~~~~~~~~~~
This job sends notifications in daily and weekly email digests. Daily
notifications are sent every time the command runs, while weekly notifications
are sent only on the configured day (e.g., Friday).

.. code-block:: bash

   ./manage.py send_notification_emails

Send Monthly Activity Emails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This job sends a summary of monthly activity to users via email. It is designed
to run on a specific day of the month but can be forced to run at any time
using the --force argument.

.. code-block:: bash

   ./manage.py send_monthly_activity_emails

Send Onboarding Emails
~~~~~~~~~~~~~~~~~~~~~~
Pontoon sends onboarding emails to new users. The first one is sent upon
registration, while this job sends the 2nd and 3rd email. You can configure
the number of days to wait before sending the 2nd and 3rd emails. The command
is designed to run daily.

.. code-block:: bash

   ./manage.py send_oboarding_emails

Send Inactive Account Emails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This command sends reminder emails to inactive users. Users in different roles
get different emails based on different activity criteria, which can be
configured in settings. The command is designed to run daily.

.. code-block:: bash

   ./manage.py send_inactive_account_emails

.. _collect-insights:

Collect Insights
~~~~~~~~~~~~~~~~
The Insights tab in the dashboards presents data that cannot be retrieved from
the existing data models efficiently upon each request. This job gathers all
the required data and stores it in a dedicated denormalized data model. The job
is designed to run in the beginning of the day, every day.

.. code-block:: bash

   ./manage.py collect_insights

Warm up cache
~~~~~~~~~~~~~
We cache data for some of the views (e.g. Contributors) for a day. Some of them
don't get a lot of visits, not even one per day, meaning that the visitors of
these pages often hit the cold cache. We use this job to refresh data in the
cache every day, because it changes often. The command is designed to run daily.

.. code-block:: bash

   ./manage.py warmup_cache

Clearing the session store
~~~~~~~~~~~~~~~~~~~~~~~~~~
When a user logs in, Django adds a row to the ``django_session`` database
table. If the user logs out manually, Django deletes the row. But if the user
does not log out, the row never gets deleted.

Django does not provide automatic purging of expired sessions. Therefore, it’s
your job to purge expired sessions on a regular basis. Django provides a
clean-up management command for this purpose: ``clearsessions``. It’s
recommended to run this command as a daily cron job.

.. code-block:: bash

   ./manage.py clearsessions

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
