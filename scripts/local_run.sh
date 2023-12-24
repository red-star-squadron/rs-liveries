#!/usr/bin/env bash

set -e
set -o pipefail

# Warning, this will delete any files previously in Staging and Compressed dirs
echo "Cleaning up Staging and Compressed dirs"
sudo umount Staging || true
sudo umount Compressed || true

mkdir -p Staging
mkdir -p Compressed

# Now we can mount
sudo mount -t tmpfs -o uid=1000 tmpfs Staging/
sudo mount -t tmpfs -o uid=1000 tmpfs Compressed/

pipenv run python rs_liveries_downloader.py

pushd Staging || exit 1
makensis -V4 rs-liveries-rendered.nsi
popd || exit 1
