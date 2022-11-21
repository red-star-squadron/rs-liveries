#
# Red Star Skins - Livery priorities
# This script changes the livery priorities based on user choice selected in the installer
#

#
# NO WARRANTY WHATSOEVER
#

# https://github.com/Kaurin/rs-skins

# Exit on any error
$ErrorActionPreference = "Stop"

$dcs_liveries="$args[0]"
$pilot="$args[1]"

foreach ($i in Get-Childitem -Path $dcs_liveries -Include description.lua -File -Recurse -ErrorAction SilentlyContinue){
    if ($i.Directory | Split-Path -Leaf | Select-String -Pattern "RED STAR" | Select-String -Pattern $pilot)
    {
        (Get-Content -path $i.FullName) -replace '^order += -?\d+','order = -1000' | Set-Content -Path $i.FullName
    }
}
