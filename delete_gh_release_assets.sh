#!/usr/bin/env bash

set -e

# Delete all 7z files from a GitHub release
# Usage: delete_gh_release_assets <release>
# Example: delete_gh_release_assets "v0.9.13+2023-06-18-001"
function delete_gh_release_assets() {
  gh release view "$1"  --json assets -q '.assets[].name' | grep '\.7z$' | xargs -n1 gh release delete-asset "$1"
}

# You can get a list of releases by running:
# gh release list

delete_gh_release_assets "v0.9.13+2023-06-18-001"
delete_gh_release_assets "v0.9.13+2023-06-01-001"
delete_gh_release_assets "v0.9.13+2023-05-31-001"
delete_gh_release_assets "v0.9.12+2023-05-07-001"
delete_gh_release_assets "v0.9.11+2023-03-31-002"
delete_gh_release_assets "v0.9.10+2023-03-17-001"
delete_gh_release_assets "v0.9.9+2023-03-08-001"
delete_gh_release_assets "v0.9.9+2023-03-07-001"
delete_gh_release_assets "v0.9.8+2023-03-05-001"
delete_gh_release_assets "v0.9.8+2023-02-26-001"
delete_gh_release_assets "v0.9.7+2023-01-29-001"
delete_gh_release_assets "v0.9.6+2022-12-15-001"
