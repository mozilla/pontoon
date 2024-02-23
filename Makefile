DC := $(shell which docker-compose)
DOCKER := $(shell which docker)

# *IMPORTANT*
# Don't use this instance in a production setting. More info at:
# https://docs.djangoproject.com/en/dev/ref/django-admin/#runserver
SITE_URL ?= http://localhost:8000

USER_ID?=1000
GROUP_ID?=1000

.PHONY: build build-translate build-tagadmin build-server server-env setup run clean shell ci test test-translate test-tagadmin test-server jest pytest format lint types eslint prettier check-prettier flake8 pyupgrade check-pyupgrade black check-black dropdb dumpdb loaddb sync-projects requirements

help:
	@echo "Welcome to Pontoon!\n"
	@echo "The list of commands for local development:\n"
	@echo "  build            Builds the docker images for the docker-compose setup"
	@echo "  build-translate  Builds just the translate frontend component"
	@echo "  build-tagadmin   Builds just the tag-admin frontend component"
	@echo "  build-server     Builds just the Django server image"
	@echo "  server-env       Regenerates the env variable file used by server"
	@echo "  setup            Configures a local instance after a fresh build"
	@echo "  run              Runs the whole stack, served on http://localhost:8000/"
	@echo "  clean            Forces a rebuild of docker containers"
	@echo "  shell            Opens a Bash shell in a server docker container"
	@echo "  ci               Test and lint all code"
	@echo "  test             Runs all test suites"
	@echo "  test-translate   Runs the translate frontend test suite (Jest)"
	@echo "  test-tagadmin    Runs the tag-admin test suite (Jest)"
	@echo "  test-server      Runs the server test suite (Pytest)"
	@echo "  format           Runs all formatters"
	@echo "  lint             Runs all linters"
	@echo "  types            Runs the tsc compiler to check TypeScript on all frontend code"
	@echo "  eslint           Runs a code linter on the JavaScript code"
	@echo "  prettier         Runs the Prettier formatter"
	@echo "  check-prettier   Runs a check for format issues with the Prettier formatter"
	@echo "  flake8           Runs the flake8 style guides on all Python code"
	@echo "  pyupgrade        Upgrades all Python code to newer syntax of Python"
	@echo "  check-pyupgrade  Runs a check for outdated syntax of Python with the pyupgrade formatter"
	@echo "  black            Runs the black formatter on all Python code"
	@echo "  check-black      Runs a check for format issues with the black formatter"
	@echo "  dropdb           Completely remove the postgres container and its data"
	@echo "  dumpdb           Create a postgres database dump with timestamp used as file name"
	@echo "  loaddb           Load a database dump into postgres, file name in DB_DUMP_FILE"
	@echo "  sync-projects    Runs the synchronization task on all projects"
	@echo "  requirements     Compiles all requirements files with pip-compile\n"

translate/dist:
	make build-translate
tag-admin/dist:
	make build-tagadmin
.server-build:
	make build-server
node_modules:
	npm install

build: build-translate build-tagadmin build-server

build-translate: node_modules
	npm run build -w translate

build-tagadmin: node_modules
	npm run build -w tag-admin

build-server: server-env translate/dist tag-admin/dist
	"${DC}" build --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) server
	touch .server-build

server-env:
	sed -e 's/#SITE_URL#/$(subst /,\/,${SITE_URL})/g' \
	./docker/config/server.env.template > ./docker/config/server.env

setup: .server-build
	"${DC}" run server //app/docker/server_setup.sh

run: translate/dist tag-admin/dist .server-build
	"${DC}" up --detach
	bash -c 'set -m; bash ./bin/watch.sh'
	"${DC}" stop

clean:
	rm -rf translate/dist tag-admin/dist .server-build

shell:
	"${DC}" run --rm server //bin/bash

ci: test lint

test: test-server test-translate test-tagadmin

test-translate: jest
jest:
	npm test -w translate

test-tagadmin:
	npm test -w tag-admin

test-server: pytest
pytest:
	"${DC}" run ${run_opts} --rm server pytest --cov-report=xml:pontoon/coverage.xml --cov=. $(opts)

format: prettier pyupgrade black

lint: types eslint check-prettier flake8 check-pyupgrade check-black

types:
	npm run types -w translate

eslint:
	npm run eslint

prettier:
	npm run prettier

check-prettier:
	npm run check-prettier

flake8:
	"${DC}" run --rm server flake8 pontoon/

pyupgrade:
	"${DC}" run --rm server pyupgrade --exit-zero-even-if-changed --py39-plus *.py `find pontoon -name \*.py`

check-pyupgrade:
	"${DC}" run --rm server pyupgrade --py39-plus *.py `find pontoon -name \*.py`

black:
	"${DC}" run --rm server black pontoon/

check-black:
	"${DC}" run --rm server black --check pontoon

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

sync-projects:
	"${DC}" run --rm server .//manage.py sync_projects $(opts)

requirements:
	# Pass --upgrade to upgrade all dependencies
	# The arguments are passed through to pip-compile
	"${DC}" run --rm server //app/docker/compile_requirements.sh ${opts}
