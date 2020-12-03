FROM python:3.8.3-buster

ARG USER_ID=1000
ARG GROUP_ID=1000

ENV DEBIAN_FRONTEND=noninteractive
ENV HGPYTHON3=1

# Python environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /app

# JavaScript applications paths
ENV WEBPACK_BINARY /app/node_modules/.bin/webpack
ENV YUGLIFY_BINARY /app/node_modules/.bin/yuglify

# Install required software.
RUN apt-get update \
    # Enable downloading packages over https
    && apt-get install -y apt-transport-https \
    # Get source for node.js
    && curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - \
    && echo 'deb https://deb.nodesource.com/node_10.x jessie main' > /etc/apt/sources.list.d/nodesource.list \
    && echo 'deb-src https://deb.nodesource.com/node_10.x jessie main' >> /etc/apt/sources.list.d/nodesource.list \
    # Get source for yarn
    && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo 'deb https://dl.yarnpkg.com/debian/ stable main' > /etc/apt/sources.list.d/yarn.list \
    # Install software
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libmemcached-dev \
        nodejs \
        postgresql-client-11 \
        postgresql-server-dev-11 \
        yarn \
    # Clean up what can be cleaned up.
    && apt-get autoremove -y

WORKDIR /app

# Install Pontoon Python requirements
COPY requirements/* /app/requirements/
RUN pip install -U 'pip>=8' && \
    pip install --no-cache-dir --require-hashes --use-deprecated=legacy-resolver -r requirements/dev.txt && \
    pip install --no-cache-dir --require-hashes --use-deprecated=legacy-resolver -r requirements/test.txt

# Create the app user
RUN groupadd -r --gid=${GROUP_ID} pontoon && useradd --uid=${USER_ID} --no-log-init -r -m -g pontoon pontoon
RUN chown -R pontoon:pontoon /app
USER pontoon

# Install node requirements
COPY package.json .
COPY package-lock.json .
RUN npm install

RUN mkdir frontend
WORKDIR frontend
COPY frontend/package.json .
COPY --chown=pontoon:pontoon frontend/yarn.lock .
RUN yarn install

WORKDIR /app
COPY ./docker/config/webapp.env .env
COPY --chown=pontoon:pontoon . /app/

# Create the folder for front-end assets
RUN mkdir -p assets
# Run webpack to compile JS files
RUN $WEBPACK_BINARY

# Build Translate.Next frontend resources
WORKDIR frontend
RUN yarn build

WORKDIR /app

# Run collectstatic in container which puts files in the default place for
# static files.
RUN python manage.py collectstatic --noinput

CMD ["/app/docker/run_webapp.sh"]
