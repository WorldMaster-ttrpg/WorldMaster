FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN \
  --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  set -euxf; \
  apt update; \
  apt upgrade -y; \
  apt install -y \
    node-typescript \
    nodejs \
    python3-dev \
    python3-pip \
    python3-venv \
    tini \
    wget \
    yarnpkg \
  ; \
  :

# install watchexec for the tsc recompilation
RUN \
  --mount=type=tmpfs,target=/tmp/watchexecinstall \
  set -euxf; \
  cd /tmp/watchexecinstall; \
  wget -O watchexec.deb https://github.com/watchexec/watchexec/releases/download/v1.23.0/watchexec-1.23.0-x86_64-unknown-linux-gnu.deb; \
  apt install -y ./watchexec.deb; \
  :

WORKDIR /mnt/source

# Note: We always run development boxes as root.  This is because root in the
# container, by default, maps to the user outside the container. This can give
# the container the right to write into the source directory.

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/usr/bin/tini", "--"]
