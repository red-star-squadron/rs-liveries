param($7a_exec_path, $destination_dir, $archive_path)

# Exit on any error
$ErrorActionPreference = "Stop"

& "$7a_exec_path" -bd -bb0 -o"$destination_dir" x "$archive_path"