from typing import Dict


class ItemTransformers:
    """
    Provides mapping dictionaries for transforming various Minecraft item names
    between different formats (e.g., simplified to canonical names).

    This class contains standardized mappings for:
    - Armor trims
    - Pottery sherds
    - Miscellaneous items

    Usage:
        >>> transformers = ItemTransformers()
        >>> transformers.transform_item("ward_trim")
        # 'ward_armor_trim_smithing_template'
    """

    ARMOUR_TRIM_TRANSFORMER: Dict[str, str] = {
        "ward_trim": "ward_armor_trim_smithing_template",
        "spire_trim": "spire_armor_trim_smithing_template",
        "coast_trim": "coast_armor_trim_smithing_template",
        "eye_trim": "eye_armor_trim_smithing_template",
        "dune_trim": "dune_armor_trim_smithing_template",
        "wild_trim": "wild_armor_trim_smithing_template",
        "rib_trim": "rib_armor_trim_smithing_template",
        "tide_trim": "tide_armor_trim_smithing_template",
        "sentry_trim": "sentry_armor_trim_smithing_template",
        "vex_trim": "vex_armor_trim_smithing_template",
        "snout_trim": "snout_armor_trim_smithing_template",
        "wayfinder_trim": "wayfinder_armor_trim_smithing_template",
        "sharper_trim": "sharper_armor_trim_smithing_template",
        "silence_trim": "silence_armor_trim_smithing_template",
        "raiser_trim": "raiser_armor_trim_smithing_template",
        "host_trim": "host_armor_trim_smithing_template",
        "flow_trim": "flow_armor_trim_smithing_template",
        "bolt_trim": "bolt_armor_trim_smithing_template",
    }

    POTTERY_SHERD_TRANSFORMER: Dict[str, str] = {
        "angler_sherd": "angler_pottery_sherd",
        "archer_sherd": "archer_pottery_sherd",
        "arms_up_sherd": "arms_up_pottery_sherd",
        "blade_sherd": "blade_pottery_sherd",
        "brewer_sherd": "brewer_pottery_sherd",
        "burn_sherd": "burn_pottery_sherd",
        "danger_sherd": "danger_pottery_sherd",
        "explorer_sherd": "explorer_pottery_sherd",
        "friend_sherd": "friend_pottery_sherd",
        "heart_sherd": "heart_pottery_sherd",
        "heartbreak_sherd": "heartbreak_pottery_sherd",
        "howl_sherd": "howl_pottery_sherd",
        "miner_sherd": "miner_pottery_sherd",
        "mourner_sherd": "mourner_pottery_sherd",
        "plenty_sherd": "plenty_pottery_sherd",
        "prize_sherd": "prize_pottery_sherd",
        "sheaf_sherd": "sheaf_pottery_sherd",
        "shelter_sherd": "shelter_pottery_sherd",
        "skull_sherd": "skull_pottery_sherd",
        "snort_sherd": "snort_pottery_sherd",
        "flow_sherd": "flow_pottery_sherd",
        "guster_sherd": "guster_pottery_sherd",
        "scrape_sherd": "scrape_pottery_sherd",
    }

    MISC_ITEM_TRANSFORMER: Dict[str, str] = {
        "sherds": "pottery_sherd",
        "sherd": "pottery_sherd",
        "crimson_log": "crimson_stem",
        "warped_log": "warped_stem",
        "block_of_quartz": "quartz_block",
        "pot": "decorated_pot",
        "cherry_blossoms_leave": "cherry_leaves",
        "glowberry": "glow_berries",
        "flowering_azalea_bush": "flowering_azalea",
        "azalea_bush": "azalea",
        "horse_armor": "leather_horse_armor",
        "nametag": "name_tag",
        "totem": "totem_of_undying",
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
        "block_of_resin": "resin_block",
        "glowberrie": "glow_berries",
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
        "mos": "moss_block",
        "bookcase": "bookshelf",
        "dried_ghast.": "dried_ghast",
        "jukeboxe": "jukebox",
        "mosaic_block": "bamboo_mosaic",
        "mosaic_slab": "bamboo_mosaic_slab",
        "mosaic_stair": "bamboo_mosaic_stairs",
        "soul_torche": "soul_torch",
        "torche": "torch",
        "dark_oak": "dark_oak_log",
        "netherite": "netherite_ingot",
        "xp_bottle": "experience_bottle",
        "lapi": "lapis_lazuli",
        "red_stone": "redstone",
        "Bottle_O’_Enchanting": "experience_bottle",
        "snow_bucket": "powder_snow_bucket",
        "deepslate_tile": "deepslate_tiles",
        "bamboo_wood": "bamboo_block",
        "enchanted_bow": "bow",
        "prismarine_brick": "prismarine_bricks",
    }
