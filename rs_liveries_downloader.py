"""
RS Liveries Downloader
"""

from rs_util_shared import GITHUB_REF_NAME
from rs_util_shared import STAGING_DIR

from rs_Assets import LiveryAssetCollection

from jinja2 import FileSystemLoader
from jinja2 import Environment
from locale import getpreferredencoding
from os.path import join as os_join
from shutil import copy as su_copy


def main() -> None:
    collection = LiveryAssetCollection("assets.yml")

    file_loader = FileSystemLoader("templates")
    # jinja_env = Environment(loader=file_loader, extensions=['jinja2.ext.debug'])
    jinja_env = Environment(loader=file_loader)

    template = jinja_env.get_template("rs-liveries.nsi.j2")
    output = template.render(
        top_level_assets=collection.top_level_assets,
        all_assets=collection.all_assets,
        pilots=collection.all_pilots,
        github_ref_name=GITHUB_REF_NAME,
        size_bin_kb=collection.get_total_size_in_bytes(),
    )
    with open(
        "Staging/rs-liveries-rendered.nsi", "w+", encoding=getpreferredencoding()
    ) as file:
        file.write(output)

    template = jinja_env.get_template("livery-priorities.ps1.j2")
    output = template.render(assets=collection.get_assets_with_dcs_codename())
    with open(
        "Staging/livery-priorities.ps1", "w+", encoding=getpreferredencoding()
    ) as file:
        file.write(output)

    su_copy("psexec.nsh", os_join(STAGING_DIR, "psexec.nsh"))
    su_copy("rs.ico", os_join(STAGING_DIR, "rs.ico"))
    su_copy("rssplash.bmp", os_join(STAGING_DIR, "rssplash.bmp"))
    su_copy("mig29flyby.wav", os_join(STAGING_DIR, "mig29flyby.wav"))
    su_copy("extract-file.ps1", os_join(STAGING_DIR, "extract-file.ps1"))


if __name__ == "__main__":
    main()
