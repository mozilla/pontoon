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
