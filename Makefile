all: dockerrun

.PHONY: dockerbuild dockersetup dockerclean dockertest dockertestshell dockerrun

DC := $(shell which docker-compose)

.docker-build:
	make dockerbuild

dockerbuild:
	${DC} build webapp
	touch .docker-build

dockersetup: .docker-build
	${DC} exec webapp python /app/manage.py createsuperuser
	${DC} exec webapp python /app/manage.py updatefxaprovider

dockerclean:
	rm .docker-build

# dockertest:
# 	./docker/run_tests_in_docker.sh ${ARGS}
#
# dockertestshell:
# 	./docker/run_tests_in_docker.sh --shell

dockerrun:
	${DC} up
