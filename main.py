import logging
import os

from colorama import Fore

from constants import INPUT_FILE, OUTPUT_FILE
from converters.convert import process_shop_item
from converters.minecraft_data import extract_items_and_blocks
from managers.download_csv import query_notion_database
from managers.file_manager import load_minecraft_data, save_to_csv
from managers.server_manager import connect_to_server, execute_command, upload_file_to_server, update_version_on_server

logging.basicConfig(
    level=logging.INFO,
    format=f"{Fore.WHITE} %(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

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

    try:
        ssh_client = connect_to_server()

        if not os.path.exists(OUTPUT_FILE):
            logging.error(f"Error: {OUTPUT_FILE} does not exist locally.")
            raise FileNotFoundError(f"{OUTPUT_FILE} was not found.")


        execute_command(ssh_client, "cd /var/www/files")
        execute_command(ssh_client, "rm -f /var/www/files/shops.csv")
        upload_file_to_server(ssh_client, "shops.csv", "/var/www/files/shops.csv")

        update_version_on_server(ssh_client)

        ssh_client.close()
        os.remove("shops.csv")
    except Exception as e:
        logging.error(f"Error processing server operations: {str(e)}")

if __name__ == "__main__":
    main()
