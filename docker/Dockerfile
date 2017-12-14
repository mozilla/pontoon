FROM local/pontoon_base

WORKDIR /app

# Install OS-level things
COPY docker/set_up_ubuntu.sh /app/
RUN DEBIAN_FRONTEND=noninteractive /app/set_up_ubuntu.sh

# Install Pontoon Python requirements
COPY requirements.txt /app/requirements.txt
COPY requirements-dev.txt /app/requirements-dev.txt
COPY requirements-test.txt /app/requirements-test.txt
RUN pip install -U 'pip>=8'
RUN pip install --no-cache-dir --require-hashes -r requirements-dev.txt
RUN pip install --no-cache-dir --require-hashes -r requirements-test.txt

COPY . /app/
COPY ./docker/config/webapp.env /app/.env

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /app

CMD ["/app/docker/run_webapp.sh"]
