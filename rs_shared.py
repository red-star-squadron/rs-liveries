from os.path import dirname as os_dirname
from os.path import join as os_join
from inspect import getsourcefile
from os import environ


SCRIPT_DIR = os_dirname(getsourcefile(lambda: 0))  # type: ignore
STAGING_DIR = os_join(SCRIPT_DIR, "Staging")
CHECKSUMS_DIR = os_join(STAGING_DIR, "Checksums")
COMPRESSED_DIR = os_join(SCRIPT_DIR, "Compressed")


if "GITHUB_REF_NAME" in environ:
    GITHUB_REF_NAME = environ["GITHUB_REF_NAME"]
else:
    GITHUB_REF_NAME = "no_GITHUB_REF_NAME"


if not GITHUB_REF_NAME.startswith("v"):
    GITHUB_REF_NAME = "testing"


if environ["MINIMAL_SAMPLE_SIZE"].lower() == "true":
    MINIMAL_SAMPLE_SIZE = True
else:
    MINIMAL_SAMPLE_SIZE = False


if environ["DELETE_AFTER_COMPRESS"].lower() == "true":
    DELETE_AFTER_COMPRESS = True
else:
    DELETE_AFTER_COMPRESS = False


def main():
    pass


if __name__ == "__main__":
    main()
