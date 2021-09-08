FROM postgres:13.4

RUN echo "tr_TR.UTF-8 UTF-8\nen_US.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen

ADD ./docker-entrypoint-initdb.d /docker-entrypoint-initdb.d
