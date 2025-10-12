from enum import Enum

class ItemType(Enum):
    ARMOR_TRIM = "armor_trim"
    POTTERY_SHERD = "pottery_sherd"
    FROGLIGHT = "froglight"
    FLOWER = "flower"
    CONCRETE = "concrete"
    CONCRETE_POWDER = "concrete_powder"
    WOOL = "wool"
    DYE = "dye"
    GLAZED_TERRACOTTA = "glazed_terracotta"
    STAINED_GLASS_PANE = "stained_glass_pane"
    STAINED_GLASS = "stained_glass"
    BANNERS = "banner"
    CORAL = "coral"
    SAPLINGS = "sapling"
    LOGS = "log"
    WOOD = "wood"
    STEWS = "stew"
    SEEDS = "seed"
    MAPART = "map_art"

    def format_item(self, item_name: str) -> str:
        """Format an item name based on its type."""
        return item_name.lower()
