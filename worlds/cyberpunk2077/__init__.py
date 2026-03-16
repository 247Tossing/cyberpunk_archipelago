"""
Cyberpunk 2077 Archipelago World Implementation

This file defines the main World class for Cyberpunk 2077, which manages the
randomization logic for this game in the Archipelago multiworld system.

The World class handles:
- Generating regions (game areas) and locations (item checks)
- Creating the item pool that gets distributed across all players
- Setting access rules that determine item/location requirements
- Providing player-specific configuration options
"""

from typing import Dict, List, Set, Any
from BaseClasses import Region, Item, ItemClassification, Tutorial, MultiWorld
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import Component, components, Type, launch
from .items import Cyberpunk2077Item, item_table, item_name_to_id, item_name_groups
from .locations import Cyberpunk2077Location, location_table, location_name_to_id, location_name_groups, location_internal_id_to_display_name
from .options import Cyberpunk2077Options
from .regions import create_regions
from .rules import set_rules


def launch_client(*args: str):
    """
    Launch the Cyberpunk 2077 client.

    Called when the user clicks the client button in the Archipelago launcher.
    Starts the client in a separate process to handle communication between
    the Archipelago server and the game.
    """
    from .client import launch as client_main
    launch(client_main, name="Cyberpunk 2077 Client", args=args)


# Register the client in the Archipelago Launcher
# This makes the "Cyberpunk 2077 Client" button appear in the launcher GUI
components.append(Component("Cyberpunk 2077 Client", func=launch_client, component_type=Type.CLIENT))


class Cyberpunk2077Web(WebWorld):
    """
    Web interface configuration for Cyberpunk 2077.

    Defines the visual theme and documentation links shown on the
    Archipelago web interface for this game.
    """
    theme = "stone"  # Visual theme for the web interface (options: dirt, grass, ice, jungle, ocean, partyTime, stone)

    # TODO: Create setup guide markdown file in docs/setup_en.md when ready
    # tutorials = [Tutorial(
    #     "Multiworld Setup Guide",
    #     "A guide to setting up the Archipelago Cyberpunk 2077 client on your computer.",
    #     "English",
    #     "setup_en.md",
    #     "setup/en",
    #     ["YourNameHere"]
    # )]


class Cyberpunk2077World(World):
    """
    Main World class for Cyberpunk 2077.

    This class defines how the game integrates with Archipelago's randomization system.
    It handles world generation, item creation, and access logic for a single player slot.

    Each player in a multiworld gets their own instance of this class, which manages
    their specific randomization settings and generated world state.
    """

    # ===== REQUIRED CLASS ATTRIBUTES =====
    # These class-level attributes define core properties of this world

    game: str = "Cyberpunk 2077"  # Game name - must match across all files
    web = Cyberpunk2077Web()  # Web interface configuration

    # Player options - configured via YAML file
    options_dataclass = Cyberpunk2077Options
    options: Cyberpunk2077Options  # Populated with player's chosen settings during generation

    # Base ID for items/locations
    # Archipelago assigns each game a unique ID range to avoid conflicts between games
    # All item/location IDs for this game start from this number
    base_id = 77_2077_000

    # Minimum client version required to play this world
    # Format: (major, minor, patch) tuple
    # The client checks this during connection to ensure compatibility
    required_client_version = (0, 1, 0)

    # ===== ITEM AND LOCATION MAPPINGS =====
    # These dictionaries map human-readable names to numeric IDs for network communication

    # Maps item names to their unique IDs
    # Example: {"Mantis Blades": 77_2077_001, "Kerenzikov": 77_2077_002, ...}
    item_name_to_id = item_name_to_id

    # Maps location names to their unique IDs
    # Example: {"Watson - Completed Gig": 1000, "Westbrook - Main Quest": 1001, ...}
    location_name_to_id = location_name_to_id

    # Optional: Group items/locations by category for easier YAML configuration
    # Example: {"Cyberware": ["Mantis Blades", "Kerenzikov"], "Weapons": [...]}
    item_name_groups = item_name_groups
    location_name_groups = location_name_groups


    # ===== INSTANCE ATTRIBUTES =====
    # Instance variables for this specific player's world
    # These store player-specific state during world generation


    def __init__(self, multiworld: MultiWorld, player: int):
        """
        Initialize a new Cyberpunk 2077 world for a player.

        Called once per player when setting up a multiworld game.
        Use this to initialize any custom state needed for generation.

        Args:
            multiworld: The MultiWorld instance managing all players
            player: This player's slot number (1-indexed)
        """
        super().__init__(multiworld, player)
        # Initialize any custom attributes here if needed
        # Example: self.custom_player_state = {}


    def generate_early(self) -> None:
        """
        Early generation phase - runs before item/location creation.

        This is the first generation step for each player. Use it to:
        - Process player options from their YAML file
        - Make random decisions that affect world generation
        - Initialize data structures needed for later steps

        The random number generator (self.random) is seeded per-player,
        so random choices here are deterministic and reproducible.
        """
        # Example: Handle player options
        # if self.options.include_cyberware:
        #     self.enabled_item_categories.add("cyberware")

        # Example: Make deterministic random choices
        # self.starting_district = self.random.choice(["Watson", "Westbrook", "Heywood"])

        pass


    def create_regions(self) -> None:
        """
        Create all regions (game areas) and locations (item checks).

        Regions represent different areas of the game (Watson, Westbrook, etc.)
        Locations are specific spots where items can be found (quest completions, collectibles)

        Regions are connected via Entrances, which can have access rules
        (e.g., need a specific item to travel between regions)

        The actual implementation is in regions.py for better organization.
        """
        create_regions(self)


    def create_items(self) -> None:
        """
        Create all items that will be placed in the multiworld.

        This method populates the item pool with all items that will be
        randomly distributed across all players' games. The number of items
        created should match the number of locations available.

        Item classifications:
        - progression: Required to complete the game (key items, critical unlocks)
        - useful: Helpful but not required (stat boosts, quality-of-life items)
        - filler: Used to fill extra locations (consumables, money)
        - trap: Negative effects (optional, can hinder the player)
        """

        # Count how many items we need to create
        # Must match the number of locations (excluding event locations)
        # Event locations have address=None and are auto-completed
        total_locations = len([loc for loc in self.multiworld.get_locations(self.player)
                              if loc.address is not None])

        # Create the item pool
        item_pool: List[Item] = []

        # Add all defined items from item_table
        for item_name, item_data in item_table.items():
            # Skip event items - they have code=None and are placed manually on event locations
            # Event items should NEVER go in the item pool
            if item_data.code is None:
                continue

            # TODO: Add logic to determine how many of each item to include
            # For now, add each item once
            item_pool.append(self.create_item(item_name))

        # Fill remaining slots with filler items if needed
        # This ensures we have exactly enough items for all locations
        filler_count = total_locations - len(item_pool)
        for _ in range(filler_count):
            item_pool.append(self.create_item(self.get_filler_item_name()))

        # Add all items to the multiworld pool
        # These will be randomly distributed across all players' games
        self.multiworld.itempool += item_pool


    def get_filler_item_name(self) -> str:
        """
        Get a filler item name to use for filling extra item pool slots.

        Dynamically selects from all available filler items in the item_table.
        If multiple filler items exist, randomly chooses one for variety.

        Returns:
            The display name of a filler item from item_table

        Raises:
            Exception: If no filler items are defined in item_table
        """
        # Get all filler items from item_table
        # NOTE: ItemClassification.filler = 0, so we check for ABSENCE of other type flags
        # Filler items are those without progression, useful, or trap flags
        # They may still have modifier flags like deprioritized or skip_balancing
        filler_items = [
            name for name, data in item_table.items()
            if (not (data.classification & (ItemClassification.progression |
                                           ItemClassification.useful |
                                           ItemClassification.trap))) and data.code is not None
        ]

        if not filler_items:
            raise Exception("No filler items defined in item_table! Add at least one filler item.")

        # Return random filler item if multiple exist, otherwise return the only one
        return self.random.choice(filler_items) if len(filler_items) > 1 else filler_items[0]


    def create_item(self, name: str) -> Item:
        """
        Factory method to create an item instance.

        Takes an item name and returns a configured Item object ready
        to be added to the item pool.

        Args:
            name: The item name (must exist in item_table)

        Returns:
            A new Cyberpunk2077Item instance with the correct properties
        """
        item_data = item_table[name]
        return Cyberpunk2077Item(
            name,
            item_data.classification,
            item_data.code,
            self.player
        )


    def create_event(self, name: str) -> Item:
        """
        Factory method to create an event item.

        Event items are used for internal logic during generation and never
        appear in the actual game. They represent in-game actions like completing
        quests or defeating bosses, and are used to create logical dependencies.

        Args:
            name: The event item name (must exist in item_table with code=None)

        Returns:
            A new Cyberpunk2077Item instance for the event (with code=None)
        """
        item_data = item_table[name]
        return Cyberpunk2077Item(
            name,
            item_data.classification,
            None,  # Events always have code=None
            self.player
        )


    def set_rules(self) -> None:
        """
        Define access rules for regions and locations.

        Rules determine what items are needed to:
        - Travel between regions (region access rules)
        - Complete specific locations (location access rules)
        - Beat the game (victory condition)

        Rules are lambda functions that check the player's current item collection.
        Example: lambda state: state.has("Mantis Blades", player)

        The actual implementation is in rules.py for better organization.
        """
        set_rules(self)


    def fill_slot_data(self) -> Dict[str, Any]:
        """
        Create data to send to the client when connecting.

        This data is sent to the client when a player connects to the multiworld.
        Use it to communicate world-specific settings, seed information, or
        custom configuration that the client needs to know.

        Returns:
            Dictionary of data to send to the client
        """
        # Return any data the client needs to know about this player's world
        # This data is accessible in client.py via self.slot_data
        slot_data: Dict[str, Any] = {
            "world_version": 1,  # Version of your world implementation
            # Configuration options sent to RedScript client via SYNC_CONFIG
            "death_link": bool(self.options.death_link.value),
            # TODO: Add skill_points_as_items option when implemented
            # "skill_points_as_items": bool(self.options.skill_points_as_items.value),
            # Mapping of internal game IDs to display names for UI
            "location_internal_id_to_display_name": location_internal_id_to_display_name,
        }
        return slot_data
