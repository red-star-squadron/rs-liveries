## Google credentials

Assumes you have the credentials.json. I think I used  google's IAM console to create a user with no permissions which can be assumed to use anonymous-access google drives.

```shell
export GOOGLE_APPLICATION_CREDENTIALS=credentials.json
```

## Skipping downloads

During testing, it is good to skip download is they have already been performed once and known good.
To do this, use the following environment variable:

```shell
export SKIP_DOWNLOADS=true
```

## Google Drive secrets

The program expects to see a yaml file in gdrive_secret.yml

Format is as follows:

```yml
Folders_RS:
  - dcs-codename: mig-29a
    gdrive-path: <gdrive-shared-folder-ID>
  - dcs-codename: mig-29g
    gdrive-path: <gdrive-shared-folder-ID>
    ...
Folders_RSC:
  - dcs-codename: mig-21bis
    gdrive-path: <gdrive-shared-folder-ID>
  - dcs-codename: mig-29a
    gdrive-path: <gdrive-shared-folder-ID>
    ...
Folders_BIN:
  - dcs-codename: '' # Keep as empty string
    gdrive-path: <gdrive-shared-folder-ID>
Folders_RoughMets:
  - dcs-codename: '' # Keep as empty string
    gdrive-path: <gdrive-shared-folder-ID>

```

* BIN folder: It contains various assets shared across multiple aircraft
* RoughMets folder: Reason why we need admin privileges - those files end up in the DCS installation instead of the "Saved Games" location. They are also flat files in a already used dir, so handling install/uninstall of Roughmets needed some more doing.

