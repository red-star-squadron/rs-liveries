# RS Liveries

## DISCLAIMER
This software comes with absolutely no warranty. Use at your own risk.

## Description
This repo packages RS liveries for the Digital Combat Simulator (DCS World)

## How to download?
[Releases page](../../releases) contains the Downloads link. Each release offers the `.exe` installer.

## Install options

By far, the easiest method of installation is to download the exe from the [releases page](../../releases) which provides a simple interface of installing/updating/removing RS liveries.

If you are not comfortable running the `.exe`, you can extract it using the popular [7-Zip](https://www.7-zip.org/) archive utility to `Saved Games\DCS\Liveries` or `Saved Games\DCS.openbeta\Liveries`

## Security concerns

Q: I inspected the code and noticed that you guys don't expose the source of the liveries files. Why?  
A: This is to protect the privacy of the author(s). Their workflow involves using shared personal google drive folders, and we'd prefer our authors don't get doxxed.

Q: This means that you can create a virus exe!  
A: As far as the nsis installer that produces the `.exe` goes, that pipeline is fully transparent and is fairly simple (check the .nsi script and `.github/workflows/`). Creating an exe that triggers a virus is only possible if Github's Ubuntu executor decides to have the nsis installer maliciously modified, which is highly unlikely.

Q: But, you can still have flat DCS livery files that contain viruses.  
A: This is true. However, we assume that Github and your Antivirus will scan for potential threats (as well as us during testing). 

Q: What's the biggest threat?  
A: There is a possibility for DCS to somehow trigger a virus through lua files contained in liveries, but the lua files are available for review by extracting the liveries in a safe location.
