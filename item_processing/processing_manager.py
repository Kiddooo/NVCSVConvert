from typing import Callable, Optional, Dict, Any

from item_processing.item_groups import (
    BLOCKS_ENDS_WITH_S,
    ARMOUR_TRIMS,
    POTTERY_SHERDS,
    FROGLIGHTS,
    CONCRETE,
    CONCRETE_POWDER,
    GLAZED_TERRACOTTA,
    STAINED_GLASS,
    STAINED_GLASS_PANE,
    WOOL,
    DYES,
    FLOWERS,
    UNFILTERABLE_ITEMS,
    BANNERS,
    CORAL,
)
from item_processing.item_type import ItemType
from item_processing.transformer import ItemTransformers


class ProcessingManager:
    def __init__(self):
        self.processing_list = list()
        self.minecraft_data = dict()
        self.item_transformers = ItemTransformers()
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
                _failed.append(item)
                continue

            if self.is_in_minecraft_data(item):
                _processed_inventory.append(item)
            else:
                try:
                    print(item)
                    item_type = ItemType(item)
                    special_item = self.process_special_item(
                        item_type=item_type, items=self.items_map[item_type]
                    )
                    [_processed_inventory.append(item) for item in special_item]
                except ValueError:
                    try:
                        for _transformer, formatter in self.transformers:
                            transformed = self.transform_item(
                                item=item,
                                _transformer=_transformer,
                                formatter=formatter,
                            )
                            if transformed:
                                if self.is_in_minecraft_data(transformed):
                                    print(f"Transformed '{item}' to '{transformed}'")
                                    _processed_inventory.append(transformed)
                                    continue
                                else:
                                    item_type = ItemType(transformed)
                                    special_item = self.process_special_item(
                                        item_type=item_type,
                                        items=self.items_map[item_type],
                                    )
                                    [
                                        _processed_inventory.append(item)
                                        for item in special_item
                                    ]
                    except Exception:
                        _failed.append(item)
                        continue
        return _failed, _processed_inventory
