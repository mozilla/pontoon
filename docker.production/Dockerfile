# Frontend build
FROM node:14-bullseye-slim AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install
COPY frontend/ .
RUN yarn build


FROM python:3.9-slim-bullseye AS webapp_build

ENV DEBIAN_FRONTEND=noninteractive
ENV HGPYTHON3=1

# Python environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /app

# JavaScript applications paths
ENV WEBPACK_BINARY /app/node_modules/.bin/webpack
ENV YUGLIFY_BINARY /app/node_modules/.bin/yuglify
ENV TERSER_BINARY /app/node_modules/.bin/terser

# Django environment variables
ENV DJANGO_DEV False
ENV SECRET_KEY override_me_at_runtime
ENV DATABASE_URL postgres://pontoon:asdf@postgresql/pontoon

# Install required software.
RUN apt-get update \
    # Enable downloading packages over https
    && apt-get install -y --no-install-recommends \
        apt-transport-https \
        curl \
    # Get source for node.js
    && curl -fsSL https://deb.nodesource.com/setup_14.x | bash - \
    # Get source for yarn
    && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo 'deb https://dl.yarnpkg.com/debian/ stable main' > /etc/apt/sources.list.d/yarn.list \
    # Install software
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libmemcached-dev \
        nodejs \
        postgresql-client \
        postgresql-server-dev-13 \
        yarn \
    # Clean up what can be cleaned up.
    && apt-get autoremove -y

WORKDIR /app

# Install Pontoon Python requirements
COPY requirements/* /app/requirements/
RUN pip install -U 'pip>=8' && \
    pip install --no-cache-dir --require-hashes -r requirements/default.txt


COPY package.json .
COPY package-lock.json .
RUN npm install

COPY ./pontoon /app/pontoon
COPY --from=frontend /frontend/build /app/frontend/build
COPY webpack.config.js .babelrc manage.py setup.py /app/

# Create the folder for front-end assets
RUN mkdir -p assets
# Run webpack to compile JS files
RUN $WEBPACK_BINARY

# Run collectstatic in container which puts files in the default place for
# static files.
RUN python manage.py collectstatic --noinput

RUN rm -rf node_modules


FROM python:3.9-slim-bullseye AS server

ARG USER_ID=1000
ARG GROUP_ID=1000

# Install required software.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        subversion \
        git \
        openssh-client \
    # Clean up what can be cleaned up.
    && apt-get autoremove -y


COPY --from=webapp_build /usr/local/bin /usr/local/bin
COPY --from=webapp_build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

WORKDIR /app

COPY --from=webapp_build /app ./
COPY --from=frontend /frontend/build ./frontend/build/static
COPY --from=frontend /frontend/build ./frontend

COPY ./docker.production /app/docker

RUN groupadd -r --gid=${GROUP_ID} pontoon && useradd --uid=${USER_ID} --no-log-init -r -m -g pontoon pontoon
RUN chown -R pontoon:pontoon /app
USER pontoon

CMD ["/app/docker/server_run.sh"]
