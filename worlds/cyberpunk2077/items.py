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
        classification: How the item behaves in the randomizer
    """
    name: str
    code: Optional[int]  # None for event items
    classification: ItemClassification


# ===== ITEM CLASSIFICATION TYPES =====
# ItemClassification is an enum that determines how the randomizer treats items
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
#
# ItemClassification.trap:
#   - Negative effects (optional, for challenge/fun)
#   - Examples: Debuffs, wanted level increases, temporary handicaps
#   - Can make the game harder


# ===== ITEM TABLE =====
# This dictionary maps item names to their definitions
# The item table is the single source of truth for all items in the game

# TODO: Replace these example items with actual Cyberpunk 2077 items
# The item codes should start at base_id + 1 and increment from there
item_table: Dict[str, ItemData] = {
    # ===== EXAMPLE PROGRESSION ITEMS =====
    # These items are required to beat the game
    # They might unlock new areas, allow access to quests, or enable critical gameplay

    # IDs starting with 4 are required for progression
    # IDs starting with 5 are useful items
    # IDs starting with 6 are filler items

    #====================================
    # Prologue Items
    #====================================

    "Dex's Limo Keys": ItemData(
        name="ap_qk_dex_keys",
        code=4000,  # base_id + 1
        classification=ItemClassification.progression
    ),

    "Konpeki Plaza Room Key": ItemData(
        name="ap_qk_konpeki_keys",
        code=4001,
        classification=ItemClassification.progression
    ),

    #====================================
    # Main Story Items
    #====================================

    #====================================
    # Phantom Liberty Items
    #====================================

    "Myers' Plane Ticket": ItemData(
        name="ap_qk_myers_ticket",
        code=5000,
        classification=ItemClassification.progression
    ),

    # ===== USEFUL ITEMS =====
    # These items are helpful but not required

    # ===== FILLER ITEMS =====
    # These items are used to fill extra locations

    "500 Eddies": ItemData(
        name="ap_it_Items.money_500",  # In-game currency
        code=6000,
        classification=ItemClassification.filler
    ),

    "1000 Eddies" : ItemData(
        name = "ap_it_Items.money_1000",
        code = 6001,
        classification = ItemClassification.filler
    ),

    "5000 Eddies" : ItemData(
        name = "ap_it_Items.money_5000",
        code = 6002,
        classification = ItemClassification.filler
    ),

    # ===== TRAP ITEMS =====
    # These items have negative effects
    # Remove if you don't want traps in your world

    # "NCPD Wanted": ItemData(
    #     name="NCPD Wanted",
    #     code=77_2077_008,
    #     classification=ItemClassification.trap
    # ),


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
        classification=ItemClassification.progression
    ),
}


# ===== DERIVED MAPPINGS =====
# These are automatically generated from item_table
# Don't modify these manually - they're computed based on item_table

# Dictionary mapping item names to their IDs
# Example: {"Mantis Blades": 77_2077_001, "Kerenzikov": 77_2077_002, ...}
# Filters out event items (code=None) to get only real items
item_name_to_id: Dict[str, int] = {
    name: data.code
    for name, data in item_table.items()
    if data.code is not None  # Exclude event items
}

# Dictionary mapping item IDs to their display names (reverse lookup)
# Example: {4000: "Dex's Limo Keys", 5000: "Myers' Plane Ticket", ...}
# Allows bidirectional lookup - searching by ID to get the display name
# Used for Archipelago UI and logging
item_id_to_name: Dict[int, str] = {
    data.code: name
    for name, data in item_table.items()
    if data.code is not None  # Exclude event items
}

# Dictionary mapping Archipelago IDs to internal game IDs
# Example: {4000: "ap_qk_dex_keys", 5000: "ap_qk_myers_ticket", ...}
# Used by the client to translate item IDs to game-recognizable identifiers
# RedScript needs these internal IDs to give items to the player
item_id_to_game_id: Dict[int, str] = {
    data.code: data.name  # Maps to ItemData.name field (internal game ID)
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
    - Item name prefix (ap_qk_, ap_it_, ap_cw_, ap_sp_, ap_trp_)

    Returns:
        Dictionary mapping group names to lists of item display names
    """
    groups: Dict[str, List[str]] = {}

    # Group by classification
    progression_items = []
    useful_items = []
    filler_items = []
    trap_items = []

    # Group by prefix/type
    quest_keys = []
    in_game_items = []
    cyberware_items = []
    skill_points = []
    traps = []

    for display_name, item_data in item_table.items():
        if item_data.code is None:
            continue  # Skip event items

        item_name = item_data.name

        # Group by classification
        if item_data.classification == ItemClassification.progression:
            progression_items.append(display_name)
        elif item_data.classification == ItemClassification.useful:
            useful_items.append(display_name)
        elif item_data.classification == ItemClassification.filler:
            filler_items.append(display_name)
        elif item_data.classification == ItemClassification.trap:
            trap_items.append(display_name)

        # Group by prefix
        if item_name.startswith("ap_qk_"):
            quest_keys.append(display_name)
        elif item_name.startswith("ap_it_"):
            in_game_items.append(display_name)
        elif item_name.startswith("ap_cw_"):
            cyberware_items.append(display_name)
        elif item_name.startswith("ap_sp_"):
            skill_points.append(display_name)
        elif item_name.startswith("ap_trp_"):
            traps.append(display_name)

    # Add groups only if they have items
    if progression_items:
        groups["Progression Items"] = progression_items
    if useful_items:
        groups["Useful Items"] = useful_items
    if filler_items:
        groups["Filler Items"] = filler_items
    if trap_items:
        groups["Trap Items"] = trap_items

    if quest_keys:
        groups["Quest Keys"] = quest_keys
    if in_game_items:
        groups["In-Game Items"] = in_game_items
    if cyberware_items:
        groups["Cyberware"] = cyberware_items
    if skill_points:
        groups["Skill Points"] = skill_points
    if traps:
        groups["Traps"] = traps

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

    Args:
        item_name: The name of the item

    Returns:
        True if the item is progression, False otherwise
    """
    return get_item_classification(item_name) == ItemClassification.progression


def get_item_name_by_id(item_id: int) -> Optional[str]:
    """
    Get an item's name by its Archipelago ID.

    Reverse lookup from numeric ID to item name. Useful when
    receiving item IDs over the network.

    Args:
        item_id: The Archipelago item ID

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
        The Archipelago item ID, or None if not found
    """
    return item_name_to_id.get(item_name, None)
