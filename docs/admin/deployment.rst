Deployment
==========

Pontoon is designed to be deployed on Heroku. To deploy an instance of Pontoon
on Heroku, you must first create an app on your Heroku dashboard. The steps
below assume you've already created an app and have installed the
`Heroku Toolbelt`_.

.. _Heroku Toolbelt: https://toolbelt.heroku.com/

Buildpack
---------
Pontoon uses `heroku-buildpack-multi`_ as its buildpack. You can set this (and
pin it to the correct version) with the following toolbelt command:

.. code-block:: bash

   heroku buildpacks:set https://github.com/heroku/heroku-buildpack-multi.git#26fa21ac7156e63d3d36df1627329aa57f8f137c

.. _heroku-buildpack-multi: https://github.com/heroku/heroku-buildpack-multi

Environment Variables
---------------------
The following is a list of environment variables you'll want to set on the app
you create:

``ADMIN_EMAIL``
   Optional. Email address for the ``ADMINS`` setting.

``ADMIN_NAME``
   Optional. Name for the ``ADMINS`` setting.

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

``HMAC_KEY``
   Required. Secret key used for hashing passwords.

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

``SVN_LD_LIBRARY_PATH``
   Path to prepend to ``LD_LIBRARY_PATH`` when running SVN. This is necessary
   on Heroku because the Python buildpack alters the path in a way that breaks
   the built-in SVN command. Set this to ``/usr/lib/x86_64-linux-gnu/``.

.. note:: Some environment variables, such as the SSH-related ones, may contain
   newlines. The easiest way to set these is using the ``heroku`` command-line
   tool to pass the contents of an existing file to them:

   .. code-block:: bash

      heroku config:set SSH_KEY="`cat /path/to/key_rsa`"

.. _Babel: http://babeljs.io/
.. _Yuglify: https://github.com/yui/yuglify

Add-ons
-------
Pontoon is designed to run with the following add-ons enabled:

- Database: Heroku Postgres
- Performance Monitoring: New Relic APM
- Log Management: Papertrail
- Error Tracking: Raygun.io
- Email: Sendgrid
- Scheduled Jobs: Heroku Scheduler
- Cache: Memcached Cloud

It's possible to run with the free tiers of all of these add-ons, but it is
recommended that, at a minimum, you run the "Standard 0" tier of Postgres.

Cache Add-ons
~~~~~~~~~~~~~
Pontoon uses `django-pylibmc`_, which expects the following environment
variables from the cache add-on:

``MEMCACHE_SERVERS``
   Semi-colon separated list of memcache server addresses.
``MEMCACHE_USERNAME``
   Username to use for authentication.
``MEMCACHE_PASSWORD``
   Password to use for authentication.

.. note::

   By default, the environment variables added by Memcached Cloud are prefixed
   with ``MEMCACHEDCLOUD`` instead of ``MEMCACHE``. You can "attach" the
   configuration variables with the correct prefix using the ``addons:attach``
   command:

   .. code-block:: bash

      heroku addons:attach resource_name --as MEMCACHE

   Replace ``resource_name`` with the name of the resource provided by the cache
   addon you wish to use, such as ``memcachedcloud:30``. Use the
   ``heroku addons`` command to see a list of resource names that are available.

.. _django-pylibmc: https://github.com/django-pylibmc/django-pylibmc/

Scheduled Jobs
--------------
Pontoon requires a single scheduled job that runs the following command:

.. code-block:: bash

   ./bin/sync_projects.sh

It's recommended to run this job once an hour. It commits any string changes in
the database to the remote VCS servers associated with each project, and pulls
down the latest changes to keep the database in sync.

Database Migrations
-------------------
After deploying Pontoon for the first time, and during any upgrade that involves
a change to the database, you must run the database migrations. This can be done
via the toolbelt:

.. code-block:: bash

   heroku run ./manage.py migrate

Creating an Admin User
----------------------
After deploying the site, you can create a superuser account using the
``createsuperuser`` management command:

.. code-block:: bash

   heroku run ./manage.py createsuperuser --noinput --user=admin --email=your@email.com

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

Gotchas
-------
- Changing the ``SSH_KEY`` or ``SSH_CONFIG`` environment variables *requires*
  a rebuild of the site, as these settings are only used at build time. Simply
  changing them will not actually update the site until the next build.

  The `Heroku Repo`_ plugin includes a rebuild command that is handy for
  triggering builds without making code changes.

.. _Heroku Repo: https://github.com/heroku/heroku-repo
