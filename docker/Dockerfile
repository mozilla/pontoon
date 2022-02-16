# Frontend build
FROM node:16-bullseye AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
COPY frontend/package.json ./frontend/
RUN npm ci
COPY frontend/ ./frontend/
WORKDIR /app/frontend
RUN npm run build
CMD ["npm", "start"]

FROM python:3.9-bullseye AS server

ARG USER_ID=1000
ARG GROUP_ID=1000

ENV DEBIAN_FRONTEND=noninteractive
ENV HGPYTHON3=1

# Python environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /app

# JavaScript applications paths
ENV YUGLIFY_BINARY /app/node_modules/.bin/yuglify
ENV TERSER_BINARY /app/node_modules/.bin/terser

# Install required software.
RUN apt-get update \
    # Enable downloading packages over https
    && apt-get install -y apt-transport-https \
    # Get source for node.js
    && curl -fsSL https://deb.nodesource.com/setup_14.x | bash - \
    # Install software
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libmemcached-dev \
        nodejs \
        postgresql-client \
        postgresql-server-dev-13 \
    && npm install --global npm@8 \
    # Clean up what can be cleaned up.
    && apt-get autoremove -y

WORKDIR /app

# Install Pontoon Python requirements
COPY requirements/* /app/requirements/
RUN pip install -U 'pip>=8' && \
    pip install --no-cache-dir --require-hashes -r requirements/default.txt -r requirements/dev.txt -r requirements/test.txt -r requirements/lint.txt

# Create the app user
RUN groupadd -r --gid=${GROUP_ID} pontoon && useradd --uid=${USER_ID} --no-log-init -r -m -g pontoon pontoon
RUN chown -R pontoon:pontoon /app
USER pontoon

# Install node requirements
COPY package.json .
COPY package-lock.json .
COPY --chown=pontoon:pontoon tag-admin/package.json ./tag-admin/
RUN npm ci

COPY ./docker/config/server.env .env
COPY --chown=pontoon:pontoon . /app/

# Create the folder for front-end assets
RUN mkdir -p assets
# Build JS files
RUN npm run build

COPY --from=frontend /app/frontend/ ./frontend/

# Run collectstatic in container which puts files in the default place for
# static files.
RUN python manage.py collectstatic --noinput

CMD ["/app/docker/server_run.sh"]
