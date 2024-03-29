# RS Liveries
DCS liveries for the RED STAR SQUADRON by `RS ✯ | Striker 45` and `RS ✯ | Wyvern`

## DISCLAIMER
This software comes with absolutely no warranty. Use at your own risk.

## Description
This repo packages RS liveries for the Digital Combat Simulator (DCS World)

## How to download?
[Releases page](../../releases) contains the Downloads link. Each release offers the `.exe` installer.

## Security concerns

#### I inspected the code and noticed that you guys don't expose the source of the liveries files. Why?

This is to protect the privacy of the author(s). Their workflow involves using shared personal google drive folders, and we'd prefer our authors don't get doxxed.

#### This means that you can create a virus exe!

As far as the nsis installer that produces the `.exe` goes, that pipeline is fully transparent and is fairly simple (check the .nsi script and `.github/workflows/`). Creating an exe that triggers a virus is only possible if Github's Ubuntu executor decides to have the nsis installer maliciously modified, which is highly unlikely.

#### But, you can still have flat DCS livery files that contain viruses.

This is true. However, we assume that Github and your Antivirus will scan for potential threats (as well as us during testing).

#### What's the biggest threat?

There is a possibility for DCS to somehow trigger a virus through lua files contained in liveries, but the lua files are available for review by extracting the liveries in a safe location.

## Third party software

### 7-Zip
7-Zip software which is available on https://www.7-zip.org and licensed under the GNU LGPL license

### NSIS
NSIS software which is available on https://nsis.sourceforge.io and licensed under the Common Public License version 1.0
