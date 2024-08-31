#!/usr/bin/env bash

set -e
set -o pipefail

# You can run this script as-is. It will delete all assets in all tags except the assets in the latest tag.

# Delete all 7z files from a GitHub release
# Usage: delete_gh_release_assets <release>
# Example: delete_gh_release_assets "v0.9.13+2023-06-18-001"
function delete_gh_release_assets() {
  gh release view "$1"  --json assets -q '.assets[].name' | grep '\.7z$' | xargs -n1 gh release delete-asset "$1"
}

# Deletes all assets in parallel from all releases except from the latest release
# Documentation: Call bash function via xargs: https://unix.stackexchange.com/questions/158564/how-to-use-defined-function-with-xargs
export -f delete_gh_release_assets
gh release list --json tagName -q '.[1:].[].tagName' | xargs -P0 -n1 bash -c 'delete_gh_release_assets "$@"' _
