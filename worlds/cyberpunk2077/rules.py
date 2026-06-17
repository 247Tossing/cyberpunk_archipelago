"""
Cyberpunk 2077 Access Rules
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, TypeAlias
from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule
from .locations import location_table, LocationCategory
from .options import CompletionGoal, get_gated_major_districts, has_effective_phantom_liberty_dlc, is_goal_all_side_quests

if TYPE_CHECKING:
    from . import Cyberpunk2077World


@dataclass(frozen=True)
class PrereqAny:
    """Represents an OR dependency over location names."""

    names: tuple[str, ...]


Prerequisite: TypeAlias = str | tuple[str, ...] | PrereqAny


def any_of(*names: str) -> PrereqAny:
    return PrereqAny(tuple(names))


# Base questline + default ending dependencies.
BASE_LOCATION_PREREQUISITES: dict[str, Prerequisite] = {
    "Prologue - The Ripperdoc": "Prologue - The Rescue",
    "Prologue - The Ride": "Prologue - The Ripperdoc",
    "Prologue - The Heist": ("Prologue - The Pickup", "Prologue - The Information"),
    "Prologue - Love Like Fire": "Prologue - The Heist",
    "Main - Playing for Time": "Prologue - Love Like Fire",
    "Main - Automatic Love": "Main - Playing for Time",
    "Main - Transmission": "Main - Automatic Love",
    "Main - Ghost Town": "Main - Playing for Time",
    "Main - Life During Wartime": "Main - Ghost Town",
    "Main - Down on the Street": "Main - Playing for Time",
    "Main - Search and Destroy": "Main - Down on the Street",
    "Point of No Return - Nocturne Op55N1": (
        "Main - Transmission",
        "Main - Life During Wartime",
        "Main - Search and Destroy",
    ),
    "Ending Reached": "Point of No Return - Nocturne Op55N1",
}

# Additional requirements only used in "all side quests" goal mode.
SIDE_QUEST_GOAL_PREREQUISITES: dict[str, Prerequisite] = {
    "Riders on the Storm": "Main - Life During Wartime",
    "Queen of the Highway": "Riders on the Storm",
    "Chippin' In": "Main - Search and Destroy",
    "Blistering Love": "Chippin' In",
}

# Phantom Liberty-only questline requirements.
PHANTOM_LIBERTY_ONLY_PREREQUISITES: dict[str, Prerequisite] = {
    "Phantom Liberty - Phantom Liberty": "Lifepath Chosen",
    "Phantom Liberty - Dog Eat Dog": "Phantom Liberty - Phantom Liberty",
    "Phantom Liberty - Hole in the Sky": "Phantom Liberty - Dog Eat Dog",
    "Phantom Liberty - Spider and the Fly": "Phantom Liberty - Hole in the Sky",
    "Phantom Liberty - Lucretia My Reflection": "Phantom Liberty - Spider and the Fly",
    "Phantom Liberty - The Damned": "Phantom Liberty - Lucretia My Reflection",
    "Phantom Liberty - Get It Together": "Phantom Liberty - The Damned",
    "Phantom Liberty - You Know My Name": "Phantom Liberty - Get It Together",
    "Phantom Liberty - Birds with Broken Wings": "Phantom Liberty - You Know My Name",
    "Phantom Liberty - I've Seen That Face Before": "Phantom Liberty - Birds with Broken Wings",
    "Phantom Liberty - Firestarter": "Phantom Liberty - I've Seen That Face Before",
    "PL - Split Quest 1": "Phantom Liberty - Firestarter",
    "PL - Split Quest 2": "Phantom Liberty - Firestarter",
    "PL - Split Quest 3": "Phantom Liberty - Firestarter",
    "Phantom Liberty - Who Wants to Live Forever": any_of(
        "PL - Split Quest 1",
        "PL - Split Quest 2",
        "PL - Split Quest 3",
    ),
    "Ending Reached": "Phantom Liberty - Who Wants to Live Forever",
}


# Stable exported prerequisite catalog (source of truth for tests and rules).
LOCATION_PREREQUISITES: dict[str, dict[str, Prerequisite]] = {
    "base": BASE_LOCATION_PREREQUISITES,
    "all_side_quests": SIDE_QUEST_GOAL_PREREQUISITES,
    "phantom_liberty_only": PHANTOM_LIBERTY_ONLY_PREREQUISITES,
}

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

    _apply_location_prerequisites(world, player, _get_goal_location_prerequisites(world))

    _apply_vendor_rules(world, player)
    _apply_multi_region_rules(world, player)
    _set_victory_rule(world, player)

    world.multiworld.completion_condition[player] = lambda state: state.has("Victory", player)


def _completion_goal(world: "Cyberpunk2077World") -> int:
    return int(world.options.completion_goal.value)


def _get_goal_location_prerequisites(world: "Cyberpunk2077World") -> dict[str, Prerequisite]:
    goal = _completion_goal(world)
    if goal == CompletionGoal.option_complete_only_phantom_liberty_questline:
        return dict(LOCATION_PREREQUISITES["phantom_liberty_only"])

    edges = dict(LOCATION_PREREQUISITES["base"])
    if is_goal_all_side_quests(world.options):
        edges.update(LOCATION_PREREQUISITES["all_side_quests"])
    return edges


def get_active_location_prerequisites(world: "Cyberpunk2077World") -> dict[str, Prerequisite]:
    """
    Return active location prerequisite edges for the configured world/options.

    This mirrors the rule application behavior and filters out prerequisite rules
    for locations not present in the generated location set.
    """
    player = world.player
    edges = _get_goal_location_prerequisites(world)
    edges.update(_get_vendor_location_prerequisites(world))
    return {
        location_name: required
        for location_name, required in edges.items()
        if _location_exists(world, player, location_name)
    }


def _build_prerequisite_rule(required: Prerequisite, player: int) -> Callable[[CollectionState], bool]:
    if isinstance(required, PrereqAny):
        return lambda state, reqs=required.names: any(state.can_reach_location(req, player) for req in reqs)
    if isinstance(required, tuple):
        return lambda state, reqs=required: all(state.can_reach_location(req, player) for req in reqs)
    return lambda state, req=required: state.can_reach_location(req, player)


def _apply_location_prerequisites(
    world: "Cyberpunk2077World",
    player: int,
    edges: dict[str, Prerequisite],
) -> None:
    for location_name, required in edges.items():
        if not _location_exists(world, player, location_name):
            continue
        set_rule(
            world.multiworld.get_location(location_name, player),
            _build_prerequisite_rule(required, player),
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
    _apply_location_prerequisites(world, player, _get_vendor_location_prerequisites(world))


def _get_vendor_location_prerequisites(world: "Cyberpunk2077World") -> dict[str, Prerequisite]:
    if not bool(world.options.vendor_sanity.value):
        return {}

    subtype_option_map = {
        "ripperdoc": world.options.vendor_ripperdocs,
        "gunsmith": world.options.vendor_gunsmiths,
        "clothing": world.options.vendor_clothing,
        "melee": world.options.vendor_melee,
        "netrunner": world.options.vendor_netrunners,
    }
    edges: dict[str, Prerequisite] = {}
    for internal_key in VENDOR_CHECK_INTERNAL_KEYS:
        loc_data = location_table[internal_key]
        subtype = loc_data.vendor_subtype
        if subtype and not subtype_option_map.get(subtype):
            continue
        edges[loc_data.display_name] = "Prologue - The Ripperdoc"
    return edges


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
