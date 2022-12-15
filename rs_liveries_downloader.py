'''
RS Liveries Downloader
'''


from __future__ import print_function
import os
import shutil
import fnmatch
import io
from concurrent.futures import ThreadPoolExecutor
import threading
from locale import getpreferredencoding
from pathlib import Path
from inspect import getsourcefile
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import google.auth
import yaml
from jinja2 import Environment, FileSystemLoader


THREAD_LOCAL = threading.local()
EXECUTOR_FILES = ThreadPoolExecutor(max_workers=16)
SCRIPT_DIR = os.path.dirname(getsourcefile(lambda:0)) # type: ignore
STAGING_DIR = os.path.join(SCRIPT_DIR, "Staging")
if 'GITHUB_REF_NAME' in os.environ:
    GH_REF = os.environ['GITHUB_REF_NAME']
    GH_RUNNER = True
else:
    GH_REF = "no_GH_REF"
    GH_RUNNER = False

if os.environ['MINIMAL_SAMPLE_SIZE'].lower() == "true":
    MINIMAL_SAMPLE_SIZE = True
else:
    MINIMAL_SAMPLE_SIZE = False


def list_gdrive_folders(filid, des, is_rootfolder):
    '''
    Lists folders within a google drive
    Downloads files
    Recurses itself to go down the directory structure
    '''
    if is_rootfolder:
        query="'" + filid + "'" + " in parents"
    else:
        query="\'" + filid + "\'" + " in parents"
    service = get_service()
    results = service.files().list(
        pageSize=1000,
        q=query,
        fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    if len(items) == 0 and is_rootfolder:
        raise ValueError(f"Google Drive folder empty or other issue: {filid}")
    iter_file_count = 0
    for item in items:
        fullpath = os.path.join(des, item['name'])
        parentdir = Path(fullpath).resolve().parents[0]
        if not os.path.exists(parentdir):
            Path(parentdir).mkdir(parents=True, exist_ok=True)
            print(f"Created directory {parentdir}")
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            list_gdrive_folders(item['id'], fullpath, False)
        else:
            if MINIMAL_SAMPLE_SIZE:
                if fullpath.lower().endswith("lua") \
                        or fullpath.lower().endswith("txt"):
                    EXECUTOR_FILES.submit(downloadfiles, item['id'], fullpath)
                else:
                    if iter_file_count > 0:
                        continue
                    EXECUTOR_FILES.submit(downloadfiles, item['id'], fullpath)
                    iter_file_count += 1
            else:
                EXECUTOR_FILES.submit(downloadfiles, item['id'], fullpath)


def downloadfiles(dowid, dfilespath):
    '''
    Downloads a single google drive file
    '''
    service = get_service()
    request = service.files().get_media(fileId=dowid)
    file_handler = io.BytesIO()
    downloader = MediaIoBaseDownload(file_handler, request)
    done = False
    while done is False:
        _, done = downloader.next_chunk()
        # NOTE: replace above _ with status
        # print("Download %d%%." % int(status.progress() * 100))
    with io.open(dfilespath, 'wb') as file:
        file_handler.seek(0)
        file.write(file_handler.read())
    print(f"Downloaded: {dfilespath}")


def dir_pilot_and_livery_parser(dcs_airframe_codenames, livery_directories):
    '''
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
    '''
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
        liveries.append({
                "dcs_airframe_codename": os.path.basename(dcs_airframe_codename),
                "livery_base_dirname": os.path.basename(smallest_dirname),
                "livery_base_fulldir": os.path.join(STAGING_DIR, dcs_airframe_codename,
                                                     os.path.basename(smallest_dirname)),
                "livery_pilot_dirs": [os.path.basename(pilot_dir) for pilot_dir in pilot_dirs]
            })
        if len(livery_dirs) > 1:
            livery_dirs.remove(smallest_dirname)
            for liv in livery_dirs:
                pilots.add(liv.removeprefix(smallest_dirname).strip())
    return pilots, liveries


def dir_roughmet_parser(roughmet_directories):
    '''
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
    '''
    roughmet_aircrafts = []
    for roughmet_directory in roughmet_directories:
        roughmet_directory_basename = os.path.basename(roughmet_directory)
        roughmet_aircrafts.append({
            'roughmet_directory' : roughmet_directory,
            'roughmet_directory_basename' : roughmet_directory_basename,
            'files' : os.listdir(roughmet_directory),
            'size' : int(single_dir_size(roughmet_directory) / 1024) # kilobytes
        })

    return roughmet_aircrafts


def livery_sizes(liveries_list):
    '''
    Input should be a "liveries" list as returned by dir_pilot_and_livery_parser()
    Appends each dict elemet in the input list with
    a ['total_size'] key and value in kilobytes
    '''
    for livery in liveries_list:
        basedir = os.path.join(STAGING_DIR, livery['dcs_airframe_codename'])
        total_size = 0
        dir_basename = os.path.join(basedir, livery['livery_base_dirname'])
        total_size += single_dir_size(dir_basename)
        for pilot_livery in livery['livery_pilot_dirs']:
            dir_pilot = os.path.join(basedir, pilot_livery)
            total_size += single_dir_size(dir_pilot)
        livery['total_size'] = int(total_size / 1024) # kilobytes


def single_dir_size(start_path):
    '''
    Returns size of a single dir in bytes
    Stolen from: https://stackoverflow.com/a/1392549
    '''
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        for fileee in filenames:
            filepath = os.path.join(dirpath, fileee)
            # skip if it is symbolic link
            if not os.path.islink(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def get_service():
    '''
    Ensures we get one google service object per thread
    '''
    if not hasattr(THREAD_LOCAL, "service"):
        creds, _ = google.auth.default()
        THREAD_LOCAL.service = build('drive', 'v3', credentials=creds)
    return THREAD_LOCAL.service


def main():
    '''Main loop'''
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(
        SCRIPT_DIR,
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    with open('gdrive_secret.yml', 'r', encoding=getpreferredencoding()) as file:
        folders = yaml.safe_load(file)

    if os.environ['SKIP_DOWNLOADS'].lower() != "true":
        if os.path.isdir(STAGING_DIR):
            shutil.rmtree(STAGING_DIR, ignore_errors=True)
        Path(STAGING_DIR).mkdir(parents=True, exist_ok=True)
        os.chdir(STAGING_DIR)

        if MINIMAL_SAMPLE_SIZE:
            folders["Folders_RS"] = [folders["Folders_RS"][0]]
            folders["Folders_RSC"] = [folders["Folders_RSC"][0]]

        for dl_list in [
            folders["Folders_RS"],
            folders["Folders_RSC"],
            folders["Folders_Bin"],
            folders["Folders_RoughMets"]]:
            for item in dl_list:
                list_gdrive_folders(
                    item["gdrive-path"],
                    os.path.join(STAGING_DIR, item["dcs-codename"]),
                    True)
        EXECUTOR_FILES.shutdown(wait=True)
    else:
        os.chdir(STAGING_DIR)

    for root, dirs, files in os.walk(STAGING_DIR):
        for name in files:
            if fnmatch.fnmatch(name.lower(), 'readme*.txt'):  # Remove readmes
                print(f"Removing {os.path.join(root, name)}")
                os.remove(os.path.join(root, name))
            else:
                pass

    dcs_airframe_codenames = []
    max_depth = 2
    min_depth = 1
    for root, dirs, _ in os.walk(STAGING_DIR, topdown=True):
        if root.count(os.sep) - STAGING_DIR.count(os.sep) < min_depth:
            continue
        if root.count(os.sep) - STAGING_DIR.count(os.sep) == max_depth - 1:
            del dirs[:]

        if "RED STAR BIN" not in root and "RED STAR ROUGHMETS" not in root:
            dcs_airframe_codenames.append(root)

    dirs_rs_liveries = []
    dirs_rsc_liveries = []
    dirs_roughmets = []
    max_depth = 3
    min_depth = 2
    for root, dirs, _ in os.walk(STAGING_DIR, topdown=True):
        if root.count(os.sep) - STAGING_DIR.count(os.sep) < min_depth:
            continue
        if root.count(os.sep) - STAGING_DIR.count(os.sep) == max_depth - 1:
            del dirs[:]
        if "BLACK SQUADRON" in root:
            dirs_rsc_liveries.append(root)
        elif "RED STAR ROUGHMETS" in root:
            dirs_roughmets.append(root)
        elif "RED STAR BIN" not in root:
            dirs_rs_liveries.append(root)
        else:
            pass # Red Star Bin

    pilots = set()
    rs_pilots, rs_liveries = dir_pilot_and_livery_parser(dcs_airframe_codenames,
                                                         dirs_rs_liveries)
    rsc_pilots, rsc_liveries = dir_pilot_and_livery_parser(dcs_airframe_codenames,
                                                           dirs_rsc_liveries)

    livery_sizes(rs_liveries)
    livery_sizes(rsc_liveries)
    size_bin_kb = int(single_dir_size(os.path.join(STAGING_DIR, "RED STAR BIN")) / 1024 )
    pilots.update(rs_pilots, rsc_pilots)
    pilots_list = list(pilots)
    pilots_list.sort()

    roughmets = dir_roughmet_parser(dirs_roughmets)

    os.chdir("..")
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    template = env.get_template('compress_list.sh.j2')
    output = template.render(
        rs_liveries=rs_liveries,
        rsc_liveries=rsc_liveries,
        roughmets=roughmets,
        delete_after_compress=os.environ['DELETE_AFTER_COMPRESS'].lower(),
        minimal_sample_size=str(MINIMAL_SAMPLE_SIZE).lower(),
        dest=os.path.join(SCRIPT_DIR, "Compressed"),
        staging_dir=STAGING_DIR)
    with open('Staging/compress_list.sh',
              'w+', encoding=getpreferredencoding()) as file:
        file.write(output)

    template = env.get_template('rs-liveries.nsi.j2')
    output = template.render(
        rs_liveries=rs_liveries,
        rsc_liveries=rsc_liveries,
        pilots=pilots_list,
        roughmets=roughmets,
        gh_ref=GH_REF,
        size_bin_kb=size_bin_kb)
    with open('Staging/rs-liveries-rendered.nsi',
              'w+', encoding=getpreferredencoding()) as file:
        file.write(output)

    template = env.get_template('livery-priorities.ps1.j2')
    output = template.render(rs_liveries=rs_liveries,rsc_liveries=rsc_liveries)
    with open('Staging/livery-priorities.ps1',
              'w+', encoding=getpreferredencoding()) as file:
        file.write(output)

    shutil.copy("psexec.nsh", os.path.join(STAGING_DIR, "psexec.nsh"))
    shutil.copy("rs.ico", os.path.join(STAGING_DIR, "rs.ico"))
    shutil.copy("rssplash.bmp", os.path.join(STAGING_DIR, "rssplash.bmp"))
    shutil.copy("mig29flyby.wav", os.path.join(STAGING_DIR, "mig29flyby.wav"))
    shutil.copy("extract-file.ps1", os.path.join(STAGING_DIR, "extract-file.ps1"))


if __name__ == '__main__':
    main()
