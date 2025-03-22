import logging
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

from extract_items_and_blocks import MinecraftExtractor
from item_processing.processing_manager import ProcessingManager
from load_minecraft_data import MinecraftData
from notion.manager import NotionManager

load_dotenv()

# Console logger
# Initialize rich console
console = Console(
    log_time=True,
    log_time_format="[%Y-%m-%d %H:%M:%S.%f]",
    record=True,
    soft_wrap=True,
    markup=True,
)

# Configure logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        RichHandler(
            console=console,
            rich_tracebacks=True,
        ),
        logging.FileHandler("server_manager.log"),  # Keep file logging for records
    ],
)

OUTPUT_FILE = "shops.csv"

MINECRAFT_VERSION = "1.21.4"
MINECRAFT_EXTRACTOR = MinecraftExtractor(
    version=MINECRAFT_VERSION,
    output_file_path=f"{MINECRAFT_VERSION}.json",
    toppings="items,blocks",
    console=console,
)
MINECRAFT_DATA = MinecraftData(version=MINECRAFT_VERSION, console=console)
NOTION_MANAGER = NotionManager(
    os.getenv("NOTION_API"),
    os.getenv("NOTION_SECRET"),
    os.getenv("NOTION_VERSION"),
    console=console,
)
PROCESSING_MANAGER = ProcessingManager()
