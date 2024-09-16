import logging
from typing import List, Dict, Any

from colorama import Fore

from ShopItem import ShopItem
from groups import (
    BLOCKS_ENDS_WITH_S,
    UNFILTERABLE_ITEMS,
    ARMOUR_TRIMS,
    POTTERY_SHERDS,
    FROGLIGHTS,
    FLOWERS, CONCRETE, CONCRETE_POWDER, WOOL,
)
from transformers import (
    ARMOUR_TRIM_TRANSFORMER,
    POTTERY_SHERD_TRANSFORMER,
    MISC_ITEM_TRANSFORMER,
)

logging.basicConfig(
    level=logging.INFO,
    format=f"{Fore.WHITE} %(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def process_item(item: str, mcitems: List[str], mcblocks: List[str]) -> str:
    """Process a single item."""
    item = item.strip().replace(" ", "_").lower()
    if item.endswith("s"):
        item = item[:-1]
        if item + "s" in BLOCKS_ENDS_WITH_S:
            item = item + "s"

    if item in UNFILTERABLE_ITEMS:
        return ""

    if item in mcblocks or item in mcitems:
        logging.info(f"{Fore.LIGHTGREEN_EX}{item}{Fore.RESET}")
        return item

    transformers = [
        (
            ARMOUR_TRIM_TRANSFORMER,
            lambda trim: f"{trim.lower()}",
        ),
        (POTTERY_SHERD_TRANSFORMER, lambda sherd: f"{sherd.lower()}"),
        (MISC_ITEM_TRANSFORMER, lambda misc_item: misc_item.lower()),
    ]

    for transformer, formatter in transformers:
        if item in transformer:
            result = formatter(transformer[item])
            logging.info(f"{Fore.LIGHTGREEN_EX}{result}{Fore.RESET}")
            return result

    if item == "armor_trim":
        return ", ".join(
            [f"{trim.lower()}_armor_trim_smithing_template" for trim in ARMOUR_TRIMS]
        )
    elif item in ["pottery_sherd", "sherd"]:
        return ", ".join([f"{sherd.lower()}_pottery_sherd" for sherd in POTTERY_SHERDS])
    elif item == "froglight":
        return ", ".join([f"{froglight.lower()}_froglight" for froglight in FROGLIGHTS])
    elif item == "flower":
        return ", ".join(FLOWERS)
    elif item == "concrete":
        return ", ".join(CONCRETE)
    elif item =="concrete_powder":
        return ", ".join(CONCRETE_POWDER)
    elif item == "wool":
        return ", ".join(WOOL)
    else:
        logging.warning(f"{Fore.LIGHTRED_EX}{item}{Fore.RESET}")
        return ""


def process_shop_item(
    row: Dict[str, Any], mcitems: list, mcblocks: list
) -> tuple[ShopItem, list[str]]:
    """Process a shop item"""
    if not row.get("properties"):
        raise ValueError(f"No 'properties' found in row: {row}")
    shop = ShopItem(shop_row=row["properties"])
    shop_inv = list()

    for item in shop.get_inventory():
        processed_item = process_item(item=item, mcitems=mcitems, mcblocks=mcblocks)
        if processed_item:
            shop_inv.append(processed_item)

    return shop, shop_inv
