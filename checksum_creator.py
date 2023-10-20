'''
This script:
1. Iterates multiple .7z files in series
2. Extracts each file into a directory
3. iterates all files in the directory to checksum the total
4. Writes the checksum as <basename_of_7z>.sha256sum
'''
import subprocess
import hashlib
from pathlib import Path, PurePath
import os
from inspect import getsourcefile
from locale import getpreferredencoding


def get_files_in_dir(directory: str) -> list[str]:
    '''
    Get all files in a directory (recursively)
    '''
    all_files = []
    for root, _, files in os.walk(directory):
        all_files.extend([os.path.join(root, single_file) for single_file in files])
    return all_files


def main():
    '''main loop'''
    script_dir = os.path.dirname(getsourcefile(lambda: 0))  # type: ignore
    staging_dir = os.path.join(script_dir, "Staging")
    compressed_dir = os.path.join(script_dir, "Compressed")
    checksums_dir = os.path.join(staging_dir, "Checksums")
    list_of_7z_files = [arch_file for arch_file in get_files_in_dir(compressed_dir)
                        if arch_file.endswith(".7z")]
    for file_7z in list_of_7z_files:
        # Py7zr library doesn't offer a simple way to get the complete extracted
        # bytestream like the 7z utility.
        z_subprocess = subprocess.run(["7z", "e", "-so", file_7z],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      check=True,
                                      text=False)
        chksum = hashlib.sha256(z_subprocess.stdout).hexdigest()
        dest_chksumfile = os.path.join(checksums_dir,
                                       PurePath(file_7z).stem + ".sha256sum")
        print(f"Writing {dest_chksumfile}")
        Path(Path(dest_chksumfile).resolve().parents[0]).mkdir(parents=True, exist_ok=True)
        with open(dest_chksumfile, "w", encoding=getpreferredencoding()) as file_final:
            file_final.write(chksum)


if __name__ == '__main__':
    main()
