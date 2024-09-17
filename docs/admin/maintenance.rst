Maintenance
===========
The following describes tricks and tools useful for debugging and maintaining
an instance of Pontoon deployed to Heroku.

Monitoring Celery
-----------------
`Flower`_ is a web interface for monitoring a `Celery`_ task queue. It's useful
for seeing how the worker dynos are handling sync jobs.

After installation, you can run a local instance of Flower and connect it to a
Heroku-hosted instance of RabbitMQ:

.. code-block:: bash

   # Replace my-app-name with your Heroku app's name.
   flower --broker=`heroku config:get RABBITMQ_URL --app=my-app-name`

.. _Flower: https://github.com/mher/flower
.. _Celery: http://www.celeryproject.org/

Releasing the queue
-------------------
If queue gets stuck, tasks don't make it to the worker until manual
intervention. You can fix this by running the following commands from your
local development environment.

First, you need to purge the queue:

.. code-block:: bash

   # Replace my-app-name with your Heroku app's name.
   celery --broker=`heroku config:get RABBITMQ_URL --app=my-app-name` amqp
   # Replace my-queue-name with your queue's name (e.g. celery).
   1> queue.purge my-queue-name

Finally, you need to simply access the worker:

.. code-block:: bash

   # Replace my-app-name with your Heroku app's name.
   celery --broker=`heroku config:get RABBITMQ_URL --app=my-app-name` worker

Mitigating DDoS attacks
-----------------------
In a distributed denial-of-service attack (`DDoS`_ attack), the incoming traffic
flooding the victim originates from many different sources. This stops everyone
else from accessing the website as there is too much traffic flowing to it.

One way to mitigate DDoS attacks is to identify the IP addresses of the
attackers (see the handy `IP detection script`_ to help with that) and block them.
Find the attacking IP addresses in the Log Management Add-On (Papertrail)
and add them to the BLOCKED_IPs config variable in Heroku Settings.

.. _DDoS: https://en.wikipedia.org/wiki/Denial-of-service_attack
.. _IP detection script: https://github.com/mozilla-l10n/pontoon-scripts/blob/main/dev/check_ips_heroku_log.py

Vacuuming a Database
--------------------
To reduce the size of Postgres DB tables and improve performance, it is recommended to
`vacuum the database`_ regularly. Heroku already does that partially by running the
`VACUUM` command automatically, but that only marks the space as available for reuse.

Running `VACUUM FULL` offers a more exhaustive cleanup and reduces bloat.

   .. Warning::

    `VACUUM FULL` is a heavyweight operation, which prevents any other statements from
    running concurrently, even simple SELECT queries. For most tables it only takes a
    few seconds to complete, but on the bigger tables it can take up to a few minutes.
    During that time, the application will be unresponsive.

You can run `VACUUM FULL` with the following command:

.. code-block:: bash

   $ heroku pg:psql --app mozilla-pontoon
   => VACUUM FULL table_name;

To list the DB tables, ordered by size, run:

.. code-block:: bash

   $ heroku pg:psql --app mozilla-pontoon
   => SELECT
        table_name,
        pg_size_pretty(pg_total_relation_size(table_name::text)) AS size
      FROM
        information_schema.tables
      WHERE
        table_schema = 'public'
      ORDER BY
        pg_total_relation_size(table_name::text) DESC;

.. _vacuum the database: https://devcenter.heroku.com/articles/managing-vacuum-on-heroku-postgres
