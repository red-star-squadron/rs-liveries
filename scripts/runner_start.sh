#!/usr/bin/env bash

set -e

docker volume create --driver local \
    --opt type=tmpfs \
    --opt device=tmpfs \
    gh_tmpfs_vol || true

docker run \
  --detach \
  --env ORGANIZATION=red-star-squadron/rs-liveries \
  --env REG_TOKEN="REDACTED" \
  --name runner \
  -v gh_tmpfs_vol:/home/docker/actions-runner/_work \
  gh-runner-image
