"""
Cyberpunk 2077 Region Definitions

This file defines the regions (game areas) and their connections for Cyberpunk 2077.

Regions represent different areas of the game (districts of Night City).
Each region contains locations (item checks) and can be connected to other regions
via entrances. Entrances can have access rules that determine when players can
travel between regions.
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

    This function:
    - Creates Region objects for each area of the game
    - Populates each region with Location objects
    - Connects regions via Entrance objects
    - Registers everything with the MultiWorld

    Args:
        world: The Cyberpunk2077World instance for this player
    """

    # ===== CREATE MENU REGION =====
    # The Menu region is required by Archipelago
    # It represents the starting point before entering the game
    # Think of this as the main menu or character select screen

    menu_region = Region("Menu", world.player, world.multiworld)
    world.multiworld.regions.append(menu_region)


    # ===== CREATE GAME REGIONS =====
    # These represent actual areas in Cyberpunk 2077 (Night City districts)
    # Each region is a container for locations (item checks) in that area

    # Dictionary to store regions for easy reference
    regions: Dict[str, Region] = {
        "Menu": menu_region
    }

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

    # TODO: Add more regions as needed for your game


    # ===== CONNECT REGIONS =====
    # Define how regions are connected (which areas lead to which areas)
    # Each connection is one-way, so you need two entrances for two-way travel

    # Connect Menu to the starting region (Watson in this example)
    # This is the initial "New Game" entrance
    connect_regions(world, menu_region, regions["Watson"], "New Game")

    # Connect districts to each other
    # In a real implementation, these would have access rules
    # Example: Might need a car, metro pass, or story progression

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

    # Pacifica connections
    connect_regions(world, regions["Pacifica"], regions["City Center"], "Pacifica to City Center")

    # Santo Domingo connections
    connect_regions(world, regions["City Center"], regions["Santo Domingo"], "City Center to Santo Domingo")
    connect_regions(world, regions["Santo Domingo"], regions["City Center"], "Santo Domingo to City Center")

    # Badlands connections (accessible from Watson and Santo Domingo)
    connect_regions(world, regions["Watson"], regions["Badlands"], "Watson to Badlands")
    connect_regions(world, regions["Badlands"], regions["Watson"], "Badlands to Watson")
    connect_regions(world, regions["Santo Domingo"], regions["Badlands"], "Santo Domingo to Badlands")
    connect_regions(world, regions["Badlands"], regions["Santo Domingo"], "Badlands to Santo Domingo")

    # TODO: Add more connections as needed
    # TODO: Add access rules to connections in rules.py
    # Example: Might need to complete certain quests to unlock some districts


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
        # Only add locations that belong to this region
        if location_data.region == region_name:
            # Create the location instance
            location = Cyberpunk2077Location(
                world.player,
                location_name,
                location_data.code,
                region
            )

            # Add the location to the region
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
