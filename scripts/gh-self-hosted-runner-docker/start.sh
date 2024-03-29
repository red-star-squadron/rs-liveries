#!/bin/bash

cd /home/docker/actions-runner || exit 1

./config.sh --url "https://github.com/${ORGANIZATION}/${REPO}" --token "${REG_TOKEN}"

cleanup() {
    echo "Removing runner..."
    ./config.sh remove --token "${REG_TOKEN}"
}

trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM

./run.sh & wait $!
