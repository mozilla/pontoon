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
