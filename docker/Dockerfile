FROM local/pontoon_base

WORKDIR /app

# Install OS-level things
COPY docker/set_up_ubuntu.sh /tmp/
RUN DEBIAN_FRONTEND=noninteractive /tmp/set_up_ubuntu.sh

# Create the app user
RUN useradd --shell /bin/bash -c "" -m app

# Install Pontoon Python requirements
COPY requirements.txt /app/requirements.txt
COPY requirements-dev.txt /app/requirements-dev.txt
COPY requirements-test.txt /app/requirements-test.txt
RUN pip install -U 'pip>=8'
RUN pip install --no-cache-dir --require-hashes -r requirements-dev.txt
RUN pip install --no-cache-dir --require-hashes -r requirements-test.txt

# Install nodejs and npm from Nodesource's 8.x branch
# RUN DEBIAN_FRONTEND=noninteractive apt-get install -y curl
RUN curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
    echo 'deb https://deb.nodesource.com/node_9.x jessie main' > /etc/apt/sources.list.d/nodesource.list && \
    echo 'deb-src https://deb.nodesource.com/node_9.x jessie main' >> /etc/apt/sources.list.d/nodesource.list
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs

COPY ./package.json /webapp-frontend-deps/package.json
COPY ./package-lock.json /webapp-frontend-deps/package-lock.json
RUN cd /webapp-frontend-deps/ && npm install

COPY . /app/
COPY ./docker/config/webapp.env /app/.env

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /app

# JavaScript applications paths
ENV WEBPACK_BINARY /webapp-frontend-deps/node_modules/.bin/webpack
ENV NPM_ROOT_PATH /webapp-frontend-deps/

# Run collectstatic in container which puts files in the default place for
# static files.
RUN cd /app/ && python manage.py collectstatic --noinput

# Run webpack
RUN cd /app/ && $WEBPACK_BINARY

CMD ["/app/docker/run_webapp.sh"]
