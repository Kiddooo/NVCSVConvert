"""
Processing Manager Module
=========================

Handles the processing and validation of Minecraft inventory items
against known item databases and registered item groups.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

from item_processing.registry import ItemRegistry, get_registry


@dataclass
class ProcessingResult:
    """
    Results from processing an inventory list.

    Attributes:
        found: Items that were successfully validated
        missing: Items that could not be validated
        transformed: Mapping of original -> transformed item names
    """

    found: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    transformed: dict = field(default_factory=dict)

    def as_tuple(self) -> Tuple[List[str], List[str]]:
        """Return result as (missing, found) tuple for backwards compatibility."""
        return (self.missing, self.found)


class ProcessingManager:
    """
    Manages the processing and validation of Minecraft inventory items.

    This class handles:
    - Normalizing item names (lowercase, underscores)
    - Checking items against Minecraft data
    - Expanding item groups (e.g., "wool" -> all wool colors)
    - Transforming common aliases to canonical names

    Example:
        >>> manager = ProcessingManager()
        >>> manager.add_minecraft_data({"items": {...}, "blocks": {...}})
        >>> manager.add_inventory(["Diamond", "wool", "glowberry"])
        >>> result = manager.process_data()
        >>> print(result.found)  # ['diamond', 'white_wool', 'gray_wool', ..., 'glow_berries']
    """

    # Items that grammatically end with 's' (shouldn't have 's' stripped)
    PLURAL_ITEMS: Set[str] = {
        "acacia_leaves",
        "acacia_planks",
        "acacia_stairs",
        "ancient_debris",
        "andesite_stairs",
        "azalea_leaves",
        "bamboo_planks",
        "bamboo_stairs",
        "beetroot_seeds",
        "birch_leaves",
        "birch_planks",
        "birch_stairs",
        "blackstone_stairs",
        "black_stained_glass",
        "blue_stained_glass",
        "bricks",
        "brick_stairs",
        "brown_stained_glass",
        "cactus",
        "chainmail_boots",
        "chainmail_leggings",
        "cherry_leaves",
        "cherry_planks",
        "cherry_stairs",
        "chiseled_nether_bricks",
        "chiseled_stone_bricks",
        "chiseled_tuff_bricks",
        "cobbled_deepslate_stairs",
        "cobblestone_stairs",
        "cocoa_beans",
        "compass",
        "cracked_deepslate_bricks",
        "cracked_nether_bricks",
        "cracked_polished_blackstone_bricks",
        "cracked_stone_bricks",
        "crimson_fungus",
        "crimson_planks",
        "crimson_roots",
        "crimson_stairs",
        "cut_copper_stairs",
        "cyan_stained_glass",
        "dark_oak_leaves",
        "dark_oak_planks",
        "dark_oak_stairs",
        "dark_prismarine_stairs",
        "deepslate_bricks",
        "deepslate_brick_stairs",
        "diamond_boots",
        "diamond_leggings",
        "diorite_stairs",
        "end_stone_bricks",
        "end_stone_brick_stairs",
        "expoded_cut_copper_stairs",
        "flowering_azalea_leaves",
        "glass",
        "glow_berries",
        "golden_boots",
        "golden_leggings",
        "granite_stairs",
        "gray_stained_glass",
        "green_stained_glass",
        "hanging_roots",
        "iron_bars",
        "iron_boots",
        "iron_leggings",
        "jungle_leaves",
        "jungle_planks",
        "jungle_stairs",
        "leather_boots",
        "leather_leggings",
        "light_blue_stained_glass",
        "light_gray_stained_glass",
        "lime_stained_glass",
        "magenta_stained_glass",
        "mangrove_leaves",
        "mangrove_planks",
        "mangrove_stairs",
        "mangrove_roots",
        "melon_seeds",
        "mossy_stone_bricks",
        "mossy_stone_brick_stairs",
        "mud_bricks",
        "mud_brick_stairs",
        "music_disc_blocks",
        "netherite_boots",
        "netherite_leggings",
        "nether_bricks",
        "nether_brick_stairs",
        "nether_sprouts",
        "oak_leaves",
        "oak_planks",
        "oak_stairs",
        "orange_stained_glass",
        "oxidized_cut_copper_stairs",
        "pink_petals",
        "pink_stained_glass",
        "polished_andesite_stairs",
        "polished_blackstone_bricks",
        "polished_blackstone_brick_stairs",
        "polished_blackstone_stairs",
        "polished_deepslate_stairs",
        "polished_diorite_stairs",
        "polished_granite_stairs",
        "polished_tuff_stairs",
        "prismarine_bricks",
        "prismarine_brick_stairs",
        "prismarine_crystals",
        "prismarine_stairs",
        "pumpkin_seeds",
        "purple_stained_glass",
        "purpur_stairs",
        "quartz_bricks",
        "quartz_stairs",
        "recovery_compass",
        "red_nether_bricks",
        "red_nether_brick_stairs",
        "red_sandstone_stairs",
        "red_stained_glass",
        "sandstone_stairs",
        "seagrass",
        "shears",
        "short_grass",
        "smooth_quartz_stairs",
        "smooth_red_sandstone_stairs",
        "smooth_sandstone_stairs",
        "spruce_leaves",
        "spruce_planks",
        "spruce_stairs",
        "spyglass",
        "stone_bricks",
        "stone_brick_stairs",
        "stone_stairs",
        "sweet_berries",
        "tall_grass",
        "tinted_glass",
        "torchflower_seeds",
        "tuff_bricks",
        "tuff_brick_stairs",
        "tuff_stairs",
        "twisting_vines",
        "warped_fungus",
        "warped_planks",
        "warped_roots",
        "warped_stairs",
        "waxed_cut_copper_stairs",
        "waxed_exposed_cut_copper_stairs",
        "waxed_oxidized_cut_copper_stairs",
        "waxed_weathered_cut_copper_stairs",
        "weathered_cut_copper_stairs",
        "weeping_vines",
        "wheat_seeds",
        "white_stained_glass",
        "yellow_stained_glass",
        "pale_oak_leaves",
        "pale_moss",
        "pale_hanging_moss",
        "hanging_roots",
        "hanging_signs",
        "short_dry_grass",
        "tall_dry_grass",
        "wildflowers",
        "light_blue_harness",
        "dry_grass",
    }

    def __init__(self, registry: Optional[ItemRegistry] = None, console=None):
        """
        Initialize the processing manager.

        Args:
            registry: Optional custom ItemRegistry (uses global if not provided)
            console: Optional Rich console for logging
        """
        self.registry = registry or get_registry()
        self.console = console
        self._inventory: List[str] = []
        self._minecraft_data: dict = {}

    def add_inventory(self, inventory: List[str]) -> None:
        """Set the inventory list to process."""
        self._inventory = inventory

    def add_minecraft_data(self, minecraft_data: dict) -> None:
        """Set the Minecraft data dictionary for validation."""
        self._minecraft_data = minecraft_data

    def is_valid_item(self, item: str) -> bool:
        """Check if an item exists in Minecraft data."""
        return item in self._minecraft_data.get(
            "blocks", {}
        ) or item in self._minecraft_data.get("items", {})

    def normalize_item(self, item: str) -> str:
        """
        Normalize an item name to standard format.

        - Strips whitespace
        - Converts to lowercase
        - Replaces spaces with underscores
        - Handles plural forms
        """
        normalized = item.strip().replace(" ", "_").lower()

        # Handle plurals carefully
        if normalized.endswith("s") and normalized not in self.PLURAL_ITEMS:
            singular = normalized[:-1]
            # Only use singular if it's a valid item
            if self.is_valid_item(singular):
                return singular

        return normalized

    def process_item(self, item: str) -> Tuple[List[str], bool]:
        """
        Process a single item.

        Returns:
            Tuple of (list of resolved items, success boolean)
        """
        normalized = self.normalize_item(item)
        # print(f"DEBUG: '{item}' -> normalized='{normalized}'")
        # print(f"DEBUG: transform('{normalized}') = {self.registry.transform(normalized)}")
        # print(f"DEBUG: transform('{normalized[:-1]}') = {self.registry.transform(normalized[:-1])}")

        # Skip unfilterable items
        if self.registry.is_unfilterable(normalized):
            return ([], True)  # Success but no items added

        # Check if it triggers a group expansion
        group = self.registry.get_group_by_trigger(normalized)
        if group:
            return (list(group.items), True)

        # Check if it's a valid item directly
        if self.is_valid_item(normalized):
            return ([normalized], True)

        # Try transformation
        transformed = self.registry.transform(normalized)
        if transformed:
            if self.is_valid_item(transformed):
                self._log(f"Transformed '{item}' -> '{transformed}'")
                return ([transformed], True)

            # Transformed item might be a group trigger
            group = self.registry.get_group_by_trigger(transformed)
            if group:
                return (list(group.items), True)

        # Item not found
        return ([], False)

    def process_data(self) -> Tuple[List[str], List[str]]:
        """
        Process all items in the inventory.

        Returns:
            Tuple of (missing_items, found_items)
        """
        result = ProcessingResult()

        for item in self._inventory:
            resolved_items, success = self.process_item(item)

            if success:
                result.found.extend(resolved_items)
            else:
                normalized = self.normalize_item(item)
                result.missing.append(normalized)
                self._log(
                    f"[yellow]Unrecognized item: {item}[/yellow]", level="warning"
                )

        return result.as_tuple()

    def _log(self, message: str, level: str = "info") -> None:
        """Log a message if console is available."""
        if self.console:
            if level == "warning":
                self.console.print(f"[yellow]{message}[/yellow]")
            else:
                self.console.print(message)
