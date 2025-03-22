import csv
import os
from contextlib import contextmanager
from typing import Generator, List

from paramiko import SSHClient
from rich.tree import Tree

from constants import (
    NOTION_MANAGER,
    PROCESSING_MANAGER,
    MINECRAFT_VERSION,
    MINECRAFT_EXTRACTOR,
    MINECRAFT_DATA,
    OUTPUT_FILE,
    console,
)
from notion.models import (
    ShopInventoryModel,
    ShopOwnerModel,
    ShopCoordsModel,
    ShopSpawnModel,
    ShopNameModel,
    ShopDatabaseProperties,
)
from server_manager import ServerManager


class Main:
    def __init__(self):
        self.console = console
        self.version = MINECRAFT_VERSION
        self.output_file = OUTPUT_FILE
        self.extractor = MINECRAFT_EXTRACTOR
        self.minecraft_data = MINECRAFT_DATA
        self.notion_manager = NOTION_MANAGER
        self.processing_manager = PROCESSING_MANAGER
        self.server_manager = ServerManager()

    def load_data(self):
        return self.minecraft_data.load_data(
            file_path=f"{self.version}.json", extractor=self.extractor
        )

    def query_notion_database(self):
        return self.notion_manager.query_notion_database()

    def process_data(self, _minecraft_data: dict, inventory: list):
        self.processing_manager.add_inventory(inventory=inventory)
        self.processing_manager.add_minecraft_data(minecraft_data=_minecraft_data)
        return self.processing_manager.process_data()

    def normalize_display_name(self, item_id: str) -> str:
        """Convert a Minecraft item ID to a readable display name."""
        # Split by underscores and capitalize each word
        return " ".join(word.capitalize() for word in item_id.split("_"))

    @contextmanager
    def ssh_connection(self) -> Generator[SSHClient, None, None]:
        """
        Context manager for handling SSH connections.

        Yields:
            SSHClient: Connected SSH client that will be automatically closed after use.

        Raises:
            ConnectionError: If connection to the server fails.
        """
        client = None
        try:
            client = self.server_manager.connect_to_server()
            yield client
        finally:
            if client:
                client.close()

    def upload_to_server(self) -> None:
        """
        Upload the processed shop data to the server.

        This function:
        1. Verifies the output file exists
        2. Establishes SSH connection
        3. Uploads the file to the server
        4. Removes the local file after successful upload

        Raises:
            FileNotFoundError: If output file doesn't exist
            ConnectionError: If server connection fails
            Exception: For other upload-related errors
        """
        if not os.path.exists(OUTPUT_FILE):
            raise FileNotFoundError(f"{OUTPUT_FILE} was not found.")

        try:
            with self.ssh_connection() as ssh_client:
                self.server_manager.execute_command("cd /var/www/files", ssh_client)
                self.server_manager.upload_file_to_server(OUTPUT_FILE, f"/var/www/files/{OUTPUT_FILE}", ssh_client)
            os.remove(OUTPUT_FILE)
        except ConnectionError as e:
            console.log(f"Failed to connect to server: {e}")
            raise
        except Exception as e:
            console.log(f"Error during file upload: {e}")
            raise

    def save_to_csv(self, filename: str, data: List[str]) -> None:
        """Save data to a CSV file.

        Args:
            filename: Path to the CSV file
            data: List of strings to be written as a row
        """
        try:
            with open(
                    file=filename, mode="a", encoding="utf8", newline=""
            ) as csvfile_writer:
                writer = csv.writer(
                    csvfile_writer, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
                )
                writer.writerow(data)
        except IOError as e:
            console.print(f"Failed to write to CSV file {filename}: {e}")
            raise


if __name__ == "__main__":
    main = Main()
    minecraft_data = main.load_data()
    notion_database = main.query_notion_database()["results"]
    for row in notion_database:
        shop_database_properties = ShopDatabaseProperties(
            owner_ign=ShopOwnerModel(**row["properties"]["Owner IGN"]),
            coords=ShopCoordsModel(**row["properties"]["Coords (X, Z)"]),
            spawn=ShopSpawnModel(**row["properties"]["Spawn"]),
            shop_name=ShopNameModel(**row["properties"]["Shop Name"]),
        )

        processed_inventory = main.process_data(
            _minecraft_data=minecraft_data,
            inventory=row["properties"]["Inventory"]["rich_text"][0][
                "plain_text"
            ].split(","),
        )
        shop_database_properties.inventory = ShopInventoryModel(processed_inventory)

        shop_tree = Tree(
            f"[bold yellow]{shop_database_properties.shop_name.plain_text}[/] ([yellow]{shop_database_properties.owner_ign.plain_text}[/])"
        )
        location_branch = shop_tree.add(f"[cyan]Location[/]")
        location_branch.add(
            f"[cyan]Coords[/] [green]{shop_database_properties.coords.plain_text}[/]"
        )
        location_branch.add(
            f"[cyan]Spawn[/] [green]{shop_database_properties.spawn.name}[/]"
        )

        items_branch = shop_tree.add(f"[cyan]Found Items[/]")
        for item in sorted(shop_database_properties.inventory.inventory[1]):
            items_branch.add(f"[green]{main.normalize_display_name(item)}[/]")
        items_branch = shop_tree.add(f"[cyan]Missing Items[/]")
        for item in sorted(shop_database_properties.inventory.inventory[0]):
            items_branch.add(f"[red]{main.normalize_display_name(item)}[/]")

        console.print(shop_tree)
        console.save_text("server_manager.log", clear=False)

        if len(shop_database_properties.inventory.inventory[1]) >= 1:
            main.save_to_csv(filename="shops.csv", data=shop_database_properties.__list__())
        else:
            continue

    main.upload_to_server()

    # for item in row["properties"]["Inventory"]["rich_text"][0]["plain_text"].split(
    #     ","
    # ):
    #     print(item.strip())
    # print("\n")
    #
    # print(shop_database_properties.inventory.plain_text)
