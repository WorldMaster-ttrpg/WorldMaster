set positional-arguments

export DOCKER := env_var_or_default('DOCKER', 'podman')

# Run containers
all: containers

images: (image "development")

image name:
	"{{DOCKER}}" image build -t worldmaster:{{name}} -f ./oci/{{name}}.Containerfile .

# runserver and watchtsc
containers: runserver watchtsc

# Runs a django `manage.py {{args}}`, possibly in the background.
development *args='': (image "development")
	#!/usr/bin/env python3

	from os import environ, execvp, getuid, getgid
	from shlex import join
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument('--port', '-p', type=lambda value: tuple(map(int, value.split(':'))))
	parser.add_argument('--background', '-b', action='store_true')
	parser.add_argument('--name', '-n')
	parser.add_argument('--entrypoint', '-E', default='/mnt/source/oci/django.sh')
	parser.add_argument('--container-arg', '-a', action='append', default=[])
	parser.add_argument('--mount', '-m', action='append', default=['static', 'fixtures'])
	parser.add_argument('--write-mount', '-w', action='append', default=['dev'])
	parser.add_argument('args', nargs='*')
	args = parser.parse_args()

	# Need to make sure we maintain order.
	writable = args.write_mount
	writable_set = frozenset(writable)
	read_only = [i for i in args.mount if i not in writable_set]

	cmd = [
		environ.get('DOCKER', 'podman'), 'container', 'run', '--rm',
		'--security-opt', 'label=disable',
		'-d' if args.background else '-it',
		'--userns', 'keep-id',
		'--user', f'{getuid()}:{getgid()}',
		'--env', 'venv=/mnt/venv',
		'--mount', 'type=volume,source=worldmaster-venv,destination=/mnt/venv',
		'--mount', 'type=bind,source=.,destination=/mnt/source,ro=true',
	]

	for name in read_only:
		cmd += [
			'--mount',
			f'type=bind,source=./{name},destination=/mnt/source/{name},ro=true',
		]

	for name in writable:
		cmd += [
			'--mount',
			f'type=bind,source=./{name},destination=/mnt/source/{name},ro=false',
		]

	if args.name is not None:
		cmd += ['--replace', '--name', args.name]

	port = args.port
	if port:
		cmd.append('--publish')

		if len(port) == 1:
			port *= 2

		cmd.append(':'.join(map(str, port)))

	cmd += args.container_arg

	cmd += [
		'worldmaster:development',
		args.entrypoint,
	] + args.args

	print(f'executing {join(cmd)}')
	execvp(cmd[0], cmd)

# Runs django `manage.py shell_plus`
shell: (development 'shell_plus')

# Runs django `manage.py runserver` in the background
runserver: (development '-bp8000' '-nworldmaster-django' 'runserver' '0.0.0.0:8000')

# Runs django `manage.py makemigrations`
makemigrations: (
	development
	'-w' 'src/roles/migrations'
	'-w' 'src/wiki/migrations'
	'-w' 'src/worldmaster/migrations'
	'-w' 'src/worlds/migrations'
	'makemigrations'
)


# Creates a dev:dev superuser
createsuperuser username='dev' password='dev': (
	development
	'-wsource'
	('-a-eDJANGO_SUPERUSER_PASSWORD=' + password)
	'--' 'createsuperuser'
	'--username' username
	'--email' 'dev@worldmaster.test'
	'--noinput'
)

# Creates a dev:dev superuser
createuser username password='': (
	development
	'-wsource'
	('-a-eusername=' + username)
	("-a-epassword=" + password)
	'--' 'shell'
	'-c' '''
from worldmaster.models import User
from getpass import getpass
from os import environ
username = environ["username"]
User.objects.create_user(
	username = username,
	password = environ.get("password") or getpass(),
	email = f"{username}@worldmaster.test",
)
'''
)

# This technically mounts more things than need to be mounted, because the tsc
# watcher doesn't need the db or anything.  We'll live with that for now.

# Runs watchexec on tsc files in the background.
watchtsc: (development '-bnworldmaster-tsc' '-E/mnt/source/oci/tsc.sh' '-wstatic')

# Runs django manage.py dumpdata 
dumpdata: (development '-E/mnt/source/oci/dumpdata.sh' '-wfixtures')

clean:
	-"{{DOCKER}}" container stop -i worldmaster-tsc worldmaster-django
	-"{{DOCKER}}" volume rm -f worldmaster-venv
