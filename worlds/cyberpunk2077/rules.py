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
from .locations import location_table

if TYPE_CHECKING:
    from . import Cyberpunk2077World


def set_rules(world: "Cyberpunk2077World") -> None:
    """
    Set all access rules for quest progression and victory condition.

    This implements the canonical Cyberpunk 2077 quest chain structure:
    - Prologue (linear progression)
    - Act 2 (three branches that can be done in any order, all required)
    - Point of No Return (requires all three Act 2 branches)
    - Endings (each with different prerequisites)
    """
    player = world.player

    # ===== PROLOGUE CHAIN =====
    # Linear progression through prologue quests

    set_rule(
        world.multiworld.get_location("Prologue - The Ripperdoc", player),
        lambda state: state.can_reach_location("Prologue - The Rescue", player)
    )

    set_rule(
        world.multiworld.get_location("Prologue - The Ride", player),
        lambda state: state.can_reach_location("Prologue - The Ripperdoc", player)
    )

    # Both The Information AND The Pickup must be completed before The Heist
    set_rule(
        world.multiworld.get_location("Prologue - The Heist", player),
        lambda state: (
            state.can_reach_location("Prologue - The Pickup", player) and
            state.can_reach_location("Prologue - The Information", player)
        )
    )

    set_rule(
        world.multiworld.get_location("Act 1 - Love Like Fire", player),
        lambda state: state.can_reach_location("Prologue - The Heist", player)
    )

    set_rule(
        world.multiworld.get_location("Act 1 - Playing for Time", player),
        lambda state: state.can_reach_location("Act 1 - Love Like Fire", player)
    )

    # NOTE: Prologue milestone event access rules removed - these events were orphaned
    # and not used by any progression logic

    # NOTE: Branch completion event access rules removed - events eliminated to avoid
    # circular dependencies with region access tokens

    # NOTE: Side quest progression is handled by include_all_endings option (lines ~150-185)
    # which checks quest locations directly, not via events

    # NOTE: Phantom Liberty progression handled directly via quest location access rules
    # DLC quests gated by region access and quest chain, not through event items

    # ========== Act 2 ============

    # Only need to put the FIRST and LAST quest of a given chain for the generator to understand whats going on theoretically
    # Vodoo Boys
    set_rule(world.multiworld.get_location("Main - Automatic Love", player),
             lambda state: state.can_reach_location("Act 1 - Playing for Time", player))

    set_rule(world.multiworld.get_location("Main - Transmission", player),
             lambda state: state.can_reach_location("Main - Automatic Love", player))

    # Hellman
    set_rule(world.multiworld.get_location("Main - Ghost Town", player),
             lambda state: state.can_reach_location("Act 1 - Playing for Time", player))

    set_rule(world.multiworld.get_location("Main - Life During Wartime", player),
             lambda state: state.can_reach_location("Main - Ghost Town", player))

    # Takemura
    set_rule(world.multiworld.get_location("Main - Down on the Street", player),
             lambda state: state.can_reach_location("Act 1 - Playing for Time", player))

    set_rule(world.multiworld.get_location("Main - Search and Destroy", player),
             lambda state: state.can_reach_location("Main - Down on the Street", player))

    # ======= Point of No Return ======
    # Requires ALL THREE Act 2 branches to be completed
    # Check quest locations directly instead of using event items to avoid circular dependencies

    set_rule(world.multiworld.get_location("Endgame - Nocturne Op55N1", player), lambda state: (
            state.can_reach_location("Main - Transmission", player) and
            state.can_reach_location("Main - Life During Wartime", player) and
            state.can_reach_location("Main - Search and Destroy", player)
    ))

    # Ending Reached - accessible after completing Nocturne Op55N1 and any ending path
    # The epilogue quests (q201_heir, q202_nomads, q203_legend, q204_reborn, q307_tomorrow)
    # all map to this single location, so completing ANY ending triggers this check
    set_rule(world.multiworld.get_location("Ending Reached", player), lambda state: (
        state.can_reach_location("Endgame - Nocturne Op55N1", player)
    ))

    # ==========================================
    # Ending Side Quest Prerequisites
    # ==========================================
    # Set ending side quest chain rules when either include_all_endings OR include_side_quests is enabled
    # These quests have ENDING_SIDE_QUEST category and are included automatically when either option is true
    if (world.options.include_all_endings or world.options.include_side_quests):
        # --- PANAM'S BRANCH (For The Star Ending) ---
        # Unlocked after finishing Branch B (Hellman)
        set_rule(world.multiworld.get_location("Riders on the Storm", player),
                 lambda state: state.can_reach_location("Main - Life During Wartime", player))

        # Shortcut: Tying the end of Panam's arc to the beginning of it
        set_rule(world.multiworld.get_location("Queen of the Highway", player),
                 lambda state: state.can_reach_location("Riders on the Storm", player))

        # --- ROGUE & JOHNNY'S BRANCH (For The Sun / Temperance Endings) ---
        # Unlocked after finishing Branch C (Takemura)
        set_rule(world.multiworld.get_location("Chippin' In", player),
                 lambda state: state.can_reach_location("Main - Search and Destroy", player))

        # Shortcut: Tying the end of Rogue's arc to the beginning of it
        set_rule(world.multiworld.get_location("Blistering Love", player),
                 lambda state: state.can_reach_location("Chippin' In", player))


    # List of locations of which only ONE must be accessible to reach a point of no return
    no_return_locations = [
        "Epilogue - Where is My Mind?",
        "Epilogue - All Along the Watchtower",
        "Epilogue - Path of Glory",
        "Epilogue - New Dawn Fades",
        "Phantom Liberty - Firestarter",
        "Phantom Liberty - The Last Stand"
    ]

    # ===== VICTORY CONDITION =====
    # Victory requires reaching any ending (consolidated into "Ending Reached" location)
    set_rule(
        world.multiworld.get_location("Victory", world.player),
        lambda state: state.can_reach_location("Ending Reached", player)
    )

    # Set completion condition - player wins when they collect the Victory event item
    world.multiworld.completion_condition[player] = \
        lambda state: state.has("Victory", player)

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
