param($7a_exec_path, $destination_dir, $archive_path)

# Exit on any error
$ErrorActionPreference = "Stop"

Set-Location -Path "$destination_dir"
& "$7a_exec_path" -bd -bb0 -o x "$archive_path"
