"""
Cyberpunk 2077 Region Definitions
"""

from typing import Dict, TYPE_CHECKING
from BaseClasses import Region, Entrance, LocationProgressType
from .locations import Cyberpunk2077Location, location_table, LocationCategory
from .options import (
    has_effective_phantom_liberty_dlc,
    is_goal_all_side_quests,
    is_goal_phantom_liberty_only,
    is_major_district_token_gated,
)
from worlds.generic.Rules import set_rule

# TYPE_CHECKING is used for type hints without circular imports
# This allows us to reference Cyberpunk2077World for type hints without actually importing it
if TYPE_CHECKING:
    from . import Cyberpunk2077World


MAJOR_DISTRICT_TOKEN_REQUIREMENTS = (
    ("Westbrook", "Westbrook Access Token"),
    ("City Center", "City Center Access Token"),
    ("Heywood", "Heywood Access Token"),
    ("Santo Domingo", "Santo Domingo Access Token"),
    ("Pacifica", "Pacifica Access Token"),
    ("Badlands", "Badlands Access Token"),
    ("Dogtown", "Dogtown Access Token"),
)

SUBDISTRICT_TOKEN_REQUIREMENTS = (
    ("Westbrook - Japantown", "Westbrook", "Westbrook Access Token", "Westbrook Japantown Access Token"),
    ("Westbrook - Charter Hill", "Westbrook", "Westbrook Access Token", "Westbrook Charter Hill Access Token"),
    ("Westbrook - North Oak", "Westbrook", "Westbrook Access Token", "Westbrook North Oak Access Token"),
    ("City Center - Corpo Plaza", "City Center", "City Center Access Token", "City Center Corpo Plaza Access Token"),
    ("City Center - Downtown", "City Center", "City Center Access Token", "City Center Downtown Access Token"),
    ("Heywood - Wellsprings", "Heywood", "Heywood Access Token", "Heywood Wellsprings Access Token"),
    ("Heywood - The Glen", "Heywood", "Heywood Access Token", "Heywood The Glen Access Token"),
    ("Heywood - Vista del Rey", "Heywood", "Heywood Access Token", "Heywood Vista Del Rey Access Token"),
    ("Santo Domingo - Arroyo", "Santo Domingo", "Santo Domingo Access Token", "Santo Domingo Arroyo Access Token"),
    (
        "Santo Domingo - Rancho Coronado",
        "Santo Domingo",
        "Santo Domingo Access Token",
        "Santo Domingo Rancho Coronado Access Token",
    ),
    ("Pacifica - Coastview", "Pacifica", "Pacifica Access Token", "Pacifica Coastview Access Token"),
    ("Pacifica - West Wind Estate", "Pacifica", "Pacifica Access Token", "Pacifica West Wind Estate Access Token"),
    ("Badlands - Biotechnica Flats", "Badlands", "Badlands Access Token", "Badlands Biotechnica Flats Access Token"),
    ("Badlands - Jackson Plains", "Badlands", "Badlands Access Token", "Badlands Jackson Plains Access Token"),
    ("Badlands - Laguna Bend", "Badlands", "Badlands Access Token", "Badlands Laguna Bend Access Token"),
    ("Badlands - Red Peaks", "Badlands", "Badlands Access Token", "Badlands Red Peaks Access Token"),
    ("Badlands - Rocky Ridge", "Badlands", "Badlands Access Token", "Badlands Rocky Ridge Access Token"),
    ("Badlands - Sierra Sonora", "Badlands", "Badlands Access Token", "Badlands Sierra Sonora Access Token"),
    ("Badlands - SoCal Badlands", "Badlands", "Badlands Access Token", "Badlands SoCal Badlands Access Token"),
    ("Badlands - Yucca", "Badlands", "Badlands Access Token", "Badlands Yucca Access Token"),
    ("Badlands - Morro Rock", "Badlands", "Badlands Access Token", "Badlands Morro Rock Access Token"),
)


def create_regions(world: "Cyberpunk2077World") -> None:
    """
    Create all regions for this world and connect them.
    Args:
        world: The Cyberpunk2077World instance for this player
    """
    effective_dlc_enabled = has_effective_phantom_liberty_dlc(world.options)

    # ===== CREATE MENU REGION =====
    # The Menu region is required by Archipelago
    # It represents the starting point before entering the game
    # We create it manually because it needs special handling for the Victory event

    menu_region = Region("Menu", world.player, world.multiworld)
    world.multiworld.regions.append(menu_region)

    # Create Victory event location manually (NOT from location_table)
    # Event locations created through location_table may get auto-assigned addresses
    # Creating manually ensures address stays None and filters properly
    victory_location = Cyberpunk2077Location(
        world.player,
        "Victory",
        None,  # Event location - no address
        menu_region
    )
    # Place the Victory event item on the Victory event location
    victory_location.place_locked_item(world.create_event("Victory"))
    # Add to region so it can be found by get_location() in rules.py
    menu_region.locations.append(victory_location)

    # ===== CREATE GAME REGIONS =====
    # These represent actual areas in Cyberpunk 2077 (Night City districts)
    # Each region is a container for locations (item checks) in that area

    # Dictionary to store regions for easy reference
    regions: Dict[str, Region] = {
        "Menu": menu_region
    }

    # ===== CREATE MAIN DISTRICT REGIONS =====
    # Watson - Starting district (no restrictions)
    watson = create_region(world, "Watson")
    regions["Watson"] = watson

    # Other main districts
    westbrook = create_region(world, "Westbrook")
    regions["Westbrook"] = westbrook

    city_center = create_region(world, "City Center")
    regions["City Center"] = city_center

    heywood = create_region(world, "Heywood")
    regions["Heywood"] = heywood

    santo_domingo = create_region(world, "Santo Domingo")
    regions["Santo Domingo"] = santo_domingo

    pacifica = create_region(world, "Pacifica")
    regions["Pacifica"] = pacifica

    badlands = create_region(world, "Badlands")
    regions["Badlands"] = badlands

    # ===== CREATE SPECIAL REGIONS =====
    afterlife = create_region(world, "Afterlife")
    regions["Afterlife"] = afterlife

    cyberspace = create_region(world, "Cyberspace")
    regions["Cyberspace"] = cyberspace

    orbital_station = create_region(world, "Orbital Station")
    regions["Orbital Station"] = orbital_station

    north_oak = create_region(world, "North Oak")
    regions["North Oak"] = north_oak

    # ===== CREATE SUBDISTRICT REGIONS (if restriction enabled) =====
    if world.options.restrict_by_sub_district:
        # Watson Subdistricts
        for subdistrict in ["Arasaka Waterfront", "Northside", "Little China", "Kabuki"]:
            region = create_region(world, f"Watson - {subdistrict}")
            regions[f"Watson - {subdistrict}"] = region

        # Westbrook Subdistricts
        for subdistrict in ["Japantown", "North Oak", "Charter Hill"]:
            region = create_region(world, f"Westbrook - {subdistrict}")
            regions[f"Westbrook - {subdistrict}"] = region

        # City Center Subdistricts
        for subdistrict in ["Downtown", "Corpo Plaza"]:
            region = create_region(world, f"City Center - {subdistrict}")
            regions[f"City Center - {subdistrict}"] = region

        # Heywood Subdistricts
        for subdistrict in ["Wellsprings", "The Glen", "Vista del Rey"]:
            region = create_region(world, f"Heywood - {subdistrict}")
            regions[f"Heywood - {subdistrict}"] = region

        # Santo Domingo Subdistricts
        for subdistrict in ["Arroyo", "Rancho Coronado"]:
            region = create_region(world, f"Santo Domingo - {subdistrict}")
            regions[f"Santo Domingo - {subdistrict}"] = region

        # Pacifica Subdistricts
        for subdistrict in ["Coastview", "West Wind Estate"]:
            region = create_region(world, f"Pacifica - {subdistrict}")
            regions[f"Pacifica - {subdistrict}"] = region

        # Badlands Subdistricts (9 total)
        badlands_subs = [
            "Biotechnica Flats", "Jackson Plains", "Laguna Bend",
            "Red Peaks", "Rocky Ridge", "Sierra Sonora",
            "SoCal Badlands", "Yucca", "Morro Rock"
        ]
        for subdistrict in badlands_subs:
            region = create_region(world, f"Badlands - {subdistrict}")
            regions[f"Badlands - {subdistrict}"] = region

    # ===== CREATE DLC REGIONS (if DLC enabled) =====
    if effective_dlc_enabled:
        dogtown = create_region(world, "Dogtown")
        regions["Dogtown"] = dogtown

        morro_rock = create_region(world, "Morro Rock")
        regions["Morro Rock"] = morro_rock

    # ===== CONNECT REGIONS =====
    # Define how regions are connected (which areas lead to which areas)
    # Each connection is one-way, so you need two entrances for two-way travel

    # Connect Menu to the starting region (Watson in this example)
    # This is the initial "New Game" entrance
    connect_regions(world, menu_region, regions["Watson"], "New Game")

    # Watson connections
    connect_regions(world, regions["Watson"], regions["Westbrook"], "Watson to Westbrook")
    connect_regions(world, regions["Watson"], regions["City Center"], "Watson to City Center")

    # Watson Sub-Districts
    if world.options.restrict_by_sub_district:
        watson_subs = ["Watson - Arasaka Waterfront", "Watson - Northside", "Watson - Little China", "Watson - Kabuki"]
        for start in watson_subs:
            for end in watson_subs:
                if start != end:
                    connect_regions(world, regions[start], regions[end], f"{start} to {end}")

        # Bridge connections from Watson to other districts
        connect_regions(world, regions["Watson - Little China"], regions["City Center - Downtown"],
                        "Little China to Downtown")
        connect_regions(world, regions["Watson - Kabuki"], regions["Westbrook - Japantown"], "Kabuki to Japantown")

    # Westbrook connections
    connect_regions(world, regions["Westbrook"], regions["Watson"], "Westbrook to Watson")
    connect_regions(world, regions["Westbrook"], regions["City Center"], "Westbrook to City Center")
    connect_regions(world, regions["Westbrook"], regions["Heywood"], "Westbrook to Heywood")
    connect_regions(world, regions["Westbrook"], regions["Santo Domingo"], "Westbrook to Santo Domingo")
    connect_regions(world, regions["Westbrook"], regions["Badlands"], "Westbrook to Badlands")

    # City Center connections
    connect_regions(world, regions["City Center"], regions["Watson"], "City Center to Watson")
    connect_regions(world, regions["City Center"], regions["Westbrook"], "City Center to Westbrook")
    connect_regions(world, regions["City Center"], regions["Heywood"], "City Center to Heywood")

    # Heywood connections
    connect_regions(world, regions["Heywood"], regions["City Center"], "Heywood to City Center")
    connect_regions(world, regions["Heywood"], regions["Pacifica"], "Heywood to Pacifica")
    connect_regions(world, regions["Heywood"], regions["Santo Domingo"], "Heywood to Santo Domingo")

    # Santo Domingo connections
    connect_regions(world, regions["City Center"], regions["Santo Domingo"], "City Center to Santo Domingo")
    connect_regions(world, regions["Santo Domingo"], regions["City Center"], "Santo Domingo to City Center")
    connect_regions(world, regions["Santo Domingo"], regions["Heywood"], "Santo Domingo to Heywood")
    connect_regions(world, regions["Santo Domingo"], regions["Pacifica"], "Santo Domingo to Pacifica")
    connect_regions(world, regions["Santo Domingo"], regions["Badlands"], "Santo Domingo to Badlands")

    # Pacifica connections
    connect_regions(world, regions["Pacifica"], regions["City Center"], "Pacifica to City Center")
    connect_regions(world, regions["Pacifica"], regions["Heywood"], "Pacifica to Heywood")
    connect_regions(world, regions["Pacifica"], regions["Santo Domingo"], "Pacifica to Santo Domingo")

    # Badlands connections (accessible from Watson and Santo Domingo)
    connect_regions(world, regions["Badlands"], regions["Westbrook"], "Badlands to Westbrook")
    connect_regions(world, regions["Badlands"], regions["Santo Domingo"], "Badlands to Santo Domingo")
    connect_regions(world, regions["Badlands"], regions["Pacifica"], "Badlands to Pacifica")

    # Special Regions
    connect_regions(world, regions["Watson"], regions["Afterlife"], "Watson to Afterlife")
    connect_regions(world, regions["Afterlife"], regions["Watson"], "Afterlife to Watson")
    # Cyberspace and Orbital Station are usually late-game/one-way or specific event triggers
    connect_regions(world, regions["City Center"], regions["Orbital Station"], "Arasaka Tower to Orbital Station")

    # DLC Only Connections
    if effective_dlc_enabled:
        connect_regions(world, regions["City Center"], regions["Morro Rock"], "City Center to Morro Rock")
        connect_regions(world, regions["Morro Rock"], regions["City Center"], "Morro Rock to City Center")
        connect_regions(world, regions["Santo Domingo"], regions["Dogtown"], "Santo Domingo to Dogtown")
        connect_regions(world, regions["Dogtown"], regions["Santo Domingo"], "Dogtown to Santo Domingo")
        connect_regions(world, regions["Dogtown"], regions["Pacifica"], "Dogtown to Pacifica")
        connect_regions(world, regions["Pacifica"], regions["Dogtown"], "Pacifica to Dogtown")


    # ===== SET REGION ACCESS RULES =====
    # Set basic access rules on regions to ensure accessibility check passes
    # These rules apply to ALL locations within each region
    # More specific location rules can be added in rules.py

    # All main districts require completing the prologue (having chosen a lifepath)
    # This ensures the generator knows these areas aren't accessible from the start
    # NOTE: "Lifepath Chosen" location is granted by completing any ONE of the 3 lifepath intros
    # (Streetkid, Corpo, or Nomad) - player doesn't need to complete all 3
    lifepath_location = "Lifepath Chosen"

    # Watson is the starting region, accessible from Menu with "New Game"
    # No additional requirements beyond entering the game

    # Other districts require having completed a lifepath intro
    # Set rules on all entrances leading to these regions
    for region_name in ["Westbrook", "City Center", "Heywood", "Pacifica", "Santo Domingo", "Badlands", "North Oak", "Afterlife", "Cyberspace", "Orbital Station"]:
        region = regions[region_name]
        # Set access rule on all entrances leading to this region
        for entrance in region.entrances:
            set_rule(entrance, lambda state, w=world: state.can_reach_location(lifepath_location, w.player))

    if effective_dlc_enabled:
        for entrance in regions["Dogtown"].entrances:
            set_rule(entrance, lambda state, w=world: state.can_reach_location(lifepath_location, w.player))

    # Set rules for selected major district restrictions.
    # These rules combine with the lifepath requirement using AND logic.
    for region_name, token_name in MAJOR_DISTRICT_TOKEN_REQUIREMENTS:
        if region_name not in regions or not is_major_district_token_gated(world.options, region_name):
            continue

        for entrance in regions[region_name].entrances:
            set_rule(
                entrance,
                lambda state, token=token_name: (
                    state.can_reach_location(lifepath_location, world.player) and
                    state.has(token, world.player)
                ),
            )


    # Set rules for subdistrict restrictions if enabled. Subdistrict tokens are
    # only meaningful when their parent major district is also token-gated.
    if world.options.restrict_by_sub_district:
        for region_name, parent_region, parent_token, subdistrict_token in SUBDISTRICT_TOKEN_REQUIREMENTS:
            if region_name not in regions or not is_major_district_token_gated(world.options, parent_region):
                continue

            for entrance in regions[region_name].entrances:
                set_rule(
                    entrance,
                    lambda state, major=parent_token, sub=subdistrict_token: (
                        state.can_reach_location(lifepath_location, world.player) and
                        state.has(major, world.player) and
                        state.has(sub, world.player)
                    ),
                )


def create_region(world: "Cyberpunk2077World", region_name: str) -> Region:
    """
    Create a single region and populate it with locations.

    This function:
    - Creates a Region object for a specific area
    - Finds all locations that belong to this region
    - Creates Location objects for each location
    - Registers the region with the MultiWorld

    Args:
        world: The Cyberpunk2077World instance
        region_name: Name of the region to create

    Returns:
        The created Region instance
    """

    # Create the region object
    region = Region(region_name, world.player, world.multiworld)

    pl_only_goal = is_goal_phantom_liberty_only(world.options)
    effective_dlc_enabled = has_effective_phantom_liberty_dlc(world.options)
    side_quests_enabled = is_goal_all_side_quests(world.options)
    pl_only_fixed_checks = {"Lifepath Chosen", "Ending Reached"}

    # Add all locations that belong to this region
    for location_name, location_data in location_table.items():
        if pl_only_goal:
            if (
                location_name not in pl_only_fixed_checks and
                not (location_data.dlc_only and location_data.category == LocationCategory.DLC_MAIN)
            ):
                continue

        # Skip DLC locations if the player didn't enable them
        # Check both regions membership and dlc_only flag (events may be in Watson to avoid circular deps)
        if ("Dogtown" in location_data.regions or location_data.dlc_only) and not effective_dlc_enabled:
            continue
        # Skip location if the category is not enabled in the options
        if location_data.category in (LocationCategory.SIDE_QUEST, LocationCategory.DLC_SIDE) and not side_quests_enabled:
            continue
        # Ending side quests follow the side-quest toggle.
        if location_data.category == LocationCategory.ENDING_SIDE_QUEST and not side_quests_enabled:
            continue
        if location_data.category == LocationCategory.GIG and not world.options.include_gigs:
            continue
        if location_data.category == LocationCategory.TAROT and not world.options.include_tarot:
            continue
        if location_data.category == LocationCategory.CYBERPSYCHO and not world.options.include_cyber_psycho_sighting:
            continue
        if location_data.category == LocationCategory.NCPD_HUSTLE and not world.options.include_ncpd_hustles:
            continue
        if location_data.category == LocationCategory.MINOR_QUEST and not world.options.include_minor_quests:
            continue


        # Only add locations whose graph parent matches this region.
        # parent_region is placement_region when set, otherwise regions[0] -- this
        # lets multi-district umbrella quests be parked on a hub (e.g. Watson)
        # without changing where the player physically completes them.
        if location_data.parent_region == region_name:
            # Handle event locations - they have code=None
            if location_data.code is None:
                # Event location - create it and add to region
                event_location = Cyberpunk2077Location(
                    world.player,
                    location_name,
                    None,
                    region
                )
                # Automatically place an event item with the same name as the location
                event_location.place_locked_item(world.create_event(location_name))

                # Add event location to region so it can be found via get_location()
                # It will be automatically filtered out when serializing to server
                region.locations.append(event_location)
                continue

            # Create regular location instance
            # Add base_id to location code to get the full Archipelago location ID
            location = Cyberpunk2077Location(
                world.player,
                location_data.display_name,  # Use display name for UI
                world.base_id + location_data.code,  # Convert offset to full ID
                region
            )

            # Apply the progress type from LocationData (DEFAULT, PRIORITY, or EXCLUDED)
            location.progress_type = location_data.progress_type

            # Add the regular location to the region
            region.locations.append(location)

    # Add the region to the multiworld
    world.multiworld.regions.append(region)

    return region


def connect_regions(
    world: "Cyberpunk2077World",
    source: Region,
    target: Region,
    entrance_name: str
) -> Entrance:
    """
    Create a connection (entrance) between two regions.

    An Entrance represents a one-way connection between regions.
    You need to create two entrances for two-way travel.
    Access rules can be applied to entrances in rules.py to control
    when players can use them.

    Args:
        world: The Cyberpunk2077World instance
        source: The region to connect from
        target: The region to connect to
        entrance_name: Human-readable name for this connection

    Returns:
        The created Entrance instance
    """

    # Create the entrance (connection)
    entrance = Entrance(world.player, entrance_name, source)

    # Add the entrance to the source region's exit list
    source.exits.append(entrance)

    # Connect the entrance to the target region
    # This sets which region the entrance leads to
    entrance.connect(target)

    return entrance


def place_event_on_location(
    world: "Cyberpunk2077World",
    location_name: str,
    event_name: str
) -> None:
    """
    Place an event item on a specific location.

    This creates a logical dependency - when the location is completed,
    the event item is received, which can then be used as a requirement
    for accessing other locations.

    Args:
        world: The Cyberpunk2077World instance
        location_name: The name of the location to place the event on
        event_name: The name of the event item to place
    """
    location = world.multiworld.get_location(location_name, world.player)
    location.place_locked_item(world.create_event(event_name))


# ===== NOTES ON ACCESS RULES =====
# Access rules are applied in rules.py, not here
#
# To add an access rule to an entrance:
#   entrance.access_rule = lambda state: state.has("Some Item", world.player)
#
# This makes the entrance only usable when the player has "Some Item"
#
# To check if a region is accessible:
#   state.can_reach_region("Watson", world.player)
#
# To check if a location is accessible:
#   state.can_reach_location("Watson - Complete Gig 1", world.player)
