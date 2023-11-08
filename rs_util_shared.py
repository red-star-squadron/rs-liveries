from os.path import dirname as os_dirname
from os.path import join as os_join
from os.path import getsize as os_getsize
from os.path import isdir as os_isdir
from os.path import islink as os_islink

from os import sep as os_sep
from os import environ
from os import walk as os_walk
from os import remove as os_remove

from inspect import getsourcefile
from shutil import rmtree
from glob import glob

import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
logger_console_handler = logging.StreamHandler()
logger_console_handler.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
logger_console_handler.setFormatter(logger_formatter)
LOGGER.addHandler(logger_console_handler)


SCRIPT_DIR = os_dirname(getsourcefile(lambda: 0))  # type: ignore
STAGING_DIR = os_join(SCRIPT_DIR, "Staging")
CHECKSUMS_DIR = os_join(STAGING_DIR, "Checksums")
COMPRESSED_DIR = os_join(SCRIPT_DIR, "Compressed")


GITHUB_REF_NAME = "no_GITHUB_REF_NAME"
if "GITHUB_REF_NAME" in environ:
    GITHUB_REF_NAME = environ["GITHUB_REF_NAME"]

if not GITHUB_REF_NAME.startswith("v"):
    GITHUB_REF_NAME = "testing"


MINIMAL_SAMPLE_SIZE = False
if "MINIMAL_SAMPLE_SIZE" in environ:
    if environ["MINIMAL_SAMPLE_SIZE"].lower() == "true":
        MINIMAL_SAMPLE_SIZE = True

DELETE_AFTER_COMPRESS = True
if "DELETE_AFTER_COMPRESS" in environ:
    if environ["DELETE_AFTER_COMPRESS"].lower() == "false":
        DELETE_AFTER_COMPRESS = False


def dir_list_one_deep(dirname):
    dirlist = []
    max_depth = 2
    min_depth = 1
    for root, dirs, _ in os_walk(dirname, topdown=True):
        if root.count(os_sep) - dirname.count(os_sep) < min_depth:
            continue
        if root.count(os_sep) - dirname.count(os_sep) == max_depth - 1:
            del dirs[:]
        dirlist.append(root)
    return dirlist


def single_dir_size(dirname):
    """
    Returns size of a single dir in bytes
    Stolen from: https://stackoverflow.com/a/1392549
    """
    total_size = 0
    for dirpath, _, filenames in os_walk(dirname):
        for fileee in filenames:
            filepath = os_join(dirpath, fileee)
            # skip if it is symbolic link
            if not os_islink(filepath):
                total_size += os_getsize(filepath)
    return total_size


def nuke_dir_contents(dirname):
    if dirname:  # Failsafe so we don't nuke the root dir
        files = glob(dirname + "/*")  # We just nuke regular files
        for f in files:
            if os_isdir(f):
                rmtree(f)
            else:
                os_remove(f)


def main():
    pass


if __name__ == "__main__":
    main()
