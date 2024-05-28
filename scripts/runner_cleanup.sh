#!/usr/bin/env bash

set -e

podman stop runner
podman rm runner
podman volume rm gh_tmpfs_vol
