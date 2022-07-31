# RS Skins

## DISCLAIMER
This software comes with absolutely no warranty. Use at your own risk.

## Description
This repo packages RS skins for the Digital Combat Simulator (DCS World)

## How to download?
[Releases page](../../releases) contains the Downloads links. Each release offers the `.exe` installer (nullsoft installer, super optimized), or a large `.zip`. 

## Install options

By far, the easiest method of installation is to download the exe from the [releases page](../../releases) which provides a simple interface of installing/updating/removing RS skins.

If you are not comfortable with downloading the `.exe`, we also offer the flat `.zip` file which you'll have to unzip to `Saved Games\DCS\Liveries` or `Saved Games\DCS Open Beta\Liveries`

There is also a third option which is to download the `.exe` and Extract it using the popular 7-Zip archive utility. This is useful if you are on a slow internet connection as the `.exe` is about 3x smaller than the `.zip`

## Security concerns

Q: I inspected the code and noticed that you guys don't expose the source of the liveries files. Why?  
A: This is to protect the privacy of the author(s). Their workflow involves using shared personal google drive folders, and we'd prefer our authors don't get doxxed.

Q: This means that you can create a virus exe!  
A: As far as the nsis installer that produces the `.exe` goes, that pipeline is fully transparent and is fairly simple (check the .nsi script and `.github/workflows/`). Creating an exe that triggers a virus is only possible if Github's Ubuntu executor decides to have the nsis installer maliciously modified, which is highly unlikely.

Q: But, you can still have flat DCS livery files that contain viruses.  
A: This is true. However, we assume that Github and your Antivirus will scan for potential threats (as well as us during testing). 

Q: What's the biggest threat?  
A: There is a possibility for DCS to somehow trigger a virus through lua files contained in liveries, but the lua files are available for review by extracting the skins in a safe location.
