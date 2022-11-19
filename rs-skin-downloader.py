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
import time
import yaml

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
            print(item['name'])
            listfolders(service, item['id'], fullpath)  # LOOP un-till the files are found
        else:
            downloadfiles(service, item['id'], fullpath)
            print(item['name'])
    return folder

# To Download Files
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
                downloadfiles(service, item['id'], fullpath)
                print(fullpath) # TODO Make a normal print

def main():
    creds, _ = google.auth.default()
    service = build('drive', 'v3', credentials=creds)
    with open('gdrive_secret.yml', 'r') as file:
        Folders = yaml.safe_load(file)

    if os.path.isdir("Staging"):
        shutil.rmtree("Staging")
    if os.path.isfile("../RS-Skins.zip"):
        os.remove("../RS-Skins.zip")
    os.mkdir("Staging")
    os.chdir("Staging")

    for dl_list in [Folders["Folders_RS"], Folders["Folders_RSC"], Folders["Folders_BIN"]]:
        for item in dl_list:
            download_root_folder(item["dcs-codename"], item["gdrive-path"], service)
    
    for root, dirs, files in os.walk(os.getcwd()):
        for name in files:
            if fnmatch.fnmatch(name.lower(), 'readme*.txt'): # Don't zip readmes
                print("Removing %s" % os.path.join(root, name))
                os.remove(os.path.join(root, name))
            else:
                pass

if __name__ == '__main__':
    main()
