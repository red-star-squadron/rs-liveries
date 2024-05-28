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

mypodman() {
  podman --log-level error "$@"
}

if mypodman inspect -f '{{.State.Running}}' "runner" > /dev/null 2>&1
  then
  echo "Clean up existing podman resources"
  mypodman stop runner > /dev/null
  mypodman rm runner > /dev/null
  mypodman volume rm gh_tmpfs_vol > /dev/null
fi

echo "Create the podman volume"
mypodman volume create --driver local \
    --opt type=tmpfs \
    --opt device=tmpfs \
    gh_tmpfs_vol > /dev/null


echo "Grab GH hosted runner token"
REG_TOKEN="$(gh_get_token | jq -r .token)"

echo "Start the gh hosted runner in podman"
mypodman run \
  --detach \
  --env ORGANIZATION="${ORG}" \
  --env REG_TOKEN="${REG_TOKEN}" \
  --env REPO="${REPO}" \
  --name runner \
  -v gh_tmpfs_vol:/home/docker/actions-runner/_work \
  gh-runner-image > /dev/null

echo "Check the status of this podman container with:"
echo "podman logs -f runner"
