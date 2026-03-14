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

    #==================================
    # Prologue Locations
    #==================================

    # TODO: Make sure that the rules only use one of the path checks during generation
    "q000_street_kid": LocationData(display_name="Prologue - The Streetkid", code=1000, region="Watson"),
    "q000_corpo": LocationData(display_name="Prologue - The Corpo-Rat", code=1001, region="Watson"),
    "q000_nomad": LocationData(display_name="Prologue - The Nomad", code=1002, region="Watson"),
    "q000_tutorial": LocationData(display_name="Prologue - Practice Makes Perfect", code=1003, region="Watson"),
    "q001_intro": LocationData(display_name="Prologue - The Rescue", code=1004, region="Watson"),
    "q001_01_victor": LocationData(display_name="Prologue - The Ripperdoc", code=1005, region="Watson"),
    "q001_02_dex": LocationData(display_name="Prologue - The Ride", code=1006, region="Watson"),
    "q003_maelstrom": LocationData(display_name="Prologue - The Pickup", code=1007, region="Watson"),
    "q004_braindance": LocationData(display_name="Prologue - The Information", code=1008, region="Watson"),
    "q005_heist": LocationData(display_name="Prologue - The Heist", code=1009, region="Watson"),

    # =================================
    # Post-Heist Main Story
    # =================================
    "q101_01_firestorm": LocationData(display_name="Act 1 - Love Like Fire", code=1010, region="Watson"),
    "q101_resurrection": LocationData(display_name="Act 1 - Playing for Time", code=1011, region="Watson"),
    "q103_warhead": LocationData(display_name="Main - Ghost Town", code=1012, region="Badlands"),
    "q104_01_sabotage": LocationData(display_name="Main - Lightning Breaks", code=1013, region="Badlands"),
    "q104_02_av_chase": LocationData(display_name="Main - Life During Wartime", code=1014, region="Badlands"),
    "q105_dollhouse": LocationData(display_name="Main - Automatic Love", code=1015, region="Westbrook"),
    "q105_02_jigjig": LocationData(display_name="Main - The Space in Between", code=1016, region="Westbrook"),
    "q105_03_braindance_studio": LocationData(display_name="Main - Disasterpiece", code=1017, region="Santo Domingo"),
    "q105_04_judys": LocationData(display_name="Main - Double Life", code=1018, region="Watson"),
    "q110_01_voodooboys": LocationData(display_name="Main - M'ap Tann Pèlen", code=1019, region="Pacifica"),
    "q110_voodoo": LocationData(display_name="Main - I Walk the Line", code=1020, region="Pacifica"),
    "q110_03_cyberspace": LocationData(display_name="Main - Transmission", code=1021, region="Pacifica"),
    "q108_johnny": LocationData(display_name="Main - Never Fade Away", code=1022, region="Pacifica"),
    "q112_01_old_friend": LocationData(display_name="Main - Down on the Street", code=1023, region="City Center"),
    "q112_02_industrial_park": LocationData(display_name="Main - Gimme Danger", code=1024, region="Santo Domingo"),
    "q112_03_dashi_parade": LocationData(display_name="Main - Play It Safe", code=1025, region="Westbrook"),
    "q112_04_hideout": LocationData(display_name="Main - Search and Destroy", code=1026, region="Heywood"),

    # =====================================
    # Endings
    # =====================================
    "02_sickness": LocationData(display_name="Endgame - Nocturne Op55N1", code=1027, region="Heywood"),
    "01_climbing_the_ladder": LocationData(display_name="Endgame - Become A Legend", code=1028, region="Afterlife"),
    "09_solo": LocationData(display_name="Endgame - (Don't Fear) The Reaper", code=1029, region="City Center"),
    "q113_rescuing_hanako": LocationData(display_name="Ending - Last Caress", code=1030, region="North Oak"),
    "q113_corpo": LocationData(display_name="Ending - Totalimmortal", code=1031, region="City Center"),
    "q114_01_nomad_initiation": LocationData(display_name="Ending - We Gotta Live Together", code=1032, region="Badlands"),
    "q114_02_maglev_line_assault": LocationData(display_name="Ending - Forward to Death", code=1033, region="Badlands"),
    "q114_03_attack_on_arasaka_tower": LocationData(display_name="Ending - Belly of the Beast", code=1034,region="City Center"),
    "q115_afterlife": LocationData(display_name="Ending - For Whom the Bell Tolls", code=1035, region="Afterlife"),
    "q115_rogues_last_flight": LocationData(display_name="Ending - Knockin' on Heaven's Door", code=1036,                                    region="City Center"),
    "q116_cyberspace": LocationData(display_name="Ending - Changes", code=1037, region="Cyberspace"),
    "q201_heir": LocationData(display_name="Epilogue - Where is My Mind?", code=1038, region="Orbital Station"),
    "q202_nomads": LocationData(display_name="Epilogue - All Along the Watchtower", code=1039, region="Badlands"),
    "q203_legend": LocationData(display_name="Epilogue - Path of Glory", code=1040, region="Afterlife"),
    "q204_reborn": LocationData(display_name="Epilogue - New Dawn Fades", code=1041, region="Badlands"),

    # =====================================
    # Phantom Liberty Checks
    # (Only applicable w/DLC)
    # =====================================
    "q300_phantom_liberty": LocationData(display_name="DLC - Phantom Liberty", code=1042, region="Dogtown"),
    "q301_crash": LocationData(display_name="DLC - Dog Eat Dog", code=1043, region="Dogtown"),
    "q301_finding_myers": LocationData(display_name="DLC - Hole in the Sky", code=1044, region="Dogtown"),
    "q301_q302_rescue_myers": LocationData(display_name="DLC - Spider and the Fly", code=1045, region="Dogtown"),
    "q302_reed": LocationData(display_name="DLC - Lucretia My Reflection", code=1046, region="Dogtown"),
    "q303_baron": LocationData(display_name="DLC - The Damned", code=1047, region="Dogtown"),
    "q303_hands": LocationData(display_name="DLC - Get It Together", code=1048, region="Dogtown"),
    "q303_songbird": LocationData(display_name="DLC - You Know My Name", code=1049, region="Dogtown"),
    "q304_stadium": LocationData(display_name="DLC - Birds with Broken Wings", code=1050, region="Dogtown"),
    "q304_netrunners": LocationData(display_name="DLC - I've Seen That Face Before", code=1051, region="Dogtown"),
    "q304_deal": LocationData(display_name="DLC - Firestarter", code=1052, region="Dogtown"),
    "q305_prison_convoy": LocationData(display_name="DLC - Black Steel In The Hour of Chaos", code=1053, region="Dogtown"),
    "q305_bunker": LocationData(display_name="DLC - Somewhat Damaged", code=10, region="Dogtown"),
    "q305_border_crossing": LocationData(display_name="DLC - Leave in Silence", code=1054, region="Dogtown"),
    "q306_devils_bargain": LocationData(display_name="DLC - The Killing Moon", code=1055, region="Dogtown"),
    "q307_before_tomorrow": LocationData(display_name="DLC - Who Wants to Live Forever", code=1056, region="Dogtown"),
    "q307_tomorrow": LocationData(display_name="DLC - Things Done Changed", code=1057, region="Dogtown"),

    # =================================
    # Side Quests
    # =================================

    # =================================
    # Gigs
    # =================================

    # =================================
    # Unique Item Checks
    # =================================

    # =================================
    # Progression Checks
    # =================================

    # =================================
    # Tarot Cards
    # =================================

    # =================================
    #
    # =================================

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


# ===== LOCATION NAME GROUPS =====
# Auto-generated groups based on region and ID ranges (quest type)
# Players can use these in YAML to reference multiple locations at once

def _build_location_name_groups() -> Dict[str, List[str]]:
    """
    Automatically build location name groups from location_table.

    Groups are generated based on:
    - Region (Watson, City Center, Heywood, Pacifica, Santo Domingo, Badlands)
    - ID ranges indicating quest type:
      * 1000-1999: Main Quests
      * 2000-2999: Side Quests
      * 3000-3999: Cyberpsycho Sightings

    Returns:
        Dictionary mapping group names to lists of location internal IDs
    """
    groups: Dict[str, List[str]] = {}

    # Group by region
    regions: Dict[str, List[str]] = {}
    for loc_name, loc_data in location_table.items():
        if loc_data.code is None:
            continue  # Skip event locations

        # Add to region group
        if loc_data.region not in regions:
            regions[loc_data.region] = []
        regions[loc_data.region].append(loc_name)

    # Add all region groups
    groups.update(regions)

    # Group by ID range (quest type)
    main_quests = []
    side_quests = []
    cyberpsychos = []

    for loc_name, loc_data in location_table.items():
        if loc_data.code is None:
            continue  # Skip event locations

        # Categorize by ID range
        if 1000 <= loc_data.code < 2000:
            main_quests.append(loc_name)
        elif 2000 <= loc_data.code < 3000:
            side_quests.append(loc_name)
        elif 3000 <= loc_data.code < 4000:
            cyberpsychos.append(loc_name)

    # Add quest type groups only if they have locations
    if main_quests:
        groups["Main Quests"] = main_quests
    if side_quests:
        groups["Side Quests"] = side_quests
    if cyberpsychos:
        groups["Cyberpsycho Sightings"] = cyberpsychos

    return groups

# Generate location name groups automatically
location_name_groups: Dict[str, List[str]] = _build_location_name_groups()


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
