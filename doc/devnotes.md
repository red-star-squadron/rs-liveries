## Google credentials

Assumes you have the credentials.json. I think I used  google's IAM console to create a user with no permissions which can be assumed to use anonymous-access google drives.

export GOOGLE_APPLICATION_CREDENTIALS=credentials.json

## gdrive secrets

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

```

Note that BIN currently has only one shared folder