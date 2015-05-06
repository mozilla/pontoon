FROM python:2.7
RUN apt-get update && apt-get install -y libmysqlclient-dev gettext libjpeg62-turbo-dev postgresql-client nodejs npm

WORKDIR /pontoon

RUN npm install -g yuglify

# First copy requirements.txt and peep so we can take advantage of
# docker caching.
COPY requirements.txt /tmp/requirements.txt
COPY ./bin/peep.py /tmp/peep.py
RUN /tmp/peep.py install -r /tmp/requirements.txt

EXPOSE 8000
ENV PYTHONUNBUFFERED 1
