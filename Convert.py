import csv

from colorama import Fore

from MinecraftData import MinecraftData
from ShopItem import ShopItem
from groups import (
    unfilterable_items,
    pottery_sherds,
    armor_trims,
    blocksendswiths,
    froglights,
    flowers,
)
from transformers import (
    armor_trim_transformer,
    pottery_sherd_transformer,
    misc_item_transformer,
)

mcitems = []
mcblocks = []
version = "1.21.1"

with open(f"{version}.json", "r", encoding="utf8") as version_file:
    mcdata = MinecraftData().from_json(version_file.read())
    for item in mcdata["item"]:
        if item.startswith("minecraft."):
            mcitems.append(item.replace("minecraft.", ""))
    for block in mcdata["block"]:
        if block.startswith("minecraft."):
            mcblocks.append(block.replace("minecraft.", ""))


with open("shops.csv", newline="", encoding="utf8") as csvfile:
    reader = csv.reader(csvfile, delimiter=",", quotechar='"')
    for row in reader:
        shop = ShopItem(row)
        shop_inv = []
        for item in shop.get_inventory():
            item = item.strip().replace(" ", "_").lower()
            if item.endswith("s"):
                item = item[:-1]
                if item + "s" in blocksendswiths:
                    item = item + "s"

            if item not in unfilterable_items:
                if item in mcblocks or item in mcitems:
                    print(f"{Fore.LIGHTGREEN_EX}{item}{Fore.RESET}")
                    shop_inv.append(item)
                else:
                    if item in armor_trim_transformer:
                        shop_inv.append(armor_trim_transformer[item])
                        print(
                            f"{Fore.LIGHTGREEN_EX}{armor_trim_transformer[item].lower()}{Fore.RESET}"
                        )
                    elif item in pottery_sherd_transformer:
                        shop_inv.append(pottery_sherd_transformer[item])
                        print(
                            f"{Fore.LIGHTGREEN_EX}{pottery_sherd_transformer[item].lower()}{Fore.RESET}"
                        )
                    elif item in misc_item_transformer:
                        shop_inv.append(misc_item_transformer[item])
                        print(
                            f"{Fore.LIGHTGREEN_EX}{misc_item_transformer[item].lower()}{Fore.RESET}"
                        )
                    elif item == "trim":
                        for trim in armor_trims:
                            shop_inv.append(trim)
                            print(
                                f"{Fore.LIGHTGREEN_EX}{trim.lower()}_armor_trim_smithing_template{Fore.RESET}"
                            )
                    elif item in ["pottery_sherd", "sherd"]:
                        for sherd in pottery_sherds:
                            shop_inv.append(sherd.lower() + "_pottery_sherd")
                            print(
                                f"{Fore.LIGHTGREEN_EX}{sherd.lower()}_pottery_sherd{Fore.RESET}"
                            )
                    elif item == "froglight":
                        for froglight in froglights:
                            shop_inv.append(froglight)
                            print(
                                f"{Fore.LIGHTGREEN_EX}{froglight.lower()}_froglight{Fore.RESET}"
                            )
                    elif item == "flower":
                        for flower in flowers:
                            shop_inv.append(flower)
                            print(f"{Fore.LIGHTGREEN_EX}{flower}{Fore.RESET}")
                    else:
                        print(f"{Fore.LIGHTRED_EX}{item}{Fore.RESET}")
                        pass
        if len(shop_inv) >= 1:
            with open(
                "shops_processed.csv", "a", encoding="utf8", newline=""
            ) as csvfile_writer:
                writer = csv.writer(
                    csvfile_writer,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                )
                writer.writerow(
                    [
                        shop.get_shop_name(),
                        ", ".join(shop_inv),
                        shop.get_owner_ign(),
                        shop.get_coords(),
                        shop.get_spawn(),
                    ]
                )
            print(
                shop.get_shop_name(),
                ", ".join(shop_inv),
                shop.get_owner_ign(),
                shop.get_coords(),
                shop.get_spawn(),
            )
