param($7a_exec_path, $destination_dir, $archive_path)

# Exit on any error
$ErrorActionPreference = "Stop"

# Write-Host "$7a_exec_path"
# Write-Host "$destination_dir"
# Write-Host "$archive_path"
Set-Location -Path "$destination_dir"
& "$7a_exec_path" -y -bd -bb0 x "$archive_path" | Out-Null
