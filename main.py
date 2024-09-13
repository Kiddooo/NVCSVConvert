import logging

from constants import INPUT_FILE, OUTPUT_FILE
from convert import process_shop_item
from download_csv import query_notion_database
from file_manager import load_minecraft_data, save_to_csv
from minecraft_data import extract_items_and_blocks


def main():
    mcdata = load_minecraft_data(INPUT_FILE)
    mcitems, mcblocks = extract_items_and_blocks(mcdata)

    results = query_notion_database()["results"]
    for row in results:
        shop, shop_inv = process_shop_item(row, mcitems=mcitems, mcblocks=mcblocks)

        if shop_inv:
            save_to_csv(
                filename=OUTPUT_FILE,
                data=[
                    shop.get_shop_name(),
                    ", ".join(shop_inv),
                    shop.get_owner_ign(),
                    shop.get_coords(),
                    shop.get_spawn(),
                ],
            )

            logging.info(
                f"Processed shop: {shop.get_shop_name()} | Items: {', '.join(shop_inv)} | Owner: {shop.get_owner_ign()}"
            )


if __name__ == "__main__":
    main()
