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
RUN pip install -U 'pip>=8' && \
    pip install --no-cache-dir --require-hashes -r requirements-dev.txt && \
    pip install --no-cache-dir --require-hashes -r requirements-test.txt

# Install nodejs and npm from Nodesource's 10.x branch, as well as yarn
RUN curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
    echo 'deb https://deb.nodesource.com/node_10.x jessie main' > /etc/apt/sources.list.d/nodesource.list && \
    echo 'deb-src https://deb.nodesource.com/node_10.x jessie main' >> /etc/apt/sources.list.d/nodesource.list
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    echo 'deb https://dl.yarnpkg.com/debian/ stable main' > /etc/apt/sources.list.d/yarn.list
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs yarn

COPY . /app/

# Create the folder for front-end assets
RUN mkdir -p /app/assets

# Install node requirements
RUN cd /app && npm install
RUN cd /app/frontend && yarn install

COPY ./docker/config/webapp.env /app/.env

# Python environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /app

# JavaScript applications paths
ENV WEBPACK_BINARY /app/node_modules/.bin/webpack
ENV YUGLIFY_BINARY /app/node_modules/.bin/yuglify

# Run webpack to compile JS files
RUN cd /app/ && $WEBPACK_BINARY

# Build Translate.Next frontend resources
RUN cd /app/frontend/ && yarn build

# Run collectstatic in container which puts files in the default place for
# static files.
RUN cd /app/ && python manage.py collectstatic --noinput

RUN chown -R app:app /app

CMD ["/app/docker/run_webapp.sh"]
