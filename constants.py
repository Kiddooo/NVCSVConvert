"""
Application Constants and Configuration
========================================

Central configuration module for the shop inventory processor.
Initializes shared resources and configuration values.
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

# Load environment variables
load_dotenv()

# =============================================================================
# Console and Logging Configuration
# =============================================================================

console = Console(
    log_time=True,
    log_time_format="[%Y-%m-%d %H:%M:%S.%f]",
    record=True,
    soft_wrap=True,
    markup=True,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        RichHandler(console=console, rich_tracebacks=True),
        logging.FileHandler("server_manager.log"),
    ],
)

logger = logging.getLogger(__name__)

# =============================================================================
# Application Configuration
# =============================================================================

OUTPUT_FILE = "shops.csv"
MINECRAFT_VERSION = "1.21.11"

# =============================================================================
# Lazy-loaded Managers (to avoid circular imports)
# =============================================================================

_minecraft_extractor: Optional["MinecraftExtractor"] = None
_minecraft_data: Optional["MinecraftData"] = None
_notion_manager: Optional["NotionManager"] = None
_processing_manager: Optional["ProcessingManager"] = None


def get_minecraft_extractor():
    """Get or create the Minecraft extractor instance."""
    global _minecraft_extractor
    if _minecraft_extractor is None:
        from extract_items_and_blocks import MinecraftExtractor

        _minecraft_extractor = MinecraftExtractor(
            version=MINECRAFT_VERSION,
            output_file_path=f"{MINECRAFT_VERSION}.json",
            toppings="items,blocks",
            console=console,
        )
    return _minecraft_extractor


def get_minecraft_data():
    """Get or create the Minecraft data loader instance."""
    global _minecraft_data
    if _minecraft_data is None:
        from load_minecraft_data import MinecraftData

        _minecraft_data = MinecraftData(version=MINECRAFT_VERSION, console=console)
    return _minecraft_data


def get_notion_manager():
    """Get or create the Notion manager instance."""
    global _notion_manager
    if _notion_manager is None:
        from notion.manager import NotionManager

        _notion_manager = NotionManager(
            notion_api=os.getenv("NOTION_API"),
            notion_secret=os.getenv("NOTION_SECRET"),
            notion_version=os.getenv("NOTION_VERSION"),
            console=console,
        )
    return _notion_manager


def get_processing_manager():
    """Get or create the processing manager instance."""
    global _processing_manager
    if _processing_manager is None:
        from item_processing.processing_manager import ProcessingManager

        _processing_manager = ProcessingManager(console=console)
    return _processing_manager


# Backwards-compatible property-style access
class _LazyConstants:
    @property
    def MINECRAFT_EXTRACTOR(self):
        return get_minecraft_extractor()

    @property
    def MINECRAFT_DATA(self):
        return get_minecraft_data()

    @property
    def NOTION_MANAGER(self):
        return get_notion_manager()

    @property
    def PROCESSING_MANAGER(self):
        return get_processing_manager()


_lazy = _LazyConstants()


# Add this at the end of the file
def __getattr__(name):
    """
    Module-level getattr to handle lazy loading of constants.
    This allows 'from constants import NOTION_MANAGER' to work dynamically.
    """
    if name == "MINECRAFT_EXTRACTOR":
        return get_minecraft_extractor()
    elif name == "MINECRAFT_DATA":
        return get_minecraft_data()
    elif name == "NOTION_MANAGER":
        return get_notion_manager()
    elif name == "PROCESSING_MANAGER":
        return get_processing_manager()

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")