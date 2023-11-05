set positional-arguments
set ignore-comments

_list:
	@just --list

# Build all images.
images: (image "development")

# Push all images.
push-images: (push-image "development")

# Build the named image as the worldmaster tag.
image name:
	podman image build --pull -t docker.io/worldmasterttrpg/worldmaster:{{name}} -f ./containers/{{name}}.Containerfile .

# Push the named image as the worldmaster tag.
push-image name: (image name)
	podman image push docker.io/worldmasterttrpg/worldmaster:{{name}}

# Start up development pods.  This is necessary to access the site on a web browser.
pods: postgres django watchtsc

# Tear down running worldmaster pods.
down:
	-just kube-down django
	-just kube-down watchtsc
	-just kube-down dev
	-just kube-down postgres

# Create the worldmaster network.
network:
	podman network inspect worldmaster >/dev/null 2>&1 || \
		podman network create worldmaster

# Run the postgres pod.
postgres: network
	podman pod inspect worldmaster-postgres >/dev/null 2>&1 || \
		podman kube play --network worldmaster ./containers/kube/postgres.yml

# Run the django pod, which runs `runserver`.
django: network postgres
	podman pod inspect worldmaster-django >/dev/null 2>&1 || \
		podman kube play --network worldmaster ./containers/kube/django.yml

# Run the watchtsc pod, which compiles typescript to js on all changes into the shared static volume.
watchtsc: network
	podman pod inspect worldmaster-watchtsc >/dev/null 2>&1 || \
		podman kube play --network worldmaster ./containers/kube/watchtsc.yml

# Start up the dev pod.  This is like the django pod, but just sets up the venv and drops you into a shell.
dev: network postgres
	podman pod inspect worldmaster-dev >/dev/null 2>&1 || \
		podman kube play --network worldmaster ./containers/kube/dev.yml

# Run a shell on the dev pod.
dev-shell: dev
	podman container exec -it worldmaster-dev-dev /bin/bash -il

# Run a django-admin command on the dev pod.
django-admin *args: dev
	podman container exec -it worldmaster-dev-dev /opt/worldmaster/venv/bin/django-admin "$@"

test: (django-admin 'test')
makemigrations: (django-admin 'makemigrations')

# Tear down the pod.
kube-down pod:
	podman kube down ./containers/kube/{{pod}}.yml
