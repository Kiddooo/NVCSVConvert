import traceback
from typing import Callable, Optional, Dict, Any

from item_processing.item_groups import (
    BLOCKS_ENDS_WITH_S,
    ARMOUR_TRIMS,
    LOGS,
    MAPART,
    POTTERY_SHERDS,
    FROGLIGHTS,
    CONCRETE,
    CONCRETE_POWDER,
    GLAZED_TERRACOTTA,
    SAPLINGS,
    STAINED_GLASS,
    STAINED_GLASS_PANE,
    STEWS,
    WOOD,
    WOOL,
    DYES,
    FLOWERS,
    UNFILTERABLE_ITEMS,
    BANNERS,
    CORAL,
    SEEDS
)
from item_processing.item_type import ItemType
from item_processing.transformer import ItemTransformers


class ProcessingManager:
    def __init__(self):
        from constants import console

        self.processing_list = list()
        self.minecraft_data = dict()
        self.item_transformers = ItemTransformers()
        self.console = console
        self.transformers = [
            (self.item_transformers.ARMOUR_TRIM_TRANSFORMER, lambda trim: trim.lower()),
            (
                self.item_transformers.POTTERY_SHERD_TRANSFORMER,
                lambda sherd: sherd.lower(),
            ),
            (self.item_transformers.MISC_ITEM_TRANSFORMER, lambda misc: misc.lower()),
        ]
        self.items_map = {
            ItemType.ARMOR_TRIM: ARMOUR_TRIMS,
            ItemType.POTTERY_SHERD: POTTERY_SHERDS,
            ItemType.FROGLIGHT: FROGLIGHTS,
            ItemType.FLOWER: FLOWERS,
            ItemType.CONCRETE: CONCRETE,
            ItemType.CONCRETE_POWDER: CONCRETE_POWDER,
            ItemType.WOOL: WOOL,
            ItemType.DYE: DYES,
            ItemType.GLAZED_TERRACOTTA: GLAZED_TERRACOTTA,
            ItemType.STAINED_GLASS: STAINED_GLASS,
            ItemType.STAINED_GLASS_PANE: STAINED_GLASS_PANE,
            ItemType.BANNERS: BANNERS,
            ItemType.CORAL: CORAL,
            ItemType.SAPLINGS: SAPLINGS,
            ItemType.LOGS: LOGS,
            ItemType.WOOD: WOOD,
            ItemType.STEWS: STEWS,
            ItemType.SEEDS: SEEDS,
            ItemType.MAPART: MAPART
        }

    def add_inventory(self, inventory: list) -> None:
        self.processing_list = inventory

    def add_minecraft_data(self, minecraft_data: dict) -> None:
        self.minecraft_data = minecraft_data

    def is_in_minecraft_data(self, item: str) -> bool:
        return (
            item in self.minecraft_data["blocks"]
            or item in self.minecraft_data["items"]
        )

    def is_unfilterable(self, item: str) -> bool:
        return item in UNFILTERABLE_ITEMS

    def process_special_item(
        self, item_type: ItemType, items: frozenset[str]
    ) -> list[str] | None:
        if hasattr(item_type, "format_item"):
            return [item_type.format_item(item) for item in items]
        else:
            return None

    def transform_item(
        self, item: str, _transformer: Dict[str, str], formatter: Callable
    ) -> Optional[str]:
        result = _transformer.get(item)
        return formatter(result) if result else None

    def process_data(self) -> tuple[list[Any], list[Any]]:
        _processed_inventory = list()
        _failed = list()
        try:
            for item in self.processing_list:
                item = item.strip().replace(" ", "_").lower()
                if item.endswith("s"):
                    singular_item = item[:-1]
                    item = (
                        singular_item + "s"
                        if singular_item + "s" in BLOCKS_ENDS_WITH_S
                        else singular_item
                    )

                if self.is_unfilterable(item):
                    continue

                if self.is_in_minecraft_data(item):
                    _processed_inventory.append(item)
                else:
                    try:
                        item_type = ItemType(item)
                        special_item = self.process_special_item(
                            item_type=item_type, items=self.items_map[item_type]
                        )
                        if special_item:
                            [_processed_inventory.append(item) for item in special_item]
                    except ValueError:
                        transformed_successfully = False
                        for _transformer, formatter in self.transformers:
                            transformed = self.transform_item(
                                item=item,
                                _transformer=_transformer,
                                formatter=formatter,
                            )
                            if transformed:
                                if self.is_in_minecraft_data(transformed):
                                    self.console.print(
                                        f"Transformed '{item}' to '{transformed}'"
                                    )
                                    _processed_inventory.append(transformed)
                                    transformed_successfully = True
                                    break
                                else:
                                    try:
                                        item_type = ItemType(transformed)
                                        special_item = self.process_special_item(
                                            item_type=item_type,
                                            items=self.items_map[item_type],
                                        )
                                        if special_item:
                                            [
                                                _processed_inventory.append(
                                                    special_item_instance
                                                )
                                                for special_item_instance in special_item
                                            ]
                                        transformed_successfully = True
                                        break
                                    except ValueError:
                                        continue

                        if not transformed_successfully:
                            _failed.append(item)
            return _failed, _processed_inventory
        except Exception:
            print(traceback.format_exc())
            return _failed, _processed_inventory
