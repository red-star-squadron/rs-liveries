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
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import google.auth
import yaml
from jinja2 import Environment, FileSystemLoader

thread_local = threading.local()
executor_files = ThreadPoolExecutor(max_workers=16)
current_dir = os.getcwd()

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
    for item in items:
        fullpath = os.path.join(des, item['name'])
        parentdir = Path(fullpath).resolve().parents[0]
        if not os.path.exists(parentdir):
            Path(parentdir).mkdir(parents=True, exist_ok=True)
            print(f"Created directory {parentdir}")
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            list_gdrive_folders(item['id'], fullpath, False)
        else:
            executor_files.submit(downloadfiles, item['id'], fullpath)


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
        Is a dict of lists. Dict is an identifier like "F-15C RoughMet"
        Each nested list is a list of strings with elements like "f15_wing_r_RoughMet_RS.dds"
    '''
    roughmet_aircrafts = dict()
    for roughmet_directory in roughmet_directories:
        roughmet_directory_basename = os.path.basename(roughmet_directory)

        if roughmet_directory_basename not in roughmet_aircrafts:
            roughmet_aircrafts[roughmet_directory_basename] = []

        roughmet_aircrafts[roughmet_directory_basename].extend(os.listdir(roughmet_directory))

    return roughmet_aircrafts


def get_service():
    '''
    Ensures we get one google service object per thread
    '''
    if not hasattr(thread_local, "service"):
        creds, _ = google.auth.default()
        thread_local.service = build('drive', 'v3', credentials=creds)
    return thread_local.service

def main():
    '''Main loop'''
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(
        current_dir,
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    with open('gdrive_secret.yml', 'r', encoding=getpreferredencoding()) as file:
        folders = yaml.safe_load(file)

    if os.environ['SKIP_DOWNLOADS'].lower() != "true":
        if os.path.isdir("Staging"):
            shutil.rmtree("Staging", ignore_errors=True)
        Path("Staging").mkdir(parents=True, exist_ok=True)
        os.chdir("Staging")
        staging_dir = os.getcwd()

        for dl_list in [
            folders["Folders_RS"],
            folders["Folders_RSC"],
            folders["Folders_Bin"],
            folders["Folders_RoughMets"]]:
            for item in dl_list:
                list_gdrive_folders(
                    item["gdrive-path"],
                    os.path.join(os.getcwd(), item["dcs-codename"]),
                    True)
        executor_files.shutdown(wait=True)

    else:
        os.chdir("Staging")
        staging_dir = os.getcwd()

    for root, dirs, files in os.walk(os.getcwd()):
        for name in files:
            if fnmatch.fnmatch(name.lower(), 'readme*.txt'):  # Remove readmes
                print(f"Removing {os.path.join(root, name)}")
                os.remove(os.path.join(root, name))
            else:
                pass

    dcs_airframe_codenames = []
    max_depth = 2
    min_depth = 1
    for root, dirs, _ in os.walk(staging_dir, topdown=True):
        if root.count(os.sep) - staging_dir.count(os.sep) < min_depth:
            continue
        if root.count(os.sep) - staging_dir.count(os.sep) == max_depth - 1:
            del dirs[:]

        if "RED STAR BIN" not in root and "RED STAR ROUGHMETS" not in root:
            dcs_airframe_codenames.append(root)

    dirs_rs_liveries = []
    dirs_rsc_liveries = []
    dirs_roughmets = []
    max_depth = 3
    min_depth = 2
    for root, dirs, _ in os.walk(staging_dir, topdown=True):
        if root.count(os.sep) - staging_dir.count(os.sep) < min_depth:
            continue
        if root.count(os.sep) - staging_dir.count(os.sep) == max_depth - 1:
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
    pilots.update(rs_pilots, rsc_pilots)

    roughmets = dir_roughmet_parser(dirs_roughmets)

    os.chdir("..")
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    pilots_list = list(pilots)
    pilots_list.sort()

    template = env.get_template('rs-liveries.nsi.j2')
    output = template.render(
        rs_liveries=rs_liveries,
        rsc_liveries=rsc_liveries,
        pilots=pilots_list,
        roughmets=roughmets)
    with open('Staging/rs-liveries-rendered.nsi',
              'w+', encoding=getpreferredencoding()) as file:
        file.write(output)

    template = env.get_template('rs-liveries-pilot-priorities.ps1.j2')
    output = template.render(rs_liveries=rs_liveries,rsc_liveries=rsc_liveries)
    with open('Staging/rs-liveries-pilot-priorities.ps1',
              'w+', encoding=getpreferredencoding()) as file:
        file.write(output)

    template = env.get_template('compress_list.sh.j2')
    output = template.render(
        rs_liveries=rs_liveries,
        rsc_liveries=rsc_liveries,
        roughmets=roughmets,
        delete_after_compress=os.environ['DELETE_AFTER_COMPRESS'].lower())
    with open('Staging/compress_list.sh',
              'w+', encoding=getpreferredencoding()) as file:
        file.write(output)

    shutil.copy("psexec.nsh", "Staging/psexec.nsh")
    shutil.copy("rs.ico", "Staging/rs.ico")
    shutil.copy("rssplash.bmp", "Staging/rssplash.bmp")
    shutil.copy("mig29flyby.wav", "Staging/mig29flyby.wav")


if __name__ == '__main__':
    main()
