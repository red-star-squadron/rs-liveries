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


## Iterative process


### Make a change

Self explanatory. You should be on a non-main branch.

We'll hold off the push for later, because that triggers a pipeline run on specific branches.


### Temporarily set `MINIMAL_SAMPLE_SIZE` to true in `.env`

This is to significantly reduce the run time.

What this env var does is reduce so that every livery will get 1 .dds file and the lua file.

The lua file is significant if you are testing the installer. The powershell sciprt which changes pilot priorities needs it.


### Run locally

`scripts/local_run.sh`

Before running it. you will need nsis, relevant nsis plugins etc. Check the github workflow file to see how to set up your machine.

We could rework this script so it runs in docker with everything set-up, but it was a personal preference to have a local-run enbabled.

Unfortunately, the .exe file we get this way can be tested for everything except downloading liveries.

We require a Github release for downloads to work.

Assuming the exe was created and you ran initial tests, you can proceed to the next step. Otherwise back to the start and iterate!

TODO: Maybe make it source files locally so the exe can "download" stuff? Potentially too much work. Idea: web server in a docker container!

TODO: also give a docker option


### Run the local github runner

Pre-requisite: GitHub CLI configured and authenticaed with admin permissions on the repo.

* `scripts/runner_build.sh` to build the image if not already present
* `scripts/runner_start.sh` to start the runner

Make sure to check the logs of the runner. The start script should give you the command on how to do that.

With the runner up, we're ready to push. More about that in the next section.

Sidenote: Local runner will use tmpfs for it's run. I think 32GB of ram is a requirement here.


### Trigger a non-main workflow run

This is done by pushing to branches such as `wip**`, `feature**` etc. Check `.github/on_push.yml` to see which branch names are valid.


### Sit and wait.

Workflow will take about 15 minutes. A much better alternative to ~1h that it takes on the github-hosted runner.

Once done, it will produce a "Testing" release where you should go grab the exe


### Go and test

Go test the installer

TODO: how to test the installer


### Merge to main and create a release

If all went well, congrats! To trigger the main workflow, we must create a release manually.

Example release:

Release tag follows this format: `v0.10.0+2023-11-03-001` (semver + date + release attempt)

Title: `Red Star Livery Installer 2023-11-03-001`

Body:
```
## Version 2023-11-03-001 brings

### New aircraft

...

### Updated aircraft

...

### Updated common assets

...

## Installer v0.10.0 - changes

``
Once a release is created on the main branch, a workflow will trigger. It currently takes about an hour to complete.


### Et voila

Once the release is done, do another test, and then distribute to folks waiting for their fancy planes!