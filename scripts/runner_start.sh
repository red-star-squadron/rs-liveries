#!/usr/bin/env bash

set -e
set -o pipefail

ORG=red-star-squadron
REPO=rs-liveries

gh_get_token() {
  gh api \
    --method POST \
    -H 'Accept: application/vnd.github+json' \
    -H 'X-GitHub-Api-Version: 2022-11-28' \
    /repos/$ORG/$REPO/actions/runners/registration-token
}

mydocker() {
  docker -l error "$@"
}

if mydocker inspect -f '{{.State.Running}}' "runner" > /dev/null 2>&1
  then
  echo "Clean up existing docker resources"
  mydocker stop runner > /dev/null
  mydocker rm runner > /dev/null
  mydocker volume rm gh_tmpfs_vol > /dev/null
fi

echo "Create the docker volume"
mydocker volume create --driver local \
    --opt type=tmpfs \
    --opt device=tmpfs \
    gh_tmpfs_vol > /dev/null


echo "Grab GH hosted runner token"
REG_TOKEN="$(gh_get_token | jq -r .token)"

echo "Start the gh hosted runner in docker"
mydocker run \
  --detach \
  --env ORGANIZATION="${ORG}" \
  --env REG_TOKEN="${REG_TOKEN}" \
  --env REPO="${REPO}" \
  --name runner \
  -v gh_tmpfs_vol:/home/docker/actions-runner/_work \
  gh-runner-image > /dev/null

echo "Check the status of this docker container with:"
echo "docker logs -f runner"
