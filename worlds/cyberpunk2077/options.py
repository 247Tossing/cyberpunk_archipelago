"""
Cyberpunk 2077 Player Options

This file defines configuration options that players can set in their YAML files.

Options control world generation behavior - what's included, difficulty settings,
starting conditions, etc. Players configure these in their YAML before generating
a multiworld seed.
"""

from dataclasses import dataclass
from Options import (
    Toggle,           # On/Off option (like a checkbox)
    DefaultOnToggle,  # Toggle that defaults to On
    Choice,           # Multiple choice option (like a dropdown)
    Range,            # Numeric range option (like a slider)
    PerGameCommonOptions,  # Base class for game options
    OptionGroup,       # For grouping options on WebHost
    Visibility
)

# ===== OPTION CLASSES =====
# Each class defines one configurable option that appears in the player's YAML

#class IncludeCyberware(DefaultOnToggle):
#    """Include cyberware items in the randomizer."""
#    display_name = "Add Cyberware Checks"

#class IncludeWeapons(DefaultOnToggle):
#    """Include weapon items in the randomizer."""
#    display_name = "Add Unique World Weapon Checks"

#class StartingPath(Choice):
#    display_name = "Starting path"
#    option_street_kid = 0
#    option_corpo_rat = 1
#    option_nomad = 2

class IncludeGigs(Toggle):
    display_name = "Include Gigs"
    default = 1

class IncludeTarot(Toggle):
    display_name = "Include Tarot"
    default = 1

class IncludeCyberPsychoSighting(Toggle):
    display_name = "Include Cyber Psycho Sighting"
    default = 1

class IncludeSideQuests(Toggle):
    display_name = "Include Side Quests"
    default = 1

class IncludeAllEndings(Toggle):
    """By default, this will only require you to reach Nocturne Op55N1 and the default ending
    Enabling this option will include any possible ending in the generated multiworld and the requisite items to do so
    """
    display_name = "Include All Endings"
    default = 0

class IncludeContracts(Toggle):
    display_name = "Include Contracts"
    default = 1

class IncludeNCPDHustles(Toggle):
    display_name = "Include NCPD Hustles"
    default = 1

class IncludeMinorQuests(Toggle):
    display_name = "Include Minor Quests"
    default = 1

class RestrictByMajorDistrict(Toggle):
    """Restrict access to districts
    When enabled, players will only be able to access major districts by aquiring access tokens from the multiworld.
    """
    display_name = "Restrict by Major District"
    default = 1

class RestrictBySubDistrict(Toggle):
    """Restrict access to subdistricts
    When enabled, players will only be able to access subdistricts by aquiring access tokens from the multiworld.
    **Restrict by Major District must be enabled for this option to work.**
    """
    display_name = "Restrict by Sub District"
    default = 0
    visibility = Visibility.none # Temporary

class QuickHacksAsItems(Toggle):
    """Put progressive quickhack items into the multiworld"""
    display_name = "Quick Hacks as Items"
    default = 1


class IncludePhantomLibertyDLC(Toggle):
    display_name = "Include Phantom Liberty DLC"
    default = 0

class EnableDeathLink(Toggle):
    display_name = "Death Link"
    default = 0


# TODO: Add more options as needed for your implementation
# Examples:
# - Randomize quest order
# - Include side quests
# - Randomize enemy difficulty
# - Include crafting materials
# - Enable/disable specific content packs


# ===== OPTIONS DATACLASS =====
# This combines all options into a single configuration object

@dataclass
class Cyberpunk2077Options(PerGameCommonOptions):
    """
    Container for all Cyberpunk 2077 options.

    Uses Python's @dataclass decorator to automatically generate methods
    from the field definitions. PerGameCommonOptions provides standard
    options like local_items and start_inventory.

    Accessing options in code:
        In __init__.py: self.options.include_cyberware
        Returns the value based on what the player set in their YAML
        Example: if self.options.include_cyberware: add_cyberware_items()
    """

    restrict_by_major_district: RestrictByMajorDistrict
    restrict_by_sub_district: RestrictBySubDistrict
    include_phantom_liberty_dlc: IncludePhantomLibertyDLC
    death_link: EnableDeathLink
    include_gigs: IncludeGigs
    include_tarot: IncludeTarot
    include_cyber_psycho_sighting: IncludeCyberPsychoSighting
    include_side_quests: IncludeSideQuests
    include_contracts: IncludeContracts
    quick_hacks_as_items: QuickHacksAsItems
    include_ncpd_hustles: IncludeNCPDHustles
    include_minor_quests: IncludeMinorQuests
    include_all_endings: IncludeAllEndings

    #starting_path: StartingPath
    #include_cyberware: IncludeCyberware
    #include_weapons: IncludeWeapons


# ===== OPTION GROUPS =====
# Groups organize options on the WebHost for better user experience
# Options are displayed in the order specified here

cyberpunk_option_groups = [
    OptionGroup("Quest Options", [
        IncludeAllEndings,
        IncludeGigs,
        IncludeTarot,
        IncludeCyberPsychoSighting,
        IncludeSideQuests,
        IncludeContracts,
        IncludeNCPDHustles,
        IncludeMinorQuests,
    ]),
    OptionGroup("DLC Options", [
        IncludePhantomLibertyDLC,
    ]),
    OptionGroup("Restriction Options", [
        RestrictByMajorDistrict,
        RestrictBySubDistrict,
    ]),
    OptionGroup("Item Options", [
        QuickHacksAsItems,
    ]),
    OptionGroup("Extra Challenge", [
        EnableDeathLink,
    ], start_collapsed=True),
]


# ===== USAGE EXAMPLES =====
#
# In the World class (__init__.py), you can access options like this:
#
# 1. Check a toggle:
#    if self.options.include_cyberware:
#        # Add cyberware items
#        pass
#
# 2. Get a choice value:
#    starting_district = self.options.starting_district.value
#    if starting_district == StartingDistrict.option_watson:
#        # Start in Watson
#        pass
#
# 3. Get a range value:
#    gig_count = self.options.gig_count.value
#    for i in range(gig_count):
#        # Create gigs
#        pass
#
# 4. Use options to control generation:
#    def create_items(self):
#        if self.options.include_weapons:
#            item_pool.extend(weapon_items)
#        if self.options.include_cyberware:
#            item_pool.extend(cyberware_items)

# ===== YAML CONFIGURATION =====
# Players set these options in their YAML file like this:
#
# Cyberpunk 2077:
#   include_cyberware: true
#   include_weapons: false
#   starting_district: watson
#   gig_count: 75
#   difficulty_level: hard
#   death_link: false
#
# Or they can use ranges for random selection:
#
# Cyberpunk 2077:
#   gig_count:
#     random-range: [30, 70]  # Pick a random number between 30 and 70
#   starting_district:
#     random: true  # Pick a random district


# ===== OPTION TYPE REFERENCE =====
#
# Toggle:
#   - Simple on/off option
#   - Value is a boolean (True/False)
#   - Default is False
#
# DefaultOnToggle:
#   - Same as Toggle but defaults to True
#   - Use when you want the option enabled by default
#
# Choice:
#   - Multiple choice option (dropdown)
#   - Define choices with option_* class attributes
#   - Value is an integer (0, 1, 2, etc.)
#   - Access the integer with .value
#
# Range:
#   - Numeric range with min/max
#   - Define range_start, range_end, default
#   - Value is an integer
#   - Access with .value
#
# OptionList:
#   - List of values
#   - Good for multi-select options
#   - Not used in this example but available
#
# FreeText:
#   - Free-form text input
#   - Not used in this example but available
#   - Useful for custom seeds or keywords
