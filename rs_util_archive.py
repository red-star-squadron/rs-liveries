"""
This script aims to compress the individual liveries and then
create checksums of individual livery archives.

We use ThreadPoolExecutor from the concurrent.features module.
This is so we can utilize maximum resources of any given system this runs on.

Concurrency is particulary useful on systems with many threads available as we
do a tally of how many threads are available to python, and then use them all.

In short, here are the steps. Note that they are jumbled due to concurrency.

* Grab the pickle file from rs_liveries_downloader
  It contains info about the liveries and their locations
* Concurrently invoke the sevenz_archive function which:
  * Compresses the given livery (or roughmet or bin)
  * Removes the processed source files
  * Creates a checksum

Checksum feature in a bit more detail
* Runs the 7z utility (as-in system binary) to extract the archive to stdout
* Gets the checksum of the stdout
* Writes the checksum as <basename_of_7z>.sha256sum
"""

# pickle to import our liveries data from disk
from pickle import load as pickle_load

# subprocess to run 7z outside of python
from subprocess import run as sp_run
from subprocess import PIPE as sp_pipe

# Checksum stuff
from hashlib import sha256
from locale import getpreferredencoding

# Path stuff
from os.path import join as os_join
from os import remove as os_remove
from pathlib import Path, PurePath
from shutil import rmtree

# concurrency stuff
from concurrent.futures import ThreadPoolExecutor
from os import sched_getaffinity

# Our includes
from rs_util_shared import MINIMAL_SAMPLE_SIZE
from rs_util_shared import CHECKSUMS_DIR
from rs_util_shared import COMPRESSED_DIR
from rs_util_shared import DELETE_AFTER_COMPRESS

# Set up our threadpool executor so it has NUM_CPUS threads
available_cpus = len(sched_getaffinity(0))
EXECUTOR = ThreadPoolExecutor(max_workers=available_cpus)


def load_rs_var_dump():
    with open("rs_var_dump.pickle", "rb") as f:
        rs_var_dump = pickle_load(f)
    return rs_var_dump


def calculate_and_write_checksum(input_7z):
    z_subprocess = sp_run(
        ["7z", "e", "-so", "-mmt=4", input_7z],
        stdout=sp_pipe,
        stderr=sp_pipe,
        check=True,
        text=False,
    )
    chksum = sha256(z_subprocess.stdout).hexdigest()
    dest_chksumfile = os_join(CHECKSUMS_DIR, PurePath(input_7z).stem + ".sha256sum")
    print(f"Checksum: '{chksum}' -> '{dest_chksumfile}'")
    Path(Path(dest_chksumfile).resolve().parents[0]).mkdir(parents=True, exist_ok=True)
    with open(dest_chksumfile, "w", encoding=getpreferredencoding()) as file_final:
        file_final.write(chksum)
    return


def sevenz_archive(entrypoint, files_and_or_dirs, destination_file):
    if MINIMAL_SAMPLE_SIZE:
        sevenz_exec = ["7z", "a", "-bd", "-bb0", "-mx=1", "-mmt=4"]
    else:
        sevenz_exec = ["7z", "a", "-bd", "-bb0", "-mx=9", "-mmt=4"]
    appended_files_and_or_dirs = []
    for file in files_and_or_dirs:
        appended_files_and_or_dirs.append(os_join(entrypoint, file))
    print(f"Compressing: {destination_file}")
    sp_run(
        sevenz_exec + [destination_file] + appended_files_and_or_dirs,
        capture_output=False,
        check=True,
    )

    if DELETE_AFTER_COMPRESS:
        for target in appended_files_and_or_dirs:
            print(f"Removing: {target}")
            my_file = Path(target)
            if my_file.is_dir():
                rmtree(target)
            if my_file.is_file():
                os_remove(target)

    calculate_and_write_checksum(destination_file)
    return


def compress_and_checksum(assets):
    for asset in assets:
        if asset.asset_type == "shared":
            EXECUTOR.submit(
                sevenz_archive,
                asset._dl_dir,
                [asset.basename],
                os_join(COMPRESSED_DIR, f"{asset.basename}.7z"),
            )

        if asset.asset_type == "roughmets_multi":
            for roughmets_dir, roughmets_files in asset._roughmets_files.items():
                EXECUTOR.submit(
                    sevenz_archive,
                    os_join(asset._dl_dir, asset.basename, roughmets_dir),
                    roughmets_files,
                    os_join(COMPRESSED_DIR, f"{roughmets_dir}.7z"),
                )

        if asset.asset_type == "livery":
            EXECUTOR.submit(
                sevenz_archive,
                asset._dl_dir,
                asset._asset_dirs,
                os_join(COMPRESSED_DIR, f"{asset.basename}.7z"),
            )

    EXECUTOR.shutdown(wait=True)


def main():
    pass


if __name__ == "__main__":
    main()
