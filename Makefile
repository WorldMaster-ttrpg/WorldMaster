DOCKER ?= docker

.PHONY: all clean \
	images development_image \
	containers worldmaster-django worldmaster-tsc \
	volumes worldmaster-static worldmaster-db worldmaster-venv 

all: containers

images: development_image

containers: worldmaster-django worldmaster-tsc

volumes: worldmaster-static worldmaster-venv worldmaster-db

development_image:
	$(DOCKER) image build -t worldmaster:development -f ./oci/development.Containerfile .

worldmaster-static:
	$(DOCKER) volume create --ignore worldmaster-static

worldmaster-venv:
	$(DOCKER) volume create --ignore worldmaster-venv

worldmaster-db:
	$(DOCKER) volume create --ignore worldmaster-db

# Runs django manage.py django in the background
worldmaster-django: development_image worldmaster-static worldmaster-venv worldmaster-db
	$(DOCKER) container run --replace --rm -d \
		--name worldmaster-django \
		--security-opt label=disable \
		--mount type=bind,source=.,destination=/mnt/source,ro=true \
		--mount type=volume,source=worldmaster-static,destination=/mnt/static,ro=true \
		--mount type=volume,source=worldmaster-venv,destination=/mnt/venv \
		--mount type=volume,source=worldmaster-db,destination=/mnt/db \
		--env worldmaster_db=/mnt/db/db.sqlite3 \
		--env worldmaster_static=/mnt/static \
		--publish 8000:8000 \
		worldmaster:development \
		/mnt/source/oci/django.sh \
		runserver \
		0.0.0.0:8000

# Runs django manage.py shell_plus in the foreground
shell: development_image worldmaster-static worldmaster-venv worldmaster-db
	$(DOCKER) container run -it --rm \
		--security-opt label=disable \
		--mount type=bind,source=.,destination=/mnt/source,ro=true \
		--mount type=volume,source=worldmaster-static,destination=/mnt/static,ro=true \
		--mount type=volume,source=worldmaster-venv,destination=/mnt/venv \
		--mount type=volume,source=worldmaster-db,destination=/mnt/db \
		--env worldmaster_db=/mnt/db/db.sqlite3 \
		--env worldmaster_static=/mnt/static \
		worldmaster:development \
		/mnt/source/oci/django.sh \
		shell_plus

# Runs watchexec on tsc files in the background
worldmaster-tsc: development_image worldmaster-static
	$(DOCKER) container run --replace --rm -d \
		--name worldmaster-tsc \
		--security-opt label=disable \
		--mount type=bind,source=.,destination=/mnt/source,ro=true \
		--mount type=volume,source=worldmaster-static,destination=/mnt/static \
		--env worldmaster_static=/mnt/static \
		worldmaster:development \
		/mnt/source/oci/tsc.sh

clean:
	-$(DOCKER) container stop worldmaster-tsc
	-$(DOCKER) container stop worldmaster-django
	-$(DOCKER) volume rm worldmaster-static
	-$(DOCKER) volume rm worldmaster-venv
	-$(DOCKER) volume rm worldmaster-db
