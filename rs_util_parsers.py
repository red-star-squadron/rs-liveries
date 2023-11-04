from os.path import join as os_join
from os.path import basename as os_basename
from os.path import islink as os_islink
from os.path import getsize as os_getsize
from os import sep as os_sep
from os import listdir as os_listdir
from os import walk as os_walk

# Our includes
from rs_util_shared import STAGING_DIR


def livery_sizes(liveries_list):
    """
    Input should be a "liveries" list as returned by dir_pilot_and_livery_parser()
    Appends each dict elemet in the input list with
    a ['total_size'] key and value in kilobytes
    """
    for livery in liveries_list:
        basedir = os_join(STAGING_DIR, livery["dcs_airframe_codename"])
        total_size = 0
        dir_basename = os_join(basedir, livery["livery_base_dirname"])
        total_size += single_dir_size(dir_basename)
        for pilot_livery in livery["livery_pilot_dirs"]:
            dir_pilot = os_join(basedir, pilot_livery)
            total_size += single_dir_size(dir_pilot)
        livery["total_size"] = int(total_size / 1024)  # kilobytes


def single_dir_size(start_path):
    """
    Returns size of a single dir in bytes
    Stolen from: https://stackoverflow.com/a/1392549
    """
    total_size = 0
    for dirpath, _, filenames in os_walk(start_path):
        for fileee in filenames:
            filepath = os_join(dirpath, fileee)
            # skip if it is symbolic link
            if not os_islink(filepath):
                total_size += os_getsize(filepath)
    return total_size


def dir_pilot_and_livery_parser(dcs_airframe_codenames, livery_directories):
    """
    Inputs:
    * dcs_airframe_codenames - list of strings where each is
        like "mig-29s" (what DCS recognizes)
    * livery_directories - list of strings where each string
        is a directory path
    Outputs:
    * pilots
        Is a set of strings
        Each string corresponds to a pilot, like "SQuID"
    * liveries
        Is a list of dictionaries. Each dict structure:
            * dcs_airframe_codename - string like mig-29s
            * livery_base_dirname - string like "RED STAR FA-18C BLACK SQUADRON"
            * livery_pilot_dirs - list of strings like "RED STAR FA-18C BLACK SQUADRON SQuID"
    """
    pilots = set()
    liveries = []
    for dcs_airframe_codename in dcs_airframe_codenames:
        livery_dirs = []
        for livery in livery_directories:
            if f"{ dcs_airframe_codename }/" in livery:
                livery_dirs.append(livery.removeprefix(dcs_airframe_codename))
        # Depending on whether looping regular (RS) or competitive (RSC) liveries,
        # we can end up with empty list, which means we need to continue with the next loop
        if not livery_dirs:
            continue
        smallest_dirname = min(livery_dirs, key=len)
        pilot_dirs = livery_dirs.copy()
        pilot_dirs.remove(smallest_dirname)
        liveries.append(
            {
                "dcs_airframe_codename": os_basename(dcs_airframe_codename),
                "livery_base_dirname": os_basename(smallest_dirname),
                "livery_base_fulldir": os_join(
                    STAGING_DIR,
                    dcs_airframe_codename,
                    os_basename(smallest_dirname),
                ),
                "livery_pilot_dirs": [
                    os_basename(pilot_dir) for pilot_dir in pilot_dirs
                ],
            }
        )
        if len(livery_dirs) > 1:
            livery_dirs.remove(smallest_dirname)
            for liv in livery_dirs:
                pilots.add(liv.removeprefix(smallest_dirname).strip())
    return pilots, liveries


def dir_roughmet_parser(roughmet_directories):
    """
    Inputs:
    * livery_directories - list of strings where each string
        is a directory path
    Outputs:
    * roughmet_aircrafts
        Is a list of dicts. Each dict:
        roughmet_directory - Staging dir of roughmets for a single aircraft
        roughmet_directory_basename - basename of the above, example F-15C Roughmet
        files - List of files contained in roughmet_directory
        size - size in kilobytes of roughmet_directory
    """
    roughmet_aircrafts = []
    for roughmet_directory in roughmet_directories:
        roughmet_directory_basename = os_basename(roughmet_directory)
        roughmet_aircrafts.append(
            {
                "roughmet_directory": roughmet_directory,
                "roughmet_directory_basename": roughmet_directory_basename,
                "files": os_listdir(roughmet_directory),
                "size": int(single_dir_size(roughmet_directory) / 1024),  # kilobytes
            }
        )

    return roughmet_aircrafts


def get_dcs_airframe_codenames():
    dcs_airframe_codenames = []
    max_depth = 2
    min_depth = 1
    for root, dirs, _ in os_walk(STAGING_DIR, topdown=True):
        if root.count(os_sep) - STAGING_DIR.count(os_sep) < min_depth:
            continue
        if root.count(os_sep) - STAGING_DIR.count(os_sep) == max_depth - 1:
            del dirs[:]

        if "RED STAR BIN" not in root and "RED STAR ROUGHMETS" not in root:
            dcs_airframe_codenames.append(root)
    return dcs_airframe_codenames


def rs_enum_dirs():
    dirs_rs_liveries = []
    dirs_rsc_liveries = []
    dirs_roughmets = []
    max_depth = 3
    min_depth = 2
    for root, dirs, _ in os_walk(STAGING_DIR, topdown=True):
        if root.count(os_sep) - STAGING_DIR.count(os_sep) < min_depth:
            continue
        if root.count(os_sep) - STAGING_DIR.count(os_sep) == max_depth - 1:
            del dirs[:]
        if "BLACK SQUADRON" in root:
            dirs_rsc_liveries.append(root)
        elif "RED STAR ROUGHMETS" in root:
            dirs_roughmets.append(root)
        elif "RED STAR BIN" not in root:
            dirs_rs_liveries.append(root)
        else:
            pass  # Red Star Bin
    return dirs_rs_liveries, dirs_rsc_liveries, dirs_roughmets


def main():
    pass


if __name__ == "__main__":
    main()
