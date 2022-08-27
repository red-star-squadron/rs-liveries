from __future__ import print_function
from genericpath import isfile
import os
import shutil
import fnmatch
import zipfile
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import io
from googleapiclient import errors
from googleapiclient import http
import logging
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient import discovery
import google.auth
import ray
import time
import json

# To list folders
def listfolders(service, filid, des):
    results = service.files().list(
        pageSize=1000, q="\'" + filid + "\'" + " in parents",
        fields="nextPageToken, files(id, name, mimeType)").execute()
    folder = results.get('files', [])
    for item in folder:
        if str(item['mimeType']) == str('application/vnd.google-apps.folder'):
            if not os.path.isdir(des+"/"+item['name']):
                os.mkdir(path=des+"/"+item['name'])
            print(item['name'])
            listfolders(service, item['id'], des+"/"+item['name'])  # LOOP un-till the files are found
        else:
            downloadfiles(service, item['id'], item['name'], des)
            print(item['name'])
    return folder


# To Download Files
def downloadfiles(service, dowid, name,dfilespath):
    request = service.files().get_media(fileId=dowid)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        # print("Download %d%%." % int(status.progress() * 100))
    with io.open(dfilespath + "/" + name, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())

@ray.remote
def downloadfolder(rootfolder, folderid, service):
    folderid="'"+folderid+"'" # surrounding ' Needed for the "q" parameter to google drive's "list" API call
    results = service.files().list(
        pageSize=1000, q=folderid+" in parents", fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        # print('Files:')
        for item in items:
            if not os.path.isdir(rootfolder):
                os.mkdir(rootfolder)
            bfolderpath = os.getcwd()+"/%s/" % rootfolder
            if not os.path.isdir(bfolderpath + item['name']):
                os.mkdir(bfolderpath + item['name'])
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                folderpath = bfolderpath + item['name']
                listfolders(service, item['id'], folderpath)
            else:
                filepath = bfolderpath + item['name']
                downloadfiles(service, item['id'], item['name'], filepath)

def main():
    creds, _ = google.auth.default()
    service = build('drive', 'v3', credentials=creds)

    if os.path.isdir("Staging"):
        shutil.rmtree("Staging")
    if os.path.isfile("../RS-Skins.zip"):
        os.remove("../RS-Skins.zip")
    os.mkdir("Staging")
    os.chdir("Staging")

    ##
    ##       !!!!! If updating these values with new skins, please ensure to update the .nsi script !!!!!!!
    ##
    ## Format of the ingested env vars looks like this:
    # {
    #     "mig-29s"       : "GOOGLE-DRIVE-SHARED-FOLDER-ID",
    #     "mig-29a"       : "GOOGLE-DRIVE-SHARED-FOLDER-ID",
    #     "mig-29g"       : "GOOGLE-DRIVE-SHARED-FOLDER-ID",
    #     "jf-17"         : "GOOGLE-DRIVE-SHARED-FOLDER-ID",
    #     "j-11a"         : "GOOGLE-DRIVE-SHARED-FOLDER-ID",
    #     "su-27"         : "GOOGLE-DRIVE-SHARED-FOLDER-ID",
    #     "f-16c_50"      : "GOOGLE-DRIVE-SHARED-FOLDER-ID",
    #     "fa-18c_hornet" : "GOOGLE-DRIVE-SHARED-FOLDER-ID",
    #     "f-15c"         : "GOOGLE-DRIVE-SHARED-FOLDER-ID"
    # }
    ##
    Folders_RS = json.loads(os.environ['GOOGLE_DRIVE_RS_SKINS'])
    Folders_RSC = json.loads(os.environ['GOOGLE_DRIVE_RSC_SKINS'])
    # Future skin categories if added here must be added a few lines below (dl_list loop)

    ray.init()
    ray_obj_refs = []
    for dl_list in [Folders_RS, Folders_RSC]:
        for rootfolder, Folder_id in dl_list.items():
           ray_obj_refs.append(downloadfolder.remote(rootfolder, Folder_id, service))
    print("Started waiting for parallel downloads...")
    ray.wait(ray_obj_refs, num_returns=len(ray_obj_refs))
    print("Finished waiting for parallel downloads.")

    # print("Zipping now...")
    # zipped = zipfile.ZipFile('../RS-Skins.zip', 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(os.getcwd()):
        for name in files:
            if fnmatch.fnmatch(name.lower(), 'readme*.txt'): # Don't zip readmes
                print("Removing %s" % os.path.join(root, name))
                os.remove(os.path.join(root, name))
            else:
                # zipped.write(os.path.join(root, name), arcname=os.path.relpath(os.path.join(root, name), os.getcwd())) # Add to zip
                # os.remove(os.path.join(root, name)) # Remove after zipping
                pass

if __name__ == '__main__':
    main()
