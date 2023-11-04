"""
This is where we keep all our google related functions
"""
from threading import local as threading_local
from io import BytesIO as io_BytesIO
from io import open as io_open
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build as google_build
from google.auth import default as google_default
from os.path import join as os_join
from os.path import exists as os_pexists
from os import environ
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


# Our includes
from rs_util_shared import MINIMAL_SAMPLE_SIZE
from rs_util_shared import SCRIPT_DIR

THREAD_LOCAL = threading_local()
EXECUTOR_FILES = ThreadPoolExecutor(max_workers=16)

environ["GOOGLE_APPLICATION_CREDENTIALS"] = os_join(
    SCRIPT_DIR, environ["GOOGLE_APPLICATION_CREDENTIALS"]
)


def get_service():
    """
    Ensures we get one google service object per thread
    """
    if not hasattr(THREAD_LOCAL, "service"):
        creds, _ = google_default()
        THREAD_LOCAL.service = google_build("drive", "v3", credentials=creds)
    return THREAD_LOCAL.service


def download_gdrive_folder(filid, des, is_rootfolder):
    """
    Lists folders within a google drive
    Downloads files
    Recurses itself to go down the directory structure
    """
    if is_rootfolder:
        query = "'" + filid + "'" + " in parents"
    else:
        query = "'" + filid + "'" + " in parents"
    service = get_service()
    results = (
        service.files()
        .list(pageSize=1000, q=query, fields="nextPageToken, files(id, name, mimeType)")
        .execute()
    )
    items = results.get("files", [])
    if len(items) == 0 and is_rootfolder:
        raise ValueError(f"Google Drive folder empty or other issue: {filid}")
    iter_file_count = 0
    for item in items:
        fullpath = os_join(des, item["name"])
        parentdir = Path(fullpath).resolve().parents[0]
        if not os_pexists(parentdir):
            Path(parentdir).mkdir(parents=True, exist_ok=True)
            print(f"Created directory {parentdir}")
        if item["mimeType"] == "application/vnd.google-apps.folder":
            download_gdrive_folder(item["id"], fullpath, False)
        else:
            if MINIMAL_SAMPLE_SIZE:
                if fullpath.lower().endswith("lua") or fullpath.lower().endswith("txt"):
                    EXECUTOR_FILES.submit(downloadfiles, item["id"], fullpath)
                else:
                    if iter_file_count > 0:
                        continue
                    EXECUTOR_FILES.submit(downloadfiles, item["id"], fullpath)
                    iter_file_count += 1
            else:
                EXECUTOR_FILES.submit(downloadfiles, item["id"], fullpath)


def downloadfiles(dowid, dfilespath):
    """
    Downloads a single google drive file
    """
    service = get_service()
    request = service.files().get_media(fileId=dowid)
    file_handler = io_BytesIO()
    downloader = MediaIoBaseDownload(file_handler, request)
    done = False
    while done is False:
        _, done = downloader.next_chunk()
        # NOTE: replace above _ with status
        # print("Download %d%%." % int(status.progress() * 100))
    with io_open(dfilespath, "wb") as file:
        file_handler.seek(0)
        file.write(file_handler.read())
    print(f"Downloaded: {dfilespath}")


def main():
    pass


if __name__ == "__main__":
    main()
