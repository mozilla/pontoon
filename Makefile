DC := $(shell which docker-compose)
DOCKER := $(shell which docker)

# *IMPORTANT*
# Don't use this instance in a production setting. More info at:
# https://docs.djangoproject.com/en/dev/ref/django-admin/#runserver
FRONTEND_URL ?= http://frontend:3000
SITE_URL ?= http://localhost:8000

USER_ID?=1000
GROUP_ID?=1000

.PHONY: build build-frontend build-server server-env setup run clean shell ci test test-frontend test-server jest pytest format lint types eslint prettier check-prettier flake8 pyupgrade check-pyupgrade black check-black dropdb dumpdb loaddb build-tagadmin build-tagadmin-w sync-projects requirements

help:
	@echo "Welcome to Pontoon!\n"
	@echo "The list of commands for local development:\n"
	@echo "  build            Builds the docker images for the docker-compose setup"
	@echo "  build-frontend   Builds just the frontend image"
	@echo "  build-server     Builds just the Django server image"
	@echo "  server-env       Regenerates the env variable file used by server"
	@echo "  setup            Configures a local instance after a fresh build"
	@echo "  run              Runs the whole stack, served on http://localhost:8000/"
	@echo "  clean            Forces a rebuild of docker containers"
	@echo "  shell            Opens a Bash shell in a server docker container"
	@echo "  ci               Test and lint both frontend and server"
	@echo "  test             Runs both frontend and server test suites"
	@echo "  test-frontend    Runs the translate frontend test suite (Jest)"
	@echo "  test-server      Runs the server test suite (Pytest)"
	@echo "  format           Runs formatters for both the frontend and Python code"
	@echo "  lint             Runs linters for both the frontend and Python code"
	@echo "  types            Runs the tsc compiler to check TypeScript on all frontend code"
	@echo "  eslint           Runs a code linter on the JavaScript code"
	@echo "  prettier         Runs the prettier formatter on the frontend code"
	@echo "  check-prettier   Runs a check for format issues with the prettier formatter"
	@echo "  flake8           Runs the flake8 style guides on all Python code"
	@echo "  pyupgrade        Upgrades all Python code to newer syntax of Python"
	@echo "  check-pyupgrade  Runs a check for outdated syntax of Python with the pyupgrade formatter"
	@echo "  black            Runs the black formatter on all Python code"
	@echo "  check-black      Runs a check for format issues with the black formatter"
	@echo "  dropdb           Completely remove the postgres container and its data"
	@echo "  dumpdb           Create a postgres database dump with timestamp used as file name"
	@echo "  loaddb           Load a database dump into postgres, file name in DB_DUMP_FILE"
	@echo "  build-tagadmin   Builds the tag_admin frontend static files"
	@echo "  build-tagadmin-w Watches the tag_admin frontend static files and builds on change"
	@echo "  sync-projects    Runs the synchronization task on all projects"
	@echo "  requirements     Compiles all requirements files with pip-compile\n"

.frontend-build:
	make build-frontend
.server-build:
	make build-server

build: build-frontend build-server
build-frontend: server-env
	"${DC}" build frontend
	touch .frontend-build
build-server: server-env
	"${DC}" build --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) server
	touch .server-build

server-env:
	cp ./docker/config/server.env.template ./docker/config/server.env
	sed -i -e 's/#FRONTEND_URL#/$(subst /,\/,${FRONTEND_URL})/g;s/#SITE_URL#/$(subst /,\/,${SITE_URL})/g' ./docker/config/server.env

setup: .server-build
	"${DC}" run server //app/docker/server_setup.sh

run: .frontend-build .server-build
	"${DC}" up

clean:
	rm -f .docker-build .frontend-build .server-build

shell:
	"${DC}" run --rm server //bin/bash

ci: test lint

test: test-server test-frontend

test-frontend: jest
jest:
	"${DC}" run --rm -w //frontend frontend npm test

test-server: pytest
pytest:
	"${DC}" run ${run_opts} --rm server pytest --cov-report=xml:pontoon/coverage.xml --cov=. $(opts)

format: prettier pyupgrade black

lint: types eslint check-prettier flake8 check-pyupgrade check-black

types:
	"${DC}" run --rm -w //frontend frontend npm run types

eslint:
	"${DC}" run --rm frontend npm run lint
	"${DC}" run --rm server npm run eslint

prettier:
	"${DC}" run --rm frontend npm run prettier
	"${DC}" run --rm server npm run prettier

check-prettier:
	"${DC}" run --rm frontend npm run check-prettier
	"${DC}" run --rm server npm run check-prettier

flake8:
	"${DC}" run --rm server flake8 pontoon/

pyupgrade:
	"${DC}" run --rm server pyupgrade --exit-zero-even-if-changed --py38-plus *.py `find pontoon -name \*.py`

check-pyupgrade:
	"${DC}" run --rm webapp pyupgrade --py38-plus *.py `find pontoon -name \*.py`

black:
	"${DC}" run --rm server black pontoon/

check-black:
	"${DC}" run --rm webapp black --check pontoon

dropdb:
	"${DC}" down --volumes postgresql

dumpdb:
	"${DOCKER}" exec -t `"${DC}" ps -q postgresql` pg_dumpall -c -U pontoon > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql

loaddb:
	# Stop connections to the database so we can drop it.
	-"${DC}" stop server
	# Make sure the postgresql container is running.
	-"${DC}" start postgresql
	-"${DC}" exec postgresql dropdb -U pontoon pontoon
	"${DC}" exec postgresql createdb -U pontoon pontoon
	# Note: docker-compose doesn't support the `-i` (--interactive) argument
	# that we need to send the dump file through STDIN. We thus are forced to
	# use docker here instead.
	"${DOCKER}" exec -i `"${DC}" ps -q postgresql` pg_restore -U pontoon -d pontoon -O < "${DB_DUMP_FILE}"

build-tagadmin:
	"${DC}" run --rm server npm run build

build-tagadmin-w:
	"${DC}" run --rm server npm run build-w

sync-projects:
	"${DC}" run --rm server .//manage.py sync_projects $(opts)

requirements:
	# Pass --upgrade to upgrade all dependencies
	# The arguments are passed through to pip-compile
	"${DC}" run --rm server //app/docker/compile_requirements.sh ${opts}
