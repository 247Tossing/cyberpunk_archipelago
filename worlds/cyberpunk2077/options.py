"""
Cyberpunk 2077 Player Options

This file defines configuration options that players can set in their YAML files.

Options control world generation behavior - what's included, difficulty settings,
starting conditions, etc. Players configure these in their YAML before generating
a multiworld seed.
"""

from dataclasses import dataclass
from typing import Dict, Tuple
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

class WeaponRestrictionType(Choice):
    """
        Choose the restriction behavior:
        Cannot Equip - Nothing will allow you to use the selected weapon types during this run
        Require Multiworld Item - You will need to acquire an item from the multiworld to use the selected weapon types during this run
    """
    display_name = "Weapon Restriction Type"
    option_none = 0
    option_cannotEquip = 1
    option_requireMultiworldItem = 2

class RestrictPistols(Toggle):
    display_name = "Restrict Pistols"
    default = 0

class RestrictMelee(Toggle):
    display_name = "Restrict Melee"
    default = 0

class RestrictShotgun(Toggle):
    display_name = "Restrict Shotgun"
    default = 0

class RestrictSniper(Toggle):
    display_name = "Restrict Sniper Rifles"
    default = 0

class RestrictRifle(Toggle):
    display_name = "Restrict Rifle"
    default = 0

class RestrictLMG(Toggle):
    display_name = "Restrict LMG"
    default = 0

class RestrictSMG(Toggle):
    display_name = "Restrict SMG"
    default = 0

class IncludeGigs(Toggle):
    display_name = "Include Gigs"
    default = 1

class IncludeTarot(Toggle):
    display_name = "Include Tarot"
    default = 1

class IncludeCyberPsychoSighting(Toggle):
    display_name = "Include Cyber Psycho Sighting"
    default = 1

class CompletionGoal(Choice):
    """
    Choose what counts as completing the world:
    - Complete Any Ending: reach Ending Reached (default behavior).
    - Complete Any Ending W/ All Side Quests: reach Ending Reached and have
      logical access to every included SIDE_QUEST / DLC_SIDE location.
    - Complete Only Phantom Liberty Questline: complete PL's main questline.
      This mode implies Phantom Liberty DLC for world generation and disables
      district token restrictions to keep the pool aligned to PL checks.
    """
    display_name = "Completion Goal"
    option_complete_any_ending = 0
    option_complete_any_ending_w_all_side_quests = 1
    option_complete_only_phantom_liberty_questline = 2
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

class DistrictRestrictionType(Choice):
    """
    Choose the major-district restriction behavior:
    - None: District tokens are not placed and the client will not enforce district locks.
    - Require District Token: Selected districts require their access token.
    """
    display_name = "District Restriction Type"
    option_none = 0
    option_require_district_token = 1
    default = 1

class RestrictWestbrook(Toggle):
    display_name = "Restrict Westbrook"
    default = 1

class RestrictCityCenter(Toggle):
    display_name = "Restrict City Center"
    default = 1

class RestrictHeywood(Toggle):
    display_name = "Restrict Heywood"
    default = 1

class RestrictSantoDomingo(Toggle):
    display_name = "Restrict Santo Domingo"
    default = 1

class RestrictPacifica(Toggle):
    display_name = "Restrict Pacifica"
    default = 1

class RestrictBadlands(Toggle):
    display_name = "Restrict Badlands"
    default = 1

class RestrictDogtown(Toggle):
    display_name = "Restrict Dogtown"
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


class EnableTraps(Toggle):
    display_name = "Enable Traps"
    default = 1

class TrapItemsPerTrap(Range):
    display_name = "Trap Items per Trap"
    range_start = 1
    range_end = 5
    default = 3

class IncludePhantomLibertyDLC(Toggle):
    display_name = "Include Phantom Liberty DLC"
    default = 0

class EnableDeathLink(Toggle):
    display_name = "Death Link"
    default = 0

class OopsAllTraps(Toggle):
    """Replaces all Useful and Filler items with traps"""
    display_name = "Oops! All Traps!"
    default = 0


class VendorSanity(Toggle):
    display_name = "Vendor Sanity"
    default = 0

class VendorRipperdocs(DefaultOnToggle):
    """Include ripperdoc vendor checks when Vendor Sanity is enabled."""
    display_name = "Include Ripperdocs"

class VendorGunsmiths(Toggle):
    """Include weapon vendor checks when Vendor Sanity is enabled."""
    display_name = "Include Weapon Vendors"
    default = 0

class VendorClothing(Toggle):
    """Include clothing vendor checks when Vendor Sanity is enabled."""
    display_name = "Include Clothing Vendors"
    default = 0

class VendorMelee(Toggle):
    """Include melee weapon vendor checks when Vendor Sanity is enabled."""
    display_name = "Include Melee Vendors"
    default = 0

class VendorNetrunners(Toggle):
    """Include netrunner vendor checks when Vendor Sanity is enabled."""
    display_name = "Include Netrunners"
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

    weapon_restriction_type: WeaponRestrictionType
    weapon_restrict_pistol: RestrictPistols
    weapon_restrict_melee: RestrictMelee
    weapon_restrict_rifle: RestrictRifle
    weapon_restrict_sniper: RestrictSniper
    weapon_restrict_lmg: RestrictLMG
    weapon_restrict_shotgun: RestrictShotgun
    weapon_restrict_smg: RestrictSMG
    completion_goal: CompletionGoal
    district_restriction_type: DistrictRestrictionType
    district_restrict_westbrook: RestrictWestbrook
    district_restrict_city_center: RestrictCityCenter
    district_restrict_heywood: RestrictHeywood
    district_restrict_santo_domingo: RestrictSantoDomingo
    district_restrict_pacifica: RestrictPacifica
    district_restrict_badlands: RestrictBadlands
    district_restrict_dogtown: RestrictDogtown
    restrict_by_sub_district: RestrictBySubDistrict
    include_phantom_liberty_dlc: IncludePhantomLibertyDLC
    death_link: EnableDeathLink
    include_gigs: IncludeGigs
    include_tarot: IncludeTarot
    include_cyber_psycho_sighting: IncludeCyberPsychoSighting
    include_contracts: IncludeContracts
    quick_hacks_as_items: QuickHacksAsItems
    include_ncpd_hustles: IncludeNCPDHustles
    include_minor_quests: IncludeMinorQuests
    vendor_sanity: VendorSanity
    vendor_ripperdocs: VendorRipperdocs
    vendor_gunsmiths: VendorGunsmiths
    vendor_clothing: VendorClothing
    vendor_melee: VendorMelee
    vendor_netrunners: VendorNetrunners
    enable_traps: EnableTraps
    trap_amount: TrapItemsPerTrap
    oops_all_traps: OopsAllTraps

    #starting_path: StartingPath
    #include_cyberware: IncludeCyberware
    #include_weapons: IncludeWeapons


# ===== OPTION GROUPS =====
# Groups organize options on the WebHost for better user experience
# Options are displayed in the order specified here

cyberpunk_option_groups = [
    OptionGroup("Quest Options", [
        CompletionGoal,
        IncludeGigs,
        IncludeTarot,
        IncludeCyberPsychoSighting,
        IncludeContracts,
        IncludeNCPDHustles,
        IncludeMinorQuests,
    ]),
    OptionGroup("DLC Options", [
        IncludePhantomLibertyDLC,
    ]),
    OptionGroup("Trap Options", [
        EnableTraps,
        TrapItemsPerTrap,
    ]),
    OptionGroup("District Restriction Options", [
        DistrictRestrictionType,
        RestrictWestbrook,
        RestrictCityCenter,
        RestrictHeywood,
        RestrictSantoDomingo,
        RestrictPacifica,
        RestrictBadlands,
        RestrictDogtown,
        RestrictBySubDistrict,
    ]),
    OptionGroup("Weapon Restriction Options", [
        WeaponRestrictionType,
        RestrictSniper,
        RestrictLMG,
        RestrictMelee,
        RestrictRifle,
        RestrictPistols,
        RestrictShotgun,
        RestrictSMG,
    ]),
    OptionGroup("Item Options", [
        QuickHacksAsItems,
    ]),
    OptionGroup("Vendor Sanity Options", [
        VendorSanity,
        VendorRipperdocs,
        VendorGunsmiths,
        VendorClothing,
        VendorMelee,
        VendorNetrunners,
    ]),
    OptionGroup("Extra Challenge", [
        EnableDeathLink,
        OopsAllTraps
    ], start_collapsed=True),
]


def is_goal_phantom_liberty_only(options: Cyberpunk2077Options) -> bool:
    """Return True when Completion Goal is PL-questline-only mode."""
    return int(options.completion_goal.value) == CompletionGoal.option_complete_only_phantom_liberty_questline


def is_goal_all_side_quests(options: Cyberpunk2077Options) -> bool:
    """Return True when Completion Goal requires clearing all side quests."""
    return int(options.completion_goal.value) == CompletionGoal.option_complete_any_ending_w_all_side_quests


def has_effective_phantom_liberty_dlc(options: Cyberpunk2077Options) -> bool:
    """
    Return True when DLC content should be treated as enabled for generation.

    PL-only completion mode requires Dogtown/PL quest nodes even if the explicit
    include_phantom_liberty_dlc toggle is off.
    """
    return bool(options.include_phantom_liberty_dlc.value) or is_goal_phantom_liberty_only(options)


MAJOR_DISTRICT_OPTION_MAP: Dict[str, str] = {
    "Westbrook": "district_restrict_westbrook",
    "City Center": "district_restrict_city_center",
    "Heywood": "district_restrict_heywood",
    "Santo Domingo": "district_restrict_santo_domingo",
    "Pacifica": "district_restrict_pacifica",
    "Badlands": "district_restrict_badlands",
    "Dogtown": "district_restrict_dogtown",
}

MAJOR_DISTRICT_SLOT_MASK: Dict[str, int] = {
    "Westbrook": 1 << 0,
    "City Center": 1 << 1,
    "Heywood": 1 << 2,
    "Santo Domingo": 1 << 3,
    "Pacifica": 1 << 4,
    "Badlands": 1 << 5,
    "Dogtown": 1 << 6,
}


def is_major_district_token_gated(options: Cyberpunk2077Options, region_name: str) -> bool:
    """Return True when the named major district should require its access token."""
    if int(options.district_restriction_type.value) != DistrictRestrictionType.option_require_district_token:
        return False
    if region_name == "Dogtown" and not has_effective_phantom_liberty_dlc(options):
        return False

    option_attr = MAJOR_DISTRICT_OPTION_MAP.get(region_name)
    return bool(option_attr and getattr(options, option_attr).value)


def get_gated_major_districts(options: Cyberpunk2077Options) -> Tuple[str, ...]:
    """Return the major districts selected for token gating, in stable slot-data order."""
    return tuple(
        district
        for district in MAJOR_DISTRICT_OPTION_MAP
        if is_major_district_token_gated(options, district)
    )


def district_restriction_active(options: Cyberpunk2077Options) -> bool:
    """Return True when any major district token gate is active."""
    return bool(get_gated_major_districts(options))


def get_gated_major_district_mask(options: Cyberpunk2077Options) -> int:
    """Encode gated major districts for the RedScript client slot-data contract."""
    mask = 0
    for district in get_gated_major_districts(options):
        mask |= MAJOR_DISTRICT_SLOT_MASK[district]
    return mask


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
