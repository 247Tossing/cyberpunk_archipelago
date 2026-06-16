"""
Cyberpunk 2077 Access Rules
"""

from typing import TYPE_CHECKING
from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule
from .locations import location_table, LocationCategory
from .options import CompletionGoal, get_gated_major_districts, has_effective_phantom_liberty_dlc, is_goal_all_side_quests

if TYPE_CHECKING:
    from . import Cyberpunk2077World

# Internal ``location_table`` keys ``VendorCheck_*`` (sorted for stable slot_data order).
# Archipelago Location.name is each row's ``display_name``; rules and slot_data resolve that from here.
VENDOR_CHECK_INTERNAL_KEYS = tuple(
    sorted(
        (
            name
            for name, data in location_table.items()
            if data.category == LocationCategory.VENDOR and data.code is not None
        ),
        key=lambda name: (location_table[name].display_name, name),
    )
)


def set_rules(world: "Cyberpunk2077World") -> None:
    """Set location and victory rules for the selected completion goal."""
    player = world.player

    if _completion_goal(world) == CompletionGoal.option_complete_only_phantom_liberty_questline:
        _set_phantom_liberty_only_rules(world, player)
    else:
        _set_base_game_rules(world, player)

    _apply_vendor_rules(world, player)
    _apply_multi_region_rules(world, player)
    _set_victory_rule(world, player)

    world.multiworld.completion_condition[player] = lambda state: state.has("Victory", player)


def _completion_goal(world: "Cyberpunk2077World") -> int:
    return int(world.options.completion_goal.value)


def _set_base_game_rules(world: "Cyberpunk2077World", player: int) -> None:
    """Apply existing base-game progression logic."""
    set_rule(
        world.multiworld.get_location("Prologue - The Ripperdoc", player),
        lambda state: state.can_reach_location("Prologue - The Rescue", player),
    )
    set_rule(
        world.multiworld.get_location("Prologue - The Ride", player),
        lambda state: state.can_reach_location("Prologue - The Ripperdoc", player),
    )
    set_rule(
        world.multiworld.get_location("Prologue - The Heist", player),
        lambda state: (
            state.can_reach_location("Prologue - The Pickup", player) and
            state.can_reach_location("Prologue - The Information", player)
        ),
    )
    set_rule(
        world.multiworld.get_location("Prologue - Love Like Fire", player),
        lambda state: state.can_reach_location("Prologue - The Heist", player),
    )
    set_rule(
        world.multiworld.get_location("Main - Playing for Time", player),
        lambda state: state.can_reach_location("Prologue - Love Like Fire", player),
    )

    set_rule(
        world.multiworld.get_location("Main - Automatic Love", player),
        lambda state: state.can_reach_location("Main - Playing for Time", player),
    )
    set_rule(
        world.multiworld.get_location("Main - Transmission", player),
        lambda state: state.can_reach_location("Main - Automatic Love", player),
    )
    set_rule(
        world.multiworld.get_location("Main - Ghost Town", player),
        lambda state: state.can_reach_location("Main - Playing for Time", player),
    )
    set_rule(
        world.multiworld.get_location("Main - Life During Wartime", player),
        lambda state: state.can_reach_location("Main - Ghost Town", player),
    )
    set_rule(
        world.multiworld.get_location("Main - Down on the Street", player),
        lambda state: state.can_reach_location("Main - Playing for Time", player),
    )
    set_rule(
        world.multiworld.get_location("Main - Search and Destroy", player),
        lambda state: state.can_reach_location("Main - Down on the Street", player),
    )
    set_rule(
        world.multiworld.get_location("Point of No Return - Nocturne Op55N1", player),
        lambda state: (
            state.can_reach_location("Main - Transmission", player) and
            state.can_reach_location("Main - Life During Wartime", player) and
            state.can_reach_location("Main - Search and Destroy", player)
        ),
    )
    set_rule(
        world.multiworld.get_location("Ending Reached", player),
        lambda state: state.can_reach_location("Point of No Return - Nocturne Op55N1", player),
    )

    if is_goal_all_side_quests(world.options):
        set_rule(
            world.multiworld.get_location("Riders on the Storm", player),
            lambda state: state.can_reach_location("Main - Life During Wartime", player),
        )
        set_rule(
            world.multiworld.get_location("Queen of the Highway", player),
            lambda state: state.can_reach_location("Riders on the Storm", player),
        )
        set_rule(
            world.multiworld.get_location("Chippin' In", player),
            lambda state: state.can_reach_location("Main - Search and Destroy", player),
        )
        set_rule(
            world.multiworld.get_location("Blistering Love", player),
            lambda state: state.can_reach_location("Chippin' In", player),
        )


def _set_phantom_liberty_only_rules(world: "Cyberpunk2077World", player: int) -> None:
    """Apply PL questline progression for PL-only completion goal."""
    _set_rule_if_present(world, player, "Phantom Liberty - Phantom Liberty", "Lifepath Chosen")
    _set_rule_if_present(world, player, "Phantom Liberty - Dog Eat Dog", "Phantom Liberty - Phantom Liberty")
    _set_rule_if_present(world, player, "Phantom Liberty - Hole in the Sky", "Phantom Liberty - Dog Eat Dog")
    _set_rule_if_present(world, player, "Phantom Liberty - Spider and the Fly", "Phantom Liberty - Hole in the Sky")
    _set_rule_if_present(world, player, "Phantom Liberty - Lucretia My Reflection", "Phantom Liberty - Spider and the Fly")
    _set_rule_if_present(world, player, "Phantom Liberty - The Damned", "Phantom Liberty - Lucretia My Reflection")
    _set_rule_if_present(world, player, "Phantom Liberty - Get It Together", "Phantom Liberty - The Damned")
    _set_rule_if_present(world, player, "Phantom Liberty - You Know My Name", "Phantom Liberty - Get It Together")
    _set_rule_if_present(world, player, "Phantom Liberty - Birds with Broken Wings", "Phantom Liberty - You Know My Name")
    _set_rule_if_present(world, player, "Phantom Liberty - I've Seen That Face Before", "Phantom Liberty - Birds with Broken Wings")
    _set_rule_if_present(world, player, "Phantom Liberty - Firestarter", "Phantom Liberty - I've Seen That Face Before")
    _set_rule_if_present(world, player, "PL - Split Quest 1", "Phantom Liberty - Firestarter")
    _set_rule_if_present(world, player, "PL - Split Quest 2", "Phantom Liberty - Firestarter")
    _set_rule_if_present(world, player, "PL - Split Quest 3", "Phantom Liberty - Firestarter")

    if _location_exists(world, player, "Phantom Liberty - Who Wants to Live Forever"):
        set_rule(
            world.multiworld.get_location("Phantom Liberty - Who Wants to Live Forever", player),
            lambda state: (
                state.can_reach_location("PL - Split Quest 1", player) or
                state.can_reach_location("PL - Split Quest 2", player) or
                state.can_reach_location("PL - Split Quest 3", player)
            ),
        )

    if _location_exists(world, player, "Ending Reached"):
        set_rule(
            world.multiworld.get_location("Ending Reached", player),
            lambda state: state.can_reach_location("Phantom Liberty - Who Wants to Live Forever", player),
        )


def _set_victory_rule(world: "Cyberpunk2077World", player: int) -> None:
    victory_location = world.multiworld.get_location("Victory", player)
    goal = _completion_goal(world)

    if goal == CompletionGoal.option_complete_any_ending_w_all_side_quests:
        side_quest_locations = tuple(_get_required_side_quest_locations(world, player))
        set_rule(
            victory_location,
            lambda state, required=side_quest_locations: (
                state.can_reach_location("Ending Reached", player) and
                all(state.can_reach_location(name, player) for name in required)
            ),
        )
        return

    set_rule(
        victory_location,
        lambda state: state.can_reach_location("Ending Reached", player),
    )


def _apply_vendor_rules(world: "Cyberpunk2077World", player: int) -> None:
    if not bool(world.options.vendor_sanity.value):
        return

    subtype_option_map = {
        "ripperdoc": world.options.vendor_ripperdocs,
        "gunsmith":  world.options.vendor_gunsmiths,
        "clothing":  world.options.vendor_clothing,
        "melee":     world.options.vendor_melee,
        "netrunner": world.options.vendor_netrunners,
    }

    for internal_key in VENDOR_CHECK_INTERNAL_KEYS:
        loc_data = location_table[internal_key]
        subtype = loc_data.vendor_subtype
        if subtype and not subtype_option_map.get(subtype):
            continue
        display_name = loc_data.display_name
        _set_rule_if_present(world, player, display_name, "Prologue - The Ripperdoc")


def _get_required_side_quest_locations(world: "Cyberpunk2077World", player: int) -> list[str]:
    """Collect included SIDE_QUEST / DLC_SIDE checks for all-side-quests goal."""
    included_names = {loc.name for loc in world.multiworld.get_locations(player)}
    required: list[str] = []

    for data in location_table.values():
        if data.display_name not in included_names:
            continue
        if data.category == LocationCategory.SIDE_QUEST:
            required.append(data.display_name)
        elif data.category == LocationCategory.DLC_SIDE and has_effective_phantom_liberty_dlc(world.options):
            required.append(data.display_name)

    return required


def _set_rule_if_present(world: "Cyberpunk2077World", player: int, location_name: str, required_location: str) -> None:
    if not _location_exists(world, player, location_name):
        return
    set_rule(
        world.multiworld.get_location(location_name, player),
        lambda state, req=required_location: state.can_reach_location(req, player),
    )


def _location_exists(world: "Cyberpunk2077World", player: int, location_name: str) -> bool:
    return any(loc.name == location_name for loc in world.multiworld.get_locations(player))

# ===== MULTI-REGION HELPERS =====

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
    listed gated major district. A permissive ``any`` would let generation
    place a key item on a multi-district location while only one gated district
    is reachable; the in-game check would never fire, creating a soft-lock.
    Quests with looser semantics can override this with their own ``set_rule``
    higher up.

    The rule is only added for selected gated majors. Non-gated districts are
    intentionally ignored because the client auto-opens those districts from
    slot-data during sync.

    Subdistrict mode (``restrict_by_sub_district``) is intentionally not
    handled here: subdistrict tokens layer on top of the major-district
    token, so the major-district rule we add already covers reachability.
    If/when ``regions`` entries start naming subdistricts directly, this
    helper should be extended to recognise ``"<Major> - <Sub>"`` names.
    """
    gated_major_districts = set(get_gated_major_districts(world.options))
    if not gated_major_districts:
        return

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

        applicable = tuple(r for r in loc_data.regions if r in gated_major_districts)
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
