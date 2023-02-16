web: newrelic-admin run-program gunicorn pontoon.wsgi:application -t 120 --log-file -
worker: newrelic-admin run-program celery --app=pontoon.base.celeryapp worker --loglevel=info --without-gossip --without-mingle --without-heartbeat
automl-warmup: newrelic-admin run-program python pontoon/machinery/automl_warmup.py
