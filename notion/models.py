"""
Notion Data Models
==================

Pydantic-style dataclasses for Notion database properties.
Provides type-safe access to shop data from Notion.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class NotionPropertyBase(ABC):
    """Base class for Notion property models with common extraction logic."""

    @abstractmethod
    def get_display_value(self) -> str:
        """Extract the human-readable value from this property."""
        pass


@dataclass
class RichTextProperty(NotionPropertyBase):
    """
    Base class for Notion properties that contain rich_text.

    Handles extraction of plain text from Notion's rich_text format.
    """

    id: str = ""
    type: str = ""
    rich_text: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def plain_text(self) -> str:
        """Extract plain text content from rich_text."""
        if self.rich_text and len(self.rich_text) > 0:
            return self.rich_text[0].get("plain_text", "")
        return ""

    def get_display_value(self) -> str:
        return self.plain_text


@dataclass
class TitleProperty(NotionPropertyBase):
    """Notion title property (used for page names)."""

    id: str = ""
    type: str = ""
    title: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def plain_text(self) -> str:
        """Extract plain text from title."""
        if self.title and len(self.title) > 0:
            return self.title[0].get("plain_text", "")
        return ""

    def get_display_value(self) -> str:
        return self.plain_text


@dataclass
class SelectProperty(NotionPropertyBase):
    """Notion select property."""

    id: str = ""
    type: str = ""
    select: Optional[Dict[str, Any]] = None

    @property
    def name(self) -> str:
        """Extract the selected option name."""
        if self.select:
            return self.select.get("name", "")
        return ""

    def get_display_value(self) -> str:
        return self.name


# Type aliases for clarity
@dataclass
class ShopOwnerModel(RichTextProperty):
    """Shop owner's in-game name."""

    pass


@dataclass
class ShopCoordsModel(RichTextProperty):
    """Shop coordinates (X, Z)."""

    pass


@dataclass
class ShopNameModel(TitleProperty):
    """Shop name/title."""

    pass


@dataclass
class ShopSpawnModel(SelectProperty):
    """Spawn location for the shop."""

    pass


@dataclass
class ShopInventoryModel:
    """
    Processed shop inventory.

    Attributes:
        items: Tuple of (missing_items, found_items)
    """

    items: tuple = field(default_factory=lambda: ([], []))

    def __init__(self, inventory_tuple: tuple = None):
        if inventory_tuple:
            self.items = inventory_tuple
        else:
            self.items = ([], [])

    @property
    def found(self) -> List[str]:
        """Items successfully found in Minecraft data."""
        return self.items[1] if len(self.items) > 1 else []

    @property
    def missing(self) -> List[str]:
        """Items that couldn't be validated."""
        return self.items[0] if len(self.items) > 0 else []

    # Backwards compatibility
    @property
    def inventory(self):
        return self.items


@dataclass
class ShopDatabaseProperties:
    """
    Complete shop database entry.

    Contains all properties for a shop from the Notion database.
    """

    shop_name: ShopNameModel = None
    owner_ign: ShopOwnerModel = None
    coords: ShopCoordsModel = None
    spawn: ShopSpawnModel = None
    inventory: ShopInventoryModel = None

    def to_csv_row(self) -> List[str]:
        """Convert to a list suitable for CSV export."""
        inventory_str = ", ".join(self.inventory.found) if self.inventory else ""

        return [
            self.shop_name.plain_text if self.shop_name else "",
            inventory_str,
            self.owner_ign.plain_text if self.owner_ign else "",
            self.coords.plain_text if self.coords else "",
            self.spawn.name if self.spawn else "",
        ]

    # Backwards compatibility
    def __list__(self) -> List[str]:
        return self.to_csv_row()

    @classmethod
    def from_notion_row(cls, row: Dict[str, Any]) -> "ShopDatabaseProperties":
        """
        Create a ShopDatabaseProperties from a Notion database row.

        Args:
            row: A single result from Notion's query database API

        Returns:
            Populated ShopDatabaseProperties instance
        """
        props = row.get("properties", {})

        return cls(
            shop_name=ShopNameModel(**props.get("Shop Name", {})),
            owner_ign=ShopOwnerModel(**props.get("Owner IGN", {})),
            coords=ShopCoordsModel(**props.get("Coords (X, Z)", {})),
            spawn=ShopSpawnModel(**props.get("Spawn", {})),
        )

    def get_raw_inventory(self, row: Dict[str, Any]) -> List[str]:
        """Extract raw inventory list from a Notion row."""
        try:
            props = row.get("properties", {})
            inventory_prop = props.get("Inventory", {})
            rich_text = inventory_prop.get("rich_text", [])

            if rich_text:
                text = rich_text[0].get("plain_text", "")
                return [item.strip() for item in text.split(",") if item.strip()]
        except (KeyError, IndexError):
            pass

        return []
