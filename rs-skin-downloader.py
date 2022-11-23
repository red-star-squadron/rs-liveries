from __future__ import print_function
import os
import shutil
import fnmatch
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload
import google.auth
import yaml
from jinja2 import Environment, FileSystemLoader
import ray

# To list folders
def listfolders(service, filid, des):
    results = service.files().list(
        pageSize=1000, q="\'" + filid + "\'" + " in parents",
        fields="nextPageToken, files(id, name, mimeType)").execute()
    folder = results.get('files', [])
    for item in folder:
        fullpath = os.path.join(des, item['name'])
        if str(item['mimeType']) == str('application/vnd.google-apps.folder'):
            if not os.path.isdir(fullpath):
                os.mkdir(path=fullpath)
            print("Creating folder %s" % fullpath)
            listfolders(service, item['id'], fullpath)  # LOOP un-till the files are found
        else:
            ray_futures.append(downloadfiles.remote(service, item['id'], fullpath))
            print("Downloaded %s" % fullpath)
    return folder

ray_futures = []
@ray.remote
def downloadfiles(service, dowid, dfilespath):
    request = service.files().get_media(fileId=dowid)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        # print("Download %d%%." % int(status.progress() * 100))
    with io.open(dfilespath, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())

def download_root_folder(rootfolder, folderid, service):
    folderid="'"+folderid+"'" # surrounding ' Needed for the "q" parameter to google drive's "list" API call
    results = service.files().list(
        pageSize=1000, q=folderid+" in parents", fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        # print('Files:')
        for item in items:
            if rootfolder and not os.path.isdir(rootfolder): # If rootfolder is defined, and if the directory does not exist
                os.mkdir(rootfolder)
            fullpath = os.path.join(os.getcwd(), rootfolder, item['name'])
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                if not os.path.isdir(fullpath):
                    os.mkdir(fullpath)
                listfolders(service, item['id'], fullpath)
            else:
                ray_futures.append(downloadfiles.remote(service, item['id'], fullpath))
                print("Downloaded %s" % fullpath)

def directory_pilot_and_livery_parser(dcs_airframe_codenames, livery_directories):
    pilots = set()        
    liveries = []
    liveries_with_pilotnames = []
    for dcs_airframe_codename in dcs_airframe_codenames:
        livery_dirs = []
        for livery in livery_directories:          
            if dcs_airframe_codename in livery:
                livery_dirs.append((livery.removeprefix(dcs_airframe_codename)))      
        if not livery_dirs: # Depending on whether looping rs/RSC liveries, we can end up with empty list, which means we need to continue with the next loop
            continue
        smallest_dirname = min(livery_dirs, key = len)
        liveries.append({
                "dcs_airframe_codename" : os.path.basename(dcs_airframe_codename),
                "dirname": os.path.basename(smallest_dirname)
            })
        for livdir in livery_dirs:
            liveries_with_pilotnames.append({
                "dcs_airframe_codename" : os.path.basename(dcs_airframe_codename),
                "dirname": os.path.basename(livdir)
            })
        if len(livery_dirs) > 1:
            livery_dirs.remove(smallest_dirname)
            for liv in livery_dirs:
                pilots.add(liv.removeprefix(smallest_dirname))
    
    return pilots, liveries, liveries_with_pilotnames



def main():
    creds, _ = google.auth.default()
    service = build('drive', 'v3', credentials=creds)
    with open('gdrive_secret.yml', 'r') as file:
        Folders = yaml.safe_load(file)

    if os.environ['SKIP_DOWNLOADS'].lower() != "true":
        if os.path.isdir("Staging"):
            shutil.rmtree("Staging")
        os.mkdir("Staging")
        os.chdir("Staging")
        staging_dir = os.getcwd()


        ray.init(num_cpus=16)
        for dl_list in [Folders["Folders_RS"], Folders["Folders_RSC"], Folders["Folders_BIN"]]:
            for item in dl_list:
                download_root_folder(item["dcs-codename"], item["gdrive-path"], service)

        # wait for downloads:
        ray.get(ray_futures)
    else:
        os.chdir("Staging")
        staging_dir = os.getcwd()

    for root, dirs, files in os.walk(os.getcwd()):
        for name in files:
            if fnmatch.fnmatch(name.lower(), 'readme*.txt'): # Don't zip readmes
                print("Removing %s" % os.path.join(root, name))
                os.remove(os.path.join(root, name))
            else:
                pass


    dcs_airframe_codenames = []
    MAX_DEPTH = 2
    MIN_DEPTH = 1
    for root, dirs, files in os.walk(staging_dir, topdown=True):
        if root.count(os.sep) - staging_dir.count(os.sep) < MIN_DEPTH:
            continue
        if root.count(os.sep) - staging_dir.count(os.sep) == MAX_DEPTH - 1:
            del dirs[:]  
     
        if "RED STAR BIN" not in root:
            dcs_airframe_codenames.append(root)


    rs_livery_directories = []
    rsc_livery_directories = []
    MAX_DEPTH = 3
    MIN_DEPTH = 2
    for root, dirs, files in os.walk(staging_dir, topdown=True):
        if root.count(os.sep) - staging_dir.count(os.sep) < MIN_DEPTH:
            continue
        if root.count(os.sep) - staging_dir.count(os.sep) == MAX_DEPTH - 1:
            del dirs[:]  
        if "BLACK SQUADRON" in root:
            rsc_livery_directories.append(root)
        else:
            rs_livery_directories.append(root)

    pilots = set()
    rs_pilots, rs_liveries, rs_liveries_with_pilotnames = directory_pilot_and_livery_parser(dcs_airframe_codenames, rs_livery_directories)
    rsc_pilots, rsc_liveries, rsc_liveries_with_pilotnames = directory_pilot_and_livery_parser(dcs_airframe_codenames, rsc_livery_directories)
    pilots.update(rs_pilots, rsc_pilots)


    os.chdir("..")
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    pilots_list = list(pilots)
    pilots_list.sort()
    # rs-skins
    template = env.get_template('rs-skins.nsi.j2')
    output = template.render(rs_liveries=rs_liveries, rsc_liveries=rsc_liveries, pilots=pilots_list, rs_liveries_with_pilotnames=rs_liveries_with_pilotnames, rsc_liveries_with_pilotnames=rsc_liveries_with_pilotnames)
    with open('Staging/rs-skins-rendered.nsi', 'w+') as f:
        f.write(output)

    shutil.copy("rs-skins-pilot-priorities.ps1", "Staging/rs-skins-pilot-priorities.ps1")

if __name__ == '__main__':
    main()
