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
   celery amqp --broker=`heroku config:get RABBITMQ_URL --app=my-app-name`
   # Replace my-queue-name with your queue's name (e.g. celery).
   1> queue.purge my-queue-name

Finally, you need to simply access the worker:

.. code-block:: bash

   # Replace my-app-name with your Heroku app's name.
   celery worker --broker=`heroku config:get RABBITMQ_URL --app=my-app-name`
