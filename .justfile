set positional-arguments

export DOCKER := env_var_or_default('DOCKER', 'podman')

# Run containers
all: containers

images: (image "development")

volumes: (volume "static") (volume "fixtures") (volume "venv") (volume "db")

image name:
	"{{DOCKER}}" image build -t worldmaster:{{name}} -f ./oci/{{name}}.Containerfile .

volume name:
	"{{DOCKER}}" volume create --ignore worldmaster-{{name}}

# runserver and watchtsc
containers: runserver watchtsc

# this is a pretty complex little job.  I'd like a better way of handling this.

# Runs a django `manage.py {{args}}`, possibly in the background.
development *args='': (image "development") (volume "static") (volume "venv") (volume "db")
	#!/usr/bin/env python3

	from os import environ, execvp
	from shlex import join, quote
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument('--port', '-p', type=int)
	parser.add_argument('--background', '-b', action='store_true')
	parser.add_argument('--name', '-n')
	parser.add_argument('--entrypoint', '-e', default='/mnt/source/oci/django.sh')
	parser.add_argument('--writable', '-w', action='append', default=['venv', 'db'])
	parser.add_argument('args', nargs='*')
	args = parser.parse_args()

	docker = environ['DOCKER']

	cmd = [docker, 'container', 'run', '--rm', '--security-opt', 'label=disable']

	if args.background:
		cmd += ['-d']
	else:
		cmd += ['-it']

	if args.name is not None:
		cmd += ['--replace', '--name', args.name]

	cmd += [
		'--env', 'worldmaster_db=/mnt/db/db.sqlite3',
		'--env', 'worldmaster_static=/mnt/static',
		'--env', 'worldmaster_fixtures=/mnt/fixtures',
		'--mount', 'type=bind,source=.,destination=/mnt/source,ro=true',
	]

	for name in ('static', 'venv', 'db', 'fixtures'):
		spec = f'type=volume,source=worldmaster-{name},destination=/mnt/{name}'
		if name not in args.writable:
			spec += ',ro=true'
		cmd += ['--mount', spec]

	if args.port is not None:
		cmd += ['--publish', f'{args.port}:{args.port}']

	cmd += [
		'worldmaster:development',
		args.entrypoint,
	]

	if args.args:
		cmd += args.args

	print(f'executing {quote(join(cmd))}')
	execvp(cmd[0], cmd)

# Runs django `manage.py shell_plus`
shell: (development 'shell_plus')

# Runs django `manage.py runserver` in the background
runserver: (development '-bp8080' '-nworldmaster-django' 'shell_plus')

# This technically mounts more things than need to be mounted, because the tsc
# watcher doesn't need the db or anything.  We'll deal with that for now.

# Runs watchexec on tsc files in the background.
watchtsc: (development '-nbworldmaster-tsc' '-e/mnt/source/oci/tsc.sh' '-wstatic')

# Runs django manage.py dumpdata 
dumpdata: (development '-e/mnt/source/oci/dumpdata.sh' '-wfixtures')
	mkdir -p fixtures

	"{{DOCKER}}" volume export worldmaster-fixtures | tar -C fixtures -xv

	"{{DOCKER}}" volume rm worldmaster-fixtures

clean:
	-"{{DOCKER}}" container stop worldmaster-tsc
	-"{{DOCKER}}" container stop worldmaster-django
	-"{{DOCKER}}" volume rm worldmaster-static
	-"{{DOCKER}}" volume rm worldmaster-venv
	-"{{DOCKER}}" volume rm worldmaster-db
	-"{{DOCKER}}" volume rm worldmaster-fixtures
