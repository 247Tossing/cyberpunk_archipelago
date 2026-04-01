"""
Cyberpunk 2077 Item Definitions

This file defines all items that can be found in the Archipelago multiworld.

Items are collectibles that get randomly distributed across all players' games.
Each item has a unique ID, a classification that determines its behavior, and
optional metadata for game-specific logic.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from BaseClasses import Item, ItemClassification

# Base ID for Cyberpunk 2077 location/item IDs
# Must match the base_id in __init__.py
BASE_ID = 2077000


class Cyberpunk2077Item(Item):
    """
    An item instance for Cyberpunk 2077.

    Extends the base Archipelago Item class to add game-specific identification.
    Each instance represents one item in the multiworld item pool.
    """
    game: str = "Cyberpunk 2077"  # Must match the game name in __init__.py


@dataclass
class ItemData:
    """
    Data class defining properties of an item type.

    Uses Python's @dataclass decorator to automatically generate common methods
    (__init__, __repr__, __eq__, etc.) from the field definitions.

    Attributes:
        name: Human-readable item name (e.g., "Mantis Blades")
        code: Unique numeric ID for network communication (e.g., 77_2077_001)
              Set to None for "event" items that don't appear in the item pool
        classification: How the item behaves in the randomizer (can be combined)
                       ItemClassification is an IntFlag that supports bitwise operations.
                       Multiple flags can be combined using the | (OR) operator:
                       - progression | useful: An especially useful progression item
                       - progression | skip_balancing: Progression that won't be moved by balancing
        dlc_only: Whether this item requires Phantom Liberty DLC (default: False)
                 Items marked dlc_only=True are excluded from the item pool when
                 include_phantom_liberty_dlc option is disabled
        category: Item category for grouping and filtering (default: ItemCategory.MISC)
                 Used to group items by type (quickhacks, tokens, currency, etc.)
                 Makes it easier to filter items in options and generation logic
    """
    name: str
    code: Optional[int]  # None for event items
    classification: ItemClassification
    dlc_only: bool = False  # True for Phantom Liberty DLC items
    category: str = "misc"  # Item category (use ItemCategory constants)
    quantity: int = 1


# ===== ITEM CATEGORY TYPES =====
# These constants define item categories for grouping and filtering
# Used with the ItemData.category field to explicitly categorize items

class ItemCategory:
    """
    Item category constants for explicit categorization.

    Categories allow grouping items independently of their classification
    (progression/useful/filler), making it easier to filter items by type
    in options and generation logic.
    """
    EVENT = "event"                      # Event items (code=None, never in item pool)
    DISTRICT_TOKEN = "district_token"    # Main district access tokens
    SUBDISTRICT_TOKEN = "subdistrict_token"  # Subdistrict access tokens
    QUICKHACK = "quickhack"              # Progressive quickhacks
    CURRENCY = "currency"                # Eddies (in-game money)
    CONSUMABLE = "consumable"            # Food, drinks, RAM boosters
    CYBERWARE = "cyberware"              # Cyberware upgrades (future)
    WEAPON = "weapon"                    # Unique weapons (future)
    MISC = "misc"                        # Uncategorized/miscellaneous items
    TRAP = "trap"
    WEAPON_PASS = "weapon_pass"


# ===== ITEM CLASSIFICATION TYPES =====
# ItemClassification is an IntFlag enum that determines how the randomizer treats items
# Multiple classifications can be combined using the bitwise OR operator (|)
#
# Basic Classifications:
#
# ItemClassification.progression:
#   - Required to complete the game
#   - Examples: Main quest items, critical cyberware, key unlocks
#   - The randomizer ensures these are always accessible
#
# ItemClassification.useful:
#   - Helpful but not strictly required
#   - Examples: Powerful weapons, stat boosts, quality-of-life improvements
#   - Makes the game easier but isn't mandatory for completion
#
# ItemClassification.filler:
#   - Used to fill extra locations
#   - Examples: Eddies, crafting materials, consumables
#   - No impact on game completion
#   - IMPORTANT: filler = 0b00000 (value is 0!)
#   - To check if item is filler, check for ABSENCE of progression/useful/trap:
#     if not (classification & (progression | useful | trap))
#
# ItemClassification.trap:
#   - Negative effects (optional, for challenge/fun)
#   - Examples: Debuffs, wanted level increases, temporary handicaps
#   - Can make the game harder
#
# Combined Classifications (using | operator):
#
# progression | useful:
#   - An especially useful progression item
#   - Example: A key that also provides significant combat advantage
#
# progression | skip_balancing:
#   - Progression item that won't be moved to earlier spheres by balancing
#   - Example: Currency or tokens (avoid flooding early game)
#
# progression | deprioritized:
#   - Progression item that shouldn't be placed on priority locations
#   - Example: Minor progression items or abundant progression tokens
#
# To check if an item has a classification flag, use bitwise AND (&):
#   if item.classification & ItemClassification.progression:
#       # This item has the progression flag (possibly among others)
#


# ===== ITEM TABLE =====
# This dictionary maps item names to their definitions
# The item table is the single source of truth for all items in the game

# Item codes are OFFSETS that get added to base_id (2077000) when creating items
# Codes stored here: 4000-9999 (offsets)
# Actual Archipelago IDs: 2081000-2086999 (base_id + offset)
# This range is separate from locations to avoid conflicts

# Offset ranges by category:
# 4000-4999: Progression items (keys, access items, story progression)
# 5000-5999: Useful items (quickhacks, cyberware, weapons)
# 6000-6999: Filler items (common items, money, consumables)
# 7000-7999: Trap items (debuffs, penalties)
# 8000-9999: Reserved for future content

item_table: Dict[str, ItemData] = {

    # ===================================
    # District Access Items
    # ===================================

    "Westbrook Access Token" : ItemData(
        name = "ap_dat_westbrookAccessToken",
        code = 4001,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.DISTRICT_TOKEN
    ),

    "City Center Access Token" : ItemData(
        name = "ap_dat_cityCenterAccessToken",
        code = 4002,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.DISTRICT_TOKEN
    ),

    "Heywood Access Token" : ItemData(
        name = "ap_dat_heywoodAccessToken",
        code = 4003,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.DISTRICT_TOKEN
    ),

    "Santo Domingo Access Token" : ItemData(
        name = "ap_dat_santoDomingoAccessToken",
        code = 4004,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.DISTRICT_TOKEN
    ),

    "Pacifica Access Token" : ItemData(
        name = "ap_dat_pacificaAccessToken",
        code = 4005,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.DISTRICT_TOKEN
    ),

    "Dogtown Acccess Token" : ItemData(
        name = "ap_dat_dogtownAccessToken",
        code = 4006,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.DISTRICT_TOKEN
    ),

    "Badlands Access Token" : ItemData(
        name = "ap_dat_badlandsAccessToken",
        code = 4007,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.DISTRICT_TOKEN
    ),

    # ===== Subdistrict Access Tokens =====
    "Westbrook Japantown Access Token" : ItemData(
        name = "ap_dat_westbrookJapantownAccessToken",
        code = 4008,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    # ===== Westbrook Subdistricts =====
    "Westbrook Charter Hill Access Token" : ItemData(
        name = "ap_dat_westbrookCharterHillAccessToken",
        code = 4009,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Westbrook North Oak Access Token" : ItemData(
        name = "ap_dat_westbrookNorthOakAccessToken",
        code = 4010,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    # ===== City Center Subdistricts =====
    "City Center Corpo Plaza Access Token" : ItemData(
        name = "ap_dat_cityCenterCorpoPlazaAccessToken",
        code = 4011,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "City Center Downtown Access Token" : ItemData(
        name = "ap_dat_cityCenterDowntownAccessToken",
        code = 4012,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    # ===== Heywood Subdistricts =====
    "Heywood Wellsprings Access Token" : ItemData(
        name = "ap_dat_heywoodWellspringsAccessToken",
        code = 4013,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Heywood The Glen Access Token" : ItemData(
        name = "ap_dat_heywoodTheGlenAccessToken",
        code = 4014,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Heywood Vista Del Rey Access Token" : ItemData(
        name = "ap_dat_heywoodVistaDelReyAccessToken",
        code = 4015,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    # ===== Santo Domingo Subdistricts =====
    "Santo Domingo Arroyo Access Token" : ItemData(
        name = "ap_dat_santoDomingoArroyoAccessToken",
        code = 4016,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Santo Domingo Rancho Coronado Access Token" : ItemData(
        name = "ap_dat_santoDomingoRanchoCoronadoAccessToken",
        code = 4017,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    # ===== Pacifica Subdistricts =====
    "Pacifica Coastview Access Token" : ItemData(
        name = "ap_dat_pacificaCoastviewAccessToken",
        code = 4018,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Pacifica West Wind Estate Access Token" : ItemData(
        name = "ap_dat_pacificaWestWindEstateAccessToken",
        code = 4019,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    # ===== Badlands Subdistricts =====
    "Badlands Biotechnica Flats Access Token" : ItemData(
        name = "ap_dat_badlandsBiotechnicaFlatsAccessToken",
        code = 4020,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Badlands Jackson Plains Access Token" : ItemData(
        name = "ap_dat_badlandsJacksonPlainsAccessToken",
        code = 4021,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Badlands Laguna Bend Access Token" : ItemData(
        name = "ap_dat_badlandsLagunaBendAccessToken",
        code = 4022,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Badlands Red Peaks Access Token" : ItemData(
        name = "ap_dat_badlandsRedPeaksAccessToken",
        code = 4023,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Badlands Rocky Ridge Access Token" : ItemData(
        name = "ap_dat_badlandsRockyRidgeAccessToken",
        code = 4024,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Badlands Sierra Sonora Access Token" : ItemData(
        name = "ap_dat_badlandsSierraSonoraAccessToken",
        code = 4025,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Badlands SoCal Badlands Access Token" : ItemData(
        name = "ap_dat_badlandsSoCalBadlandsAccessToken",
        code = 4026,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Badlands Yucca Access Token" : ItemData(
        name = "ap_dat_badlandsYuccaAccessToken",
        code = 4027,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    "Badlands Morro Rock Access Token" : ItemData(
        name = "ap_dat_badlandsMorroRockAccessToken",
        code = 4028,
        classification = ItemClassification.progression | ItemClassification.skip_balancing,
        category = ItemCategory.SUBDISTRICT_TOKEN
    ),

    # ===== USEFUL ITEMS =====
    # These items are helpful but not required
    "5000 Eddies": ItemData(
        name="ap_ed_Items.money_5000",
        code=5000,
        classification=ItemClassification.useful,
        category=ItemCategory.CURRENCY
    ),
    "Progressive Overheat Quickhack": ItemData(
        name="ap_prog_overheat",
        code=5001,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity= 5
    ),
    "Progressive Short Circuit Quickhack": ItemData(
        name="ap_prog_shortCircuit",
        code=5002,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity= 5
    ),
    "Progressive Contagion Quickhack": ItemData(
        name="ap_prog_contagion",
        code=5003,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity= 5
    ),
    "Progressive Synapse Burnout Quickhack": ItemData(
        name="ap_prog_synapseBurnout",
        code=5004,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity= 5
    ),
    "Progressive Cripple Movement Quickhack": ItemData(
        name="ap_prog_crippleMovement",
        code=5005,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity= 5
    ),
    "Progressive Weapon Glitch Quickhack": ItemData(
        name="ap_prog_weaponGlitch",
        code=5006,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity= 5
    ),
    "Progressive Ping Quickhack": ItemData(
        name="ap_prog_ping",
        code=5007,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity= 4
    ),
    "Progressive Bait Quickhack": ItemData(
        name="ap_prog_bait",
        code=5008,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity= 6
    ),
    "Progressive Request Backup Quickhack": ItemData(
        name="ap_prog_requestBackup",
        code=5009,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity=5
    ),
    "Progressive Memory Wipe Quickhack": ItemData(
        name="ap_prog_memoryWipe",
        code=5010,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity=4
    ),
    "Progressive Sonic Shock Quickhack": ItemData(
        name="ap_prog_sonicShock",
        code=5011,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity=5
    ),
    "Progressive Cyberpsychosis Quickhack": ItemData(
        name="ap_prog_madness",
        code=5012,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity=3
    ),
    "Progressive Suicide Quickhack": ItemData(
        name="ap_prog_suicide",
        code=5013,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity=3
    ),
    "Progressive System Collapse Quickhack": ItemData(
        name="ap_prog_systemCollapse",
        code=5014,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity=3
    ),
    "Progressive Detonate Grenade Quickhack": ItemData(
        name="ap_prog_grenadeExplode",
        code=5015,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity=3
    ),
    "Progressive Reboot Optics Quickhack": ItemData(
        name="ap_prog_rebootOptics",
        code=5017,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity=5
    ),
    "Progressive Cyberware Malfunction Quickhack": ItemData(
        name="ap_prog_cyberwareMalfunction",
        code=5018,
        classification=ItemClassification.useful,
        category=ItemCategory.QUICKHACK,
        quantity=5
    ),

    # ===== Weapon Passes =====
    # Only used when Restrict Weapons is enabled
    "Pistol Weapon Pass": ItemData(
        name="ap_wep_pistolPass",
        code=5019,
        classification=ItemClassification.useful,
        category=ItemCategory.WEAPON_PASS
    ),

    "Shotgun Weapon Pass" : ItemData(
        name="ap_wep_shotgunPass",
        code=5020,
        classification=ItemClassification.useful,
        category=ItemCategory.WEAPON_PASS
    ),

    "Sniper Weapon Pass" : ItemData(
        name="ap_wep_sniperPass",
        code=5021,
        classification=ItemClassification.useful,
        category=ItemCategory.WEAPON_PASS
    ),

    "LMG Weapon Pass" : ItemData(
        name="ap_wep_lmgPass",
        code=5022,
        classification=ItemClassification.useful,
        category=ItemCategory.WEAPON_PASS
    ),

    "Rifle Weapon Pass" : ItemData(
        name="ap_wep_riflePass",
        code=5023,
        classification=ItemClassification.useful,
        category=ItemCategory.WEAPON_PASS
    ),

    "Melee Weapon Pass" : ItemData(
        name="ap_wep_meleePass",
        code=5024,
        classification=ItemClassification.useful,
        category=ItemCategory.WEAPON_PASS
    ),

    # ===== FILLER ITEMS =====
    # These items are used to fill extra locations

    "500 Eddies": ItemData(
        name="ap_ed_Items.money_500",  # In-game currency
        code=6000,
        classification=ItemClassification.filler,
        category=ItemCategory.CURRENCY
    ),

    "1000 Eddies" : ItemData(
        name = "ap_ed_Items.money_1000",
        code = 6001,
        classification = ItemClassification.filler,
        category = ItemCategory.CURRENCY
    ),

    "2500 Eddies" : ItemData(
        name = "ap_ed_Items.money_2500",
        code = 6002,
        classification = ItemClassification.filler,
        category = ItemCategory.CURRENCY
    ),

    "Ram Nugs" : ItemData(
        name = "ap_inv_Items.Blackmarket_MemoryBooster",
        code = 6003,
        classification = ItemClassification.filler,
        category = ItemCategory.CONSUMABLE
    ),

    "RAM Jolt" : ItemData(
        name = "ap_inv_Items.MemoryBooster",
        code = 6004,
        classification = ItemClassification.filler,
        category = ItemCategory.CONSUMABLE
    ),

    "Burrito XXXL" : ItemData(
        name = "ap_inv_Items.MediumQualityFood4",
        code = 6005,
        classification = ItemClassification.filler,
        category = ItemCategory.CONSUMABLE
    ),



    # ===== TRAP ITEMS =====
    # These items have negative effects
    # Remove if you don't want traps in your world

    # "Smasher Trap": ItemData(
    #     name="ap_tp_smasher",
    #     code=7000,
    #     classification=ItemClassification.trap
    # ),

    "NCPD False Cyberpsycho Report": ItemData(
        name = "ap_trp_mostWanted",
        code = 7000,
        classification = ItemClassification.trap,
        category = ItemCategory.TRAP,
        quantity= 5
    ),

    "Netrunner Virus": ItemData(
        name = "ap_trp_randomDebuff",
        code = 7001,
        classification = ItemClassification.trap,
        category = ItemCategory.TRAP,
        quantity= 5
    ),

    "Direct Alcohol Injection": ItemData(
        name = "ap_trp_drunk",
        code = 7002,
        classification = ItemClassification.trap,
        category = ItemCategory.TRAP,
        quantity= 5
    ),

    # ===== EVENT ITEMS =====
    # Event items don't have codes (code=None) and are used for internal logic
    # They're placed at event locations and never go into the item pool
    # Used to represent game state or milestones

    #====================================
    # Victory Event
    #====================================

    "Victory": ItemData(
        name="Victory",
        code=None,
        classification=ItemClassification.progression,
        category=ItemCategory.EVENT
    ),
}


# ===== DERIVED MAPPINGS =====
# These are automatically generated from item_table
# Don't modify these manually - they're computed based on item_table

# Dictionary mapping item names to their IDs
# Example: {"Mantis Blades": 77_2077_001, "Kerenzikov": 77_2077_002, ...}
# Filters out event items (code=None) to get only real items
item_name_to_id: Dict[str, int] = {
    name: BASE_ID + data.code
    for name, data in item_table.items()
    if data.code is not None  # Exclude event items
}

# Dictionary mapping item IDs to their display names (reverse lookup)
# Example: {4000: "Dex's Limo Keys", 5000: "Myers' Plane Ticket", ...}
# Allows bidirectional lookup - searching by ID to get the display name
# Used for Archipelago UI and logging
# Stores full Archipelago IDs (BASE_ID + offset) as keys for server database
item_id_to_name: Dict[int, str] = {
    BASE_ID + data.code: name
    for name, data in item_table.items()
    if data.code is not None  # Exclude event items
}

# Dictionary mapping Archipelago IDs to internal game IDs
# Example: {2081000: "ap_qk_dex_keys", 2085000: "ap_qk_myers_ticket", ...}
# Used by the client to translate item IDs to game-recognizable identifiers
# RedScript needs these internal IDs to give items to the player
# Stores full Archipelago IDs (BASE_ID + offset) as keys for server communication
item_id_to_game_id: Dict[int, str] = {
    BASE_ID + data.code: data.name  # Maps to ItemData.name field (internal game ID)
    for name, data in item_table.items()
    if data.code is not None  # Exclude event items
}


# ===== ITEM NAME GROUPS =====
# Auto-generated groups based on item classification and prefixes
# Players can use these in YAML to reference multiple items at once

def _build_item_name_groups() -> Dict[str, List[str]]:
    """
    Automatically build item name groups from item_table.

    Groups are generated based on:
    - Item classification (Progression, Useful, Filler, Trap)
    - Item category (from ItemData.category field)

    Returns:
        Dictionary mapping group names to lists of item display names
    """
    groups: Dict[str, List[str]] = {}

    # Group by classification
    progression_items = []
    useful_items = []
    filler_items = []
    trap_items = []

    # Group by category
    district_tokens = []
    subdistrict_tokens = []
    quickhacks = []
    currency = []
    consumables = []
    cyberware_items = []
    weapon_items = []
    misc_items = []

    for display_name, item_data in item_table.items():
        if item_data.code is None:
            continue  # Skip event items

        # Group by classification
        # Use bitwise AND (&) to check for flags since items can have multiple classifications
        # Note: Changed from if/elif to independent ifs so items can belong to multiple groups
        if item_data.classification & ItemClassification.progression:
            progression_items.append(display_name)
        if item_data.classification & ItemClassification.useful:
            useful_items.append(display_name)
        # NOTE: ItemClassification.filler = 0, so check for ABSENCE of other type flags
        if not (item_data.classification & (ItemClassification.progression |
                                            ItemClassification.useful |
                                            ItemClassification.trap)):
            filler_items.append(display_name)
        if item_data.classification & ItemClassification.trap:
            trap_items.append(display_name)

        # Group by category
        if item_data.category == ItemCategory.DISTRICT_TOKEN:
            district_tokens.append(display_name)
        elif item_data.category == ItemCategory.SUBDISTRICT_TOKEN:
            subdistrict_tokens.append(display_name)
        elif item_data.category == ItemCategory.QUICKHACK:
            quickhacks.append(display_name)
        elif item_data.category == ItemCategory.CURRENCY:
            currency.append(display_name)
        elif item_data.category == ItemCategory.CONSUMABLE:
            consumables.append(display_name)
        elif item_data.category == ItemCategory.CYBERWARE:
            cyberware_items.append(display_name)
        elif item_data.category == ItemCategory.WEAPON:
            weapon_items.append(display_name)
        elif item_data.category == ItemCategory.MISC:
            misc_items.append(display_name)

    # Add classification groups only if they have items
    if progression_items:
        groups["Progression Items"] = progression_items
    if useful_items:
        groups["Useful Items"] = useful_items
    if filler_items:
        groups["Filler Items"] = filler_items
    if trap_items:
        groups["Trap Items"] = trap_items

    # Add category groups only if they have items
    if district_tokens:
        groups["District Tokens"] = district_tokens
    if subdistrict_tokens:
        groups["Subdistrict Tokens"] = subdistrict_tokens
    if quickhacks:
        groups["Quickhacks"] = quickhacks
    if currency:
        groups["Currency"] = currency
    if consumables:
        groups["Consumables"] = consumables
    if cyberware_items:
        groups["Cyberware"] = cyberware_items
    if weapon_items:
        groups["Weapons"] = weapon_items
    if misc_items:
        groups["Miscellaneous"] = misc_items

    return groups

# Generate item name groups automatically
item_name_groups: Dict[str, List[str]] = _build_item_name_groups()


# ===== HELPER FUNCTIONS =====

def get_item_classification(item_name: str) -> ItemClassification:
    """
    Get the classification for an item by name.

    This is a lookup helper that retrieves an item's classification
    from the item_table.

    Args:
        item_name: The name of the item

    Returns:
        The ItemClassification for this item

    Raises:
        KeyError: If the item doesn't exist in item_table
    """
    return item_table[item_name].classification


def is_progression_item(item_name: str) -> bool:
    """
    Check if an item is a progression item.

    Progression items are required to complete the game and are
    prioritized by the randomizer.

    Note: Uses bitwise AND to check for the progression flag, so this
    will return True even if the item has additional flags like 'useful'.

    Args:
        item_name: The name of the item

    Returns:
        True if the item has the progression flag, False otherwise
    """
    return bool(get_item_classification(item_name) & ItemClassification.progression)


def get_item_name_by_id(item_id: int) -> Optional[str]:
    """
    Get an item's name by its Archipelago ID.

    Reverse lookup from numeric ID to item name. Useful when
    receiving item IDs over the network.

    Args:
        item_id: The full Archipelago item ID (BASE_ID + offset)

    Returns:
        The item name, or None if not found
    """
    return item_id_to_name.get(item_id, None)


def get_item_id_by_name(item_name: str) -> Optional[int]:
    """
    Get an item's Archipelago ID by its name.

    Forward lookup from item name to numeric ID. Useful when
    sending item information over the network.

    Args:
        item_name: The item name

    Returns:
        The full Archipelago item ID (BASE_ID + offset), or None if not found
    """
    return item_name_to_id.get(item_name, None)
