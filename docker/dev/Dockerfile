FROM phlax/pontoon:base

WORKDIR /app

# Install OS-level things
COPY ./set_up_ubuntu.sh /app/
RUN DEBIAN_FRONTEND=noninteractive /app/set_up_ubuntu.sh

# Create the app user
RUN useradd --shell /bin/bash -c "" -m app

# Setup apps's env
COPY ./set_up_env.sh /app/
RUN sudo -u app /app/set_up_env.sh

# Install Pontoon Python requirements
# gets from github to keep the build context nice and small
ADD https://raw.githubusercontent.com/mozilla/pontoon/master/requirements.txt /app/requirements.txt
ADD https://raw.githubusercontent.com/mozilla/pontoon/master/requirements-dev.txt /app/requirements-dev.txt
ADD https://raw.githubusercontent.com/mozilla/pontoon/master/requirements-test.txt /app/requirements-test.txt

RUN pip install -U 'pip>=8'
RUN pip install --no-cache-dir --require-hashes -r requirements-dev.txt
RUN pip install --no-cache-dir --require-hashes -r requirements-test.txt

COPY ./config/webapp.env /app/.env

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /app

CMD ["/app/docker/run_webapp.sh"]
