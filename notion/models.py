from dataclasses import dataclass


@dataclass
class ShopInventoryModel:
    inventory: list = None


@dataclass
class ShopOwnerModel:
    id: str = None
    type: str = None
    rich_text: list = None

    @property
    def plain_text(self):
        """Extract plain text content from rich_text if available"""
        if self.rich_text and len(self.rich_text) > 0:
            return self.rich_text[0].get("plain_text", "")
        return ""


@dataclass
class ShopCoordsModel:
    id: str = None
    type: str = None
    rich_text: list = None

    @property
    def plain_text(self):
        """Extract plain text content from rich_text if available"""
        if self.rich_text and len(self.rich_text) > 0:
            return self.rich_text[0].get("plain_text", "")
        return ""


@dataclass
class ShopSpawnModel:
    id: str = None
    type: str = None
    select: dict = None

    @property
    def name(self):
        """Extract plain text content from rich_text if available"""
        if self.select and len(self.select) > 0:
            return self.select.get("name", "")
        return ""


@dataclass
class ShopNameModel:
    id: str = None
    type: str = None
    title: list = None

    @property
    def plain_text(self):
        """Extract plain text content from rich_text if available"""
        if self.title and len(self.title) > 0:
            return self.title[0].get("plain_text", "")
        return ""


@dataclass
class ShopDatabaseProperties:
    inventory: ShopInventoryModel = None
    owner_ign: ShopOwnerModel = None
    coords: ShopCoordsModel = None
    spawn: ShopSpawnModel = None
    shop_name: ShopNameModel = None

    def __list__(self):
        _inventory = ", ".join(
            str(item) if not isinstance(item, list) else ", ".join(str(subitem) for subitem in item) for item in
            self.inventory.inventory[1])
        return [self.shop_name.plain_text, _inventory, self.owner_ign.plain_text, self.coords.plain_text,
                self.spawn.name]
