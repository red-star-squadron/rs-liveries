#!/usr/bin/env bash

set -e

pipenv run python rs_liveries_downloader.py

pipenv run python rs_liveries_compress_and_checksum.py

cp 7za.exe Staging/

pushd Staging || exit 1
makensis -V4 rs-liveries-rendered.nsi
popd || exit 1
