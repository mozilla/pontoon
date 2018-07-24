DC := $(shell which docker-compose)
DOCKER := $(shell which docker)

# *IMPORTANT*
# Don't use this instance in a production setting. More info at:
# https://docs.djangoproject.com/en/dev/ref/django-admin/#runserver
SITE_URL ?= http://localhost:8000

.PHONY: build setup run clean test shell loaddb build-frontend build-frontend-w

help:
	@echo "Welcome to Pontoon!\n"
	@echo "The list of commands for local development:\n"
	@echo "  build            Builds the docker images for the docker-compose setup"
	@echo "  setup            Configures a local instance after a fresh build"
	@echo "  run              Runs the whole stack, served on http://localhost:8000/"
	@echo "  clean            Forces a rebuild of docker containers"
	@echo "  shell            Opens a Bash shell"
	@echo "  test             Runs the Python test suite"
	@echo "  test-frontend    Runs the new frontend's test suite"
	@echo "  flow             Runs the Flow type checker on the frontend code"
	@echo "  loaddb           Load a database dump into postgres, file name in DB_DUMP_FILE"
	@echo "  build-frontend   Builds the frontend static files"
	@echo "  build-frontend-w Watches the frontend static files and builds on change\n"

.docker-build:
	make build

build:
	cp ./docker/config/webapp.env.template ./docker/config/webapp.env
	sed -i -e 's/#SITE_URL#/$(subst /,\/,${SITE_URL})/g' ./docker/config/webapp.env

	${DC} build base
	${DC} build webapp

	touch .docker-build

setup: .docker-build
	${DC} run webapp /app/docker/set_up_webapp.sh

run: .docker-build
	${DC} run --rm --service-ports webapp

clean:
	rm .docker-build

test:
	./docker/run_tests_in_docker.sh ${ARGS}

test-frontend:
	${DOCKER} run --rm \
		-v `pwd`/frontend/src:/app/frontend/src \
		-v `pwd`/frontend/public:/app/frontend/public \
		--workdir /app/frontend \
		--tty \
		--interactive \
		local/pontoon yarn test

flow:
	${DOCKER} run --rm \
		-v `pwd`/frontend/src:/app/frontend/src \
		-v `pwd`/frontend/public:/app/frontend/public \
		-e SHELL=bash \
		--workdir /app/frontend \
		--tty --interactive \
		local/pontoon yarn flow:dev

shell:
	./docker/run_tests_in_docker.sh --shell

loaddb:
	-${DC} stop webapp
	-${DOCKER} exec -i `${DC} ps -q postgresql` dropdb -U pontoon pontoon
	${DOCKER} exec -i `${DC} ps -q postgresql` createdb -U pontoon pontoon
	${DOCKER} exec -i `${DC} ps -q postgresql` pg_restore -U pontoon -d pontoon -O < ${DB_DUMP_FILE}

build-frontend:
	${DC} run webapp npm run build

build-frontend-w:
	${DOCKER} run --rm \
		-v `pwd`/pontoon:/app/pontoon \
		--workdir /app \
		-e LOCAL_USER_ID=$UID \
		--tty --interactive \
		local/pontoon npm run build-w

# Old targets for backwards compatibility.
dockerbuild: build
dockersetup: setup
dockerrun: run
dockerclean: clean
dockertest: test
dockershell: shell
dockerloaddb: loaddb
dockerwebpack: build-frontend-w
