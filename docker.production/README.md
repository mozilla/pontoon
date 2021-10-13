# Run Pontoon in a production environment in Docker

## Deployments required
To run Pontoon you will need a `Postgres` database as well as a `rabbitmq` or other compatible software to run Celery.

## Configure runtime
All variables usually required at build time are here used at run time.
Please provide the following variables
- SECRET_KEY=insert_random_key
- SITE_URL=https://localhost:8000
- DATABASE_URL=postgres://pontoon:asdf@postgresql/pontoon
- CELERY_BROKER_URL=amqp://guest:guest@amqp//

Then you can configure SSH using the following ENV
- SSH_CONFIG=\<base64 encoded config>
For instance
```
Host github.com
User mail@domain.com
```
- SSH_KEY=<base64 encoded private key>
- KNOWN_HOSTS=\<base64 encoded known hosts file>

You can configure the Celery and Gunicorn threading using the following ENV
- CELERY_CONCURRENCY=10
- GUNICORN_WORKERS=5
- GUNICORN_THREADS=2

Finally you can use any other environment variable already available on pontoon to setup SSO for instance.
