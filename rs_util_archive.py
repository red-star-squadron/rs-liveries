"""
This script is meant to be used as an import.

It's job is to compress the individual liveries and then
create checksums of individual livery archives.

We use ThreadPoolExecutor from the concurrent.features module
so we can utilize maximum resources of any given system this runs on.
"""

# Our includes
from rs_util_shared import MINIMAL_SAMPLE_SIZE
from rs_util_shared import DELETE_AFTER_COMPRESS
from rs_util_shared import LOGGER

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
from concurrent.futures import Future
from os import sched_getaffinity

# typing
from typing import List

# Set up our threadpool executor so it has NUM_CPUS threads
available_cpus = len(sched_getaffinity(0))
EXECUTOR = ThreadPoolExecutor(max_workers=available_cpus)


def calculate_and_write_checksum(destination_dir: str, input_7z_file: str) -> None:
    z_subprocess = sp_run(
        ["7z", "e", "-so", "-mmt=4", input_7z_file],
        stdout=sp_pipe,
        stderr=sp_pipe,
        check=True,
        text=False,
    )
    chksum = sha256(z_subprocess.stdout).hexdigest()
    dest_chksumfile = os_join(
        destination_dir, PurePath(input_7z_file).stem + ".sha256sum"
    )
    LOGGER(f"Checksum: '{chksum}' -> '{dest_chksumfile}'")
    Path(Path(dest_chksumfile).resolve().parents[0]).mkdir(parents=True, exist_ok=True)
    with open(dest_chksumfile, "w", encoding=getpreferredencoding()) as file_final:
        file_final.write(chksum)
    return


def sevenz_and_checksum_archive(
    entrypoint: str,
    checksum_dir: str,
    files_and_or_dirs: List[str],
    destination_file: str,
) -> None:
    if MINIMAL_SAMPLE_SIZE:
        sevenz_exec = ["7z", "a", "-bd", "-bb0", "-mx=1", "-mmt=4"]
    else:
        sevenz_exec = ["7z", "a", "-bd", "-bb0", "-mx=9", "-mmt=4"]
    appended_files_and_or_dirs = []
    for file in files_and_or_dirs:
        appended_files_and_or_dirs.append(os_join(entrypoint, file))
    LOGGER(f"Compressing: {destination_file}")
    sp_run(
        sevenz_exec + [destination_file] + appended_files_and_or_dirs,
        capture_output=False,
        check=True,
    )

    if DELETE_AFTER_COMPRESS:
        for target in appended_files_and_or_dirs:
            LOGGER(f"Removing: {target}")
            my_file = Path(target)
            if my_file.is_dir():
                rmtree(target)
            if my_file.is_file():
                os_remove(target)

    calculate_and_write_checksum(checksum_dir, destination_file)
    return


def compress_and_checksum(
    destination_dir: str, checksum_dir: str, files_or_dirs: list[str], archive: str
) -> Future:
    return EXECUTOR.submit(
        sevenz_and_checksum_archive,
        destination_dir,
        checksum_dir,
        files_or_dirs,
        archive,
    )


def main():
    pass


if __name__ == "__main__":
    main()
