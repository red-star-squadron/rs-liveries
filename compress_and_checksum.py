'''
TODO compression part

This script:
1. Goes through each packaged livery .7z file
2. Runs the 7z utility to extract the archive to stdout
3. Gets the checksum of the stdout
4. Writes the checksum as <basename_of_7z>.sha256sum
'''
# pickle to import our liveries data from disk
import pickle
# subprocess to run 7z outside of python
import subprocess
# Checksum stuff
import hashlib
from locale import getpreferredencoding
# Path stuff
from os.path import join as os_join
from os.path import dirname as os_dirname
from os import environ
from pathlib import Path, PurePath
from inspect import getsourcefile
from shutil import rmtree
# concurrency stuff
from concurrent.futures import ThreadPoolExecutor
from os import sched_getaffinity
from math import ceil


if environ['MINIMAL_SAMPLE_SIZE'].lower() == "true":
    MINIMAL_SAMPLE_SIZE = True
else:
    MINIMAL_SAMPLE_SIZE = False


if environ['DELETE_AFTER_COMPRESS'].lower() == "true":
    DELETE_AFTER_COMPRESS = True
else:
    DELETE_AFTER_COMPRESS = False


SCRIPT_DIR = os_dirname(getsourcefile(lambda: 0))  # type: ignore
STAGING_DIR = os_join(SCRIPT_DIR, "Staging")
CHECKSUMS_DIR = os_join(STAGING_DIR, "Checksums")
COMPRESSED_DIR = os_join(SCRIPT_DIR, "Compressed")

# TODO CPU/4 for max_workers
available_cpus = len(sched_getaffinity(0))
EXECUTOR = ThreadPoolExecutor(max_workers=ceil(available_cpus/2))


def load_rs_var_dump():
    with open("rs_var_dump.pickle", "rb") as f:
        rs_var_dump = pickle.load(f)
    return rs_var_dump


def calculate_and_write_checksum(input_7z):
    z_subprocess = subprocess.run(["7z", "e", "-so", input_7z],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  check=True,
                                  text=False)
    chksum = hashlib.sha256(z_subprocess.stdout).hexdigest()
    dest_chksumfile = os_join(CHECKSUMS_DIR,
                              PurePath(input_7z).stem + ".sha256sum")
    print(f"Checksum: '{chksum}' -> '{dest_chksumfile}'")
    Path(Path(dest_chksumfile).resolve().parents[0]).mkdir(parents=True, exist_ok=True)
    with open(dest_chksumfile, "w", encoding=getpreferredencoding()) as file_final:
        file_final.write(chksum)
    return


def sevenz_archive(entrypoint, files_and_or_dirs, destination_file):
    if MINIMAL_SAMPLE_SIZE:
        sevenz_exec = ["7z", "a", "-bd", "-bb0", "-mx=1", "-mmt=2"]
    else:
        sevenz_exec = ["7z", "a", "-bd", "-bb0", "-mx=9", "-mmt=2"]
    appended_files_and_or_dirs = []
    for file in files_and_or_dirs:
        appended_files_and_or_dirs.append(os_join(entrypoint, file))
    print(f"Compressing: {destination_file}")
    subprocess.run(sevenz_exec + [destination_file, appended_files_and_or_dirs],
                   capture_output=False,
                   check=True)

    if DELETE_AFTER_COMPRESS:
        for target in appended_files_and_or_dirs:
            print(f"Removing: {target}")
            rmtree(target)

    calculate_and_write_checksum(destination_file)
    return


def main():
    rs_var_dump = load_rs_var_dump()
    rs_liveries = rs_var_dump.rs_liveries
    rsc_liveries = rs_var_dump.rsc_liveries
    roughmets = rs_var_dump.roughmets

    # Red Star BIN
    EXECUTOR.submit(sevenz_archive,
                    STAGING_DIR,
                    ["RED STAR BIN"],
                    os_join(COMPRESSED_DIR, "RED STAR BIN.7z"))

    # Red Star ROUGHMETS
    for roughmet in roughmets:
        EXECUTOR.submit(sevenz_archive,
                        roughmet['roughmet_directory'],
                        [file for file in roughmet['files']],
                        os_join(COMPRESSED_DIR, f'{roughmet["roughmet_directory_basename"]}.7z'))

    # Red Star Liveries (camo and black)
    for livery in [rs_liveries + rsc_liveries]:
        EXECUTOR.submit(sevenz_archive,
                        os_join(STAGING_DIR, livery["dcs_airframe_codename"]),
                        [[livery["livery_base_dirname"]] + livery["livery_pilot_dirs"]],
                        os_join(COMPRESSED_DIR, f'{livery["livery_base_dirname"]}.7z'))

    EXECUTOR.shutdown(wait=True)


if __name__ == '__main__':
    main()
