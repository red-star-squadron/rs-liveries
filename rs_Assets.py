from rs_util_shared import STAGING_DIR
from rs_util_shared import COMPRESSED_DIR
from rs_util_shared import CHECKSUMS_DIR
from rs_util_shared import LOGGER
from rs_util_shared import single_dir_size

from rs_util_google import download_gdrive_folder
from rs_util_google import THREADPOOL

from rs_util_archive import compress_and_checksum

from typing import Dict, Any, List
from os.path import join as os_join
from os import remove as os_remove
from os import walk as os_walk
from os import listdir as os_listdir
from shutil import rmtree
from pathlib import PurePath
from fnmatch import fnmatch
from yaml import safe_load
from locale import getpreferredencoding
from uuid import uuid4
from json import dumps as json_dumps
from concurrent.futures import Future


class LiveryAsset:
    _supported_config_asset_types = [
        "livery",
        "roughmets",
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
        self._asset_items = None
        self._uuid = str(uuid4())
        self._children = None

    def __str__(self) -> str:
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
            f"\n_asset_items: {self._asset_items}"
            f"\n_uuid: {self._uuid}"
            f"\n_children: {self._children}"
        )

    def __iter__(self) -> Dict[str, Any]:
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
        yield "_asset_items", self._asset_items
        yield "_uuid", self._uuid,
        if self._children:
            yield "_children", [dict(d) for d in self._children]
        else:
            yield "_children", self._children

    def add_child_from_config_item(
        self, config_item: Dict[str, Any], parent: "LiveryAsset"
    ) -> "LiveryAsset":
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
        return child

    def _download_asset(self) -> "LiveryAsset":
        if self.gdrive_id is None:
            return None
        if self.dcs_codename:
            desination_dir = os_join(
                STAGING_DIR, self.dcs_codename.lower(), self.basename
            )
        else:
            desination_dir = os_join(STAGING_DIR, self.basename)
        self._dl_dir = desination_dir

        try:
            rmtree(self._dl_dir)
        except FileNotFoundError:
            pass

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

    def _update_size(self) -> None:
        self._size_in_bytes = single_dir_size(self._dl_dir)

    def _update_asset_items(self) -> None:
        asset_items = set()
        entrypoint = self._dl_dir
        if self.asset_type == "roughmets":
            entrypoint = os_join(self._dl_dir, PurePath(self._dl_dir).stem)
        for item in os_listdir(entrypoint):
            asset_items.update({item.removeprefix(entrypoint).strip().replace("/", "")})
        self._asset_items = sorted(asset_items)

    @property
    def pilots(self) -> List[str]:
        pilots = []
        for pilot in self.pilot_dirs:
            pilots.append(pilot.removeprefix(self.basename))
        return pilots

    @property
    def pilot_dirs(self) -> List[str]:
        pilot_dirs = []
        if self.asset_type != "livery":
            return []
        else:
            for asset_dir in self._asset_items:
                pilot_dir = PurePath(asset_dir).stem
                if pilot_dir != self.basename:
                    pilot_dirs.append(pilot_dir)
        return pilot_dirs

    def _compress_and_checksum(self) -> Future:
        entrypoint = self._dl_dir
        if self.asset_type == "roughmets":
            entrypoint = os_join(self._dl_dir, PurePath(self._dl_dir).stem)
        archive = os_join(COMPRESSED_DIR, f"{self.basename}.7z")
        future = compress_and_checksum(
            entrypoint,
            CHECKSUMS_DIR,
            self._asset_items,
            archive,
        )
        return future

    @classmethod
    def from_config_item(cls, config_item: Dict[str, Any]) -> "LiveryAsset":
        try:
            basename = config_item["basename"]
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

        return new_instance

    def _remove_all_readme_files(self) -> None:
        for root, dirs, files in os_walk(self._dl_dir):
            for name in files:
                if fnmatch(name.lower(), "readme*.txt"):  # Remove readmes
                    LOGGER.info(f"Removing {os_join(root, name)}")
                    os_remove(os_join(root, name))
                else:
                    pass


class LiveryAssetCollection:
    """
    A collection of LiveryAsset instances.

    This class provides methods to manage a collection of LiveryAsset instances. It allows adding,
    removing, and iterating over the LiveryAsset instances.

    Attributes:
        assets (List[LiveryAsset]): A list of LiveryAsset instances.
    """

    def __init__(self, asset_config_file: str):
        """
        Initializes a new instance of the LiveryAssetCollection class.
        """
        self._top_level_assets = []
        self._from_config_file(asset_config_file=asset_config_file)

    def __iter__(self):
        """
        Returns an iterator for the collection.

        Returns:
            An iterator for the collection.
        """
        return iter(self.all_assets)

    @property
    def top_level_assets(self) -> List["LiveryAsset"]:
        return self._top_level_assets

    @property
    def all_assets(self) -> List["LiveryAsset"]:
        """
        Getter for all_assets.

        Returns:
            List[LiveryAsset]: The list of all assets.
        """
        return self._get_all_assets_from_top_level_assets(self.top_level_assets)

    def _get_all_assets_from_top_level_assets(
        self, assets: List["LiveryAsset"]
    ) -> List["LiveryAsset"]:
        all_assets = []
        for asset in assets:
            all_assets.append(asset)
            if asset._children:
                all_assets += self._get_all_assets_from_top_level_assets(
                    asset._children
                )
        return all_assets

    def print_json(self) -> str:
        return json_dumps([dict(d) for d in self.all_assets], indent=4)

    def get_assets_with_gdrive_id(self):
        return [asset for asset in self.all_assets if asset.gdrive_id is not None]

    def get_roughmets_assets(self) -> List["LiveryAsset"]:
        assets = []
        for asset in self.all_assets:
            if asset.asset_type == "roughmets":
                assets.append(asset)
        return assets

    def get_assets_with_dcs_codename(self) -> List["LiveryAsset"]:
        assets = []
        for asset in self.all_assets:
            if asset.dcs_codename:
                assets.append(asset)
        return assets

    def get_total_size_in_bytes(self) -> int:
        size = 0
        for asset in self.get_assets_with_gdrive_id():
            size += asset._size_in_bytes
        return size

    @property
    def all_pilots(self) -> List[str]:
        pilots = set()
        for asset in self.all_assets:
            pilots.update(asset.pilots)
        return sorted(pilots)

    def _from_config_file(self, asset_config_file: str) -> List["LiveryAsset"]:
        with open(asset_config_file, "r", encoding=getpreferredencoding()) as file:
            assets_config = safe_load(file)
        for asset_config_item in assets_config:
            asset = LiveryAsset.from_config_item(asset_config_item)
            self._top_level_assets.append(asset)

        # Check if we have any duplicate basenames
        basenames = []
        for asset in self.all_assets:
            basenames.append(asset.basename)
        if len(basenames) != len(set(basenames)):
            raise ValueError(
                f"Duplicate basenames found in config file: {asset_config_file}"
            )

        # Wait for downloads to finish, and the do post-download processing
        compress_and_checksum_futures = []
        for asset in self.all_assets:
            if asset._dl_future is not None:
                for nested_future in asset._dl_future.result():
                    nested_future.result()
                asset._remove_all_readme_files()
                asset._update_asset_items()
                asset._update_size()
                compress_and_checksum_futures.append(asset._compress_and_checksum())

        for compress_and_checksum_future in compress_and_checksum_futures:
            compress_and_checksum_future.result()

        return self


def main() -> None:
    pass


if __name__ == "__main__":
    main()
