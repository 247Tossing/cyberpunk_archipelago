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

# Base ID for Cyberpunk 2077 location/item IDs
# Must match the base_id in __init__.py
BASE_ID = 2077000


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

# Location codes are OFFSETS that get added to base_id (2077000) when creating locations
# Codes stored here: 0-499 (offsets)
# Actual Archipelago IDs: 2077000-2077499 (base_id + offset)
# Organize locations by region/district for easier management

# Offset ranges by category:
# 1000-1999: Main quests (Prologue, Acts, Endings)
# 2000-2999: Side quests
# 3000-3999: Cyberpsycho Sightings
# 4000-4999: Gigs and NCPD Scanner Hustles
# 5000-5999: Reserved for future content

location_table: Dict[str, LocationData] = {
    # =================================
    # Main Quest Locations
    # =================================

    #==================================
    # Prologue Locations
    #==================================
    # NOTE: All 3 lifepath intros (Streetkid, Corpo, Nomad) map to this single location
    # Player only completes ONE lifepath per playthrough (can't restart to get all 3)
    # This ensures player doesn't need to replay game 3 times to complete all checks
    # The 3 internal IDs are manually mapped to this location below
    "Lifepath Chosen": LocationData(display_name="Lifepath Chosen", code=1000, region="Watson"),
    "Ending Reached" : LocationData(display_name="Ending Reached", code=1001, region="Watson"),
    # Tutorial might get re-added if requested
    #"q000_tutorial": LocationData(display_name="Prologue - Practice Makes Perfect", code=1003, region="Watson"),
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
    "02_sickness": LocationData(display_name="Endgame - Nocturne Op55N1", code=1027, region="Heywood"),
    "01_climbing_the_ladder": LocationData(display_name="Endgame - Become A Legend", code=1028, region="Watson"),
    "09_solo": LocationData(display_name="Endgame - (Don't Fear) The Reaper", code=1029, region="City Center"),

    # =====================================
    # Endings
    # =====================================
    "q113_rescuing_hanako": LocationData(display_name="Ending - Last Caress", code=1030, region="North Oak"),
    "q113_corpo": LocationData(display_name="Ending - Totalimmortal", code=1031, region="City Center"),
    "q114_01_nomad_initiation": LocationData(display_name="Ending - We Gotta Live Together", code=1032, region="Badlands"),
    "q114_02_maglev_line_assault": LocationData(display_name="Ending - Forward to Death", code=1033, region="Badlands"),
    "q114_03_attack_on_arasaka_tower": LocationData(display_name="Ending - Belly of the Beast", code=1034, region="City Center"),
    "q115_afterlife": LocationData(display_name="Ending - For Whom the Bell Tolls", code=1035, region="Watson"),
    "q115_rogues_last_flight": LocationData(display_name="Ending - Knockin' on Heaven's Door", code=1036,                                    region="City Center"),
    "q116_cyberspace": LocationData(display_name="Ending - Changes", code=1037, region="Watson"),

    # =====================================
    # Phantom Liberty Checks
    # (Only applicable w/DLC)
    # =====================================
    "q300_phantom_liberty": LocationData(display_name="Phantom Liberty - Phantom Liberty", code=1042, region="Dogtown"),
    "q301_crash": LocationData(display_name="Phantom Liberty - Dog Eat Dog", code=1043, region="Dogtown"),
    "q301_finding_myers": LocationData(display_name="Phantom Liberty - Hole in the Sky", code=1044, region="Dogtown"),
    "q301_q302_rescue_myers": LocationData(display_name="Phantom Liberty - Spider and the Fly", code=1045, region="Dogtown"),
    "q302_reed": LocationData(display_name="Phantom Liberty - Lucretia My Reflection", code=1046, region="Dogtown"),
    "q303_baron": LocationData(display_name="Phantom Liberty - The Damned", code=1047, region="Dogtown"),
    "q303_hands": LocationData(display_name="Phantom Liberty - Get It Together", code=1048, region="Dogtown"),
    "q303_songbird": LocationData(display_name="Phantom Liberty - You Know My Name", code=1049, region="Dogtown"),
    "q304_stadium": LocationData(display_name="Phantom Liberty - Birds with Broken Wings", code=1050, region="Dogtown"),
    "q304_netrunners": LocationData(display_name="Phantom Liberty - I've Seen That Face Before", code=1051, region="Dogtown"),
    "q304_deal": LocationData(display_name="Phantom Liberty - Firestarter", code=1052, region="Dogtown"),
    "q305_prison_convoy": LocationData(display_name="Phantom Liberty - Black Steel In The Hour of Chaos", code=1053, region="Dogtown"),
    "q305_bunker": LocationData(display_name="Phantom Liberty - Somewhat Damaged", code=1058, region="Dogtown"),
    "q305_border_crossing": LocationData(display_name="Phantom Liberty - Leave in Silence", code=1054, region="Dogtown"),
    "q306_devils_bargain": LocationData(display_name="Phantom Liberty - The Killing Moon", code=1055, region="Dogtown"),
    "q307_before_tomorrow": LocationData(display_name="Phantom Liberty - Who Wants to Live Forever", code=1056, region="Dogtown"),
    # =================================
    # Epilogues
    # =================================
    "q201_heir": LocationData(display_name="Epilogue - Where is My Mind?", code=1038, region="Watson"),
    "q202_nomads": LocationData(display_name="Epilogue - All Along the Watchtower", code=1039, region="Badlands"),
    "q203_legend": LocationData(display_name="Epilogue - Path of Glory", code=1040, region="Watson"),
    "q204_reborn": LocationData(display_name="Epilogue - New Dawn Fades", code=1041, region="Badlands"),
    "q307_tomorrow": LocationData(display_name="Phantom Liberty - Things Done Changed", code=1057, region="Dogtown"),

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
    # Tarot
    # =================================

    # =================================
    # Cyber Psycho Sighting Locations
    # ==================================
    "ma_wat_nid_22": LocationData(display_name="Cyberpsycho Sighting: Six Feet Under", code=3000, region="Watson"),
    "ma_wat_nid_15": LocationData(display_name="Cyberpsycho Sighting: Bloody Ritual", code=3001, region="Watson"),
    "ma_wat_nid_03": LocationData(display_name="Cyberpsycho Sighting: Where the Bodies Hit the Floor", code=3002, region="Watson"),
    "ma_wat_kab_02": LocationData(display_name="Cyberpsycho Sighting: Demons of War", code=3003, region="Watson"),
    "ma_wat_kab_08": LocationData(display_name="Cyberpsycho Sighting: Lt. Mower", code=3004, region="Watson"),
    "ma_wat_lch_06": LocationData(display_name="Cyberpsycho Sighting: Ticket to the Major Leagues", code=3005, region="Watson"),
    "ma_bls_ina_se1_07": LocationData(display_name="Cyberpsycho Sighting: The Wasteland",code=3006, region="Badlands"),
    "ma_bls_ina_se1_08": LocationData(display_name="Cyberpsycho Sighting: House on a Hill",code=3007, region="Badlands"),
    "ma_bls_ina_se1_22": LocationData(display_name="Cyberpsycho Sighting: Second Chances",code=3008, region="Badlands"),
    "ma_cct_dtn_03": LocationData(display_name="Cyberpsycho Sighting: On Deaf Ears",code=3009, region="City Center"),
    "ma_cct_dtn_07": LocationData(display_name="Cyberpsycho Sighting: Phantom of Night City", code=3010, region="City Center"),
    "ma_hey_spr_04": LocationData(display_name="Cyberpsycho Sighting: Seaside Cafe", code=3011, region="Heywood"),
    "ma_hey_spr_06": LocationData(display_name="Cyberpsycho Sighting: Letter of the Law", code=3012, region="Heywood"),
    "ma_pac_cvi_08": LocationData(display_name="Cyberpsycho Sighting: Smoke on the Water", code=3013, region="Pacifica"),
    "ma_pac_cvi_15": LocationData(display_name="Cyberpsycho Sighting: Lex Talionis",code=3014, region="Pacifica"),
    "ma_std_arr_06": LocationData(display_name="Cyberpsycho Sighting: Under the Bridge", code=3015, region="Santo Domingo"),
    "ma_std_rcr_11": LocationData(display_name="Cyberpsycho Sighting: Discount Doc", code=3016, region="Santo Domingo"),
    # =================================

    # =================================
    # Event Locations
    # =================================
    # Event locations have code=None and represent milestones or quest completions
    # They auto-complete when accessible and are used for internal logic

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

    # NOTE: Victory event location is created manually in regions.py, NOT here
    # Event locations created through location_table may get auto-assigned addresses
    # which prevents them from being properly filtered as events
}


# ===== DERIVED MAPPINGS =====
# These are automatically generated from location_table
# Don't modify these manually - they're computed based on location_table

# Dictionary mapping display names to their Archipelago codes
# Example: {"Prologue - The Streetkid": 1000, "Prologue - The Rescue": 1004, ...}
# Filters out event locations (code=None) to get only real locations
# This is used by Archipelago for location lookups and UI display
# Stores full Archipelago IDs (BASE_ID + offset) for server database
location_name_to_id: Dict[str, int] = {
    data.display_name: BASE_ID + data.code
    for name, data in location_table.items()
    if data.code is not None  # Exclude event locations
}

# Dictionary mapping internal game IDs to their display names
# Example: {"q000_street_kid": "Prologue - The Streetkid", ...}
# Use this to translate internal IDs from the game client to human-readable names
location_internal_id_to_display_name: Dict[str, str] = {
    name: data.display_name
    for name, data in location_table.items()
}

"""
Manual Mappings for multiples quests that result in the same thing, but require a major investment to be reached.
"""
location_internal_id_to_display_name["q000_street_kid"] = "Lifepath Chosen"
location_internal_id_to_display_name["q000_corpo"] = "Lifepath Chosen"
location_internal_id_to_display_name["q000_nomad"] = "Lifepath Chosen"




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

# Dictionary mapping Archipelago codes to display names (reverse lookup)
# Example: {1000: "Prologue - The Streetkid", 3000: "Cyberpsycho Sighting: Six Feet Under", ...}
# Bidirectional lookup - allows searching by code to get the display name
# Stores full Archipelago IDs (BASE_ID + offset) as keys for server database
location_id_to_name: Dict[int, str] = {
    BASE_ID + data.code: data.display_name
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
        location_id: The full Archipelago location ID (BASE_ID + offset)

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
        The full Archipelago location ID (BASE_ID + offset), or None if not found
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


def is_phantom_liberty_location(location_name: str) -> bool:
    """
    Check if a location is part of the Phantom Liberty DLC.

    Phantom Liberty locations are all in the Dogtown region.
    This helper function makes it easy to filter DLC content.

    Args:
        location_name: The location name to check

    Returns:
        True if the location is in Dogtown (Phantom Liberty DLC), False otherwise
    """
    location_data = location_table.get(location_name)
    if location_data is None:
        return False
    return location_data.region == "Dogtown"
