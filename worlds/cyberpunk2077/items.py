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
    """
    name: str
    code: Optional[int]  # None for event items
    classification: ItemClassification
    dlc_only: bool = False  # True for Phantom Liberty DLC items


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
# EXCEPTION - Checking for filler:
#   Since filler = 0, you cannot use bitwise AND! Instead check for absence of type flags:
#   if not (item.classification & (progression | useful | trap)):
#       # This item is filler (has no type flags, may have modifier flags)


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
    # ===== PROGRESSION ITEMS =====
    # These items are required to progress through the game
    # They unlock new areas, allow access to quests, or enable critical gameplay

    #====================================
    # Prologue Items
    #====================================

    # Lifepath Chosen Event
    # Granted when player completes any one of the 3 lifepath intros
    # (Streetkid, Corpo, or Nomad)
    # Used to unlock district access - player only needs ONE lifepath, not all 3
    "Lifepath Chosen": ItemData(
        name="ap_ev_lifepath_chosen",
        code=None,  # Event item
        classification=ItemClassification.progression
    ),

    "Dex's Limo Keys": ItemData(
        name="ap_qk_dex_keys",
        code=4000,  # First progression item
        classification=ItemClassification.progression
    ),

    # Has no effect currently
    "Konpeki Plaza Room Key": ItemData(
        name="ap_qk_konpeki_keys",
        code=4001,
        classification=ItemClassification.progression_deprioritized
    ),

    #====================================
    # Main Story Items
    #====================================

    #====================================
    # Phantom Liberty Items
    #====================================
    # Items marked dlc_only=True are excluded when Phantom Liberty DLC is disabled

    # Has no effect currently
    "Myers' Plane Ticket": ItemData(
        name="ap_qk_myers_ticket",
        code=4002,
        classification=ItemClassification.progression_deprioritized,
        dlc_only=True  # Phantom Liberty DLC required
    ),

    # ===== USEFUL ITEMS =====
    # These items are helpful but not required

    "5000 Eddies": ItemData(
        name="ap_ed_Items.money_5000",
        code=5000,
        classification=ItemClassification.useful
    ),
    "Tier 1 Overheat Quickhack": ItemData(
        name="ap_inv_Items.OverheatProgram",
        code=5001,
        classification=ItemClassification.useful
    ),
    "Tier 2 Overheat Quickhack": ItemData(
        name="ap_inv_Items.OverheatLvl1Program",
        code=5002,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 3 Overheat Quickhack": ItemData(
        name="ap_inv_Items.OverheatLvl2Program",
        code=5003,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Overheat Quickhack": ItemData(
        name="ap_inv_Items.OverheatLvl3Program",
        code=5004,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Overheat Quickhack": ItemData(
        name="ap_inv_Items.OverheatLvl4Program",
        code=5005,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Overheat Quickhack": ItemData(
        name="ap_inv_Items.OverheatLvl4PlusPlusProgram",
        code=5006,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 1 Short Circuit Quickhack": ItemData(
        name="ap_inv_Items.EMPOverloadProgram",
        code=5007,
        classification=ItemClassification.useful
    ),
    "Tier 2 Short Circuit Quickhack": ItemData(
        name="ap_inv_Items.EMPOverloadLvl1Program",
        code=5008,
        classification=ItemClassification.useful
    ),
    "Tier 3 Short Circuit Quickhack": ItemData(
        name="ap_inv_Items.EMPOverloadLvl2Program",
        code=5009,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Short Circuit Quickhack": ItemData(
        name="ap_inv_Items.EMPOverloadLvl3Program",
        code=5010,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Short Circuit Quickhack": ItemData(
        name="ap_inv_Items.EMPOverloadLvl4Program",
        code=5011,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Short Circuit Quickhack": ItemData(
        name="ap_inv_Items.EMPOverloadLvl4PlusPlusProgram",
        code=5012,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 2 Contagion Quickhack": ItemData(
        name="ap_inv_Items.ContagionProgram",
        code=5013,
        classification=ItemClassification.useful
    ),
    "Tier 3 Contagion Quickhack": ItemData(
        name="ap_inv_Items.ContagionLvl2Program",
        code=5014,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Contagion Quickhack": ItemData(
        name="ap_inv_Items.ContagionLvl3Program",
        code=5015,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Contagion Quickhack": ItemData(
        name="ap_inv_Items.ContagionLvl4Program",
        code=5016,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Contagion Quickhack": ItemData(
        name="ap_inv_Items.ContagionLvl4PlusPlusProgram",
        code=5017,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 3 Synapse Burnout Quickhack": ItemData(
        name="ap_inv_Items.BrainMeltLvl2Program",
        code=5018,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Synapse Burnout Quickhack": ItemData(
        name="ap_inv_Items.BrainMeltLvl3Program",
        code=5019,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Synapse Burnout Quickhack": ItemData(
        name="ap_inv_Items.BrainMeltLvl4Program",
        code=5020,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Synapse Burnout Quickhack": ItemData(
        name="ap_inv_Items.BrainMeltLvl4PlusPlusProgram",
        code=5021,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 1 Reboot Optics Quickhack": ItemData(
        name="ap_inv_Items.BlindProgram",
        code=5022,
        classification=ItemClassification.useful
    ),
    "Tier 2 Reboot Optics Quickhack": ItemData(
        name="ap_inv_Items.BlindLvl1Program",
        code=5023,
        classification=ItemClassification.useful
    ),
    "Tier 3 Reboot Optics Quickhack": ItemData(
        name="ap_inv_Items.BlindLvl2Program",
        code=5024,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Reboot Optics Quickhack": ItemData(
        name="ap_inv_Items.BlindLvl3Program",
        code=5025,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Reboot Optics Quickhack": ItemData(
        name="ap_inv_Items.BlindLvl4Program",
        code=5026,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Reboot Optics Quickhack": ItemData(
        name="ap_inv_Items.BlindLvl4PlusPlusProgram",
        code=5027,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 2 Cyberware Malfunction Quickhack": ItemData(
        name="ap_inv_Items.DisableCyberwareProgram",
        code=5028,
        classification=ItemClassification.useful
    ),
    "Tier 3 Cyberware Malfunction Quickhack": ItemData(
        name="ap_inv_Items.DisableCyberwareLvl2Program",
        code=5029,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Cyberware Malfunction Quickhack": ItemData(
        name="ap_inv_Items.DisableCyberwareLvl3Program",
        code=5030,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Cyberware Malfunction Quickhack": ItemData(
        name="ap_inv_Items.DisableCyberwareLvl4Program",
        code=5031,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Cyberware Malfunction Quickhack": ItemData(
        name="ap_inv_Items.DisableCyberwareLvl4PlusPlusProgram",
        code=5032,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 2 Cripple Movement Quickhack": ItemData(
        name="ap_inv_Items.LocomotionMalfunctionProgram",
        code=5033,
        classification=ItemClassification.useful
    ),
    "Tier 3 Cripple Movement Quickhack": ItemData(
        name="ap_inv_Items.LocomotionMalfunctionLvl2Program",
        code=5034,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Cripple Movement Quickhack": ItemData(
        name="ap_inv_Items.LocomotionMalfunctionLvl3Program",
        code=5035,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Cripple Movement Quickhack": ItemData(
        name="ap_inv_Items.LocomotionMalfunctionLvl4Program",
        code=5036,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Cripple Movement Quickhack": ItemData(
        name="ap_inv_Items.LocomotionMalfunctionLvl4PlusPlusProgram",
        code=5037,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 2 Weapon Glitch Quickhack": ItemData(
        name="ap_inv_Items.WeaponMalfunctionProgram",
        code=5038,
        classification=ItemClassification.useful
    ),
    "Tier 3 Weapon Glitch Quickhack": ItemData(
        name="ap_inv_Items.WeaponMalfunctionLvl2Program",
        code=5039,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Weapon Glitch Quickhack": ItemData(
        name="ap_inv_Items.WeaponMalfunctionLvl3Program",
        code=5040,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Weapon Glitch Quickhack": ItemData(
        name="ap_inv_Items.WeaponMalfunctionLvl4Program",
        code=5041,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Weapon Glitch Quickhack": ItemData(
        name="ap_inv_Items.WeaponMalfunctionLvl4PlusPlusProgram",
        code=5042,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 1 Ping Quickhack": ItemData(
        name="ap_inv_Items.PingProgram",
        code=5043,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 3 Ping Quickhack": ItemData(
        name="ap_inv_Items.PingLvl2Program",
        code=5044,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Ping Quickhack": ItemData(
        name="ap_inv_Items.PingLvl4Program",
        code=5045,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Ping Quickhack": ItemData(
        name="ap_inv_Items.PingLvl4PlusPlusProgram",
        code=5046,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),

    "Tier 1 Bait Quickhack": ItemData(
        name="ap_inv_Items.WhistleLvl0Program",
        code=5047,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 2 Bait Quickhack": ItemData(
        name="ap_inv_Items.WhistleLvl1Program",
        code=5048,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 3 Bait Quickhack": ItemData(
        name="ap_inv_Items.WhistleLvl2Program",
        code=5049,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Bait Quickhack": ItemData(
        name="ap_inv_Items.WhistleLvl3Program",
        code=5050,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Bait Quickhack": ItemData(
        name="ap_inv_Items.WhistleLvl4Program",
        code=5051,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Bait Quickhack": ItemData(
        name="ap_inv_Items.WhistleLvl4PlusPlusProgram",
        code=5052,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),

    "Tier 2 Request Backup Quickhack": ItemData(
        name="ap_inv_Items.CommsCallInLvl1Program",
        code=5053,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 3 Request Backup Quickhack": ItemData(
        name="ap_inv_Items.CommsCallInLvl2Program",
        code=5054,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Request Backup Quickhack": ItemData(
        name="ap_inv_Items.CommsCallInLvl3Program",
        code=5055,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Request Backup Quickhack": ItemData(
        name="ap_inv_Items.CommsCallInLvl4Program",
        code=5056,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Request Backup Quickhack": ItemData(
        name="ap_inv_Items.CommsCallInLvl4PlusPlusProgram",
        code=5057,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),

    "Tier 3 Memory Wipe Quickhack": ItemData(
        name="ap_inv_Items.MemoryWipeLvl2Program",
        code=5058,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Memory Wipe Quickhack": ItemData(
        name="ap_inv_Items.MemoryWipeLvl3Program",
        code=5059,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Memory Wipe Quickhack": ItemData(
        name="ap_inv_Items.MemoryWipeLvl4Program",
        code=5060,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Memory Wipe Quickhack": ItemData(
        name="ap_inv_Items.MemoryWipeLvl4PlusPlusProgram",
        code=5061,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),

    "Tier 1 Sonic Shock Quickhack": ItemData(
        name="ap_inv_Items.CommsNoiseProgram",
        code=5062,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 3 Sonic Shock Quickhack": ItemData(
        name="ap_inv_Items.CommsNoiseLvl2Program",
        code=5063,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Sonic Shock Quickhack": ItemData(
        name="ap_inv_Items.CommsNoiseLvl3Program",
        code=5064,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Sonic Shock Quickhack": ItemData(
        name="ap_inv_Items.CommsNoiseLvl4Program",
        code=5065,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Sonic Shock Quickhack": ItemData(
        name="ap_inv_Items.CommsNoiseLvl4PlusPlusProgram",
        code=5066,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Cyberpsychosis Quickhack": ItemData(
        name="ap_inv_Items.MadnessLvl3Program",
        code=5067,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Cyberpsychosis Quickhack": ItemData(
        name="ap_inv_Items.MadnessLvl4Program",
        code=5068,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Cyberpsychosis Quickhack": ItemData(
        name="ap_inv_Items.MadnessLvl4PlusPlusProgram",
        code=5069,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),

    "Tier 4 Suicide Quickhack": ItemData(
        name="ap_inv_Items.SuicideLvl3Program",
        code=5070,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Suicide Quickhack": ItemData(
        name="ap_inv_Items.SuicideLvl4Program",
        code=5071,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Suicide Quickhack": ItemData(
        name="ap_inv_Items.SuicideLvl4PlusPlusProgram",
        code=5072,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),

    "Tier 4 System Collapse Quickhack": ItemData(
        name="ap_inv_Items.SystemCollapseLvl3Program",
        code=5073,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 System Collapse Quickhack": ItemData(
        name="ap_inv_Items.SystemCollapseLvl4Program",
        code=5074,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ System Collapse Quickhack": ItemData(
        name="ap_inv_Items.SystemCollapseLvl4PlusPlusProgram",
        code=5075,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),

    "Tier 4 Detonate Grenade Quickhack": ItemData(
        name="ap_inv_Items.GrenadeExplodeLvl3Program",
        code=5076,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Detonate Grenade Quickhack": ItemData(
        name="ap_inv_Items.GrenadeExplodeLvl4Program",
        code=5077,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5++ Detonate Grenade Quickhack": ItemData(
        name="ap_inv_Items.GrenadeExplodeLvl4PlusPlusProgram",
        code=5078,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),

    "Tier 3 Blackwall Gateway Quickhack": ItemData(
        name="ap_inv_Items.BlackWallProgramLvl2",
        code=5079,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 4 Blackwall Gateway Quickhack": ItemData(
        name="ap_inv_Items.BlackWallProgramLvl3",
        code=5080,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    "Tier 5 Blackwall Gateway Quickhack": ItemData(
        name="ap_inv_Items.BlackWallProgramLvl4",
        code=5081,
        classification=ItemClassification.useful | ItemClassification.deprioritized
    ),
    # ===== FILLER ITEMS =====
    # These items are used to fill extra locations

    "500 Eddies": ItemData(
        name="ap_ed_Items.money_500",  # In-game currency
        code=6000,
        classification=ItemClassification.filler | ItemClassification.deprioritized
    ),

    "1000 Eddies" : ItemData(
        name = "ap_ed_Items.money_1000",
        code = 6001,
        classification = ItemClassification.filler | ItemClassification.deprioritized
    ),

    "Ram Nugs" : ItemData(
        name = "ap_inv_Items.Blackmarket_MemoryBooster",
        code = 6003,
        classification = ItemClassification.filler | ItemClassification.deprioritized
    ),

    "RAM Jolt" : ItemData(
        name = "ap_inv_Items.MemoryBooster",
        code = 6004,
        classification = ItemClassification.filler | ItemClassification.deprioritized
    ),

    "Burrito XXXL" : ItemData(
        name = "ap_inv_Items.MediumQualityFood4",
        code = 6005,
        classification = ItemClassification.filler | ItemClassification.deprioritized
    ),

    # ===== TRAP ITEMS =====
    # These items have negative effects
    # Remove if you don't want traps in your world

    # "Smasher Trap": ItemData(
    #     name="ap_tp_smasher",
    #     code=7000,
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
