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

    # ============================================
    # Prologue Rules
    # ============================================

    set_rule(
        world.multiworld.get_location("Prologue - The Ride", player),
        lambda state: state.has_any({"Dex's Limo Keys"}, player)
    )

    set_rule(
        world.multiworld.get_location("Prologue - The Pickup", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    set_rule(
        world.multiworld.get_location("Prologue - The Information", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    set_rule(
        world.multiworld.get_location("Prologue - The Heist", player),
        lambda state: state.can_reach_location("Prologue - The Pickup", player)
                      and state.can_reach_location("Prologue - The Information", player)
                      #and state.has("Konpeki Plaza Room Key", player)
    )

    set_rule(
        world.multiworld.get_location("Main - Transmission", player),
        lambda state: state.can_reach_location("Prologue - The Heist", player)
    )

    # =================
    # Phantom Liberty
    # =================

    # TODO: Still need the remaining rules for Phantom Liberty quests, but this should be enough
    # TODO: to make sure that the player wouldn't be locked by out-of-order logic once the blocker is in
    if world.options.include_phantom_liberty_dlc:
        # Require Myers' Plane Ticket to start Phantom Liberty
        set_rule(
            world.multiworld.get_location("Phantom Liberty - Phantom Liberty", player),
            lambda state: state.has("Myers' Plane Ticket", player)
                          and state.can_reach_location("Main - Transmission", player)
        )
        # Require completing Phantom Liberty Start to access Dog Eat Dog
        set_rule(
            world.multiworld.get_location("Phantom Liberty - Dog Eat Dog", player),
            lambda state: state.can_reach_location("Phantom Liberty - Phantom Liberty", player)
        )

    #=============
    # CyberPsychos
    #=============

    # ===== CYBERPSYCHO SIGHTINGS =====
    # All Cyberpsycho locations require completing "Prologue - The Ride"
    # Region-level access rules (set in regions.py) already require a lifepath

    # Cyberpsycho Sighting: Six Feet Under
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Six Feet Under", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Bloody Ritual
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Bloody Ritual", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Where the Bodies Hit the Floor
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Where the Bodies Hit the Floor", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Demons of War
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Demons of War", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Lt. Mower
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Lt. Mower", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Ticket to the Major Leagues
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Ticket to the Major Leagues", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: The Wasteland
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: The Wasteland", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: House on a Hill
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: House on a Hill", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Second Chances
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Second Chances", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: On Deaf Ears
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: On Deaf Ears", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Phantom of Night City
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Phantom of Night City", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Seaside Cafe
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Seaside Cafe", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Letter of the Law
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Letter of the Law", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Smoke on the Water
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Smoke on the Water", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Lex Talionis
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Lex Talionis", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Under the Bridge
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Under the Bridge", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Cyberpsycho Sighting: Discount Doc
    set_rule(
        world.multiworld.get_location("Cyberpsycho Sighting: Discount Doc", player),
        lambda state: state.can_reach_location("Prologue - The Ride", player)
    )

    # Victory item is placed directly on each epilogue location in regions.py
    # Set access rule on Victory location - requires completing one of the ending questlines
    set_rule(
        world.multiworld.get_location("Victory", world.player),
        lambda state: (
            # Arasaka/Hanako Path
            state.can_reach_location("Epilogue - Where is My Mind?", world.player) or
            # Nomad/Panam Path
            state.can_reach_location("Epilogue - All Along the Watchtower", world.player) or
            # Rogue/Johnny Path
            state.can_reach_location("Epilogue - Path of Glory", world.player) or
            # Temperance Path (Johnny takes the body)
            state.can_reach_location("Epilogue - New Dawn Fades", world.player) or
            # Phantom Liberty Ending (if DLC enabled)
            (world.options.include_phantom_liberty_dlc and
             state.can_reach_location("DLC - Things Done Changed", world.player))
        )
    )

    # Set completion condition - player wins when they collect the Victory event item
    world.multiworld.completion_condition[world.player] = \
        lambda state: state.has("Victory", world.player)

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
