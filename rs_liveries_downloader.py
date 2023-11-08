"""
RS Liveries Downloader
"""

# from rs_util_shared import LOGGER
from rs_util_shared import GITHUB_REF_NAME
from rs_util_shared import STAGING_DIR

# from rs_util_shared import LOGGER
from rs_Assets import LiveryAssets

from jinja2 import FileSystemLoader
from jinja2 import Environment
from locale import getpreferredencoding
from os.path import join as os_join
from shutil import copy as su_copy
from rs_util_archive import compress_and_checksum


def main():
    LiveryAssets.from_config_file("assets.yml")
    # for item in LiveryAssets._all_assets:
    #     LOGGER.info(f"{item.basename}  {item.category_name}  {item._uuid}")

    file_loader = FileSystemLoader("templates")
    # jinja_env = Environment(loader=file_loader, extensions=['jinja2.ext.debug'])
    jinja_env = Environment(loader=file_loader)

    template = jinja_env.get_template("rs-liveries.nsi.j2")
    output = template.render(
        top_level_assets=[dict(a) for a in LiveryAssets._top_level_assets],
        all_assets=[dict(a) for a in LiveryAssets._all_assets],
        pilots=LiveryAssets.get_all_pilots(),
        github_ref_name=GITHUB_REF_NAME,
        size_bin_kb=LiveryAssets.get_total_size_in_bytes(),
    )
    with open(
        "Staging/rs-liveries-rendered.nsi", "w+", encoding=getpreferredencoding()
    ) as file:
        file.write(output)

    template = jinja_env.get_template("livery-priorities.ps1.j2")
    output = template.render(assets=LiveryAssets.get_assets_with_dcs_codename())
    with open(
        "Staging/livery-priorities.ps1", "w+", encoding=getpreferredencoding()
    ) as file:
        file.write(output)

    su_copy("psexec.nsh", os_join(STAGING_DIR, "psexec.nsh"))
    su_copy("rs.ico", os_join(STAGING_DIR, "rs.ico"))
    su_copy("rssplash.bmp", os_join(STAGING_DIR, "rssplash.bmp"))
    su_copy("mig29flyby.wav", os_join(STAGING_DIR, "mig29flyby.wav"))
    su_copy("extract-file.ps1", os_join(STAGING_DIR, "extract-file.ps1"))

    compress_and_checksum(LiveryAssets._all_assets)


if __name__ == "__main__":
    main()
