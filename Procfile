web: newrelic-admin run-program gunicorn pontoon.wsgi:application --log-file -
worker: newrelic-admin run-program celery worker --app=pontoon.base.celeryapp --loglevel=info --without-gossip --without-mingle --without-heartbeat
