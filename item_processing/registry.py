"""
Item Registry Module
====================

Centralized registration system for Minecraft item groups and transformations.
Adding new items/groups only requires changes in this single file.

Usage:
    >>> registry = ItemRegistry()
    >>> registry.register_group("my_items", ["item1", "item2"], pattern="{}_suffix")
    >>> registry.register_transformer("short_name", "full_item_name")
"""

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set


@dataclass
class ItemGroup:
    """
    Represents a group of related Minecraft items.

    Attributes:
        name: Unique identifier for this group (e.g., "wool", "concrete")
        items: Set of item IDs belonging to this group
        trigger_keywords: Keywords that trigger expansion of this group
        pattern: Optional pattern for generating item names (e.g., "{color}_wool")
    """

    name: str
    items: FrozenSet[str]
    trigger_keywords: FrozenSet[str] = field(default_factory=frozenset)
    description: str = ""

    def __contains__(self, item: str) -> bool:
        return item in self.items

    def __iter__(self):
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)


@dataclass
class ItemTransformation:
    """
    Represents a transformation from one item name to another.

    Attributes:
        source: The input item name (what users might type)
        target: The canonical Minecraft item ID
        category: Optional category for organization (e.g., "armor_trim", "sherd")
    """

    source: str
    target: str
    category: str = "misc"


class ItemRegistry:
    """
    Central registry for all item groups and transformations.

    This class provides a single point of configuration for:
    - Item groups (wool colors, concrete, etc.)
    - Name transformations (common aliases -> canonical names)
    - Unfilterable items (items to skip during processing)

    Example:
        >>> registry = ItemRegistry()
        >>>
        >>> # Register a new group
        >>> registry.register_group(
        ...     name="my_custom_blocks",
        ...     items=["block_a", "block_b"],
        ...     triggers=["custom_block", "my_blocks"]
        ... )
        >>>
        >>> # Register a transformation
        >>> registry.register_transformer("short_name", "long_canonical_name")
    """

    # Base colors used for color-variant blocks
    COLORS: List[str] = [
        "white",
        "light_gray",
        "gray",
        "black",
        "brown",
        "red",
        "orange",
        "yellow",
        "lime",
        "green",
        "cyan",
        "light_blue",
        "blue",
        "purple",
        "magenta",
        "pink",
    ]

    def __init__(self):
        self._groups: Dict[str, ItemGroup] = {}
        self._transformations: Dict[str, str] = {}
        self._unfilterable: Set[str] = set()
        self._trigger_to_group: Dict[str, str] = {}

        # Initialize with default registrations
        self._register_defaults()

    def register_group(
        self,
        name: str,
        items: List[str],
        triggers: Optional[List[str]] = None,
        description: str = "",
    ) -> None:
        """
        Register a new item group.

        Args:
            name: Unique identifier for the group
            items: List of item IDs in this group
            triggers: Keywords that expand to all items in this group
            description: Human-readable description of the group

        Raises:
            ValueError: If group name already exists
        """
        if name in self._groups:
            raise ValueError(f"Group '{name}' already registered")

        trigger_set = frozenset(triggers) if triggers else frozenset([name])

        group = ItemGroup(
            name=name,
            items=frozenset(items),
            trigger_keywords=trigger_set,
            description=description,
        )

        self._groups[name] = group

        # Map triggers to group name for quick lookup
        for trigger in group.trigger_keywords:
            self._trigger_to_group[trigger] = name

    def register_color_variant_group(
        self,
        name: str,
        pattern: str,
        triggers: Optional[List[str]] = None,
        description: str = "",
    ) -> None:
        """
        Register a group of color-variant items.

        Args:
            name: Group name (e.g., "wool", "concrete")
            pattern: Format string with {color} placeholder (e.g., "{color}_wool")
            triggers: Keywords that expand to all variants
            description: Human-readable description
        """
        items = [pattern.format(color=color) for color in self.COLORS]
        self.register_group(name, items, triggers, description)

    def register_transformer(
        self, source: str, target: str, category: str = "misc"
    ) -> None:
        """
        Register a name transformation.

        Args:
            source: The alias/shorthand name
            target: The canonical Minecraft item ID
            category: Optional category for organization
        """
        self._transformations[source.lower()] = target.lower()

    def register_transformers(
        self, mappings: Dict[str, str], category: str = "misc"
    ) -> None:
        """Register multiple transformations at once."""
        for source, target in mappings.items():
            self.register_transformer(source, target, category)

    def register_unfilterable(self, items: List[str]) -> None:
        """Register items that should be skipped during processing."""
        self._unfilterable.update(item.lower() for item in items)

    def get_group(self, name: str) -> Optional[ItemGroup]:
        """Get a group by name."""
        return self._groups.get(name)

    def get_group_by_trigger(self, trigger: str) -> Optional[ItemGroup]:
        """Get a group by one of its trigger keywords."""
        group_name = self._trigger_to_group.get(trigger.lower())
        return self._groups.get(group_name) if group_name else None

    def transform(self, item: str) -> Optional[str]:
        """Transform an item name to its canonical form."""
        return self._transformations.get(item.lower())

    def is_unfilterable(self, item: str) -> bool:
        """Check if an item should be skipped."""
        return item.lower() in self._unfilterable

    def get_all_groups(self) -> Dict[str, ItemGroup]:
        """Get all registered groups."""
        return self._groups.copy()

    def _register_defaults(self) -> None:
        """Register all default item groups and transformations."""
        self._register_default_groups()
        self._register_default_transformers()
        self._register_default_unfilterable()

    def _register_default_groups(self) -> None:
        """Register default item groups."""

        # Color variant groups
        color_variants = [
            ("wool", "{color}_wool", ["wool", "wools"]),
            ("dye", "{color}_dye", ["dye", "dyes"]),
            ("concrete", "{color}_concrete", ["concrete"]),
            ("concrete_powder", "{color}_concrete_powder", ["concrete_powder"]),
            ("glazed_terracotta", "{color}_glazed_terracotta", ["glazed_terracotta"]),
            ("stained_glass", "{color}_stained_glass", ["stained_glass"]),
            (
                "stained_glass_pane",
                "{color}_stained_glass_pane",
                ["stained_glass_pane"],
            ),
            ("banner", "{color}_banner", ["banner", "banners"]),
        ]

        for name, pattern, triggers in color_variants:
            self.register_color_variant_group(name, pattern, triggers)

        self.register_group(
            name="terracotta",
            items=[f"{color}_terracotta" for color in self.COLORS] + ["terracotta"],
            triggers=["terracotta"],
        )
        # Armor trims
        trim_patterns = [
            "ward",
            "spire",
            "coast",
            "eye",
            "dune",
            "wild",
            "rib",
            "tide",
            "sentry",
            "vex",
            "snout",
            "wayfinder",
            "shaper",
            "silence",
            "raiser",
            "host",
            "flow",
            "bolt",
        ]
        self.register_group(
            "armor_trim",
            [f"{t}_armor_trim_smithing_template" for t in trim_patterns],
            ["armor_trim", "trim", "trims"],
            "Smithing templates for armor trims",
        )

        # Pottery sherds
        sherd_patterns = [
            "angler",
            "archer",
            "arms_up",
            "blade",
            "brewer",
            "burn",
            "danger",
            "explorer",
            "friend",
            "heart",
            "heartbreak",
            "howl",
            "miner",
            "mourner",
            "plenty",
            "prize",
            "sheaf",
            "shelter",
            "skull",
            "snort",
            "flow",
            "guster",
            "scrape",
        ]
        self.register_group(
            "pottery_sherd",
            [f"{s}_pottery_sherd" for s in sherd_patterns],
            ["pottery_sherd", "sherd", "sherds", "pottery_shards", "pottery_sherds"],
            "Decorative pottery sherds",
        )

        # Froglights
        self.register_group(
            "froglight",
            ["ochre_froglight", "pearlescent_froglight", "verdant_froglight"],
            ["froglight", "froglights"],
            "Light blocks produced by frogs",
        )

        # Flowers
        self.register_group(
            "flower",
            [
                "allium",
                "azure_bluet",
                "blue_orchid",
                "cornflower",
                "dandelion",
                "closed_eyeblossom",
                "open_eyeblossom",
                "lily_of_the_valley",
                "oxeye_daisy",
                "poppy",
                "orange_tulip",
                "pink_tulip",
                "red_tulip",
                "white_tulip",
                # 2 Tall
                "lilac",
                "peony",
                "rose_bush",
                "sunflower",
                # Other
                "pink_petals",
                "cactus_flower",
                "firefly_bush",
                "wildflowers",
            ],
            ["flower", "flowers"],
            "Decorative flowers",
        )

        # Coral
        coral_types = ["brain", "tube", "horn", "fire", "bubble"]
        coral_variants = ["_coral_block", "_coral_fan", "_coral"]
        self.register_group(
            "coral",
            [f"{t}{v}" for t in coral_types for v in coral_variants],
            ["coral", "corals"],
            "Coral blocks and fans",
        )

        # Wood types
        wood_types = [
            "oak",
            "spruce",
            "birch",
            "jungle",
            "acacia",
            "dark_oak",
            "mangrove",
            "cherry",
            "pale_oak",
        ]

        self.register_group(
            "sapling", [f"{w}_sapling" for w in wood_types], ["sapling", "saplings"]
        )

        self.register_group(
            "log",
            [f"{w}_log" for w in wood_types] + ["crimson_stem", "warped_stem"],
            ["log", "logs"],
        )

        self.register_group(
            "wood",
            [f"{w}_wood" for w in wood_types] + ["crimson_hyphae", "warped_hyphae"],
            ["wood"],
        )

        self.register_group(
            "pressure_plate",
            [f"{w}_pressure_plate" for w in wood_types]
            + ["crimson_pressure_plate", "warped_pressure_plate"],
            ["pressure_plate", "pressure_plates", "wood_pressure_plates"],
        )

        # Food/Stews
        self.register_group(
            "stew",
            ["beetroot_soup", "mushroom_stew", "rabbit_stew", "suspicious_stew"],
            ["stew", "stews", "soup", "soups"],
        )

        # Seeds
        self.register_group(
            "seed",
            ["wheat_seeds", "melon_seeds", "pumpkin_seeds", "beetroot_seeds"],
            ["seed", "seeds"],
        )

        # Map art (special category)
        self.register_group("map_art", ["map_art"], ["map_art", "mapart"])

        # Custom Player Heads / Plushies

        self.register_group(
            "heads", ["heads"], ["heads", "custom_heads", "custom_plushies"]
        )

        # Copper variants (custom additions)
        copper_states = ["", "exposed_", "weathered_", "oxidized_"]
        waxed_states = [
            "waxed_",
            "waxed_exposed_",
            "waxed_weathered_",
            "waxed_oxidized_",
        ]
        all_copper_states = copper_states + waxed_states

        self.register_group(
            "copper_golem_statue",
            [f"{s}copper_golem_statue" for s in all_copper_states],
            ["copper_golem_statue", "copper_golem"],
        )

        self.register_group(
            "copper_chest",
            [f"{s}copper_chest" for s in all_copper_states],
            ["copper_chest"],
        )

        self.register_group(
            "copper_lantern",
            [f"{s}copper_lantern" for s in all_copper_states],
            ["copper_lantern"],
        )

        horse_armor = ["leather", "iron", "golden", "diamond", "copper"]
        self.register_group(
            "horse_armor",
            [f"{s}_horse_armor" for s in horse_armor],
            ["horse_armor", "horse_armor_(all_types)"],
        )

    def _register_default_transformers(self) -> None:
        """Register default name transformations."""

        # Armor trim shortcuts
        trim_transforms = {
            f"{t}_trim": f"{t}_armor_trim_smithing_template"
            for t in [
                "ward",
                "spire",
                "coast",
                "eye",
                "dune",
                "wild",
                "rib",
                "tide",
                "sentry",
                "vex",
                "snout",
                "wayfinder",
                "shaper",
                "silence",
                "raiser",
                "host",
                "flow",
                "bolt",
            ]
        }
        self.register_transformers(trim_transforms, "armor_trim")

        # Pottery sherd shortcuts
        sherd_transforms = {
            f"{s}_sherd": f"{s}_pottery_sherd"
            for s in [
                "angler",
                "archer",
                "arms_up",
                "blade",
                "brewer",
                "burn",
                "danger",
                "explorer",
                "friend",
                "heart",
                "heartbreak",
                "howl",
                "miner",
                "mourner",
                "plenty",
                "prize",
                "sheaf",
                "shelter",
                "skull",
                "snort",
                "flow",
                "guster",
                "scrape",
            ]
        }
        self.register_transformers(sherd_transforms, "pottery_sherds")

        # Miscellaneous common aliases
        misc_transforms = {
            "crimson_log": "crimson_stem",
            "warped_log": "warped_stem",
            "block_of_quartz": "quartz_block",
            "pot": "decorated_pot",
            "cherry_blossoms_leave": "cherry_leaves",
            "glowberry": "glow_berries",
            "glowberrie": "glow_berries",
            "Glowberries": "glow_berries",
            "flowering_azalea_bush": "flowering_azalea",
            "azalea_bush": "azalea",
            "block_of_resin": "resin_block",
            "horse_armor": "leather_horse_armor",
            "nametag": "name_tag",
            "totem": "totem_of_undying",
            "totems": "totem_of_undying",
            "netherite_upgrade": "netherite_upgrade_smithing_template",
            "turtle_shell": "turtle_helmet",
            "glow_ink": "glow_ink_sac",
            "nether_quartz": "quartz",
            "stonebrick": "stone_brick",
            "blazerod": "blaze_rod",
            "mud_brick": "mud_bricks",
            "rocket": "firework_rocket",
            "clay_block": "clay",
            "gold": "gold_ingot",
            "redstone_repeater": "repeater",
            "redstone_comparator": "comparator",
            "redstone_dust": "redstone",
            "red_stone": "redstone",
            "milk": "milk_bucket",
            "sugarcane": "sugar_cane",
            "hay_bale": "hay_block",
            "raw_cod": "cod",
            "cobble_deepslate": "cobbled_deepslate",
            "muddy_root": "muddy_mangrove_roots",
            "pale_moss": "pale_moss_block",
            "warped_sprout": "nether_sprouts",
            "warped_root": "warped_roots",
            "twisting_vine": "twisting_vines",
            "weeping_vine": "weeping_vines",
            "crimson_root": "crimson_roots",
            "pale_oak": "pale_oak_log",
            "hanging_root": "hanging_roots",
            "carrot_stick": "carrot_on_a_stick",
            "dog_armor": "wolf_armor",
            "fungus_stick": "warped_fungus_on_a_stick",
            "spider_web": "cobweb",
            "raw_beef": "beef",
            "raw_chicken": "chicken",
            "raw_porkchop": "porkchop",
            "raw_mutton": "mutton",
            "totems_of_undyijng": "totem_of_undying",
            "moss": "moss_block",
            "bookcase": "bookshelf",
            "dried_ghast.": "dried_ghast",
            "jukeboxes": "jukebox",
            "mosaic_blocks": "bamboo_mosaic",
            "mosaic_slabs": "bamboo_mosaic_slab",
            "mosaic_stairs": "bamboo_mosaic_stairs",
            "soul_torches": "soul_torch",
            "dark_oak": "dark_oak_log",
            "netherite": "netherite_ingot",
            "xp_bottles": "experience_bottle",
            "exp_bottle": "experience_bottle",
            "bottle_o_enchanting": "experience_bottle",
            "lapi": "lapis_lazuli",
            "snow_bucket": "powder_snow_bucket",
            "deepslate_tile": "deepslate_tiles",
            "bamboo_wood": "bamboo_block",
            "prismarine_brick": "prismarine_bricks",
            "bonemeal": "bone_meal",
            "block_of_copper": "copper_block",
            "block_of_gold": "gold_block",
            "block_of_iron": "iron_block",
            "slimeball": "slime_ball",
            "lapis_lazuli_ore": "lapis_ore",
            "waxed_block_of_copper": "waxed_copper_block",
            "chicken_egg": "egg",
            "eye_of_ender": "ender_eye",
            "amethyst": "amethyst_shard",
            "coast_armor_trim": "coast_armor_trim_smithing_template",
            "silence_armor_trim": "silence_armor_trim_smithing_template",
            "gun_powder": "gunpowder",
            "steak": "cooked_beef",
            "waxed_oxidized_copper_blocks": "waxed_oxidized_copper",
            "waxed_weathered_copper_blocks": "waxed_weathered_copper",
            "scutes": "armadillo_scutes",
            "torches": "torch",
            "pufferfish_(bucket)": "pufferfish_bucket",
            "tropical_fish_(bucket)": "tropical_fish_bucket",
            "axolotls": "axolotl_bucket",
            "spider_webs": "cobweb",
            "chiseled_stone_brick": "chiseled_stone_bricks",
            "cherry_blossom_leaves": "cherry_leaves",
            "daylight_sensor": "daylight_detector",
            "and_netherite_upgrade": "netherite_upgrade_smithing_template",
        }
        self.register_transformers(misc_transforms, "misc")

    def _register_default_unfilterable(self) -> None:
        """Register items that should be skipped during processing."""
        unfilterable = [
            "Teleportation Services",
            "Swift Sneak",
            "Regeneration Potion",
            "Music Disc",
            "Exp",
            "Enchanted Bows",
            "Guardian Heads",
            "Villager Trading Hall",
            "Card Delivery",
            "Elytra Box",
        ]
        self.register_unfilterable(unfilterable)


# Global registry instance
_registry: Optional[ItemRegistry] = None


def get_registry() -> ItemRegistry:
    """Get the global item registry instance."""
    global _registry
    if _registry is None:
        _registry = ItemRegistry()
    return _registry
