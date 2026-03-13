"""
Cyberpunk 2077 Location Definitions

This file defines all locations (checks) where items can be found in the game.

Locations represent specific spots in the game where the player can collect
randomized items. They have unique IDs for network communication and are
organized by region for easier management.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from BaseClasses import Location


class Cyberpunk2077Location(Location):
    """
    A location instance for Cyberpunk 2077.

    Extends the base Archipelago Location class to add game-specific identification.
    Each instance represents one check/location where an item can be placed.
    """
    game: str = "Cyberpunk 2077"  # Must match the game name in __init__.py


@dataclass
class LocationData:
    """
    Data class defining properties of a location type.

    Uses Python's @dataclass decorator to automatically generate common methods
    (__init__, __repr__, __eq__, etc.) from the field definitions.

    Attributes:
        display_name: Human-readable location name (e.g., "Prologue - StreetKid Intro")
        code: Unique numeric ID for network communication (e.g., 1000)
              Set to None for "event" locations that auto-complete
        region: Which region/area this location belongs to (e.g., "Watson")
    """
    display_name: str
    code: Optional[int]  # None for event locations
    region: str  # Which region this location is in


# ===== LOCATION TABLE =====
# This dictionary maps internal location IDs to their definitions
# Keys are internal game IDs (what the game client sends)
# Values contain display names, codes, and regions

# TODO: Replace these example locations with actual Cyberpunk 2077 locations
# The location codes should start at base_id + 1 and increment from there
# Organize locations by region/district for easier management

# ID's are sorted into prefixes so its simpler to add to later
# IDs starting with 1 are main quests
# IDs starting with 2 are side quests
# IDs starting with 3 are psychos

location_table: Dict[str, LocationData] = {
    # =================================
    # Main Quest Locations
    # =================================

# TODO: Make sure that the rules only use one of these checks during generation
    "q000_street_kid": LocationData(
        display_name="Prologue - StreetKid Intro",
        code=1000,
        region="Watson"
    ),

    "q000_corpo": LocationData(
        display_name="Prologue - Corpo Intro",
        code=1001,
        region="Watson"
    ),

    "q000_nomad": LocationData(
        display_name="Prologue - Nomad Intro",
        code=1002,
        region="Watson"
    ),

    "q001_01_victor": LocationData(
        display_name="Prologue - The Ripper Doc",
        code=1003,
        region="Watson"
    ),

    # =================================
    # Cyber Psycho Sighting Locations
    # ==================================
    "ma_wat_nid_22": LocationData(
        display_name="Cyberpsycho Sighting: Six Feet Under",
        code=3000,
        region="Watson"
    ),

    "ma_wat_nid_15": LocationData(
        display_name="Cyberpsycho Sighting: Bloody Ritual",
        code=3001,
        region="Watson"
    ),

    "ma_wat_nid_03": LocationData(
        display_name="Cyberpsycho Sighting: Where the Bodies Hit the Floor",
        code=3002,
        region="Watson"
    ),

    "ma_wat_kab_02": LocationData(
        display_name="Cyberpsycho Sighting: Demons of War",
        code=3003,
        region="Watson"
    ),

    "ma_wat_kab_08": LocationData(
        display_name="Cyberpsycho Sighting: Lt. Mower",
        code=3004,
        region="Watson"
    ),

    "ma_wat_lch_06": LocationData(
        display_name="Cyberpsycho Sighting: Ticket to the Major Leagues",
        code=3005,
        region="Watson"
    ),

    "ma_bls_ina_se1_07": LocationData(
        display_name="Cyberpsycho Sighting: The Wasteland",
        code=3006,
        region="Badlands"
    ),

    "ma_bls_ina_se1_08": LocationData(
        display_name="Cyberpsycho Sighting: House on a Hill",
        code=3007,
        region="Badlands"
    ),

    "ma_bls_ina_se1_22": LocationData(
        display_name="Cyberpsycho Sighting: Second Chances",
        code=3008,
        region="Badlands"
    ),

    "ma_cct_dtn_03": LocationData(
        display_name="Cyberpsycho Sighting: On Deaf Ears",
        code=3009,
        region="City Center"
    ),

    "ma_cct_dtn_07": LocationData(
        display_name="Cyberpsycho Sighting: Phantom of Night City",
        code=3010,
        region="City Center"
    ),

    "ma_hey_spr_04": LocationData(
        display_name="Cyberpsycho Sighting: Seaside Cafe",
        code=3011,
        region="Heywood"
    ),

    "ma_hey_spr_06": LocationData(
        display_name="Cyberpsycho Sighting: Letter of the Law",
        code=3012,
        region="Heywood"
    ),

    "ma_pac_cvi_08": LocationData(
        display_name="Cyberpsycho Sighting: Smoke on the Water",
        code=3013,
        region="Pacifica"
    ),

    "ma_pac_cvi_15": LocationData(
        display_name="Cyberpsycho Sighting: Lex Talionis",
        code=3014,
        region="Pacifica"
    ),

    "ma_std_arr_06": LocationData(
        display_name="Cyberpsycho Sighting: Under the Bridge",
        code=3015,
        region="Santo Domingo"
    ),

    "ma_std_rcr_11": LocationData(
        display_name="Cyberpsycho Sighting: Discount Doc",
        code=3016,
        region="Santo Domingo"
    ),
    # =================================

    # ===== EVENT LOCATIONS =====
    # Event locations don't have codes (code=None) and represent milestones
    # They auto-complete when accessible and are used for internal logic
    # Used to track game progression or achievements

    # Example: Major story progression points
    # "Act 1 Complete": LocationData(
    #     display_name="Act 1 Complete",
    #     code=None,  # No code = event location
    #     region="Menu"  # Event locations typically go in the Menu region
    # ),

    # "Reached Cyberpunk Ending": LocationData(
    #     display_name="Reached Cyberpunk Ending",
    #     code=None,
    #     region="Menu"
    # ),
}


# ===== DERIVED MAPPINGS =====
# These are automatically generated from location_table
# Don't modify these manually - they're computed based on location_table

# Dictionary mapping internal location IDs to their Archipelago codes
# Example: {"q000_street_kid": 1000, "ma_wat_nid_22": 3000, ...}
# Filters out event locations (code=None) to get only real locations
# This is what the game client should use for lookups
location_name_to_id: Dict[str, int] = {
    name: data.code
    for name, data in location_table.items()
    if data.code is not None  # Exclude event locations
}

# Dictionary mapping internal location IDs to their display names
# Example: {"q000_street_kid": "Prologue - StreetKid Intro", ...}
# Use this to show human-readable names in the UI
location_display_names: Dict[str, str] = {
    name: data.display_name
    for name, data in location_table.items()
}


# ===== LOCATION NAME GROUPS =====
# Groups allow players to reference multiple locations at once in their YAML
#
# Example YAML usage:
#   exclude_locations:
#     - Watson  # Exclude all Watson locations from having progression items
#   priority_locations:
#     - Main Quests  # Place important items at main quest locations first

# TODO: Add your location groups here
# Note: These use internal location IDs (the keys from location_table)
location_name_groups: Dict[str, List[str]] = {
    # Group by district
    "Watson": [
        "q000_street_kid",
        "q000_corpo",
        "q000_nomad",
        "q001_01_victor",
        "ma_wat_nid_22",
        "ma_wat_nid_15",
        "ma_wat_nid_03",
        "ma_wat_kab_02",
        "ma_wat_kab_08",
        "ma_wat_lch_06",
        # Add more Watson locations here
    ],

    "Badlands": [
        "ma_bls_ina_se1_07",
        "ma_bls_ina_se1_08",
        "ma_bls_ina_se1_22",
        # Add more Badlands locations here
    ],

    "City Center": [
        "ma_cct_dtn_03",
        "ma_cct_dtn_07",
        # Add more City Center locations here
    ],

    "Heywood": [
        "ma_hey_spr_04",
        "ma_hey_spr_06",
        # Add more Heywood locations here
    ],

    "Pacifica": [
        "ma_pac_cvi_08",
        "ma_pac_cvi_15",
        # Add more Pacifica locations here
    ],

    "Santo Domingo": [
        "ma_std_arr_06",
        "ma_std_rcr_11",
        # Add more Santo Domingo locations here
    ],

    # Group by type
    "Main Quests": [
        "q000_street_kid",
        "q000_corpo",
        "q000_nomad",
        "q001_01_victor",
        # Add more main quest locations here
    ],

    "Cyberpsycho Sightings": [
        "ma_wat_nid_22",
        "ma_wat_nid_15",
        "ma_wat_nid_03",
        "ma_wat_kab_02",
        "ma_wat_kab_08",
        "ma_wat_lch_06",
        "ma_bls_ina_se1_07",
        "ma_bls_ina_se1_08",
        "ma_bls_ina_se1_22",
        "ma_cct_dtn_03",
        "ma_cct_dtn_07",
        "ma_hey_spr_04",
        "ma_hey_spr_06",
        "ma_pac_cvi_08",
        "ma_pac_cvi_15",
        "ma_std_arr_06",
        "ma_std_rcr_11",
        # Add more cyberpsycho locations here
    ],
}


# ===== LOCATION LOOKUP DICTIONARIES =====
# Don't modify these manually - they're computed based on location_table

# Dictionary mapping Archipelago codes to internal location IDs (reverse lookup)
# Example: {1000: "q000_street_kid", 3000: "ma_wat_nid_22", ...}
# Bidirectional lookup - allows searching by code to get the internal ID
location_id_to_name: Dict[int, str] = {
    data.code: name
    for name, data in location_table.items()
    if data.code is not None  # Exclude event locations
}

# Dictionary mapping Archipelago codes to display names
# Example: {1000: "Prologue - StreetKid Intro", ...}
# Use this to show human-readable names when you only have the code
location_id_to_display_name: Dict[int, str] = {
    data.code: data.display_name
    for name, data in location_table.items()
    if data.code is not None  # Exclude event locations
}


# ===== HELPER FUNCTIONS =====

def get_location_name_by_id(location_id: int) -> Optional[str]:
    """
    Get a location's name by its Archipelago ID.

    Reverse lookup from numeric ID to location name. Useful when
    receiving location IDs over the network.

    Args:
        location_id: The Archipelago location ID

    Returns:
        The location name, or None if not found
    """
    return location_id_to_name.get(location_id, None)


def get_location_id_by_name(location_name: str) -> Optional[int]:
    """
    Get a location's Archipelago ID by its name.

    Forward lookup from location name to numeric ID. Useful when
    sending location information over the network.

    Args:
        location_name: The location name

    Returns:
        The Archipelago location ID, or None if not found
    """
    return location_name_to_id.get(location_name, None)


def get_locations_by_region(region_name: str) -> List[str]:
    """
    Get all internal location IDs in a specific region.

    Filters the location_table to find all locations belonging to
    a specific region.

    Args:
        region_name: The name of the region to filter by

    Returns:
        List of internal location IDs in that region
    """
    # List comprehension syntax:
    # [name for name, data in location_table.items() if data.region == region_name]
    #
    # This is equivalent to:
    # result = []
    # for name, data in location_table.items():
    #     if data.region == region_name:
    #         result.append(name)
    # return result

    return [
        name
        for name, data in location_table.items()
        if data.region == region_name
    ]


def get_event_locations() -> List[str]:
    """
    Get all event location names (locations with code=None).

    Event locations auto-complete when accessible and don't appear
    in the normal item pool.

    Returns:
        List of event location names
    """
    return [
        name
        for name, data in location_table.items()
        if data.code is None
    ]


def get_regular_locations() -> List[str]:
    """
    Get all regular location names (locations with a code).

    Regular locations are actual checks in the game where items
    can be placed.

    Returns:
        List of regular location names
    """
    return [
        name
        for name, data in location_table.items()
        if data.code is not None
    ]
