set positional-arguments

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
pods: django watchtsc

# Tear down running worldmaster pods.
down:
	-just down-django
	-just down-watchtsc
	-just down-dev

# Run the django pod, which runs `runserver`.
django:
	podman kube play ./containers/kube/django.yml

# Run the watchtsc pod, which compiles typescript to js on all changes into the shared static volume.
watchtsc:
	podman kube play ./containers/kube/watchtsc.yml

# Start up a dev pod and run a shell on it with the venv activated.  This is usefull for running arbitrary django-admin commands in arbitrary ways.
dev:
	podman pod inspect worldmaster-dev >/dev/null 2>&1 || \
		podman kube play ./containers/kube/dev.yml
	podman container exec -it worldmaster-dev-dev /bin/bash -il

# Run makemigrations in the dev pod.
makemigrations:
	podman pod inspect worldmaster-dev >/dev/null 2>&1 || \
		podman kube play ./containers/kube/dev.yml
	podman container exec -it worldmaster-dev-dev /opt/worldmaster/venv/bin/django-admin makemigrations

# Run shell_plus in the dev pod.
shell_plus:
	podman pod inspect worldmaster-dev >/dev/null 2>&1 || \
		podman kube play ./containers/kube/dev.yml
	podman container exec -it worldmaster-dev-dev /opt/worldmaster/venv/bin/django-admin shell_plus

# Tear down the django pod.
down-django:
	podman kube down ./containers/kube/django.yml

# Tear down the watchtsc pod.
down-watchtsc:
	podman kube down ./containers/kube/watchtsc.yml

# Tear down the dev pod.
down-dev:
	podman kube down ./containers/kube/dev.yml
