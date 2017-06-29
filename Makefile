DC := $(shell which docker-compose)

.PHONY: dockerbuild dockersetup dockerclean dockertest dockertestshell dockerrun

all: dockerrun

.docker-build:
	make dockerbuild

dockerbuild:
	${DC} build base
	${DC} build webapp
	touch .docker-build

dockersetup: .docker-build
	${DC} run webapp /app/docker/set_up_webapp.sh

dockerclean:
	rm .docker-build

# dockertest:
# 	./docker/run_tests_in_docker.sh ${ARGS}
#
# dockertestshell:
# 	./docker/run_tests_in_docker.sh --shell

dockerrun:
	${DC} up webapp
