# We want to use Python 3.11, so bookworm is the best option, even though it's
# still testing.
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN \
  --mount=type=cache,target=/var/cache/apt \
  apt update && \
  apt upgrade -y && \
  apt install -y \
  nodejs \
  node-typescript \
  python3-dev \
  python3-pip \
  python3-venv \
  tini \
  wget \
  yarnpkg

# install watchexec
RUN \
  --mount=type=tmpfs,target=/tmp/watchexecinstall \
  cd /tmp/watchexecinstall && \
  wget -O watchexec.deb https://github.com/watchexec/watchexec/releases/download/v1.22.2/watchexec-1.22.2-x86_64-unknown-linux-gnu.deb && \
  apt install -y ./watchexec.deb
# This container runs as root so that the user can read all the bind mounts

VOLUME /mnt/source /mnt/venv /mnt/db /mnt/fixtures

WORKDIR /mnt/source

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/usr/bin/tini", "--"]
