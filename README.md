# WorldMaster

[![License GNU-AGPLv3](.repo/license.svg)](https://codeberg.org/WorldMaster/WorldMaster/src/branch/main/LICENSE)

WorldMaster is a platform for managing, running, sharing, and recording online TTRPG games. 

# Development

[![Documentation Wiki](.repo/wiki.svg)](https://codeberg.org/WorldMaster/WorldMaster/wiki)
[![Codeberg Issue Tracker](.repo/issues.svg)](https://codeberg.org/WorldMaster/WorldMaster/issues)

The main development branch lives on [Codeberg](https://codeberg.org/WorldMaster/WorldMaster), and is the perferred location for issues and pull requests.

When developing, there is an easy set of containers available.  You work with these via [`just`](https://github.com/casey/just):

```sh
# Create containers, or restart them.
just containers

# The same as the above.
just

# Destroy all volumes and containers.
just clean

# Restart django and run migrations
just runserver
```

All docker resources are prefixed with `worldmaster-`.

You can clean them with

```sh
just clean
```

Which might be necessary to update dependencies.

`podman` is the default container runner. If you prefer to use docker, set your
`DOCKER` environment variable to `docker`, or set the `docker` `just` variable.

```sh
DOCKER=docker just
just docker=docker
```

When the containers are running, you can access django like usual, by going
to `127.0.0.1:8000`.

* You should not use `localhost`, because if that resolves to an IPv6 address,
  it will fail to resolve. [We can only listen on ipv4 or ipv6, not both at the
  same time](https://code.djangoproject.com/ticket/24864)).

* The first run of `worldmaster-django` will take a some time before it starts
  listening, becuase running the migrations takes a while.

* You can use `podman container attach worldmaster-django` to attach to the
  running container and see its output.  `podman container logs -f worldmaster-
  django` will do something similar, but without killing the container on exit.

* Containers are started with `--rm`.  Their persistent state is kept in
  volumes, not the container filesystem.

* You can rebuild images with `just images`.  This shouldn't be necessary unless
  you want to change or update the development image.
