#!/usr/bin/env bash

set -e

docker stop runner || true
docker rm runner || true
docker volume rm gh_tmpfs_vol || true
