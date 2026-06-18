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
from .items import Cyberpunk2077Item, item_table, item_name_to_id, item_name_groups, ItemCategory
from .locations import Cyberpunk2077Location, location_table, location_name_to_id, location_name_groups, location_internal_id_to_display_name
from .options import (
    Cyberpunk2077Options,
    DistrictRestrictionType,
    apply_token_locality_options,
    cyberpunk_option_groups,
    district_restriction_active,
    get_gated_major_district_mask,
    has_effective_phantom_liberty_dlc,
    is_major_district_token_gated,
    is_goal_phantom_liberty_only,
)
from .regions import create_regions
from .rules import set_rules, VENDOR_CHECK_INTERNAL_KEYS


def _vendor_stock_parts_from_check_name(location_name: str) -> tuple[str, int] | None:
    """Parse `VendorCheck_<vendor>_<slot>` into (`vendor`, `slot`)."""
    prefix = "VendorCheck_"
    if not location_name.startswith(prefix):
        return None

    tail = location_name[len(prefix):]
    vendor_key, separator, slot_text = tail.rpartition("_")
    if separator != "_" or not vendor_key or not slot_text.isdigit():
        return None

    return vendor_key, int(slot_text)



class Cyberpunk2077Web(WebWorld):
    """
    Web interface configuration for Cyberpunk 2077.

    Defines the visual theme and documentation links shown on the
    Archipelago web interface for this game.
    """
    theme = "stone"  # Visual theme for the web interface (options: dirt, grass, ice, jungle, ocean, partyTime, stone)

    # Option groups organize player-facing options on the WebHost
    option_groups = cyberpunk_option_groups

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
    # Cyberpunk 2077 uses the range: 2077000-2077999 (1000 IDs available)
    # Format: 2077XXX where XXX is the specific offset for each item/location
    # Locations: 2077000-2077499, Items: 2077500-2077999
    base_id = 2077000

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


    # Mapping from weapon pass item name to the corresponding player option attribute
    WEAPON_PASS_OPTION_MAP: Dict[str, str] = {
        "Pistol Weapon Pass": "weapon_restrict_pistol",
        "Shotgun Weapon Pass": "weapon_restrict_shotgun",
        "Sniper Weapon Pass": "weapon_restrict_sniper",
        "LMG Weapon Pass": "weapon_restrict_lmg",
        "Rifle Weapon Pass": "weapon_restrict_rifle",
        "Melee Weapon Pass": "weapon_restrict_melee",
        "SMG Weapon Pass": "weapon_restrict_smg"
    }

    # Mapping from district token item name to the corresponding player option attribute
    DISTRICT_TOKEN_OPTION_MAP: Dict[str, str] = {
        "Westbrook Access Token": "district_restrict_westbrook",
        "City Center Access Token": "district_restrict_city_center",
        "Heywood Access Token": "district_restrict_heywood",
        "Santo Domingo Access Token": "district_restrict_santo_domingo",
        "Pacifica Access Token": "district_restrict_pacifica",
        "Badlands Access Token": "district_restrict_badlands",
        "Dogtown Access Token": "district_restrict_dogtown",
    }

    DISTRICT_TOKEN_REGION_MAP: Dict[str, str] = {
        "Westbrook Access Token": "Westbrook",
        "City Center Access Token": "City Center",
        "Heywood Access Token": "Heywood",
        "Santo Domingo Access Token": "Santo Domingo",
        "Pacifica Access Token": "Pacifica",
        "Badlands Access Token": "Badlands",
        "Dogtown Access Token": "Dogtown",
    }

    SUBDISTRICT_TOKEN_PARENT_MAP: Dict[str, str] = {
        "Westbrook Japantown Access Token": "Westbrook",
        "Westbrook Charter Hill Access Token": "Westbrook",
        "Westbrook North Oak Access Token": "Westbrook",
        "City Center Corpo Plaza Access Token": "City Center",
        "City Center Downtown Access Token": "City Center",
        "Heywood Wellsprings Access Token": "Heywood",
        "Heywood The Glen Access Token": "Heywood",
        "Heywood Vista Del Rey Access Token": "Heywood",
        "Santo Domingo Arroyo Access Token": "Santo Domingo",
        "Santo Domingo Rancho Coronado Access Token": "Santo Domingo",
        "Pacifica Coastview Access Token": "Pacifica",
        "Pacifica West Wind Estate Access Token": "Pacifica",
        "Badlands Biotechnica Flats Access Token": "Badlands",
        "Badlands Jackson Plains Access Token": "Badlands",
        "Badlands Laguna Bend Access Token": "Badlands",
        "Badlands Red Peaks Access Token": "Badlands",
        "Badlands Rocky Ridge Access Token": "Badlands",
        "Badlands Sierra Sonora Access Token": "Badlands",
        "Badlands SoCal Badlands Access Token": "Badlands",
        "Badlands Yucca Access Token": "Badlands",
        "Badlands Morro Rock Access Token": "Badlands",
    }

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
        # if self.options.include_dlc_content:
        #     # Process DLC-related setup
        #     pass

        # Example: Make deterministic random choices
        # self.starting_district = self.random.choice(["Watson", "Westbrook", "Heywood"])

        # PL-only goal intentionally strips district token gameplay.
        # Keep the option values in sync before regions/items/rules consume them.
        if is_goal_phantom_liberty_only(self.options):
            self.options.district_restriction_type.value = DistrictRestrictionType.option_none
            self.options.restrict_by_sub_district.value = 0

        apply_token_locality_options(self)
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

        pl_only_goal = is_goal_phantom_liberty_only(self.options)
        effective_dlc_enabled = has_effective_phantom_liberty_dlc(self.options)

        # Add all defined items from item_table
        for item_name, item_data in item_table.items():
            # Skip event items - they have code=None and are placed manually on event locations
            # Event items should NEVER go in the item pool
            if item_data.code is None:
                continue

            # Skip DLC items if Phantom Liberty DLC is disabled
            # Prevents unusable items from appearing in the item pool
            if item_data.dlc_only and not effective_dlc_enabled:
                continue

            # Skip subdistrict tokens unless their parent major is also token-gated.
            if item_data.category == ItemCategory.SUBDISTRICT_TOKEN:
                parent_region = self.SUBDISTRICT_TOKEN_PARENT_MAP.get(item_name)
                if (
                    not self.options.restrict_by_sub_district
                    or not parent_region
                    or not is_major_district_token_gated(self.options, parent_region)
                ):
                    continue

            # Skip district tokens unless their specific major district is selected.
            if item_data.category == ItemCategory.DISTRICT_TOKEN:
                region_name = self.DISTRICT_TOKEN_REGION_MAP.get(item_name)
                if not region_name or not is_major_district_token_gated(self.options, region_name):
                    continue

            # Skip quickhack items if quick hacks as items is disabled
            if item_data.category == ItemCategory.QUICKHACK and not self.options.quick_hacks_as_items:
                continue

            # Skip trap items when traps are disabled.
            if item_data.category == ItemCategory.TRAP and not self.options.enable_traps:
                continue

            # PL-only mode trims the pool down to DLC progression, optional traps,
            # and filler to match the reduced location count.
            if pl_only_goal:
                is_filler = not (
                    item_data.classification & (
                        ItemClassification.progression |
                        ItemClassification.useful |
                        ItemClassification.trap
                    )
                )
                if not (item_data.dlc_only or item_data.category == ItemCategory.TRAP or is_filler):
                    continue

            # Skip weapon pass items unless mode is "Require Multiworld Item" (2) AND
            # the specific weapon type is restricted by the player
            if item_data.category == ItemCategory.WEAPON_PASS:
                option_attr = self.WEAPON_PASS_OPTION_MAP.get(item_name)
                if (self.options.weapon_restriction_type != 2
                        or not option_attr
                        or not getattr(self.options, option_attr)):
                    continue

            quantity = (self.options.trap_amount
                        if item_data.category == ItemCategory.TRAP and self.options.enable_traps
                        else item_data.quantity)
            item_pool.extend([self.create_item(item_name) for _ in range(quantity)])

        if pl_only_goal and len(item_pool) > total_locations:
            item_pool = item_pool[:total_locations]

        # Fill remaining slots with filler items if needed
        # This ensures we have exactly enough items for all locations
        filler_count = max(0, total_locations - len(item_pool))
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
        # Add base_id to item code to get the full Archipelago item ID
        # Event items (code=None) don't need base_id added
        item_code = self.base_id + item_data.code if item_data.code is not None else None
        return Cyberpunk2077Item(
            name,
            item_data.classification,
            item_code,
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
        # This data is accessible to the game bridge via self.slot_data
        slot_data: Dict[str, Any] = {
            "world_version": 2,  # Version of your world implementation
            # Configuration options sent to RedScript client via SYNC_CONFIG
            "death_link": bool(self.options.death_link.value),
            "death_link_amnesty": int(self.options.death_link_amnesty.value),
            # Weapon restriction settings
            # 0 = none (no restriction), 1 = cannotEquip (hard ban), 2 = requireMultiworldItem (pass-gated)
            "weapon_restriction_type": int(self.options.weapon_restriction_type.value),
            "weapon_restrict_pistol": bool(self.options.weapon_restrict_pistol.value),
            "weapon_restrict_melee": bool(self.options.weapon_restrict_melee.value),
            "weapon_restrict_rifle": bool(self.options.weapon_restrict_rifle.value),
            "weapon_restrict_sniper": bool(self.options.weapon_restrict_sniper.value),
            "weapon_restrict_lmg": bool(self.options.weapon_restrict_lmg.value),
            "weapon_restrict_shotgun": bool(self.options.weapon_restrict_shotgun.value),
            "weapon_restrict_smg": bool(self.options.weapon_restrict_smg.value),
            # District restriction settings
            "restrict_by_major_district": district_restriction_active(self.options),
            "restrict_by_sub_district": bool(self.options.restrict_by_sub_district.value),
            "district_token_gated_major_mask": get_gated_major_district_mask(self.options),
            # Vendor sanity settings
            "vendor_sanity": int(bool(self.options.vendor_sanity.value)),
            "vendor_sanity_stock": "",
            # TODO: Add skill_points_as_items option when implemented
            # "skill_points_as_items": bool(self.options.skill_points_as_items.value),
        }
        if bool(self.options.vendor_sanity.value):
            stock_records: List[str] = []
            for internal_key in VENDOR_CHECK_INTERNAL_KEYS:
                parsed = _vendor_stock_parts_from_check_name(internal_key)
                if parsed is None:
                    continue
                vendor_key, stock_index = parsed

                stock_item_name = "Unknown Item"
                stock_recipient_name = "Unknown Player"
                display_name = location_table[internal_key].display_name
                try:
                    location = self.multiworld.get_location(display_name, self.player)
                except KeyError:
                    # Location was not created for this seed (e.g. dlc_only vendors when PL is off).
                    continue
                if location.item is not None:
                    stock_item_name = location.item.name
                    stock_recipient_name = self.multiworld.get_player_name(location.item.player)

                safe_item_name = self._sanitize_vendor_stock_token(stock_item_name)
                safe_recipient_name = self._sanitize_vendor_stock_token(stock_recipient_name)
                stock_records.append(f"{vendor_key}:{stock_index}:{safe_item_name}:{safe_recipient_name}")

            slot_data["vendor_sanity_stock"] = ",".join(stock_records)

        return slot_data

    @staticmethod
    def _sanitize_vendor_stock_token(value: str) -> str:
        return value.replace(":", " ").replace(",", " ").strip()

