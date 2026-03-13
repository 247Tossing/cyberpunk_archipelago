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

    "Dex's Limo Keys": ItemData(
        name="ap_qk_dex_keys",
        code=77_2077_001,  # base_id + 1
        classification=ItemClassification.progression
    ),

    "Kerenzikov": ItemData(
        name="Kerenzikov",
        code=77_2077_002,
        classification=ItemClassification.progression
    ),

    "Security Access Card": ItemData(
        name="Security Access Card",
        code=77_2077_003,
        classification=ItemClassification.progression
    ),


    # ===== EXAMPLE USEFUL ITEMS =====
    # These items are helpful but not required

    "Rare Quickhack": ItemData(
        name="Rare Quickhack",
        code=77_2077_004,
        classification=ItemClassification.useful
    ),

    "Tech Rifle": ItemData(
        name="Tech Rifle",
        code=77_2077_005,
        classification=ItemClassification.useful
    ),


    # ===== EXAMPLE FILLER ITEMS =====
    # These items are used to fill extra locations

    "Filler Item": ItemData(
        name="Filler Item",
        code=77_2077_006,
        classification=ItemClassification.filler
    ),

    "Eddies Stack": ItemData(
        name="Eddies Stack",
        code=77_2077_007,
        classification=ItemClassification.filler
    ),


    # ===== EXAMPLE TRAP ITEMS (Optional) =====
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

    # Example: Completing a major quest could give an event item
    # "Completed Main Quest Act 1": ItemData(
    #     name="Completed Main Quest Act 1",
    #     code=None,  # No code = event item
    #     classification=ItemClassification.progression
    # ),
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

# Dictionary mapping item IDs to their names (reverse lookup)
# Example: {77_2077_001: "Mantis Blades", 77_2077_002: "Kerenzikov", ...}
# Allows bidirectional lookup - searching by ID to get the name
item_id_to_name: Dict[int, str] = {
    data.code: name
    for name, data in item_table.items()
    if data.code is not None  # Exclude event items
}


# ===== ITEM NAME GROUPS =====
# Groups allow players to reference multiple items at once in their YAML
#
# Example YAML usage:
#   local_items:
#     - Cyberware  # Keeps all cyberware local to this player
#   start_inventory:
#     - Weapons: 2  # Start with 2 random weapons

# TODO: Add your item groups here
item_name_groups: Dict[str, List[str]] = {
    "Cyberware": [
        "Mantis Blades",
        "Kerenzikov",
        # Add more cyberware items here
    ],
    "Weapons": [
        "Tech Rifle",
        # Add more weapon items here
    ],
    "Filler": [
        "Filler Item",
        "Eddies Stack",
        # Add more filler items here
    ],
}


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
