web: newrelic-admin run-program gunicorn pontoon.wsgi:application -t 120 --log-file -
worker: newrelic-admin run-program celery worker --app=pontoon.base.celeryapp --loglevel=info --without-gossip --without-mingle --without-heartbeat
