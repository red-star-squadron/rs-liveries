## Google credentials

Assumes you have the credentials.json. I think I used  google's IAM console to create a user with no permissions which can be assumed to use anonymous-access google drives.

```shell
export GOOGLE_APPLICATION_CREDENTIALS=credentials.json
```

## Livery asset definitions

The program expects to see a yaml file in assets.yml. In the github pipeline, we get this via the ASSETS secret.

Format respects hierarchy via the "dependants" values

Format is as follows:

```yml
---
- basename: RED STAR BIN
  category_name: Liveries with shared assets (RED STAR BIN)
  gdrive_id: REDACTED
  must_contain_strings: ["RED STAR"]
  asset_type: shared
  dependants:
    - category_name: Fixed Wing - Red Star Camo (BIN dependant)
      must_not_contain_strings: ["BLACK SQUADRON"]
      dependants:
        - basename: RED STAR MiG-29S
          dcs_codename: mig-29s
          gdrive_id: REDACTED
        - basename:  RED STAR MiG-29A
          dcs_codename: mig-29a
          gdrive_id: REDACTED
          dependants:
          - basename: RED STAR MiG-29G
            dcs_codename: mig-29g
            gdrive_id: REDACTED
        - basename:  RED STAR JF-17
          dcs_codename: jf-17
          gdrive_id: REDACTED
        - basename:  RED STAR SU-27
          dcs_codename: su-27
          gdrive_id: REDACTED
          dependants:
          - basename:  RED STAR J-11A
            dcs_codename: j-11a
            gdrive_id: REDACTED
        - basename:  RED STAR SU-33
          dcs_codename: su-33
          gdrive_id: REDACTED

    - category_name: Fixed Wing - Red Star Competitive (BIN dependant)
      must_contain_strings: ["BLACK SQUADRON"]
      dependants:
        - basename:  RED STAR MiG-29S BLACK SQUADRON
          dcs_codename: mig-29s
          gdrive_id: REDACTED
        - basename:  RED STAR MiG-29A BLACK SQUADRON
          dcs_codename: mig-29a
          gdrive_id: REDACTED
          dependants:
          - basename: RED STAR MiG-29G BLACK SQUADRON
            dcs_codename: mig-29g
            gdrive_id: REDACTED
        - basename:  RED STAR F-16C_50 BLACK SQUADRON
          dcs_codename: f-16c_50
          gdrive_id: REDACTED
        - basename:  RED STAR SU-27 BLACK SQUADRON
          dcs_codename: su-27
          gdrive_id: REDACTED
          dependants:
          - basename:  RED STAR J-11A BLACK SQUADRON
            dcs_codename: j-11a
            gdrive_id: REDACTED
        - basename:  RED STAR JF-17 BLACK SQUADRON
          dcs_codename: jf-17
          gdrive_id: REDACTED
        - basename:  RED STAR SU-33 BLACK SQUADRON
          dcs_codename: su-33
          gdrive_id: REDACTED
        - basename:  RED STAR SU-25 BLACK SQUADRON
          dcs_codename: su-25
          gdrive_id: REDACTED

- category_name: Fixed Wing - Red Star Camo
  must_not_contain_strings: ["BLACK SQUADRON"]
  must_contain_strings: ["RED STAR"]
  dependants:
    - basename:  RED STAR F-16C_50
      dcs_codename: f-16c_50
      gdrive_id: REDACTED
    - basename:  RED STAR FA-18C
      dcs_codename: fa-18c_hornet
      gdrive_id: REDACTED
    - basename:  RED STAR F15C
      dcs_codename: f-15c
      gdrive_id: REDACTED
    - basename:  RED STAR F-14B
      dcs_codename: f-14b
      gdrive_id: REDACTED
      dependants:
        - basename:  RED STAR F-14A-135-GR
          dcs_codename: f-14a-135-gr
          gdrive_id: REDACTED
    - basename:  RED STAR M-2000C
      dcs_codename: m-2000c
      gdrive_id: REDACTED
    - basename:  RED STAR F-5E-3
      dcs_codename: f-5e-3
      gdrive_id: REDACTED
    - basename:  RED STAR A-4E-C
      dcs_codename: a-4e-c
      gdrive_id: REDACTED
    - basename:  RED STAR MiG-19P
      dcs_codename: mig-19p
      gdrive_id: REDACTED
    - basename:  RED STAR Mirage-F1CE
      dcs_codename: mirage-f1ce
      gdrive_id: REDACTED
      dependants:
        - basename:  RED STAR Mirage-F1EE
          dcs_codename: mirage-f1ee
          gdrive_id: REDACTED
    - basename:  RED STAR MiG-21
      dcs_codename: mig-21bis
      gdrive_id: REDACTED
    - basename:  RED STAR F-15ESE
      dcs_codename: f-15ese
      gdrive_id: REDACTED
    - basename:  RED STAR Mirage-F1BE
      dcs_codename: mirage-f1be
      gdrive_id: REDACTED

- category_name: Fixed Wing - Red Star Competitive
  must_contain_strings: ["BLACK SQUADRON", "RED STAR"]
  dependants:
    - basename:  RED STAR MIG-21 BLACK SQUADRON
      dcs_codename: mig-21bis
      gdrive_id: REDACTED
    - basename:  RED STAR FA-18C BLACK SQUADRON 
      dcs_codename: fa-18c_hornet
      gdrive_id: REDACTED
    - basename:  RED STAR F15C BLACK SQUADRON
      dcs_codename: f-15c
      gdrive_id: REDACTED
    - basename:  RED STAR F-14B BLACK SQUADRON 
      dcs_codename: f-14b
      gdrive_id: REDACTED
      dependants:
        - basename:  RED STAR F-14A-135-GR BLACK SQUADRON
          dcs_codename: f-14a-135-gr
          gdrive_id: REDACTED
    - basename:  RED STAR M-2000C BLACK SQUADRON
      dcs_codename: m-2000c
      gdrive_id: REDACTED
    - basename:  RED STAR A-10CII BLACK SQUADRON
      dcs_codename: A-10cii
      gdrive_id: REDACTED
      dependants:
        - basename:  RED STAR A-10A BLACK SQUADRON
          dcs_codename: A-10A
          gdrive_id: REDACTED
        - basename:  RED STAR A-10C BLACK SQUADRON
          dcs_codename: A-10c
          gdrive_id: REDACTED
    - basename:  RED STAR F-5E-3 BLACK SQUADRON
      dcs_codename: f-5e-3
      gdrive_id: REDACTED
    - basename:  RED STAR AV8BNA BLACK SQUADRON
      dcs_codename: av8bna
      gdrive_id: REDACTED
    - basename:  RED STAR A-4E-C BLACK SQUADRON
      dcs_codename: a-4e-c
      gdrive_id: REDACTED
    - basename:  RED STAR MiG-19P BLACK SQUADRON
      dcs_codename: mig-19p
      gdrive_id: REDACTED
    - basename:  RED STAR Mirage-F1CE BLACK SQUADRON
      dcs_codename: mirage-f1ce
      gdrive_id: REDACTED
      dependants:
        - basename:  RED STAR Mirage-F1EE BLACK SQUADRON
          dcs_codename: mirage-f1ee
          gdrive_id: REDACTED
    - basename:  RED STAR F-15ESE BLACK SQUADRON
      dcs_codename: f-15ese
      gdrive_id: REDACTED
    - basename:  RED STAR HERCULES BLACK SQUADRON
      dcs_codename: hercules
      gdrive_id: REDACTED
    - basename:  RED STAR Mirage-F1BE BLACK SQUADRON
      dcs_codename: mirage-f1be
      gdrive_id: REDACTED
    - basename:  RED STAR SU-25T BLACK SQUADRON
      dcs_codename: su-25t
      gdrive_id: REDACTED

- category_name: Rotary Wing - Red Star Competitive
  must_contain_strings: ["BLACK SQUADRON", "RED STAR"]
  dependants:
    - basename:  RED STAR AH-64D_BLK_II BLACK SQUADRON
      dcs_codename: AH-64D_BLK_II
      gdrive_id: REDACTED
    - basename:  RED STAR KA-50 BLACK SQUADRON
      dcs_codename: Ka-50_3
      gdrive_id: REDACTED
    - basename:  RED STAR UH-1H BLACK SQUADRON
      dcs_codename: uh-1h
      gdrive_id: REDACTED
    - basename:  RED STAR MI-24P BLACK SQUADRON
      dcs_codename: mi-24p
      gdrive_id: REDACTED


- basename: RED STAR ROUGHMETS
  category_name: Roughmets (Optional)
  asset_type: roughmets_multi
  gdrive_id: REDACTED


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

Prerequisite: GitHub CLI configured and authenticaed with admin permissions on the repo.

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