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
    PerGameCommonOptions  # Base class for game options
)

# ===== OPTION CLASSES =====
# Each class defines one configurable option that appears in the player's YAML


#class IncludeCyberware(DefaultOnToggle):
#    """Include cyberware items in the randomizer."""
#    display_name = "Add Cyberware Checks"

#class IncludeWeapons(DefaultOnToggle):
#    """Include weapon items in the randomizer."""
#    display_name = "Add Unique World Weapon Checks"

#class StartingPath(Choice): # TODO: Still needs to be implemented on the RedScript side
#    display_name = "Starting path"
#    option_street_kid = 0
#    option_corpo_rat = 1
#    option_nomad = 2

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

    include_phantom_liberty_dlc: IncludePhantomLibertyDLC
    #starting_path: StartingPath
    #include_cyberware: IncludeCyberware
    #include_weapons: IncludeWeapons
    death_link: EnableDeathLink

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
