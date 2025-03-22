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

    def format_item(self, item_name: str) -> str:
        """Format an item name based on its type."""
        # formatters = {
        #     ItemType.ARMOR_TRIM: lambda name: f"{name.lower()}_armor_trim_smithing_template",
        #     ItemType.POTTERY_SHERD: lambda name: f"{name.lower()}_pottery_sherd",
        #     ItemType.FROGLIGHT: lambda name: f"{name.lower()}_froglight",
        #     ItemType.CONCRETE: lambda name: f"{name.lower()}_concrete",
        #     ItemType.CONCRETE_POWDER: lambda name: f"{name.lower()}_concrete_powder",
        #     ItemType.WOOL: lambda name: f"{name.lower()}_wool",
        #     ItemType.DYE: lambda name: f"{name.lower()}_dye",
        #     ItemType.GLAZED_TERRACOTTA: lambda name: f"{name.lower()}_glazed_terracotta",
        #     ItemType.STAINED_GLASS_PANE: lambda name: f"{name.lower()}_stained_glass_pane",
        #     ItemType.STAINED_GLASS: lambda name: f"{name.lower()}_stained_glass",
        # }
        #
        # # Use the formatter if available, otherwise just return the lowercase name
        # formatter = formatters.get(self, lambda name: name.lower())
        # return formatter(item_name)
        return item_name.lower()
