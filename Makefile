DC := $(shell which docker-compose)
DOCKER := $(shell which docker)

# *IMPORTANT*
# Don't use this instance in a production setting. More info at:
# https://docs.djangoproject.com/en/dev/ref/django-admin/#runserver
FRONTEND_URL ?= http://frontend:3000
SITE_URL ?= http://localhost:8000

USER_ID?=1000
GROUP_ID?=1000

.PHONY: build build-frontend build-webapp webapp-env setup run clean shell test test-webapp test-frontend jest pytest flake8 black prettier check-prettier format types eslint dumpdb loaddb build-tagadmin build-tagadmin-w sync-projects requirements

help:
	@echo "Welcome to Pontoon!\n"
	@echo "The list of commands for local development:\n"
	@echo "  build            Builds the docker images for the docker-compose setup"
	@echo "  build-frontend   Builds just the frontend image"
	@echo "  build-webapp     Builds just the Django webapp image"
	@echo "  webapp-env       Regenerates the env variable file used by webapp"
	@echo "  setup            Configures a local instance after a fresh build"
	@echo "  run              Runs the whole stack, served on http://localhost:8000/"
	@echo "  clean            Forces a rebuild of docker containers"
	@echo "  shell            Opens a Bash shell in a webapp docker container"
	@echo "  test             Runs the entire test suite (back and front)"
	@echo "  test-webapp      Runs the webapp test suite"
	@echo "  test-frontend    Runs the translate frontend test suite"
	@echo "  jest             Runs the jest test runner on all frontend tests"
	@echo "  pytest           Runs the backend's test suite (Python)"
	@echo "  flake8           Runs the flake8 style guides on all Python code"
	@echo "  black            Runs the black formatter on all Python code"
	@echo "  prettier         Runs the prettier formatter on the frontend code"
	@echo "  check-prettier   Runs a check for format issues with the prettier formatter"
	@echo "  format           Runs formatters for both the frontend and Python code"
	@echo "  types            Runs the tsc compiler to check TypeScript on all frontend code"
	@echo "  eslint           Runs a code linter on the JavaScript code"
	@echo "  dumpdb           Create a postgres database dump with timestamp used as file name"
	@echo "  loaddb           Load a database dump into postgres, file name in DB_DUMP_FILE"
	@echo "  build-tagadmin   Builds the tag_admin frontend static files"
	@echo "  build-tagadmin-w Watches the tag_admin frontend static files and builds on change"
	@echo "  sync-projects    Runs the synchronization task on all projects"
	@echo "  requirements     Compiles all requirements files with pip-compile\n"

.frontend-build:
	make build-frontend
.webapp-build:
	make build-webapp

build: build-frontend build-webapp
build-frontend: webapp-env
	"${DC}" build frontend
	touch .frontend-build
build-webapp: webapp-env
	"${DC}" build --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) webapp
	touch .webapp-build

webapp-env:
	cp ./docker/config/webapp.env.template ./docker/config/webapp.env
	sed -i -e 's/#FRONTEND_URL#/$(subst /,\/,${FRONTEND_URL})/g;s/#SITE_URL#/$(subst /,\/,${SITE_URL})/g' ./docker/config/webapp.env

setup: .webapp-build
	"${DC}" run webapp //app/docker/set_up_webapp.sh

run: .frontend-build .webapp-build
	"${DC}" up --no-build frontend webapp

clean:
	rm -f .docker-build .frontend-build .webapp-build

test: test-webapp test-frontend

test-webapp:
	"${DC}" run --rm webapp //app/docker/run_tests.sh

test-frontend: jest
jest:
	"${DC}" run --rm -w //frontend frontend yarn test

pytest:
	"${DC}" run ${run_opts} --rm webapp pytest --cov-report=xml:pontoon/coverage.xml --cov=. $(opts)

flake8:
	"${DC}" run --rm webapp flake8 pontoon/

black:
	"${DC}" run --rm webapp black pontoon/

pyupgrade:
	"${DC}" run --rm webapp pyupgrade --exit-zero-even-if-changed --py38-plus *.py `find pontoon -name \*.py`

types:
	"${DC}" run --rm -w //frontend frontend yarn types

prettier:
	"${DC}" run --rm webapp npm run prettier

check-prettier:
	"${DC}" run --rm webapp npm run check-prettier

format:
	make prettier
	make pyupgrade
	make black

eslint:
	"${DC}" run --rm webapp npm run eslint

shell:
	"${DC}" run --rm webapp //bin/bash

dumpdb:
	"${DOCKER}" exec -t `"${DC}" ps -q postgresql` pg_dumpall -c -U pontoon > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql

loaddb:
	# Stop connections to the database so we can drop it.
	-"${DC}" stop webapp
	# Make sure the postgresql container is running.
	-"${DC}" start postgresql
	-"${DC}" exec postgresql dropdb -U pontoon pontoon
	"${DC}" exec postgresql createdb -U pontoon pontoon
	# Note: docker-compose doesn't support the `-i` (--interactive) argument
	# that we need to send the dump file through STDIN. We thus are forced to
	# use docker here instead.
	"${DOCKER}" exec -i `"${DC}" ps -q postgresql` pg_restore -U pontoon -d pontoon -O < "${DB_DUMP_FILE}"

build-tagadmin:
	"${DC}" run --rm webapp npm run build

build-tagadmin-w:
	"${DC}" run --rm webapp npm run build-w

sync-projects:
	"${DC}" run --rm webapp .//manage.py sync_projects $(opts)

requirements:
	# Pass --upgrade to upgrade all dependencies
	# The arguments are passed through to pip-compile
	"${DC}" run --rm webapp //app/docker/compile_requirements.sh ${opts}
