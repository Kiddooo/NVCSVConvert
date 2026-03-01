"""
Shop Inventory Processor
========================

Main application for processing Minecraft shop inventories from Notion
and exporting validated data to CSV for server upload.

Usage:
    python main.py
"""

import csv
import os
import traceback
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator, List, Optional

from paramiko import SSHClient
from rich.console import Console
from rich.tree import Tree

from constants import (
    MINECRAFT_DATA,
    MINECRAFT_EXTRACTOR,
    MINECRAFT_VERSION,
    NOTION_MANAGER,
    OUTPUT_FILE,
    PROCESSING_MANAGER,
    console,
)
from notion.models import ShopDatabaseProperties, ShopInventoryModel
from server_manager import ServerManager


@dataclass
class AppConfig:
    """Application configuration."""

    version: str = MINECRAFT_VERSION
    output_file: str = OUTPUT_FILE
    min_items_for_export: int = 1


class ShopProcessor:
    """
    Main application class for processing shop inventories.

    Coordinates data loading, processing, display, and export.
    """

    def __init__(
        self, config: Optional[AppConfig] = None, console: Optional[Console] = None
    ):
        """
        Initialize the shop processor.

        Args:
            config: Application configuration (uses defaults if not provided)
            console: Rich console for output (uses global if not provided)
        """
        self.config = config or AppConfig()
        self.console = console or globals().get("console")
        self.minecraft_data = MINECRAFT_DATA
        self.extractor = MINECRAFT_EXTRACTOR
        self.notion_manager = NOTION_MANAGER
        self.processing_manager = PROCESSING_MANAGER
        self.server_manager = ServerManager()

        self._minecraft_data_cache: Optional[dict] = None

    def load_minecraft_data(self) -> dict:
        """
        Load Minecraft item/block data.

        Returns:
            Dictionary with 'items' and 'blocks' keys
        """
        if self._minecraft_data_cache is None:
            self._minecraft_data_cache = self.minecraft_data.load_data(
                file_path=f"{self.config.version}.json", extractor=self.extractor
            )
        return self._minecraft_data_cache

    def fetch_notion_data(self) -> List[dict]:
        """
        Fetch shop data from Notion database.

        Returns:
            List of shop entries from Notion
        """
        response = self.notion_manager.query_notion_database()
        return response.get("results", []) if response else []

    def process_shop_inventory(self, raw_inventory: List[str]) -> ShopInventoryModel:
        """
        Process a raw inventory list.

        Args:
            raw_inventory: List of item names from Notion

        Returns:
            Processed inventory model with found/missing items
        """
        minecraft_data = self.load_minecraft_data()
        self.processing_manager.add_minecraft_data(minecraft_data)
        self.processing_manager.add_inventory(raw_inventory)

        result = self.processing_manager.process_data()
        return ShopInventoryModel(result)

    def display_shop_tree(self, shop: ShopDatabaseProperties) -> None:
        """
        Display a shop's information as a Rich tree.

        Args:
            shop: Shop properties to display
        """
        # Build tree structure
        tree = Tree(
            f"[bold yellow]{shop.shop_name.plain_text}[/] "
            f"([yellow]{shop.owner_ign.plain_text}[/])"
        )

        # Location branch
        location = tree.add("[cyan]Location[/]")
        location.add(f"[cyan]Coords:[/] [green]{shop.coords.plain_text}[/]")
        location.add(f"[cyan]Spawn:[/] [green]{shop.spawn.name}[/]")

        # Found items
        if shop.inventory.found:
            found_branch = tree.add(
                f"[cyan]Found Items ({len(shop.inventory.found)})[/]"
            )
            for item in sorted(shop.inventory.found):
                display_name = self.normalize_display_name(item)
                found_branch.add(f"[green]{display_name}[/]")

        # Missing items
        if shop.inventory.missing:
            missing_branch = tree.add(
                f"[cyan]Missing Items ({len(shop.inventory.missing)})[/]"
            )
            for item in sorted(shop.inventory.missing):
                display_name = self.normalize_display_name(item)
                missing_branch.add(f"[red]{display_name}[/]")

        self.console.print(tree)

    @staticmethod
    def normalize_display_name(item_id: str) -> str:
        """
        Convert a Minecraft item ID to a readable display name.

        Args:
            item_id: Minecraft item ID (e.g., "diamond_sword")

        Returns:
            Human-readable name (e.g., "Diamond Sword")
        """
        return " ".join(word.capitalize() for word in item_id.split("_"))

    def save_to_csv(self, shop: ShopDatabaseProperties) -> None:
        """
        Append a shop's data to the output CSV file.

        Args:
            shop: Shop properties to save
        """
        try:
            with open(
                self.config.output_file, mode="a", encoding="utf-8", newline=""
            ) as csvfile:
                writer = csv.writer(
                    csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
                )
                writer.writerow(shop.to_csv_row())
        except IOError as e:
            self.console.print(f"[red]Failed to write CSV: {e}[/red]")
            raise

    @contextmanager
    def ssh_connection(self) -> Generator[SSHClient, None, None]:
        """Context manager for SSH connections."""
        client = None
        try:
            client = self.server_manager.connect_to_server()
            yield client
        finally:
            if client:
                client.close()

    def upload_to_server(self) -> None:
        """Upload the processed CSV to the server."""
        if not os.path.exists(self.config.output_file):
            raise FileNotFoundError(f"{self.config.output_file} not found")

        try:
            with self.ssh_connection() as ssh_client:
                remote_path = f"/var/www/files/{self.config.output_file}"
                self.server_manager.upload_file_to_server(
                    self.config.output_file, remote_path, ssh_client
                )
            os.remove(self.config.output_file)
            self.console.print("[green]Successfully uploaded to server[/green]")
        except Exception as e:
            self.console.print(f"[red]Upload failed: {e}[/red]")
            raise

    def run(self) -> None:
        """
        Main execution loop.

        Fetches data from Notion, processes each shop, and exports results.
        """
        # Remove existing output file
        if os.path.exists(self.config.output_file):
            os.remove(self.config.output_file)

        # Fetch and process shops
        notion_rows = self.fetch_notion_data()
        processed_count = 0

        for row in notion_rows:
            try:
                # Parse shop properties
                shop = ShopDatabaseProperties.from_notion_row(row)

                # Get and process inventory
                raw_inventory = shop.get_raw_inventory(row)
                if not raw_inventory:
                    self.console.print(
                        f"[yellow]No inventory for {shop.shop_name.plain_text}[/yellow]"
                    )
                    continue

                shop.inventory = self.process_shop_inventory(raw_inventory)

                # Display results
                self.display_shop_tree(shop)

                # Export if enough items found
                if len(shop.inventory.found) >= self.config.min_items_for_export:
                    self.save_to_csv(shop)
                    processed_count += 1

            except Exception as e:
                self.console.print(f"[red]Error processing shop: {e}[/red]")
                self.console.print(traceback.format_exc())

        # Upload results
        if processed_count > 0:
            self.console.print(f"\n[bold]Processed {processed_count} shops[/bold]")
            self.upload_to_server()
        else:
            self.console.print("[yellow]No shops to upload[/yellow]")

        # Save log
        self.console.save_text("server_manager.log", clear=False)


def main():
    """Entry point for the application."""
    processor = ShopProcessor()
    processor.run()


if __name__ == "__main__":
    main()
