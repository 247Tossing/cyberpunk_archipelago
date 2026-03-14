"""
Cyberpunk 2077 Access Rules

This file defines the logic for when locations and regions become accessible.

Rules determine what items are needed to:
- Travel between regions (region access rules)
- Complete specific locations (location access rules)
- Beat the game (victory condition)

Rules are lambda functions that check the player's current item collection.
"""

from typing import TYPE_CHECKING
from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule

if TYPE_CHECKING:
    from . import Cyberpunk2077World


def set_rules(world: "Cyberpunk2077World") -> None:
    player = world.player

    #============================================
    # Prologue Rules
    #============================================

    set_rule(
        world.multiworld.get_location("q001_02_dex", player),
        lambda state: state.has_any({"Dex's Limo Keys"}, player)
    )

    #=================
    # Phantom Liberty
    #=================


    # TODO: add phantom libery DLC quests
    #if world.options.include_phantom_liberty_dlc is True:
    #
    #    set_rule(
    #        world.multiworld.get_location("INSERT PHANTOM LIBERTY", player),
    #        lambda state: (
    #            state.has("Phantom Liberty Key", player) and
    #            state.has("Phantom Liberty Key Fragment", player)
    #        )
    #    )

    #=============
    # CyberPsychos
    #=============

    # Cyberpsycho Sighting: Six Feet Under
    set_rule(
        world.multiworld.get_location("ma_wat_nid_22", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Bloody Ritual
    set_rule(
        world.multiworld.get_location("ma_wat_nid_15", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Where the Bodies Hit the Floor
    set_rule(
        world.multiworld.get_location("ma_wat_nid_03", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Demons of War
    set_rule(
        world.multiworld.get_location("ma_wat_kab_02", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Lt. Mower
    set_rule(
        world.multiworld.get_location("ma_wat_kab_08", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Ticket to the Major Leagues
    set_rule(
        world.multiworld.get_location("ma_wat_lch_06", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: The Wasteland
    set_rule(
        world.multiworld.get_location("ma_bls_ina_se1_07", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: House on a Hill
    set_rule(
        world.multiworld.get_location("ma_bls_ina_se1_08", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Second Chances
    set_rule(
        world.multiworld.get_location("ma_bls_ina_se1_22", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: On Deaf Ears
    set_rule(
        world.multiworld.get_location("ma_cct_dtn_03", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Phantom of Night City
    set_rule(
        world.multiworld.get_location("ma_cct_dtn_07", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Seaside Cafe
    set_rule(
        world.multiworld.get_location("ma_hey_spr_04", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Letter of the Law
    set_rule(
        world.multiworld.get_location("ma_hey_spr_06", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Smoke on the Water
    set_rule(
        world.multiworld.get_location("ma_pac_cvi_08", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Lex Talionis
    set_rule(
        world.multiworld.get_location("ma_pac_cvi_15", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Under the Bridge
    set_rule(
        world.multiworld.get_location("ma_std_arr_06", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # Cyberpsycho Sighting: Discount Doc
    set_rule(
        world.multiworld.get_location("ma_std_rcr_11", player),
        lambda state: state.has_any({"q000_street_kid", "q000_corpo", "q000_nomad"}, player)
    )

    # ===== REGION ACCESS RULES =====
    # These control when players can travel to different regions
    # Rules are applied to entrances (connections between regions)

    # Example: Require Mantis Blades to access Westbrook
    # set_rule(
    #     world.multiworld.get_entrance("Watson to Westbrook", world.player),
    #     lambda state: state.has("Mantis Blades", world.player)
    # )

    # Example: Require Security Access Card to reach City Center
    # set_rule(
    #     world.multiworld.get_entrance("Watson to City Center", world.player),
    #     lambda state: state.has("Security Access Card", world.player)
    # )




    # ===== LOCATION ACCESS RULES =====
    # These control when specific locations (checks) become accessible
    # Rules are applied directly to locations

    # Example: Require Kerenzikov to complete a specific gig
    # set_rule(
    #     world.multiworld.get_location("Watson - Complete Gig 2", world.player),
    #     lambda state: state.has("Kerenzikov", world.player)
    # )

    # Example: Require multiple items to access a location
    # set_rule(
    #     world.multiworld.get_location("City Center - Reach Arasaka Tower", world.player),
    #     lambda state: (
    #         state.has("Security Access Card", world.player) and
    #         state.has("Mantis Blades", world.player)
    #     )
    # )


    # ===== VICTORY CONDITION =====
    # Define what's required to beat the game
    # This is typically placed at a special "Victory" location

    # TODO: Create a victory location and set its rule
    # Example:
    # set_rule(
    #     world.multiworld.get_location("Reached Cyberpunk Ending", world.player),
    #     lambda state: state.has_all([
    #         "Security Access Card",
    #         "Mantis Blades",
    #         "Kerenzikov"
    #     ], world.player)
    # )

    # Then mark it as the completion condition
    # world.multiworld.completion_condition[world.player] = (
    #     lambda state: state.has("Victory", world.player)
    # )


# ===== HELPER FUNCTIONS =====
# These are utility functions to make rule creation easier

def has_item(state: CollectionState, item_name: str, player: int) -> bool:
    """
    Check if the player has collected a specific item.

    Args:
        state: The collection state to check
        item_name: Name of the item to check for
        player: Player ID

    Returns:
        True if the player has the item, False otherwise
    """
    return state.has(item_name, player)


def has_all_items(state: CollectionState, item_names: list[str], player: int) -> bool:
    """
    Check if the player has ALL of the specified items.

    Args:
        state: The collection state to check
        item_names: List of item names to check for
        player: Player ID

    Returns:
        True if the player has all items, False otherwise
    """
    return state.has_all(item_names, player)


def has_any_items(state: CollectionState, item_names: list[str], player: int) -> bool:
    """
    Check if the player has ANY of the specified items.

    Args:
        state: The collection state to check
        item_names: List of item names to check for
        player: Player ID

    Returns:
        True if the player has any of the items, False otherwise
    """
    return state.has_any(item_names, player)


def has_item_count(state: CollectionState, item_name: str, count: int, player: int) -> bool:
    """
    Check if the player has a specific number of an item.

    Useful for items that can be collected multiple times.

    Args:
        state: The collection state to check
        item_name: Name of the item to check for
        count: Required number of that item
        player: Player ID

    Returns:
        True if the player has at least 'count' of the item, False otherwise
    """
    return state.count(item_name, player) >= count


# ===== LAMBDA FUNCTIONS EXPLAINED =====
#
# Lambda syntax in Python:
#   lambda arguments: expression
#
# Lambdas are anonymous functions used for simple, single-expression functions.
# They're commonly used in Archipelago for access rules.
#
# Example comparisons:
#
# 1. Simple check:
#    lambda state: state.has("Key", player)
#
# 2. Multiple conditions (AND):
#    lambda state: state.has("Key1", player) and state.has("Key2", player)
#
# 3. Alternative conditions (OR):
#    lambda state: state.has("Key1", player) or state.has("Key2", player)
#
# 4. Complex logic:
#    lambda state: (state.has("Key1", player) or state.has("Key2", player)) and state.has("Key3", player)
#
# Using the helper functions:
#    lambda state: has_all_items(state, ["Key1", "Key2", "Key3"], world.player)
#    lambda state: has_any_items(state, ["Key1", "Key2"], world.player)
#    lambda state: has_item_count(state, "Key Fragment", 3, world.player)


# ===== COMMON RULE PATTERNS =====

# Pattern 1: Simple item requirement
# set_rule(
#     world.multiworld.get_location("Some Location", world.player),
#     lambda state: state.has("Required Item", world.player)
# )

# Pattern 2: Multiple items required (AND)
# set_rule(
#     world.multiworld.get_location("Some Location", world.player),
#     lambda state: (
#         state.has("Item 1", world.player) and
#         state.has("Item 2", world.player) and
#         state.has("Item 3", world.player)
#     )
# )
# Or use the helper:
# set_rule(
#     world.multiworld.get_location("Some Location", world.player),
#     lambda state: has_all_items(state, ["Item 1", "Item 2", "Item 3"], world.player)
# )

# Pattern 3: Any item from a list (OR)
# set_rule(
#     world.multiworld.get_location("Some Location", world.player),
#     lambda state: (
#         state.has("Item 1", world.player) or
#         state.has("Item 2", world.player)
#     )
# )
# Or use the helper:
# set_rule(
#     world.multiworld.get_location("Some Location", world.player),
#     lambda state: has_any_items(state, ["Item 1", "Item 2"], world.player)
# )

# Pattern 4: Item count requirement
# set_rule(
#     world.multiworld.get_location("Some Location", world.player),
#     lambda state: has_item_count(state, "Key Fragment", 3, world.player)
# )

# Pattern 5: Progressive items
# (Items that you get multiple copies of, each unlocking more access)
# set_rule(
#     world.multiworld.get_location("Some Location", world.player),
#     lambda state: state.count("Progressive Item", world.player) >= 2
# )

# Pattern 6: Adding to existing rules (not replacing)
# If you want to add an additional requirement without removing the existing rule:
# add_rule(
#     world.multiworld.get_location("Some Location", world.player),
#     lambda state: state.has("Additional Item", world.player)
# )


# ===== RULE API REFERENCE =====
#
# set_rule(target, rule):
#   - Sets the access rule for a location or entrance
#   - Replaces any existing rule
#   - rule is a lambda function that returns True/False
#
# add_rule(target, rule):
#   - Adds an additional requirement to existing rules
#   - Combines with AND logic (both rules must be true)
#   - Useful for adding extra requirements without replacing existing logic
#
# state.has(item_name, player):
#   - Returns True if player has at least one of the item
#
# state.has_all(item_list, player):
#   - Returns True if player has all items in the list
#
# state.has_any(item_list, player):
#   - Returns True if player has any item from the list
#
# state.count(item_name, player):
#   - Returns the number of that item the player has
#   - Useful for progressive items or items that stack
#
# state.can_reach_region(region_name, player):
#   - Returns True if player can reach the specified region
#
# state.can_reach_location(location_name, player):
#   - Returns True if player can reach the specified location
