#!/usr/bin/env bash

set -e

pushd "${0%/*}" || exit 1 # Dir of the script
podman build --pull --tag gh-runner-image gh-self-hosted-runner-podman
popd || exit 1
