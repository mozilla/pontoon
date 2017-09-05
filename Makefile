DC := $(shell which docker-compose)
WEBAPP_HOST ?= localhost:8000

.PHONY: dockerbuild dockersetup dockerclean dockertest dockertestshell dockerrun

all: dockerrun

.docker-build:
	make dockerbuild

dockerbuild:
	cp ./docker/config/webapp.env.template ./docker/config/webapp.env
	sed -i 's/#WEBAPP_HOST#/${WEBAPP_HOST}/g' ./docker/config/webapp.env

	${DC} build base
	${DC} build webapp

	touch .docker-build

dockersetup: .docker-build
	${DC} run webapp /app/docker/set_up_webapp.sh

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
	${DC} up webapp
