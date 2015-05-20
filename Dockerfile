FROM python:2.7
RUN apt-get update && apt-get install -y libjpeg62-turbo-dev postgresql-client nodejs npm vim

WORKDIR /pontoon

RUN npm install -g yuglify babel

# First copy requirements.txt and peep so we can take advantage of
# docker caching.
COPY requirements.txt /tmp/requirements.txt
COPY ./bin/peep.py /tmp/peep.py
RUN /tmp/peep.py install -r /tmp/requirements.txt

# Symlink node because Ubuntu's node binary is named nodejs.
RUN ln -s /usr/bin/nodejs /usr/bin/node

EXPOSE 8000
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
