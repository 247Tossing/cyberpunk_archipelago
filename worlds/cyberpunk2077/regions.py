"""
Cyberpunk 2077 Region Definitions
"""

from typing import Dict, TYPE_CHECKING
from BaseClasses import Region, Entrance
from .locations import Cyberpunk2077Location, location_table

# TYPE_CHECKING is used for type hints without circular imports
# This allows us to reference Cyberpunk2077World for type hints without actually importing it
if TYPE_CHECKING:
    from . import Cyberpunk2077World


def create_regions(world: "Cyberpunk2077World") -> None:
    """
    Create all regions for this world and connect them.
    Args:
        world: The Cyberpunk2077World instance for this player
    """

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

    # Include Phantom Liberty DLC regions
    # if the player has the phantom liberty DLC
    if world.options.include_phantom_liberty_dlc:
        phantom_liberty_prologue_questline = create_region(world, "Phantom Liberty Prologue Questline")
        regions["Phantom Liberty Prologue Questline"] = phantom_liberty_prologue_questline

    # Create Watson district region
    watson = create_region(world, "Watson")
    regions["Watson"] = watson

    # Create Westbrook district region
    westbrook = create_region(world, "Westbrook")
    regions["Westbrook"] = westbrook

    # Create City Center region
    city_center = create_region(world, "City Center")
    regions["City Center"] = city_center

    # Create Heywood district region
    heywood = create_region(world, "Heywood")
    regions["Heywood"] = heywood

    # Create Pacifica district region
    pacifica = create_region(world, "Pacifica")
    regions["Pacifica"] = pacifica

    # Create Santo Domingo district region
    santo_domingo = create_region(world, "Santo Domingo")
    regions["Santo Domingo"] = santo_domingo

    # Create Badlands region
    badlands = create_region(world, "Badlands")
    regions["Badlands"] = badlands

    # Create Dogtown region (Phantom Liberty DLC only)
    if world.options.include_phantom_liberty_dlc:
        dogtown = create_region(world, "Dogtown")
        regions["Dogtown"] = dogtown

    # Create North Oak region (Westbrook sub-district)
    north_oak = create_region(world, "North Oak")
    regions["North Oak"] = north_oak

    # Create Afterlife region (special location - famous bar)
    afterlife = create_region(world, "Afterlife")
    regions["Afterlife"] = afterlife

    # Create Cyberspace region (virtual location)
    cyberspace = create_region(world, "Cyberspace")
    regions["Cyberspace"] = cyberspace

    # Create Orbital Station region (space station ending location)
    orbital_station = create_region(world, "Orbital Station")
    regions["Orbital Station"] = orbital_station

    # TODO: Add more regions as needed for your game


    # ===== CONNECT REGIONS =====
    # Define how regions are connected (which areas lead to which areas)
    # Each connection is one-way, so you need two entrances for two-way travel

    # Connect Menu to the starting region (Watson in this example)
    # This is the initial "New Game" entrance
    connect_regions(world, menu_region, regions["Watson"], "New Game")

    # Watson connections
    connect_regions(world, regions["Watson"], regions["Westbrook"], "Watson to Westbrook")
    connect_regions(world, regions["Watson"], regions["City Center"], "Watson to City Center")

    # Westbrook connections
    connect_regions(world, regions["Westbrook"], regions["Watson"], "Westbrook to Watson")
    connect_regions(world, regions["Westbrook"], regions["City Center"], "Westbrook to City Center")

    # City Center connections (hub area connecting multiple districts)
    connect_regions(world, regions["City Center"], regions["Watson"], "City Center to Watson")
    connect_regions(world, regions["City Center"], regions["Westbrook"], "City Center to Westbrook")
    connect_regions(world, regions["City Center"], regions["Heywood"], "City Center to Heywood")
    connect_regions(world, regions["City Center"], regions["Pacifica"], "City Center to Pacifica")

    # Heywood connections
    connect_regions(world, regions["Heywood"], regions["City Center"], "Heywood to City Center")

    # Pacifica & Dogtown connections
    connect_regions(world, regions["Pacifica"], regions["City Center"], "Pacifica to City Center")
    if world.options.include_phantom_liberty_dlc:
        connect_regions(world, regions["Pacifica"], regions["Dogtown"], "Pacifica to Dogtown")
        connect_regions(world, regions["Dogtown"], regions["Pacifica"], "Dogtown to Pacifica")

    # Santo Domingo connections
    connect_regions(world, regions["City Center"], regions["Santo Domingo"], "City Center to Santo Domingo")
    connect_regions(world, regions["Santo Domingo"], regions["City Center"], "Santo Domingo to City Center")

    # Badlands connections (accessible from Watson and Santo Domingo)
    connect_regions(world, regions["Watson"], regions["Badlands"], "Watson to Badlands")
    connect_regions(world, regions["Badlands"], regions["Watson"], "Badlands to Watson")
    connect_regions(world, regions["Santo Domingo"], regions["Badlands"], "Santo Domingo to Badlands")
    connect_regions(world, regions["Badlands"], regions["Santo Domingo"], "Badlands to Santo Domingo")

    # North Oak connections (accessible from City Center, part of Westbrook area)
    connect_regions(world, regions["City Center"], regions["North Oak"], "City Center to North Oak")
    connect_regions(world, regions["North Oak"], regions["City Center"], "North Oak to City Center")

    # Afterlife connections (special bar, accessed from City Center)
    connect_regions(world, regions["City Center"], regions["Afterlife"], "City Center to Afterlife")
    connect_regions(world, regions["Afterlife"], regions["City Center"], "Afterlife to City Center")

    # Cyberspace connections (virtual space, accessed from Pacifica)
    connect_regions(world, regions["Pacifica"], regions["Cyberspace"], "Pacifica to Cyberspace")
    connect_regions(world, regions["Cyberspace"], regions["Pacifica"], "Cyberspace to Pacifica")

    # Orbital Station connections (ending location, accessed via City Center)
    connect_regions(world, regions["City Center"], regions["Orbital Station"], "City Center to Orbital Station")
    connect_regions(world, regions["Orbital Station"], regions["City Center"], "Orbital Station to City Center")

    # TODO: Add more connections as needed

    # ===== SET REGION ACCESS RULES =====
    # Set basic access rules on regions to ensure accessibility check passes
    # These rules apply to ALL locations within each region
    # More specific location rules can be added in rules.py

    # All main districts require completing the prologue (having chosen a lifepath)
    # This ensures the generator knows these areas aren't accessible from the start
    # NOTE: "Lifepath Chosen" is an event granted by completing any ONE of the 3 lifepath intros
    # (Streetkid, Corpo, or Nomad) - player doesn't need to complete all 3
    lifepath_event = "Lifepath Chosen"

    # Watson is the starting region, accessible from Menu with "New Game"
    # No additional requirements beyond entering the game

    # Other districts require having completed a lifepath intro
    for region_name in ["Westbrook", "City Center", "Heywood", "Pacifica", "Santo Domingo", "Badlands"]:
        region = regions[region_name]
        # Region is accessible if player has the "Lifepath Chosen" event
        # Using a closure to capture the correct world.player value
        region.access_rule = lambda state, w=world: state.has(lifepath_event, w.player)

    # Special regions with additional requirements can be set here
    # Example: Dogtown requires Phantom Liberty DLC
    if world.options.include_phantom_liberty_dlc:
        regions["Dogtown"].access_rule = lambda state, w=world: state.has(lifepath_event, w.player)

    # North Oak, Afterlife, Cyberspace, Orbital Station also require lifepath
    for region_name in ["North Oak", "Afterlife", "Cyberspace", "Orbital Station"]:
        region = regions[region_name]
        region.access_rule = lambda state, w=world: state.has(lifepath_event, w.player)


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

    # Add all locations that belong to this region
    for location_name, location_data in location_table.items():
        # Skip DLC locations if the player didn't enable them
        if location_data.region == "Dogtown" and not world.options.include_phantom_liberty_dlc:
            continue
        # Only add locations that belong to this region
        if location_data.region == region_name:
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
