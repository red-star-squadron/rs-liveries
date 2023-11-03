#!/usr/bin/env bash

set -e

pushd "${0%/*}" || exit 1 # Dir of the script
docker build --tag gh-runner-image gh-self-hosted-runner-docker
popd || exit 1
