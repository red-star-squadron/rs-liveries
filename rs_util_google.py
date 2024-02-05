"""
This is where we keep all our google related functions
"""

# Our includes
from rs_util_shared import MINIMAL_SAMPLE_SIZE
from rs_util_shared import SCRIPT_DIR
from rs_util_shared import LOGGER

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

# I have no idea why i'd ever override this. Oh well.
if "GOOGLE_APPLICATION_CREDENTIALS" not in environ:
    environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
environ["GOOGLE_APPLICATION_CREDENTIALS"] = os_join(
    SCRIPT_DIR, environ["GOOGLE_APPLICATION_CREDENTIALS"]
)


THREAD_LOCAL = threading_local()

THREADPOOL = ThreadPoolExecutor(max_workers=16)
THREADPOOL_FAKE_DL = ThreadPoolExecutor(max_workers=64)


class BaseNameError(Exception):
    ...


class SubStringError(Exception):
    ...


def get_service():
    """
    Ensures we get one google service object per thread
    """
    if not hasattr(THREAD_LOCAL, "service"):
        creds, _ = google_default()
        THREAD_LOCAL.service = google_build(
            "drive", "v3", credentials=creds, cache_discovery=False
        )
    return THREAD_LOCAL.service


def download_gdrive_folder(
    gdrive_id,
    des,
    is_rootfolder,
    verify_basename=None,
    must_contain_strings=None,
    must_not_contain_strings=None,
):
    """
    Lists folders within a google drive
    Downloads files
    Recurses itself to go down the directory structure
    """
    if is_rootfolder:
        query = "'" + gdrive_id + "'" + " in parents"
    else:
        query = "'" + gdrive_id + "'" + " in parents"
    service = get_service()
    results = (
        service.files()
        .list(pageSize=1000, q=query, fields="nextPageToken, files(id, name, mimeType)")
        .execute()
    )
    items = results.get("files", [])
    if len(items) == 0 and is_rootfolder:
        raise ValueError(f"Google Drive folder empty or other issue: {gdrive_id}")
    dl_futures = []
    # Check if our prefix matches any of the top-level dirs/files
    # This needs some work in case our directory structure grows deeper than 1-deep
    items_to_check = [
        i["name"].upper()
        for i in items
        if i["mimeType"] == "application/vnd.google-apps.folder"
    ]
    if verify_basename:
        for item_to_check in items_to_check:
            if verify_basename.upper() not in item_to_check:
                raise BaseNameError(
                    f"Prefix {verify_basename.upper()} not found in {item_to_check} "
                )

    if must_contain_strings:
        for must_contain_string in must_contain_strings:
            for folder in items_to_check:
                if must_contain_string.upper() not in folder:
                    raise SubStringError(
                        f"Text {must_contain_string.upper()} not found in: "
                        + str(folder)
                    )
    if must_not_contain_strings:
        for must_not_contain_string in must_not_contain_strings:
            for folder in items_to_check:
                if must_not_contain_string.upper() in folder:
                    raise SubStringError(
                        f"Text {must_not_contain_string.upper()} must NOT be in: "
                        + str(folder)
                    )

    for item in items:
        fullpath = os_join(des, item["name"])
        parentdir = Path(fullpath).resolve().parents[0]
        if not os_pexists(parentdir):
            Path(parentdir).mkdir(parents=True, exist_ok=True)
            LOGGER.info(f"Created directory {parentdir}")
        # Download in background if dir
        if item["mimeType"] == "application/vnd.google-apps.folder":
            dl_futures += download_gdrive_folder(item["id"], fullpath, False)
        # Download in background if file
        elif not MINIMAL_SAMPLE_SIZE or fullpath.lower().endswith(
            "lua"
        ):  # Fake file download
            dl_futures.append(
                THREADPOOL.submit(download_gdrive_file, item["id"], fullpath)
            )
        else:  # Actual file download
            dl_futures.append(
                THREADPOOL_FAKE_DL.submit(fake_download_gdrive_file, fullpath)
            )
    return dl_futures


def fake_download_gdrive_file(dfilespath):
    Path(dfilespath).touch()
    LOGGER.warn(f"FAKE Downloaded: {dfilespath}")
    return dfilespath


def download_gdrive_file(dowid, dfilespath):
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
        # logger.info("Download %d%%." % int(status.progress() * 100))
    with io_open(dfilespath, "wb") as file:
        file_handler.seek(0)
        file.write(file_handler.read())
    LOGGER.info(f"Downloaded: {dfilespath}")
    return dfilespath


def main():
    pass


if __name__ == "__main__":
    main()
