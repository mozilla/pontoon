DC := $(shell which docker-compose)

# *IMPORTANT*
# Don't use this instance in a production setting. More info at:
# https://docs.djangoproject.com/en/dev/ref/django-admin/#runserver
SITE_URL ?= http://localhost:8000

.PHONY: dockerclean dockertest dockerrun

all: dockerrun

dockerclean:
	rm .docker-build

dockertest:
	./docker/run_tests_in_docker.sh ${ARGS}

dockershell:
	./docker/run_tests_in_docker.sh --shell

dockerloaddb:
	-${DC} stop webapp
	-docker exec -i `${DC} ps -q postgresql` dropdb -U pontoon pontoon
	docker exec -i `${DC} ps -q postgresql` createdb -U pontoon pontoon
	docker exec -i `${DC} ps -q postgresql` pg_restore -U pontoon -d pontoon -O < ${DB_DUMP_FILE}

dockerrun:
	cp ./docker/dev/config/webapp.env.template ./docker/dev/config/webapp.env
	sed -i -e 's/#SITE_URL#/$(subst /,\/,${SITE_URL})/g' ./docker/dev/config/webapp.env
	${DC} run --rm --service-ports webapp

dockerwebpack:
	./docker/run_tests_in_docker.sh --shell -c " \
	  export NVM_DIR=\"/home/app/.nvm\" \
	    && . \"/home/app/.nvm/nvm.sh\" \
	    && nvm use node \
	    && ./node_modules/.bin/webpack -w"
