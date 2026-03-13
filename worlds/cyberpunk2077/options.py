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


class IncludeCyberware(DefaultOnToggle):
    """Include cyberware items in the randomizer."""
    display_name = "Include Cyberware"


class IncludeWeapons(DefaultOnToggle):
    """Include weapon items in the randomizer."""
    display_name = "Include Weapons"


class StartingDistrict(Choice):
    """
    Choose which district V starts in.

    This is a Choice option, which works like a dropdown menu.
    Each option_* field defines an available choice.
    The value is the integer index (0, 1, 2, etc.)
    """
    display_name = "Starting District"

    # Define the available choices
    option_watson = 0
    option_westbrook = 1
    option_city_center = 2
    option_heywood = 3
    option_pacifica = 4

    # Set the default choice
    default = 0  # Watson


class GigCount(Range):
    """
    Number of gigs to include in the randomizer.

    This is a Range option, which works like a slider with min/max values.
    Players can specify a number within the range to scale difficulty or game length.
    """
    display_name = "Gig Count"

    # Define the range boundaries
    range_start = 10   # Minimum value
    range_end = 100    # Maximum value
    default = 50       # Default value

    # Optional: Add tooltips for specific values
    # special_range_names = {
    #     10: "Short",
    #     50: "Normal",
    #     100: "Long"
    # }


class DifficultyLevel(Choice):
    """Overall difficulty setting for the randomizer."""
    display_name = "Difficulty"

    option_easy = 0
    option_normal = 1
    option_hard = 2
    option_very_hard = 3

    default = 1  # Normal


class EnableDeathLink(Toggle):
    """
    Enable Death Link: When you die, everyone dies. When others die, you die.

    Death Link is a special Archipelago feature that syncs deaths across all
    players who have it enabled. It's opt-in and adds extra challenge/fun.
    """
    display_name = "Death Link"


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

    # Add each option as a field
    include_cyberware: IncludeCyberware
    include_weapons: IncludeWeapons
    starting_district: StartingDistrict
    gig_count: GigCount
    difficulty_level: DifficultyLevel
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
