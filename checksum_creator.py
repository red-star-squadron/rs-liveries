'''
This script:
1. Iterates multiple .7z files in series
2. Extracts each file into a directory
3. iterates all files in the directory to checksum the total
4. Writes the checksum as <basename_of_7z>.sha256sum
'''
import hashlib
from pathlib import Path, PurePath
import os
from inspect import getsourcefile
from tempfile import TemporaryDirectory
from locale import getpreferredencoding
import py7zr


def checksum_list_of_files(filenames: list[str]) -> str:
    '''
    Calculate the sha256 sum of multiple files
    Stolen from:
    https://stackoverflow.com/questions/34807537/generating-one-md5-sha1-checksum-of-multiple-files-in-python
    '''
    hashtmp = hashlib.sha256()
    for filename in filenames:
        try:
            hashtmp.update(Path(filename).read_bytes())
        except IsADirectoryError:
            pass
    return hashtmp.hexdigest()

def extract_7z(filename: str, output_dir: str):
    '''
    Extracts a 7z file
    '''
    with py7zr.SevenZipFile(filename, mode='r') as archive:
        archive.extractall(path=output_dir)


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
    script_dir = os.path.dirname(getsourcefile(lambda:0)) # type: ignore
    staging_dir = os.path.join(script_dir, "Staging")
    compressed_dir = os.path.join(script_dir, "Compressed")
    checksums_dir = os.path.join(staging_dir, "Checksums")
    list_of_7z_files = [arch_file for arch_file in get_files_in_dir(compressed_dir) \
        if arch_file.endswith(".7z")]
    for file_7z in list_of_7z_files:
        with TemporaryDirectory() as tmpdirname:
            extract_7z(file_7z, tmpdirname)
            chksum = checksum_list_of_files(get_files_in_dir(tmpdirname))
        dest_chksumfile = os.path.join(checksums_dir,
            PurePath(file_7z).stem + ".sha256sum")
        print(f"Writing {dest_chksumfile}")
        Path(Path(dest_chksumfile).resolve().parents[0]).mkdir(parents=True, exist_ok=True)
        with open(dest_chksumfile, "w", encoding=getpreferredencoding()) as file_final:
            file_final.write(chksum)



if __name__ == '__main__':
    main()
