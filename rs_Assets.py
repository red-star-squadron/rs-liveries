from rs_util_shared import STAGING_DIR
from rs_util_shared import LOGGER
from rs_util_shared import single_dir_size
from rs_util_shared import dir_list_one_deep
from rs_util_shared import nuke_dir_contents

from rs_util_google import download_gdrive_folder
from rs_util_google import THREADPOOL

from typing import Dict, Any, List
from os.path import join as os_join
from os import remove as os_remove
from os import listdir as os_listdir
from os import walk as os_walk
from fnmatch import fnmatch
from yaml import safe_load
from locale import getpreferredencoding
from pickle import dumps as pickle_dumps
from pickle import load as pickle_load
from uuid import uuid4
from json import dumps as json_dumps


# Typing aliases
JSONDict = Dict[str, Any]
JSONArray = List[Any]


class LiveryAsset:
    _all_assets = []
    _top_level_assets = []
    _supported_config_asset_types = [
        "livery",
        "roughmets_single",
        "roughmets_multi",
        "shared",
        None,
    ]

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
        # Initialize self vars
        self.basename = basename
        self.gdrive_id = gdrive_id
        self.dcs_codename = dcs_codename
        self.must_contain_strings = must_contain_strings
        self.must_not_contain_strings = must_not_contain_strings
        self.asset_type = asset_type
        self.category_name = category_name
        self._dl_dir = None
        self._dl_future = None
        self.__parent = None
        self._size_in_bytes = None
        self._asset_dirs = None
        self._roughmets_files = None
        self._uuid = str(uuid4())
        self._children = None

    def __str__(self):
        return (
            f"basename: {self.basename}"
            f"\ngdrive_id: {self.gdrive_id}"
            f"\ndcs_codename: {self.dcs_codename}"
            f"\nmust_contain_strings: {self.must_contain_strings}"
            f"\nmust_not_contain_strings: {self.must_not_contain_strings}"
            f"\nasset_type: {self.asset_type}"
            f"\ncategory_name: {self.category_name}"
            f"\n_dl_dir: {str(self._dl_dir)}"
            f"\n_dl_future: {self._dl_future}"
            f"\n__parent: {self.__parent}"
            f"\n_size_in_bytes: {self._size_in_bytes}"
            f"\n_asset_dirs: {self._asset_dirs}"
            f"\n_roughmets_files: {self._roughmets_files}"
            f"\n_uuid: {self._uuid}"
            f"\n_children: {self._children}"
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
        yield "_dl_future", self._dl_future
        yield "__parent", self.__parent
        yield "_size_in_bytes", self._size_in_bytes
        yield "_asset_dirs", self._asset_dirs
        yield "_roughmets_files", self._roughmets_files
        yield "_uuid", self._uuid,
        if self._children:
            yield "_children", [dict(d) for d in self._children]
        else:
            yield "_children", self._children

    def add_child_from_config_item(self, config_item, parent):
        config_item_copy = config_item.copy()
        # When adding a child, we want to ensure we pass down the
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

        child = self.from_config_item(config_item_copy)
        self._children.append(child)

    def get_pilot_dirs(self):
        return [
            pilot_dir for pilot_dir in self._asset_dirs if self.basename != pilot_dir
        ]

    def _download_asset(self) -> "LiveryAsset":
        if self.gdrive_id is None:
            return None
        nuke_dir_contents(self._dl_dir)
        if self.dcs_codename:
            desination_dir = os_join(
                STAGING_DIR, self.dcs_codename.lower(), self.basename
            )
        else:
            desination_dir = os_join(STAGING_DIR, self.basename)
        self._dl_dir = desination_dir
        self._dl_future = THREADPOOL.submit(
            download_gdrive_folder,
            gdrive_id=self.gdrive_id,
            des=self._dl_dir,
            is_rootfolder=True,
            verify_basename=self.basename,
            must_contain_strings=self.must_contain_strings,
            must_not_contain_strings=self.must_not_contain_strings,
        )
        return self

    def _process_roughmets_multi(self) -> List["LiveryAsset"]:
        roughmets_multi_children = []
        for roughmets_dir in os_listdir(os_join(self._dl_dir, self.basename)):
            roughmets_files = os_listdir(
                os_join(self._dl_dir, self.basename, roughmets_dir)
            )
            new_instance = LiveryAsset(
                basename=f"Roughmets {roughmets_dir}",
                gdrive_id=self.gdrive_id,
                asset_type="roughmets_single",
            )
            new_instance.gdrive_id = self.gdrive_id
            new_instance._dl_dir = os_join(self._dl_dir, self.basename, roughmets_dir)
            new_instance._parent = self
            new_instance._roughmets_files = roughmets_files
            new_instance._update_size()
            roughmets_multi_children.append(new_instance)
            self._all_assets.append(new_instance)
        self._children = roughmets_multi_children
        # This essentially convers the asset_multi into a category without a download,
        # because it now has children of type roughmets_single
        self.gdrive_id = None
        self._dl_dir = None
        self._size_in_bytes = None
        return roughmets_multi_children

    def _update_size(self):
        self._size_in_bytes = single_dir_size(self._dl_dir)

    def _update_assets_dirs(self):
        asset_dirs = set()
        for directory in dir_list_one_deep(self._dl_dir):
            asset_dirs.update(
                {directory.removeprefix(self._dl_dir).strip().replace("/", "")}
            )
        self._asset_dirs = sorted(asset_dirs)

    @classmethod
    def get_all_assets_from_top_level_assets(
        cls, top_level_assets: List["LiveryAsset"]
    ) -> List["LiveryAsset"]:
        assets = []
        for asset in top_level_assets:
            assets.append(asset)
            if asset._children:
                assets += cls.get_all_assets_from_top_level_assets(asset._children)
        return assets

    @classmethod
    def print_json(cls):
        return json_dumps([dict(d) for d in cls._all_assets], indent=4)

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
    def dump_pickle(cls, destination_file="asset.pickle"):
        with open(destination_file, "wb") as f:
            f.write(pickle_dumps(cls._all_assets))

    @classmethod
    def load_pickle(cls, source_file="asset.pickle"):
        with open(source_file, "rb") as f:
            cls._all_assets = pickle_load(f)

    @classmethod
    def from_config_file(cls, assetfile: str) -> List["LiveryAsset"]:
        with open(assetfile, "r", encoding=getpreferredencoding()) as file:
            assets_config = safe_load(file)
        top_level_assets = []
        for asset_config_item in assets_config:
            asset = cls.from_config_item(asset_config_item)
            top_level_assets.append(asset)

        # Wait for downloads to finish, and the do post-download processing
        for asset in cls.get_all_assets_from_top_level_assets(top_level_assets):
            if asset._dl_dir is not None:
                for futures in asset._dl_future.result():
                    futures.result()
                asset._remove_all_readme_files(asset._dl_dir)
                if asset.asset_type == "roughmets_multi":
                    asset._process_roughmets_multi()
                else:
                    asset._update_assets_dirs()
                    asset._update_size()

        cls._top_level_assets = top_level_assets

        return top_level_assets

    @classmethod
    def from_config_item(cls, config_item: Dict[str, str]) -> "LiveryAsset":
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
            config_children = config_item["children"]
        except KeyError:
            config_children = None
        try:
            asset_type = config_item["asset_type"]
        except KeyError:
            asset_type = None
        try:
            category_name = config_item["category_name"]
        except KeyError:
            category_name = None

        # Check  if asset_type is one of supported types
        if asset_type not in cls._supported_config_asset_types:
            raise ValueError(
                f"type must be one of {cls._supported_config_asset_types}."
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

        new_instance = cls(
            basename=basename,
            gdrive_id=gdrive_id,
            dcs_codename=dcs_codename,
            must_contain_strings=must_contain_strings,
            must_not_contain_strings=must_not_contain_strings,
            asset_type=asset_type,
            category_name=category_name,
        )
        new_instance._download_asset()
        if config_children is not None:
            new_instance._children = []
            for config_child in config_children:
                new_instance.add_child_from_config_item(
                    config_item=config_child, parent=new_instance
                )
        cls._all_assets.append(new_instance)

        return new_instance

    @staticmethod
    def _remove_all_readme_files(directory):
        for root, dirs, files in os_walk(directory):
            for name in files:
                if fnmatch(name.lower(), "readme*.txt"):  # Remove readmes
                    LOGGER.info(f"Removing {os_join(root, name)}")
                    os_remove(os_join(root, name))
                else:
                    pass


def main():
    pass
    LiveryAsset.from_config_file("assets.yml")
    for asset in LiveryAsset._all_assets:
        LOGGER.info(asset)
        LOGGER.info("----------------")


if __name__ == "__main__":
    main()
