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

    In addition to the quest-chain rules below, ``_apply_multi_region_rules``
    adds a per-location reachability predicate for every ``LocationData`` whose
    ``regions`` tuple contains more than one district. This keeps the
    generator's reachability model in sync with the data when
    ``restrict_by_major_district`` gates districts behind tokens.
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
        world.multiworld.get_location("Prologue - Love Like Fire", player),
        lambda state: state.can_reach_location("Prologue - The Heist", player)
    )

    set_rule(
        world.multiworld.get_location("Main - Playing for Time", player),
        lambda state: state.can_reach_location("Prologue - Love Like Fire", player)
    )

    # ========== Act 2 ============

    # Only need to put the FIRST and LAST quest of a given chain for the generator to understand whats going on theoretically
    # Vodoo Boys
    set_rule(world.multiworld.get_location("Main - Automatic Love", player),
             lambda state: state.can_reach_location("Main - Playing for Time", player))

    set_rule(world.multiworld.get_location("Main - Transmission", player),
             lambda state: state.can_reach_location("Main - Automatic Love", player))

    # Hellman
    set_rule(world.multiworld.get_location("Main - Ghost Town", player),
             lambda state: state.can_reach_location("Main - Playing for Time", player))

    set_rule(world.multiworld.get_location("Main - Life During Wartime", player),
             lambda state: state.can_reach_location("Main - Ghost Town", player))

    # Takemura
    set_rule(world.multiworld.get_location("Main - Down on the Street", player),
             lambda state: state.can_reach_location("Main - Playing for Time", player))

    set_rule(world.multiworld.get_location("Main - Search and Destroy", player),
             lambda state: state.can_reach_location("Main - Down on the Street", player))

    # ======= Point of No Return ======
    # Requires ALL THREE Act 2 branches to be completed
    # Check quest locations directly instead of using event items to avoid circular dependencies

    set_rule(world.multiworld.get_location("Point of No Return - Nocturne Op55N1", player), lambda state: (
            state.can_reach_location("Main - Transmission", player) and
            state.can_reach_location("Main - Life During Wartime", player) and
            state.can_reach_location("Main - Search and Destroy", player)
    ))

    # Ending Reached - accessible after completing Nocturne Op55N1 and any ending path
    # The epilogue quests (q201_heir, q202_nomads, q203_legend, q204_reborn, q307_tomorrow)
    # all map to this single location, so completing ANY ending triggers this check
    set_rule(world.multiworld.get_location("Ending Reached", player), lambda state: (
        state.can_reach_location("Point of No Return - Nocturne Op55N1", player)
    ))

    # ==========================================
    # Ending Side Quest Prerequisites
    # ==========================================
    # Set ending side quest chain rules when either include_all_endings OR include_side_quests is enabled
    # These quests have ENDING_SIDE_QUEST category and are included automatically when either option is true
    if world.options.include_all_endings or world.options.include_side_quests:
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

    # ==========================================
    # Multi-region district reachability
    # ==========================================
    # Many quests touch more than one district. ``LocationData.regions`` lists
    # every district the quest physically requires the player to reach. When
    # ``restrict_by_major_district`` is on, each district has its own entrance
    # token, so we must add a per-location rule mirroring the data: the player
    # must be able to reach every listed major district. ``add_rule`` ANDs with
    # any quest-chain rule set earlier in this function.
    #
    # We only do this when the district randomizer is on. With it off, every
    # district is reachable as soon as the lifepath intro is done and no extra
    # rule is needed.
    _apply_multi_region_rules(world, player)

    # ===== VICTORY CONDITION =====
    # Victory requires reaching any ending (consolidated into "Ending Reached" location)
    set_rule(
        world.multiworld.get_location("Victory", world.player),
        lambda state: state.can_reach_location("Ending Reached", player)
    )

    # Set completion condition - player wins when they collect the Victory event item
    world.multiworld.completion_condition[player] = \
        lambda state: state.has("Victory", player)

# ===== MULTI-REGION HELPERS =====

# Top-level regions that have entrance token gates when
# ``restrict_by_major_district`` is enabled. ``LocationData.regions`` entries
# outside this set (e.g. ``Afterlife``, ``North Oak``, ``Cyberspace``) carry no
# token rule so we ignore them when building the OR predicate -- they cannot
# meaningfully gate the location any more than the parent region already does.
_MAJOR_DISTRICTS_BASE = frozenset({
    "Watson",
    "Westbrook",
    "City Center",
    "Heywood",
    "Santo Domingo",
    "Pacifica",
    "Badlands",
})
_MAJOR_DISTRICTS_DLC = frozenset({"Dogtown"})


def _apply_multi_region_rules(world: "Cyberpunk2077World", player: int) -> None:
    """
    Add reachability rules for locations that touch more than one district.

    For every location in ``location_table`` with ``len(regions) > 1`` we add an
    ``add_rule`` predicate requiring the player to be able to reach every
    listed major district. We restrict the predicate to known major-district
    Regions so locations whose ``regions`` include non-district areas (e.g.
    ``North Oak``) don't form a useless rule.

    Why AND (``all``) instead of OR? Multi-region locations represent quests
    that require the player to actually move between districts to complete the
    quest in-game, so the safe default is to require reach to every district
    listed. A permissive ``any`` would let generation place a key item on a
    multi-district location while only one district is reachable; the in-game
    check would never fire, creating a soft-lock. Quests with looser
    semantics can override this with their own ``set_rule`` higher up.

    The rule is only added when ``restrict_by_major_district`` is enabled --
    without it every district is reachable after the lifepath intro and the
    extra rule would be a no-op. We also skip locations that have been
    filtered out by the player's category/DLC options to avoid touching
    Locations that were never created.

    Subdistrict mode (``restrict_by_sub_district``) is intentionally not
    handled here: subdistrict tokens layer on top of the major-district
    token, so the major-district rule we add already covers reachability.
    If/when ``regions`` entries start naming subdistricts directly, this
    helper should be extended to recognise ``"<Major> - <Sub>"`` names.
    """
    if not world.options.restrict_by_major_district:
        return

    major_districts = set(_MAJOR_DISTRICTS_BASE)
    if world.options.include_phantom_liberty_dlc:
        major_districts |= _MAJOR_DISTRICTS_DLC

    # Snapshot of location names actually created for this player so we
    # silently skip rows filtered out by category/DLC options.
    existing_locations = {
        loc.name for loc in world.multiworld.get_locations(player)
    }

    for loc_data in location_table.values():
        if loc_data.code is None or len(loc_data.regions) <= 1:
            continue
        if loc_data.display_name not in existing_locations:
            continue

        applicable = tuple(r for r in loc_data.regions if r in major_districts)
        if not applicable:
            continue

        add_rule(
            world.multiworld.get_location(loc_data.display_name, player),
            lambda state, districts=applicable: all(
                state.can_reach_region(district, player) for district in districts
            ),
        )


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
