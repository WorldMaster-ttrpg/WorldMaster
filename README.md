# WorldMaster

![License GNU-AGPLv3](.repo/license.svg)
WorldMaster is a platform for managing, running, sharing, and recording online TTRPG games. 

# Development

When developing, there is an easy set of containers available.  You work with these via `make`:

```sh
# Create containers, or restart them.
make containers

# The same as the above.
make

# Destroy all volumes and containers.
make clean

# Just restart django and run migrations
make worldmaster-django
```

All docker resources are prefixed with `worldmaster-`.

You can clean them with

```sh
make clean
```

Which might be necessary to update dependencies.

If you prefer to use podman, set your `DOCKER` environment variable to `podman`.

When the containers are running, you can access django like usual, by going
to `127.0.0.1:8000`.

## Notes

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
