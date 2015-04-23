#!/bin/bash
# Start the app using the dev server when run via docker-compose.
gunicorn pontoon.wsgi:application --bind=0.0.0.0:8000 --log-file -
