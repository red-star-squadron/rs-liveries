from rs_util_shared import STAGING_DIR
from rs_util_shared import LOGGER
from rs_util_shared import single_dir_size
from rs_util_shared import dir_list_one_deep
from rs_util_shared import nuke_dir_contents

from rs_util_google import download_gdrive_folder
from rs_util_google import THREADPOOL

from os.path import join as os_join

from os import remove as os_remove
from os import listdir as os_listdir
from os import walk as os_walk
from fnmatch import fnmatch
from yaml import safe_load
from locale import getpreferredencoding
from threading import Lock
from time import time
from pickle import dumps as pickle_dumps
from pickle import load as pickle_load
from uuid import uuid4
from json import dumps as json_dumps


class LiveryAssets:
    _lock = Lock
    _all_assets = []
    _top_level_assets = []
    _supported_types = ["livery", "roughmets_single", "roughmets_multi", "shared", None]

    def __init__(
        self,
        basename=None,
        gdrive_id=None,
        dcs_codename=None,
        must_contain_strings=None,
        must_not_contain_strings=None,
        asset_type=None,
        category_name=None,
    ):
        # Add newly created instance to the list in our asset
        # variable. Thread-safe
        with LiveryAssets._lock():
            LiveryAssets._all_assets.append(self)

        # Initialize self vars
        self.basename = basename
        self.gdrive_id = gdrive_id
        self.dcs_codename = dcs_codename
        self.must_contain_strings = must_contain_strings
        self.must_not_contain_strings = must_not_contain_strings
        self.asset_type = asset_type
        self.category_name = category_name
        self._dl_dir = None
        self._parent = None
        self._size_in_bytes = None
        self._roughmets_dirs = None
        self._roughmets_files = None
        self._roughmets_sizes = None
        self._roughmets_uuids = None
        self._asset_dirs = None
        self._uuid = dict(
            {
                "install": str(uuid4()),
                "uninstall": str(uuid4()),
            }
        )
        self._dependants = None

    def __str__(self):
        return (
            f"basename: {self.basename}"
            "\ngdrive_id: {self.gdrive_id}"
            "\ndcs_codename: {self.dcs_codename}"
            "\nmust_contain_strings: {self.must_contain_strings}"
            "\nmust_not_contain_strings: {self.must_not_contain_strings}"
            "\nasset_type: {self.asset_type}"
            "\ncategory_name: {self.category_name}"
            "\n_dl_dir: {str(self._dl_dir)}"
            "\n_parent: {self._parent}"
            "\n_size_in_bytes: {self._size_in_bytes}"
            "\n_roughmets_dirs: {self._roughmets_dirs}"
            "\n_roughmets_files: {self._roughmets_files}"
            "\n_roughmets_sizes: {self._roughmets_sizes}"
            "\n_roughmets_uuids: {self._roughmets_uuids}"
            "\n_asset_dirs: {self._asset_dirs}"
            "\n_uuid: {self._uuid}"
            "\n_dependants: {self._dependants}"
        )

    def __iter__(self):
        yield "basename", self.basename
        yield "gdrive_id", self.gdrive_id
        yield "dcs_codename", self.dcs_codename
        yield "must_contain_strings", self.must_contain_strings
        yield "must_not_contain_strings", self.must_not_contain_strings
        yield "asset_type", self.asset_type
        yield "category_name", self.category_name
        yield "_dl_dir", self._dl_dir
        yield "_parent", self._parent
        yield "_size_in_bytes", self._size_in_bytes
        yield "_roughmets_dirs", self._roughmets_dirs
        yield "_roughmets_files", self._roughmets_files
        yield "_roughmets_sizes", self._roughmets_sizes
        yield "_roughmets_uuids", self._roughmets_uuids
        yield "_asset_dirs", self._asset_dirs
        yield "_uuid", self._uuid
        if self._dependants:
            yield "_dependants", [dict(d) for d in self._dependants]
        else:
            yield "_dependants", self._dependants

    def add_dependant(self, config_item, parent):
        config_item_copy = config_item.copy()
        # When adding a dependant, we want to ensure we pass down the
        # "must_contain_strings" and "must_not_contain_strings" attributes.
        # This is to maintain inheritance for sanity checks.
        try:
            config_item_copy["must_contain_strings"] += self.must_contain_strings
        except KeyError:
            config_item_copy["must_contain_strings"] = self.must_contain_strings
        try:
            config_item_copy[
                "must_not_contain_strings"
            ] += self.must_not_contain_strings
        except KeyError:
            config_item_copy["must_not_contain_strings"] = self.must_not_contain_strings

        dependant = LiveryAssets.from_config_item(config_item_copy)
        self._dependants.append(dependant)

    def get_pilot_dirs(self):
        return [
            pilot_dir for pilot_dir in self._asset_dirs if self.basename != pilot_dir
        ]

    def is_category(self):
        if self._dependants is not None:
            return True
        else:
            return False

    def is_category_with_a_download(self):
        if self._dependants is not None and self._dl_dir is not None:
            return True
        else:
            return False

    @classmethod
    def get_all_assets(cls):
        return cls._all_assets

    @classmethod
    def print_json(cls):
        print(json_dumps([dict(d) for d in cls.get_all_assets()], indent=4))

    @classmethod
    def get_all_downloaded_assets(cls):
        assets = []
        for asset in cls._all_assets:
            if asset._dl_dir:
                assets.append(asset)
        return assets

    @classmethod
    def get_assets_with_gdrive_id(cls):
        assets = []
        for asset in cls._all_assets:
            if asset.gdrive_id:
                assets.append(asset)
        return assets

    @classmethod
    def get_roughmets_assets(cls):
        assets = []
        for asset in cls._all_assets:
            if asset.asset_type == "roughmets" or asset.asset_type == "roughmets_multi":
                assets.append(asset)
        return assets

    @classmethod
    def get_assets_with_dcs_codename(cls):
        assets = []
        for asset in cls._all_assets:
            if asset.dcs_codename:
                assets.append(asset)
        return assets

    @classmethod
    def get_assets_with_dependants(cls):
        assets = []
        for asset in cls._all_assets:
            if asset._dependants:
                assets.append(asset)
        return assets

    @classmethod
    def get_total_size_in_bytes(cls):
        size = 0
        for asset in cls.get_assets_with_gdrive_id():
            size += asset._size_in_bytes
        return size

    @classmethod
    def get_all_pilots(cls):
        pilots = set()
        for asset in cls.get_assets_with_dcs_codename():
            asset_dirs = dir_list_one_deep(asset._dl_dir)
            smallest_dirname = min(asset_dirs, key=len)
            if len(asset_dirs) > 1:
                asset_dirs.remove(smallest_dirname)
                for liv in asset_dirs:
                    pilots.update({liv.removeprefix(smallest_dirname).strip()})
        return sorted(pilots)

    @classmethod
    def _update_roughmets_files_and_uuids(cls):
        """
        Run before Asset._update_sizes
        because "roughmets_multi" size calculations depend on it
        """
        for asset in cls.get_roughmets_assets():
            asset._roughmets_dirs = os_listdir(os_join(asset._dl_dir, asset.basename))
            asset._roughmets_files = dict()
            asset._roughmets_uuids = dict()
            for roughmet_dir in asset._roughmets_dirs:
                # Essentially building a dict for this asset
                # Key is the roughmet dir name, and the value is all the files in a single roughmets dir
                #
                # {
                #     "dirname1": ["file1", "file2"...],
                #     "dirname2": ["file3", "file4"...]
                # }
                asset._roughmets_files[roughmet_dir] = os_listdir(
                    os_join(asset._dl_dir, asset.basename, roughmet_dir)
                )
                asset._roughmets_uuids[roughmet_dir] = dict(
                    {"install": str(uuid4()), "uninstall": str(uuid4())}
                )

    @classmethod
    def _update_sizes(cls):
        for asset in cls.get_all_downloaded_assets():
            asset._size_in_bytes = single_dir_size(asset._dl_dir)
            if asset.asset_type == "roughmets_multi":
                asset._roughmets_sizes = dict()
                for roughmet_dir in asset._roughmets_dirs:
                    asset._roughmets_sizes[roughmet_dir] = single_dir_size(
                        os_join(asset._dl_dir, asset.basename, roughmet_dir)
                    )

    @classmethod
    def _update_assets_dirs(cls):
        for asset in cls.get_assets_with_gdrive_id():
            asset_dirs = set()
            for directory in dir_list_one_deep(asset._dl_dir):
                asset_dirs.update(
                    {directory.removeprefix(asset._dl_dir).strip().replace("/", "")}
                )
            asset._asset_dirs = sorted(asset_dirs)

    # from_config_file handles this, but we can keep it as a utility I guess
    @classmethod
    def _update_assets_parents(cls):
        for asset_parent in cls.get_all_assets():
            if asset_parent._dependants:
                for asset_child in asset_parent._dependants:
                    asset_child.parent = asset_parent

    @classmethod
    def _download_and_parse_assets(cls):
        nuke_dir_contents(STAGING_DIR)
        dl_statuses = []
        gdrive_id_assets = cls.get_assets_with_gdrive_id()
        timer_start = time()
        for asset in gdrive_id_assets:
            # This block is to handle downloads that don't have a dcs_codename,
            # like shared items or roughmets
            if asset.dcs_codename:
                desination_dir = os_join(
                    STAGING_DIR, asset.dcs_codename.lower(), asset.basename
                )
            else:
                desination_dir = os_join(STAGING_DIR, asset.basename)
            asset._dl_dir = desination_dir
            dl_status = THREADPOOL.submit(
                download_gdrive_folder,
                gdrive_id=asset.gdrive_id,
                des=asset._dl_dir,
                is_rootfolder=True,
                verify_basename=asset.basename,
                must_contain_strings=asset.must_contain_strings,
                must_not_contain_strings=asset.must_not_contain_strings,
            )
            dl_statuses.append(dl_status)

        for dl_status_local in dl_statuses:
            for dl_status_google in dl_status_local.result():
                dl_status_google.result()  # Wait for everything in THREADPOOL to finish
        LOGGER.info(f"Downloads took: {time() - timer_start}")

        # We do the following after downloads completed
        cls._remove_all_readme_files()
        cls._update_roughmets_files_and_uuids()
        cls._update_sizes()
        cls._update_assets_dirs()

    @classmethod
    def dump_pickle(cls, destination_file="asset.pickle"):
        with open(destination_file, "wb") as f:
            f.write(pickle_dumps(cls._all_assets))

    @classmethod
    def load_pickle(cls, source_file="asset.pickle"):
        with open(source_file, "rb") as f:
            cls._all_assets = pickle_load(f)

    @classmethod
    def from_config_file(cls, assetfile):
        with open(assetfile, "r", encoding=getpreferredencoding()) as file:
            assets_config = safe_load(file)

        for asset_config_item in assets_config:
            cls._top_level_assets.append(cls.from_config_item(asset_config_item))
        # Once we parse the config, we download and parse directories:
        cls._download_and_parse_assets()

    @classmethod
    def from_config_item(cls, config_item):
        try:
            basename = config_item["basename"].upper()
        except KeyError:
            basename = None
        try:
            gdrive_id = config_item["gdrive_id"]
        except KeyError:
            gdrive_id = None
        try:
            dcs_codename = config_item["dcs_codename"].lower()
        except KeyError:
            dcs_codename = None
        try:
            must_contain_strings = config_item["must_contain_strings"]
        except KeyError:
            must_contain_strings = []
        try:
            must_not_contain_strings = config_item["must_not_contain_strings"]
        except KeyError:
            must_not_contain_strings = []
        try:
            config_dependants = config_item["dependants"]
        except KeyError:
            config_dependants = None
        try:
            asset_type = config_item["asset_type"]
        except KeyError:
            asset_type = None
        try:
            category_name = config_item["category_name"]
        except KeyError:
            category_name = None

        # Check  if asset_type is one of supported types
        if asset_type not in cls._supported_types:
            raise ValueError(
                f"type must be one of {cls._supported_types}."
                f"\nYou provided {config_item}"
            )

        # If gdrive_id is provided, we expect basename as well
        if gdrive_id:
            if not basename:
                raise ValueError(
                    "If you provide 'gdrive_id', please also provide 'basename'"
                    f"\nYou provided: {config_item}"
                )

        # Livery asset type inferrence and check
        if dcs_codename:  # Inferrence
            if asset_type is None:
                asset_type = "livery"

        if asset_type == "livery":
            if dcs_codename is None or gdrive_id is None or basename is None:
                raise ValueError(
                    "If 'asset_type' is 'livery', please also provide 'dcs_codename' "
                    "'gdrive_id' and 'basename'"
                    f"\nYou provided: {config_item}"
                )
        if asset_type is None:
            if category_name is None:
                raise ValueError(
                    "If 'asset_type' is not set, you must provide 'category_name'"
                    f"\nYou provided: {config_item}"
                )
        # Roughmets_multi not suppoerted as category
        # It breaks out into children.
        if asset_type == "roughmets_multi" and config_dependants is not None:
            raise NotImplementedError(
                "We currently don't support roughmets_multi asset type "
                "as an asset with dependants."
                f"\nYou provided: {config_item}"
            )

        new_instance = cls(
            basename=basename,
            gdrive_id=gdrive_id,
            dcs_codename=dcs_codename,
            must_contain_strings=must_contain_strings,
            must_not_contain_strings=must_not_contain_strings,
            asset_type=asset_type,
            category_name=category_name,
        )

        if config_dependants is not None:
            new_instance._uuid["install_hidden"] = str(uuid4())
            new_instance._uuid["uninstall_hidden"] = str(uuid4())
            new_instance._dependants = []
            for config_dependant in config_dependants:
                new_instance.add_dependant(
                    config_item=config_dependant, parent=new_instance
                )

        return new_instance

    @staticmethod
    def _remove_all_readme_files():
        for root, dirs, files in os_walk(STAGING_DIR):
            for name in files:
                if fnmatch(name.lower(), "readme*.txt"):  # Remove readmes
                    LOGGER.info(f"Removing {os_join(root, name)}")
                    os_remove(os_join(root, name))
                else:
                    pass


def main():
    pass


if __name__ == "__main__":
    main()
