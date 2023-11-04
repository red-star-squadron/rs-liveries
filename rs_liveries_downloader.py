"""
RS Liveries Downloader
"""

from os.path import join as os_join
from os.path import isdir as os_isdir
from os import walk as os_walk
from os import chdir as os_chdir
from os import remove as os_remove
from os import sep as os_sep
from os import environ
import shutil
import fnmatch
from locale import getpreferredencoding
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader
import pickle

# Our includes
from rs_shared import STAGING_DIR
from rs_shared import GITHUB_REF_NAME
from rs_util_google import EXECUTOR_FILES
from rs_util_google import download_gdrive_folder
from rs_util_parsers import single_dir_size
from rs_util_parsers import dir_pilot_and_livery_parser
from rs_util_parsers import dir_roughmet_parser
from rs_util_parsers import livery_sizes


def main():
    """Main loop"""
    with open("gdrive_secret.yml", "r", encoding=getpreferredencoding()) as file:
        folders = yaml.safe_load(file)
    if environ["SKIP_DOWNLOADS"].lower() != "true":
        if os_isdir(STAGING_DIR):
            shutil.rmtree(STAGING_DIR, ignore_errors=True)
        Path(STAGING_DIR).mkdir(parents=True, exist_ok=True)
        os_chdir(STAGING_DIR)

        for dl_list in [
            folders["Folders_RS"],
            folders["Folders_RSC"],
            folders["Folders_Bin"],
            folders["Folders_RoughMets"],
        ]:
            for item in dl_list:
                download_gdrive_folder(
                    item["gdrive-path"],
                    os_join(STAGING_DIR, item["dcs-codename"]),
                    True,
                )
        EXECUTOR_FILES.shutdown(wait=True)
    else:
        os_chdir(STAGING_DIR)

    for root, dirs, files in os_walk(STAGING_DIR):
        for name in files:
            if fnmatch.fnmatch(name.lower(), "readme*.txt"):  # Remove readmes
                print(f"Removing {os_join(root, name)}")
                os_remove(os_join(root, name))
            else:
                pass

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
    dirs_rs_liveries.sort()
    dirs_rsc_liveries.sort()

    pilots = set()
    rs_pilots, rs_liveries = dir_pilot_and_livery_parser(
        dcs_airframe_codenames, dirs_rs_liveries
    )
    rsc_pilots, rsc_liveries = dir_pilot_and_livery_parser(
        dcs_airframe_codenames, dirs_rsc_liveries
    )

    livery_sizes(rs_liveries)
    livery_sizes(rsc_liveries)
    size_bin_kb = int(single_dir_size(os_join(STAGING_DIR, "RED STAR BIN")) / 1024)
    pilots.update(rs_pilots, rsc_pilots)
    pilots_list = list(pilots)
    pilots_list.sort()

    roughmets = dir_roughmet_parser(dirs_roughmets)

    os_chdir("..")
    file_loader = FileSystemLoader("templates")
    env = Environment(loader=file_loader)

    rs_var_dump = dict()
    rs_var_dump["rs_liveries"] = rs_liveries
    rs_var_dump["rsc_liveries"] = rsc_liveries
    rs_var_dump["roughmets"] = roughmets

    with open("rs_var_dump.pickle", "wb") as f:
        f.write(pickle.dumps(rs_var_dump))

    template = env.get_template("rs-liveries.nsi.j2")
    output = template.render(
        rs_liveries=rs_liveries,
        rsc_liveries=rsc_liveries,
        pilots=pilots_list,
        roughmets=roughmets,
        github_ref_name=GITHUB_REF_NAME,
        size_bin_kb=size_bin_kb,
    )
    with open(
        "Staging/rs-liveries-rendered.nsi", "w+", encoding=getpreferredencoding()
    ) as file:
        file.write(output)

    template = env.get_template("livery-priorities.ps1.j2")
    output = template.render(liveries=rs_liveries + rsc_liveries)
    with open(
        "Staging/livery-priorities.ps1", "w+", encoding=getpreferredencoding()
    ) as file:
        file.write(output)

    shutil.copy("psexec.nsh", os_join(STAGING_DIR, "psexec.nsh"))
    shutil.copy("rs.ico", os_join(STAGING_DIR, "rs.ico"))
    shutil.copy("rssplash.bmp", os_join(STAGING_DIR, "rssplash.bmp"))
    shutil.copy("mig29flyby.wav", os_join(STAGING_DIR, "mig29flyby.wav"))
    shutil.copy("extract-file.ps1", os_join(STAGING_DIR, "extract-file.ps1"))


if __name__ == "__main__":
    main()
