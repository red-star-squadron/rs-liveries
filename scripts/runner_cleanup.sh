#!/usr/bin/env bash

podman stop runner
podman rm runner
podman volume rm gh_tmpfs_vol
