web: newrelic-admin run-program gunicorn pontoon.wsgi:application --log-file -
worker: newrelic-admin run-program celery worker --app=pontoon.base.celery --loglevel=info
