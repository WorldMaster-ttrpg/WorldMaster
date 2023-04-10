docker := env_var_or_default('DOCKER', 'podman')

all: containers

images: (image "development")

volumes: (volume "static") (volume "fixtures") (volume "venv") (volume "db")

image name:
	"{{docker}}" image build -t worldmaster:{{name}} -f ./oci/{{name}}.Containerfile .

volume name:
	"{{docker}}" volume create --ignore worldmaster-{{name}}

containers: runserver watchtsc

# Runs django manage.py django in the background
runserver: (image "development") (volume "static") (volume "venv") (volume "db")
	"{{docker}}" container run --replace --rm -d \
		--name worldmaster-django \
		--security-opt label=disable \
		--mount type=bind,source=.,destination=/mnt/source,ro=true \
		--mount type=volume,source=worldmaster-static,destination=/mnt/static,ro=true \
		--mount type=volume,source=worldmaster-venv,destination=/mnt/venv \
		--mount type=volume,source=worldmaster-db,destination=/mnt/db \
		--env worldmaster_db=/mnt/db/db.sqlite3 \
		--env worldmaster_static=/mnt/static \
		--env worldmaster_fixtures=/mnt/fixtures \
		--publish 8000:8000 \
		worldmaster:development \
		/mnt/source/oci/django.sh

# Runs watchexec on tsc files in the background
watchtsc: (image "development") (volume "static")
	"{{docker}}" container run --replace --rm -d \
		--name worldmaster-tsc \
		--security-opt label=disable \
		--mount type=bind,source=.,destination=/mnt/source,ro=true \
		--mount type=volume,source=worldmaster-static,destination=/mnt/static \
		--env worldmaster_static=/mnt/static \
		worldmaster:development \
		/mnt/source/oci/tsc.sh

# Runs django manage.py dumpdata 
dumpdata: (image "development") (volume "static") (volume "venv") (volume "db") (volume "fixtures")
	"{{docker}}" container run --rm \
		--security-opt label=disable \
		--mount type=bind,source=.,destination=/mnt/source,ro=true \
		--mount type=volume,source=worldmaster-venv,destination=/mnt/venv \
		--mount type=volume,source=worldmaster-db,destination=/mnt/db \
		--mount type=volume,source=worldmaster-fixtures,destination=/mnt/fixtures \
		--env worldmaster_db=/mnt/db/db.sqlite3 \
		--env worldmaster_fixtures=/mnt/fixtures \
		worldmaster:development \
		/mnt/source/oci/dumpdata.sh

	mkdir -p fixtures

	"{{docker}}" volume export worldmaster-fixtures | tar -C fixtures -xv

	"{{docker}}" volume rm worldmaster-fixtures

clean:
	-"{{docker}}" container stop worldmaster-tsc
	-"{{docker}}" container stop worldmaster-django
	-"{{docker}}" volume rm worldmaster-static
	-"{{docker}}" volume rm worldmaster-venv
	-"{{docker}}" volume rm worldmaster-db
	-"{{docker}}" volume rm worldmaster-fixtures
