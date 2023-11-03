#!/usr/bin/env bash

set -e

docker stop runner
docker rm runner
docker volume rm gh_tmpfs_vol
