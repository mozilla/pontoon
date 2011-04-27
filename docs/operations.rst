Operations
==========

Care and feeding of a Playdoh-based app.

Web Server
----------

Apps are typically run under Apache and mod_wsgi in production. Entry point::

    wsgi/playdoh.wsgi
(or whatever you rename it too...)

Developers can set that up or run in stand-alone mode::

    ./manage.py runserver 0.0.0.0:8000

It is critical that developers run the app at least once via mod_wsgi before
certifying an app as **stage ready**.

Apache
~~~~~~
This is what is used in production:
    <VirtualHost *:80>
        ServerName %HOSTNAME%

        Alias /media %APP_PATH/media

        WSGIScriptAlias / %APP_PATH/wsgi/playdoh.wsgi
        WSGIDaemonProcess playdoh processes=16 threads=1 display-name=playdoh
        WSGIProcessGroup playdoh
    </VirtualHost>


gunicorn
~~~~~~~~
Totally optional and only for the cool kids.

A lighter weight method of testing your mod_wsgi setup is by using gunicorn.

One time setup:
    pip install gunicorn
    ln -s wsgi/playdoh.wsgi wsgi/playdoh.py

Each Time:
    touch wsgi/__init__.py
    gunicorn wsgi/playdoh:application

Middleware Caching
------------------

TODO (memcache, redis)

Frontend Caching
----------------

Apps are typically run behind a Zeus load balancer.

Database
--------

Apps typically use a MySQL database.

Message Queue
-------------

Playdoh comes packaged with celery and works well with RabbitMQ.

Updating your Environment
-------------------------

You can run ``update_site.py`` to keep your app current.
It does the following:

* Updates source
* Updates vendor libraries
* Runs Database Migrations
* Builds JS and CSS

::

    ./bin/update_site.py -e dev
    ./bin/update_site.py -e stage
    ./bin/update_site.py -e prod

You may pass a ``-v`` and update_site will explain what commands as it runs
them.

If there is an error on any step, the script stops.

IT will typically put ``bin/update_site.py`` into a cron for auto-deployment
to stage environments.

Edit your copy to customize your branching and/or release practices.
