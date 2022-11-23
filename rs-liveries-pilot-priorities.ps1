param($dcs_liveries, $pilot)
#
# Red Star Liveries - Livery priorities
# This script changes the livery priorities based on user choice selected in the installer
#

#
# NO WARRANTY WHATSOEVER
#

# Exit on any error
$ErrorActionPreference = "Stop"

if ("$pilot" -eq "-- STREAMER / YOUTUBER --" ){
    foreach ($i in Get-Childitem -Path $dcs_liveries -Include description.lua -File -Recurse -ErrorAction SilentlyContinue){
        if ($i.Directory | Split-Path -Leaf | Select-String -Pattern "RED STAR")
        {
            (Get-Content -path $i.FullName) -replace '^order += +-?\d+','order = 9999' | Set-Content -Path $i.FullName
        }
    }
} elseif ("$pilot" -eq "-- RS SQUAD BUT NOT IN LIST --" ) {
    # Do nothing if member is RS squad but not in list because Striker's layout already matches this
} elseif ("$pilot" -eq "") {
    # Do nothing if pilot string empty
} else {
    foreach ($i in Get-Childitem -Path $dcs_liveries -Include description.lua -File -Recurse -ErrorAction SilentlyContinue){
        if ($i.Directory | Split-Path -Leaf | Select-String -Pattern "RED STAR" | Select-String -Pattern $pilot)
        {
            (Get-Content -path $i.FullName) -replace '^order += +-?\d+','order = -1000' | Set-Content -Path $i.FullName
        }
    }
}
