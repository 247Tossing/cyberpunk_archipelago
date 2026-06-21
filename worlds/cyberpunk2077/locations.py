"""
Cyberpunk 2077 Location Definitions

This file defines all locations (checks) where items can be found in the game.

Locations represent specific spots in the game where the player can collect
randomized items. They have unique IDs for network communication and are
organized by region for easier management.

Each location declares a ``regions`` tuple listing every district the quest
physically touches. Archipelago itself still attaches each location to a
single parent Region (the graph parent); that parent is either
``placement_region`` when set, or ``regions[0]`` otherwise. For multi-district
quests, ``rules.py`` adds a reachability predicate for any listed major
districts that are token-gated, so the generator only considers the location
reachable when the player can enter the required gated districts. See
``LocationData`` for details.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from BaseClasses import Location, LocationProgressType

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

    Region model:
        - Archipelago Locations have exactly one ``parent_region`` (graph parent).
        - ``regions`` is the set of gameplay districts the quest physically touches.
          Quests that move the player through multiple districts list each one.
        - ``placement_region`` (optional) overrides which member of ``regions`` is
          used as the Archipelago graph parent. When ``None``, ``regions[0]`` is
          used. For multi-district quests we typically pick a hub like ``Watson``
          so the location's reachability is not coupled to a token-gated district.
        - When major-district token restrictions are enabled, rules.py adds an
          extra predicate to multi-region locations: the player must be able to
          reach every listed major district that is token-gated. Non-gated
          districts are ignored because the client opens them from slot data.

    Attributes:
        display_name: Human-readable location name (e.g., "Prologue - StreetKid Intro")
        regions: Tuple of region names the location belongs to. Must be non-empty.
                 A single-district quest uses ``("Watson",)``; a multi-district
                 quest uses ``("Watson", "Westbrook", ...)``.
        code: Unique numeric ID for network communication.
              Auto-assigned sequentially at module load by _assign_location_codes().
              Set to None for "event" locations that auto-complete.
        category: Location category for grouping and filtering (default: "misc")
                 Used to group locations by type (main quests, gigs, etc.)
        dlc_only: Whether this location requires Phantom Liberty DLC (default: False)
                 Locations marked dlc_only=True are excluded when DLC is disabled
        placement_region: Optional override for the Archipelago graph parent.
                 Defaults to ``regions[0]``. May intentionally be a region NOT in
                 ``regions`` so multi-district umbrella quests can be parked on a
                 reachable hub (e.g. ``Watson``) while ``regions`` still records
                 the districts the quest actually requires; rules.py adds gated
                 major-district reachability predicates in that case.
    """
    display_name: str
    regions: Tuple[str, ...]  # Districts this location touches; first entry is the default parent
    code: Optional[int] = None  # Auto-assigned at module load; None for event locations
    category: str = "misc"  # Location category (use LocationCategory constants)
    dlc_only: bool = False  # True for Phantom Liberty DLC locations
    progress_type: LocationProgressType = LocationProgressType.DEFAULT  # Controls fill priority (DEFAULT, PRIORITY, EXCLUDED)
    placement_region: Optional[str] = None  # Override of which region this location is parented to in the Archipelago graph
    vendor_subtype: str = ""  # Vendor category for sub-option filtering: "ripperdoc", "gunsmith", "clothing", "melee", "netrunner"

    def __post_init__(self) -> None:
        # Allow callers to pass a list or single string for ergonomics; normalize to tuple
        if isinstance(self.regions, str):
            self.regions = (self.regions,)
        elif not isinstance(self.regions, tuple):
            self.regions = tuple(self.regions)

        if not self.regions:
            raise ValueError(
                f"LocationData {self.display_name!r}: regions must contain at least one region"
            )

    @property
    def parent_region(self) -> str:
        """Region used as the Archipelago Location's parent_region."""
        return self.placement_region if self.placement_region is not None else self.regions[0]


# ===== LOCATION CATEGORY TYPES =====
# These constants define location categories for grouping and filtering
# Used with the LocationData.category field to explicitly categorize locations

class LocationCategory:
    """
    Location category constants for explicit categorization.

    Categories allow grouping locations independently of their region,
    making it easier to filter locations by type in options and generation logic.
    """
    EVENT = "event"                      # Event locations (code=None, auto-complete)
    MAIN_QUEST = "main_quest"            # Main story quests (critical path)
    SIDE_QUEST = "side_quest"            # Side quests (companion quests, storyline)
    ENDING_SIDE_QUEST = "ending_side_quest"  # Side quests required for alternate endings
    GIG = "gig"                          # Gig missions (fixer contracts)
    CYBERPSYCHO = "cyberpsycho"          # Cyberpsycho Sighting encounters
    NCPD_HUSTLE = "ncpd_hustle"          # NCPD Scanner Hustles (street crimes)
    MINOR_QUEST = "minor_quest"          # Minor quests (tarot, vehicles, etc.)
    ENDING = "ending"                    # Game endings
    EPILOGUE = "epilogue"                # Epilogue content
    DLC_MAIN = "dlc_main"                # Phantom Liberty main story
    DLC_SIDE = "dlc_side"                # Phantom Liberty side content
    MISC = "misc"                        # Uncategorized/miscellaneous
    TAROT = "tarot"                      # Tarot card locations
    VENDOR = "vendor"                    # Vendor stock checks


# ===== LOCATION TABLE =====
# This dictionary maps internal location IDs to their definitions
# Keys are internal game IDs (what the game client sends)
# Values contain display names, codes, and regions

# Location codes are AUTO-ASSIGNED sequentially (0, 1, 2, ...) at module load
# by _assign_location_codes() below the table. The full Archipelago ID for each
# location is BASE_ID + code (e.g., 2077000 + 0 = 2077000).

# WARNING: Codes are assigned by insertion order. Appending new entries at the
# end of a section is safe. Inserting in the middle or reordering will shift all
# subsequent codes and invalidate any previously generated seeds/games.
# Organize locations by region/district for easier management
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
    "Lifepath Chosen": LocationData(display_name="Lifepath Chosen", regions=("Watson",), category=LocationCategory.MAIN_QUEST),
    "Ending Reached" : LocationData(display_name="Ending Reached", regions=("Watson",), category=LocationCategory.MAIN_QUEST),
    # Tutorial might get re-added if requested
    #"q000_tutorial": LocationData(display_name="Prologue - Practice Makes Perfect", regions=("Watson",), category=LocationCategory.MAIN_QUEST),
    "q001_intro": LocationData(display_name="Prologue - The Rescue", regions=("Watson",), category=LocationCategory.MAIN_QUEST),
    "q001_01_victor": LocationData(display_name="Prologue - The Ripperdoc", regions=("Watson",), category=LocationCategory.MAIN_QUEST),
    "q001_02_dex": LocationData(display_name="Prologue - The Ride", regions=("Watson",), category=LocationCategory.MAIN_QUEST),
    "q003_maelstrom": LocationData(display_name="Prologue - The Pickup", regions=("Watson",), category=LocationCategory.MAIN_QUEST),
    "q004_braindance": LocationData(display_name="Prologue - The Information", regions=("Watson",), category=LocationCategory.MAIN_QUEST),
    "q005_heist": LocationData(display_name="Prologue - The Heist", regions=("Watson",), category=LocationCategory.MAIN_QUEST),
    "q101_01_firestorm": LocationData(display_name="Prologue - Love Like Fire", regions=("Watson",), category=LocationCategory.MAIN_QUEST, progress_type=LocationProgressType.PRIORITY),

    # =================================
    # Post-Heist Main Story
    # =================================
    "q101_resurrection": LocationData(display_name="Main - Playing for Time", regions=("Watson",), category=LocationCategory.MAIN_QUEST),
    "q103_warhead": LocationData(display_name="Main - Ghost Town", regions=("Badlands",), category=LocationCategory.MAIN_QUEST),
    "q104_01_sabotage": LocationData(display_name="Main - Lightning Breaks", regions=("Badlands",), category=LocationCategory.MAIN_QUEST),
    "q104_02_av_chase": LocationData(display_name="Main - Life During Wartime", regions=("Badlands",), category=LocationCategory.MAIN_QUEST),
    "q105_dollhouse": LocationData(display_name="Main - Automatic Love", regions=("Westbrook",), category=LocationCategory.MAIN_QUEST),
    "q105_02_jigjig": LocationData(display_name="Main - The Space in Between", regions=("Westbrook",), category=LocationCategory.MAIN_QUEST),
    "q105_03_braindance_studio": LocationData(display_name="Main - Disasterpiece", regions=("Santo Domingo", "Westbrook"), category=LocationCategory.MAIN_QUEST),
    "q105_04_judys": LocationData(display_name="Main - Double Life", regions=("Watson",), category=LocationCategory.MAIN_QUEST),
    "q110_01_voodooboys": LocationData(display_name="Main - M'ap Tann Pèlen", regions=("Pacifica",), category=LocationCategory.MAIN_QUEST),
    "q110_voodoo": LocationData(display_name="Main - I Walk the Line", regions=("Pacifica",), category=LocationCategory.MAIN_QUEST),
    "q110_03_cyberspace": LocationData(display_name="Main - Transmission", regions=("Pacifica",), category=LocationCategory.MAIN_QUEST, progress_type=LocationProgressType.PRIORITY),
    "q108_johnny": LocationData(display_name="Main - Never Fade Away", regions=("Pacifica",), category=LocationCategory.MAIN_QUEST),
    "q112_01_old_friend": LocationData(display_name="Main - Down on the Street", regions=("City Center",), category=LocationCategory.MAIN_QUEST),
    "q112_02_industrial_park": LocationData(display_name="Main - Gimme Danger", regions=("Santo Domingo", "Westbrook"), category=LocationCategory.MAIN_QUEST),
    "q112_03_dashi_parade": LocationData(display_name="Main - Play It Safe", regions=("Westbrook",), category=LocationCategory.MAIN_QUEST),
    "q112_04_hideout": LocationData(display_name="Main - Search and Destroy", regions=("Heywood",), category=LocationCategory.MAIN_QUEST, progress_type=LocationProgressType.PRIORITY),
    "02_sickness": LocationData(display_name="Point of No Return - Nocturne Op55N1", regions=("Heywood",), category=LocationCategory.MAIN_QUEST, progress_type=LocationProgressType.PRIORITY),

    # =====================================
    # Phantom Liberty Checks
    # (Only applicable w/DLC)
    # =====================================
    "q300_phantom_liberty": LocationData(display_name="Phantom Liberty - Phantom Liberty", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q301_crash": LocationData(display_name="Phantom Liberty - Dog Eat Dog", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True, progress_type=LocationProgressType.PRIORITY),
    "q301_finding_myers": LocationData(display_name="Phantom Liberty - Hole in the Sky", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q301_q302_rescue_myers": LocationData(display_name="Phantom Liberty - Spider and the Fly", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q302_reed": LocationData(display_name="Phantom Liberty - Lucretia My Reflection", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True, progress_type=LocationProgressType.PRIORITY),
    "q303_baron": LocationData(display_name="Phantom Liberty - The Damned", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q303_hands": LocationData(display_name="Phantom Liberty - Get It Together", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q303_songbird": LocationData(display_name="Phantom Liberty - You Know My Name", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q304_stadium": LocationData(display_name="Phantom Liberty - Birds with Broken Wings", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q304_netrunners": LocationData(display_name="Phantom Liberty - I've Seen That Face Before", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q304_deal": LocationData(display_name="Phantom Liberty - Firestarter", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True, progress_type=LocationProgressType.PRIORITY),
    # Firestarter splits the finale into Reed vs Songbird paths; only one branch is
    # playable per run. Three abstract checks cover both paths (see APQuestLocationLookup).
    "pl_split_quest_1": LocationData(display_name="PL - Split Quest 1", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "pl_split_quest_2": LocationData(display_name="PL - Split Quest 2", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "pl_split_quest_3": LocationData(display_name="PL - Split Quest 3", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True, progress_type=LocationProgressType.PRIORITY),
    "q307_before_tomorrow": LocationData(display_name="Phantom Liberty - Who Wants to Live Forever", regions=("Dogtown",), category=LocationCategory.DLC_MAIN, dlc_only=True),

    # =================================
    # Major Companion Arcs
    # =================================

    # --- Panam Palmer (The Star Ending Arc) ---
    "sq004_riders_on_the_storm": LocationData(display_name="Riders on the Storm", regions=("Badlands",), category=LocationCategory.ENDING_SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq027_01_basilisk_convoy": LocationData(display_name="With a Little Help from My Friends", regions=("Badlands",), category=LocationCategory.ENDING_SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq027_02_raffen_shiv_attack": LocationData(display_name="Queen of the Highway", regions=("Badlands",), category=LocationCategory.ENDING_SIDE_QUEST, progress_type=LocationProgressType.PRIORITY), # CAPSTONE

    # --- Judy Alvarez Arc ---
    "sq026_01_suicide": LocationData(display_name="Both Sides, Now", regions=("Watson",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq026_02_maiko": LocationData(display_name="Ex-Factor", regions=("Watson",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq026_03_pizza": LocationData(display_name="Talkin' 'bout a Revolution", regions=("Watson",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq026_04_hiromi": LocationData(display_name="Pisces", regions=("Westbrook",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq030_judy_romance": LocationData(display_name="Pyramid Song", regions=("Badlands", "Westbrook"), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.PRIORITY), # CAPSTONE

    # --- River Ward & Peralez Arcs ---
    "sq012_lost_girl": LocationData(display_name="I Fought the Law", regions=("Heywood",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED), # Branches to both River and Peralez
    "sq006_dream_on": LocationData(display_name="Dream On", regions=("City Center",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.PRIORITY), # PERALEZ CAPSTONE
    "sq021_sick_dreams": LocationData(display_name="The Hunt", regions=("Heywood",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq029_sobchak_romance": LocationData(display_name="Following the River", regions=("Santo Domingo", "Westbrook"), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.PRIORITY), # RIVER CAPSTONE

    # --- Kerry Eurodyne & Samurai Arc ---
    "sq011_kerry": LocationData(display_name="Holdin' On", regions=("Westbrook",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq011_johnny": LocationData(display_name="Second Conflict", regions=("Watson",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq011_concert": LocationData(display_name="A Like Supreme", regions=("Watson",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED), # End of Samurai reunion
    "sq017_kerry": LocationData(display_name="Rebel! Rebel!", regions=("Westbrook",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq017_01_riot_club": LocationData(display_name="I Don't Wanna Hear It", regions=("Watson",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq017_02_lounge": LocationData(display_name="Off the Leash", regions=("Westbrook",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq028_kerry_romance": LocationData(display_name="Boat Drinks", regions=("Pacifica",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.PRIORITY), # CAPSTONE

    # --- Rogue & Johnny (The Sun Ending Arc) ---
    "sq031_smack_my_bitch_up": LocationData(display_name="A Cool Metal Fire", regions=("Watson",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq031_rogue": LocationData(display_name="Chippin' In", regions=("Watson",), category=LocationCategory.ENDING_SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq031_cinema": LocationData(display_name="Blistering Love", regions=("Westbrook",), category=LocationCategory.ENDING_SIDE_QUEST, progress_type=LocationProgressType.PRIORITY), # CAPSTONE


    # =================================
    # Minor Story Arcs & Standalones
    # =================================

    # --- Delamain Arc ---
    "sq025_0_pickup": LocationData(display_name="Human Nature", regions=("Watson",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq025_compensation": LocationData(display_name="Tune Up", regions=("City Center",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq025_delamain": LocationData(display_name="Epistrophy", regions=("Heywood",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq025c01_angry": LocationData(display_name="Epistrophy: Wellsprings", regions=("Heywood",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq025c02_sad": LocationData(display_name="Epistrophy: North Oak", regions=("Westbrook",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq025c03_mean": LocationData(display_name="Epistrophy: Coastview", regions=("Pacifica",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq025c04_manic": LocationData(display_name="Epistrophy: Rancho Coronado", regions=("Santo Domingo",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq025c05_scared": LocationData(display_name="Epistrophy: Northside", regions=("Watson",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq025c06_mean": LocationData(display_name="Epistrophy: Badlands", regions=("Badlands",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq025c07_suicidal": LocationData(display_name="Epistrophy: The Glen", regions=("Heywood",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq025b_delamain_insurgence": LocationData(display_name="Don't Lose Your Mind", regions=("Heywood",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.PRIORITY), # CAPSTONE

    # --- Claire / The Beast in Me Arc ---
    "07_nc_underground": LocationData(display_name="The Beast In Me", regions=("Badlands", "City Center", "Santo Domingo"), category=LocationCategory.SIDE_QUEST, placement_region="Watson", progress_type=LocationProgressType.EXCLUDED),
    "sq024_badlands_race": LocationData(display_name="The Beast in Me: Badlands", regions=("Badlands",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq024_city_race": LocationData(display_name="The Beast in Me: City Center", regions=("City Center",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq024_santo_domingo_race": LocationData(display_name="The Beast in Me: Santo Domingo", regions=("Santo Domingo",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq024_the_big_race": LocationData(display_name="The Beast in Me: The Big Race", regions=("Santo Domingo", "Westbrook"), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.PRIORITY), # CAPSTONE

    # --- Joshua Stephenson / Sinnerman Arc ---
    "sq023_hit_order": LocationData(display_name="Sinnerman", regions=("Santo Domingo",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq023_bd_passion": LocationData(display_name="There Is A Light That Never Goes Out", regions=("Westbrook",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq023_real_passion": LocationData(display_name="They Won't Go When I Go", regions=("Westbrook",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.PRIORITY), # CAPSTONE

    # --- Early Game / Intro Standalones ---
    "sq018_jackie": LocationData(display_name="Heroes", regions=("Heywood",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED), # Great quest, but narratively early; excluded to keep priority pool tight
    "sq_q001_tbug": LocationData(display_name="The Gift", regions=("Watson",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq_q001_wakako": LocationData(display_name="The Gig", regions=("Watson",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "sq_q001_wilson": LocationData(display_name="The Gun", regions=("Watson",), category=LocationCategory.SIDE_QUEST, progress_type=LocationProgressType.EXCLUDED),
    # =================================
    # Gigs
    # =================================
    "sts_bls_ina_02": LocationData(display_name="Gig: Big Pete's Got Big Problems", regions=("Badlands",), category=LocationCategory.GIG),
    "sts_bls_ina_03": LocationData(display_name="Gig: Flying Drugs", regions=("Badlands",), category=LocationCategory.GIG),
    "sts_bls_ina_04": LocationData(display_name="Gig: Radar Love", regions=("Badlands",), category=LocationCategory.GIG),
    "sts_bls_ina_05": LocationData(display_name="Gig: Goodbye, Night City", regions=("Badlands",), category=LocationCategory.GIG),
    "sts_bls_ina_06": LocationData(display_name="Gig: No Fixers", regions=("Badlands",), category=LocationCategory.GIG),
    "sts_bls_ina_07": LocationData(display_name="Gig: Dancing on a Minefield", regions=("Badlands",), category=LocationCategory.GIG),
    "sts_bls_ina_08": LocationData(display_name="Gig: Trevor's Last Ride", regions=("Badlands",), category=LocationCategory.GIG),
    "sts_bls_ina_09": LocationData(display_name="Gig: MIA", regions=("Badlands",), category=LocationCategory.GIG),
    "sts_bls_ina_11": LocationData(display_name="Gig: Sparring Partner", regions=("Badlands",), category=LocationCategory.GIG),
    "sts_cct_cpz_01": LocationData(display_name="Gig: Serial Suicide", regions=("City Center",), category=LocationCategory.GIG),
    "sts_cct_dtn_02": LocationData(display_name="Gig: An Inconvenient Killer", regions=("City Center",), category=LocationCategory.GIG),
    "sts_cct_dtn_03": LocationData(display_name="Gig: A Lack of Empathy", regions=("City Center",), category=LocationCategory.GIG),
    "sts_cct_dtn_04": LocationData(display_name="Gig: Guinea Pigs", regions=("City Center",), category=LocationCategory.GIG),
    "sts_cct_dtn_05": LocationData(display_name="Gig: The Frolics of Councilwoman Cole", regions=("City Center",), category=LocationCategory.GIG),
    "sts_hey_gle_01": LocationData(display_name="Gig: Eye for an Eye", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_hey_gle_03": LocationData(display_name="Gig: Psychofan", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_hey_gle_04": LocationData(display_name="Gig: Fifth Column", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_hey_gle_05": LocationData(display_name="Gig: Going Up or Down?", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_hey_gle_06": LocationData(display_name="Gig: Life's Work", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_hey_rey_01": LocationData(display_name="Gig: Bring Me the Head of Gustavo Orta", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_hey_rey_02": LocationData(display_name="Gig: Sr. Ladrillo's Private Collection", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_hey_rey_06": LocationData(display_name="Gig: Jeopardy", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_hey_rey_08": LocationData(display_name="Gig: Old Friends", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_hey_rey_09": LocationData(display_name="Gig: Getting Warmer...", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_hey_spr_01": LocationData(display_name="Gig: On a Tight Leash", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_hey_spr_03": LocationData(display_name="Gig: The Lord Giveth and Taketh Away", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_hey_spr_06": LocationData(display_name="Gig: Hot Merchandise", regions=("Heywood",), category=LocationCategory.GIG),
    "sts_pac_cvi_02": LocationData(display_name="Gig: Two Wrongs Makes Us Right", regions=("Pacifica",), category=LocationCategory.GIG),
    "sts_pac_wwd_05": LocationData(display_name="Gig: For My Son", regions=("Pacifica",), category=LocationCategory.GIG),
    "sts_std_arr_01": LocationData(display_name="Gig: Serious Side Effects", regions=("Santo Domingo",), category=LocationCategory.GIG),
    "sts_std_arr_03": LocationData(display_name="Gig: Race to the Top", regions=("Santo Domingo",), category=LocationCategory.GIG),
    "sts_std_arr_05": LocationData(display_name="Gig: Breaking News", regions=("Santo Domingo",), category=LocationCategory.GIG),
    "sts_std_arr_06": LocationData(display_name="Gig: Nasty Hangover", regions=("Santo Domingo",), category=LocationCategory.GIG),
    "sts_std_arr_10": LocationData(display_name="Gig: Severance Package", regions=("Santo Domingo",), category=LocationCategory.GIG),
    "sts_std_arr_11": LocationData(display_name="Gig: Hacking the Hacker", regions=("Santo Domingo",), category=LocationCategory.GIG),
    "sts_std_arr_12": LocationData(display_name="Gig: Desperate Measures", regions=("Santo Domingo",), category=LocationCategory.GIG),
    "sts_std_rcr_01": LocationData(display_name="Gig: The Union Strikes Back", regions=("Santo Domingo",), category=LocationCategory.GIG),
    "sts_std_rcr_02": LocationData(display_name="Gig: Cuckoo's Nest", regions=("Santo Domingo",), category=LocationCategory.GIG),
    "sts_std_rcr_03": LocationData(display_name="Gig: Going-away Party", regions=("Santo Domingo",), category=LocationCategory.GIG),
    "sts_std_rcr_04": LocationData(display_name="Gig: Error 404", regions=("Santo Domingo",), category=LocationCategory.GIG),
    "sts_std_rcr_05": LocationData(display_name="Gig: Family Matters", regions=("Santo Domingo",), category=LocationCategory.GIG),
    "sts_wat_kab_01": LocationData(display_name="Gig: Concrete Cage Trap", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_kab_02": LocationData(display_name="Gig: Hippocratic Oath", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_kab_03": LocationData(display_name="Gig: Backs Against the Wall", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_kab_04": LocationData(display_name="Gig: Fixer, Merc, Soldier, Spy", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_kab_05": LocationData(display_name="Gig: Last Login", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_kab_06": LocationData(display_name="Gig: Shark in the Water", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_kab_07": LocationData(display_name="Gig: Monster Hunt", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_kab_08": LocationData(display_name="Gig: Woman of La Mancha", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_kab_101": LocationData(display_name="Gig: Small Man, Big Evil", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_kab_102": LocationData(display_name="Gig: Welcome to America, Comrade", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_kab_107": LocationData(display_name="Gig: Troublesome Neighbors", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_lch_01": LocationData(display_name="Gig: Catch a Tyger's Toe", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_lch_03": LocationData(display_name="Gig: Bloodsport", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_lch_05": LocationData(display_name="Gig: Playing for Keeps", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_lch_06": LocationData(display_name="Gig: The Heisenberg Principle", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_nid_01": LocationData(display_name="Gig: Occupational Hazard", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_nid_02": LocationData(display_name="Gig: Many Ways to Skin a Cat", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_nid_03": LocationData(display_name="Gig: Flight of the Cheetah", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_nid_04": LocationData(display_name="Gig: Dirty Biz", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_nid_05": LocationData(display_name="Gig: Rite of Passage", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_nid_06": LocationData(display_name="Gig: Lousy Kleppers", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_nid_07": LocationData(display_name="Gig: Scrolls before Swine", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wat_nid_12": LocationData(display_name="Gig: Freedom of the Press", regions=("Watson",), category=LocationCategory.GIG),
    "sts_wbr_hil_01": LocationData(display_name="Gig: Until Death Do Us Part", regions=("Westbrook",), category=LocationCategory.GIG),
    "sts_wbr_hil_06": LocationData(display_name="Gig: Family Heirloom", regions=("Westbrook",), category=LocationCategory.GIG),
    "sts_wbr_hil_07": LocationData(display_name="Gig: Tyger and Vulture", regions=("Westbrook",), category=LocationCategory.GIG),
    "sts_wbr_jpn_01": LocationData(display_name="Gig: Olive Branch", regions=("Westbrook",), category=LocationCategory.GIG),
    "sts_wbr_jpn_02": LocationData(display_name="Gig: We Have Your Wife", regions=("Westbrook",), category=LocationCategory.GIG),
    "sts_wbr_jpn_03": LocationData(display_name="Gig: A Shrine Defiled", regions=("Westbrook",), category=LocationCategory.GIG),
    "sts_wbr_jpn_05": LocationData(display_name="Gig: Wakako's Favorite", regions=("Westbrook",), category=LocationCategory.GIG),
    "sts_wbr_jpn_12": LocationData(display_name="Gig: Greed Never Pays", regions=("Westbrook",), category=LocationCategory.GIG),

    # ================================
    # Contracts
    # ================================
    "ma_bls_ina_se1_02": LocationData(display_name="Reported Crime: Comrade Red", regions=("Badlands",), category=LocationCategory.NCPD_HUSTLE),
    "ma_bls_ina_se1_03": LocationData(display_name="Reported Crime: Blood in the Air", regions=("Badlands",), category=LocationCategory.NCPD_HUSTLE),
    "ma_bls_ina_se1_06": LocationData(display_name="Reported Crime: Extremely Loud and Incredibly Close", regions=("Badlands",), category=LocationCategory.NCPD_HUSTLE),
    "ma_bls_ina_se1_18": LocationData(display_name="Reported Crime: I Don't Like Sand", regions=("Badlands",), category=LocationCategory.NCPD_HUSTLE),
    "ma_bls_ina_se5_33": LocationData(display_name="Reported Crime: Delivery From Above", regions=("Badlands",), category=LocationCategory.NCPD_HUSTLE),
    "ma_cct_dtn_12": LocationData(display_name="Reported Crime: Turn Off the Tap", regions=("City Center",), category=LocationCategory.NCPD_HUSTLE),
    "ma_hey_gle_02": LocationData(display_name="Suspected Organized Crime Activity: Chapel", regions=("Heywood",), category=LocationCategory.NCPD_HUSTLE),
    "ma_hey_gle_07": LocationData(display_name="Reported Crime: Smoking Kills", regions=("Heywood",), category=LocationCategory.NCPD_HUSTLE),
    "ma_hey_spr_11": LocationData(display_name="Suspected Organized Crime Activity: Living the Big Life", regions=("Heywood",), category=LocationCategory.NCPD_HUSTLE),
    "ma_pac_cvi_10": LocationData(display_name="Reported Crime: Roadside Picnic", regions=("Pacifica",), category=LocationCategory.NCPD_HUSTLE),
    "ma_pac_cvi_12": LocationData(display_name="Suspected Organized Crime Activity: Wipe the Gonk, Take the Implants", regions=("Pacifica",), category=LocationCategory.NCPD_HUSTLE),
    "ma_pac_cvi_13": LocationData(display_name="Reported Crime: Honey, Where are You?", regions=("Pacifica",), category=LocationCategory.NCPD_HUSTLE),
    "ma_std_arr_07": LocationData(display_name="Reported Crime: Disloyal Employee", regions=("Santo Domingo",), category=LocationCategory.NCPD_HUSTLE),
    "ma_std_arr_10": LocationData(display_name="Reported Crime: Ooh, Awkward", regions=("Santo Domingo",), category=LocationCategory.NCPD_HUSTLE),
    "ma_std_arr_14": LocationData(display_name="Reported Crime: Supply Management", regions=("Santo Domingo",), category=LocationCategory.NCPD_HUSTLE),
    "ma_std_rcr_10": LocationData(display_name="Reported Crime: Welcome to Night City", regions=("Santo Domingo",), category=LocationCategory.NCPD_HUSTLE),
    "ma_std_rcr_12": LocationData(display_name="Reported Crime: A Stroke of Luck", regions=("Santo Domingo",), category=LocationCategory.NCPD_HUSTLE),
    "ma_std_rcr_13": LocationData(display_name="Reported Crime: Justice Behind Bars", regions=("Santo Domingo",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_kab_05": LocationData(display_name="Reported Crime: Protect and Serve", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_01": LocationData(display_name="Suspected Organized Crime Activity: Opposites Attract", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_03": LocationData(display_name="Reported Crime: Worldly Possessions", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_05": LocationData(display_name="Reported Crime: Paranoia", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_08": LocationData(display_name="Suspected Organized Crime Activity: Tygers by the Tail", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_15": LocationData(display_name="Reported Crime: Dangerous Currents", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_01": LocationData(display_name="Suspected Organized Crime Activity: Vice Control", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_02": LocationData(display_name="Suspected Organized Crime Activity: Just Say No", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_06": LocationData(display_name="Suspected Organized Crime Activity: No License, No Problem", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_10": LocationData(display_name="Reported Crime: Dredged Up", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_12": LocationData(display_name="Reported Crime: Needle in a Haystack", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_26": LocationData(display_name="Reported Crime: One Thing Led to Another", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_27": LocationData(display_name="Reported Crime: Don't Forget the Parking Brake!", regions=("Watson",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_hil_05": LocationData(display_name="Reported Crime: You Play with Fire...", regions=("Westbrook",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_jpn_07": LocationData(display_name="Reported Crime: Lost and Found", regions=("Westbrook",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_jpn_09": LocationData(display_name="Reported Crime: Another Circle of Hell", regions=("Westbrook",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_nok_01": LocationData(display_name="Reported Crime: Crash Test", regions=("Westbrook",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_nok_03": LocationData(display_name="Reported Crime: Table Scraps", regions=("Westbrook",), category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_nok_05": LocationData(display_name="Suspected Organized Crime Activity: Privacy Policy Violation", regions=("Westbrook",), category=LocationCategory.NCPD_HUSTLE),

    # =================================
    # Minor Quests
    # =================================
    "mq036_overload": LocationData(display_name="Sweet Dreams", regions=("Westbrook",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED), # Inventory Wipe Risk
    "mq010_barry": LocationData(display_name="Happy Together", regions=("Watson",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED), # Timed Fail State
    "mq001_scorpion": LocationData(display_name="I'll Fly Away", regions=("Badlands",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED), # Highly Missable
    "mq041_corpo": LocationData(display_name="War Pigs", regions=("Watson",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED), # Lifepath Exclusive
    "mq017_streetkid": LocationData(display_name="Small Man, Big Mouth", regions=("Watson",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED), # Lifepath Exclusive
    "mq045_victor_debt": LocationData(display_name="Paid in Full", regions=("Watson",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED), # 21k Economy Block
    "mq033_tarot": LocationData(display_name="Fool on the Hill", regions=("Night City",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED), # Redundant with Tarot locations
    "q003_stout": LocationData(display_name="Venus in Furs", regions=("Watson",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "mq006_rollercoaster": LocationData(display_name="Love Rollercoaster", regions=("Pacifica",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "mq011_wilson": LocationData(display_name="Shoot To Thrill", regions=("Watson",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "mq028_stalker": LocationData(display_name="Every Breath You Take", regions=("Westbrook",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED),

    # --- Beat on the Brat Arc ---
    "mq025_02_kabuki": LocationData(display_name="Beat on the Brat: Kabuki", regions=("Watson",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "mq025_03_arroyo": LocationData(display_name="Beat on the Brat: Arroyo", regions=("Santo Domingo",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "mq025_05_glen": LocationData(display_name="Beat on the Brat: The Glen", regions=("Heywood",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "mq025_06_pacifica": LocationData(display_name="Beat on the Brat: Pacifica", regions=("Pacifica",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "mq025_07_fight_club": LocationData(display_name="Beat on the Brat: Rancho Coronado", regions=("Santo Domingo",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "mq025_psycho_brawl": LocationData(display_name="Beat on the Brat", regions=("Pacifica",), category=LocationCategory.MINOR_QUEST), # CAPSTONE

    # --- Zen Master Arc ---
    "mq014_zen": LocationData(display_name="Imagine", regions=("Watson",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "mq014_02_second": LocationData(display_name="Stairway To Heaven", regions=("Heywood",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "mq014_03_third": LocationData(display_name="Poem Of The Atoms", regions=("Westbrook",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.EXCLUDED),
    "mq014_04_fourth": LocationData(display_name="Meetings Along The Edge", regions=("City Center",), category=LocationCategory.MINOR_QUEST, progress_type=LocationProgressType.PRIORITY), # CAPSTONE

    # --- Standard Minor Quests (Safe to leave as default filler) ---
    "mq002_veterans": LocationData(display_name="Gun Music", regions=("Santo Domingo",), category=LocationCategory.MINOR_QUEST),
    "mq003_orbitals": LocationData(display_name="Space Oddity", regions=("Santo Domingo",), category=LocationCategory.MINOR_QUEST),
    "mq005_alley": LocationData(display_name="Only Pain", regions=("Heywood",), category=LocationCategory.MINOR_QUEST),
    "mq007_smartgun": LocationData(display_name="Machine Gun", regions=("Heywood",), category=LocationCategory.MINOR_QUEST),
    "mq008_party": LocationData(display_name="Stadium Love", regions=("Santo Domingo",), category=LocationCategory.MINOR_QUEST),
    "mq012_stud": LocationData(display_name="Burning Desire", regions=("Watson",), category=LocationCategory.MINOR_QUEST),
    "mq013_punks": LocationData(display_name="A Day In The Life", regions=("Santo Domingo",), category=LocationCategory.MINOR_QUEST),
    "mq015_wizardbook": LocationData(display_name="Spellbound", regions=("Westbrook",), category=LocationCategory.MINOR_QUEST),
    "mq016_bartmoss": LocationData(display_name="KOLD MIRAGE", regions=("Watson",), category=LocationCategory.MINOR_QUEST),
    "mq018_writer": LocationData(display_name="Killing In The Name", regions=("Westbrook",), category=LocationCategory.MINOR_QUEST),
    "mq019_paparazzi": LocationData(display_name="Violence", regions=("Westbrook",), category=LocationCategory.MINOR_QUEST),
    "mq021_guide": LocationData(display_name="Fortunate Son", regions=("Badlands",), category=LocationCategory.MINOR_QUEST),
    "mq022_ezekiel": LocationData(display_name="Ezekiel Saw the Wheel", regions=("Santo Domingo",), category=LocationCategory.MINOR_QUEST),
    "mq023_bootleg": LocationData(display_name="The Ballad of Buck Ravers", regions=("Westbrook",), category=LocationCategory.MINOR_QUEST),
    "mq024_sandra": LocationData(display_name="Full Disclosure", regions=("Watson",), category=LocationCategory.MINOR_QUEST),
    "mq026_conspiracy": LocationData(display_name="The Prophet's Song", regions=("Watson",), category=LocationCategory.MINOR_QUEST),
    "mq029_tourist": LocationData(display_name="The Highwayman", regions=("Santo Domingo",), category=LocationCategory.MINOR_QUEST),
    "mq030_melisa": LocationData(display_name="Bullets", regions=("City Center",), category=LocationCategory.MINOR_QUEST),
    "mq032_sacrum": LocationData(display_name="Sacrum Profanum", regions=("Watson",), category=LocationCategory.MINOR_QUEST),
    "mq035_ozob": LocationData(display_name="Send in the Clowns", regions=("Westbrook",), category=LocationCategory.MINOR_QUEST),
    "mq037_brendan": LocationData(display_name="Coin Operated Boy", regions=("Westbrook",), category=LocationCategory.MINOR_QUEST),
    "mq038_neweridentity": LocationData(display_name="Big in Japan", regions=("Watson",), category=LocationCategory.MINOR_QUEST),
    "mq040_biosculpt": LocationData(display_name="Raymond Chandler Evening", regions=("Heywood",), category=LocationCategory.MINOR_QUEST),
    "mq044_jakes_vehicle": LocationData(display_name="Sex On Wheels", regions=("Heywood",), category=LocationCategory.MINOR_QUEST),
    "mq047_ad_vehicle": LocationData(display_name="Dressed to Kill", regions=("Watson",), category=LocationCategory.MINOR_QUEST),
    "mq049_edgerunners": LocationData(display_name="Over the Edge", regions=("Santo Domingo",), category=LocationCategory.MINOR_QUEST),
    "mq050_ken_block_tribute": LocationData(display_name="I'm in Love with My Car", regions=("Watson",), category=LocationCategory.MINOR_QUEST),
    "mq057_motorbreath": LocationData(display_name="Motorbreath", regions=("Santo Domingo", "Westbrook"), category=LocationCategory.MINOR_QUEST),
    "mq058_semimaru_crystalcoat": LocationData(display_name="Where Eagles Dare", regions=("Westbrook",), category=LocationCategory.MINOR_QUEST),
    "mq059_freedom": LocationData(display_name="Freedom", regions=("Watson",), category=LocationCategory.MINOR_QUEST),
    "mq060_nitro": LocationData(display_name="Nitro (Youth Energy)", regions=("Watson",), category=LocationCategory.MINOR_QUEST),
    "archer_bandit": LocationData(display_name="Quartz 'Bandit'", regions=("Rancho Coronado", "Westbrook"), category=LocationCategory.MINOR_QUEST),

    # =================================
    # Phantom Liberty Gigs
    # =================================
    "sts_ep1_04": LocationData(display_name="Gig: Prototype in the Scraper", regions=("Dogtown",), category=LocationCategory.GIG, dlc_only=True, progress_type=LocationProgressType.PRIORITY),
    "sts_ep1_08": LocationData(display_name="Gig: Spy in the Jungle", regions=("Dogtown",), category=LocationCategory.GIG, dlc_only=True, progress_type=LocationProgressType.PRIORITY),
    "sts_ep1_10": LocationData(display_name="Gig: Waiting for Dodger", regions=("Dogtown",), category=LocationCategory.GIG, dlc_only=True, progress_type=LocationProgressType.PRIORITY),

    # The rest remain excluded
    "sts_ep1_01": LocationData(display_name="Gig: Dogtown Saints", regions=("Dogtown",), category=LocationCategory.GIG, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "sts_ep1_03": LocationData(display_name="Gig: The Man Who Killed Jason Foreman", regions=("Dogtown",), category=LocationCategory.GIG, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "sts_ep1_06": LocationData(display_name="Gig: Heaviest of Hearts", regions=("Dogtown",), category=LocationCategory.GIG, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "sts_ep1_07": LocationData(display_name="Gig: Roads to Redemption", regions=("Dogtown",), category=LocationCategory.GIG, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "sts_ep1_12": LocationData(display_name="Gig: Treating Symptoms", regions=("Dogtown",), category=LocationCategory.GIG, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "sts_ep1_13": LocationData(display_name="Gig: Talent Academy", regions=("Dogtown",), category=LocationCategory.GIG, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),

    # --- Phantom Liberty: Epilogues & Capstones ---
    "wst_ep1_11_bill_meeting": LocationData(display_name="New Person, Same Old Mistakes", regions=("Dogtown",), category=LocationCategory.DLC_SIDE, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "sts_ep1_08_steven_meeting_night_city": LocationData(display_name="The Show Must Go On", regions=("Dogtown",), category=LocationCategory.MINOR_QUEST, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "wst_ep1_09": LocationData(display_name="One Way or Another", regions=("Dogtown",), category=LocationCategory.MINOR_QUEST, dlc_only=True, progress_type=LocationProgressType.EXCLUDED), 
    "mq033_ep1": LocationData(display_name="Tomorrow Never Knows", regions=("Dogtown",), category=LocationCategory.MINOR_QUEST, dlc_only=True, progress_type=LocationProgressType.PRIORITY),

    # =================================
    # Unique Item Checks
    # =================================

    # =================================
    # Tarot
    # =================================
    # --- Phantom Liberty Tarot Counter (Dogtown) ---
    "ap_tarot_26": LocationData(display_name="Collected 23 Tarot", regions=("Dogtown",), category=LocationCategory.TAROT, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_25": LocationData(display_name="Collected 24 Tarot", regions=("Dogtown",), category=LocationCategory.TAROT, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_24": LocationData(display_name="Collected 25 Tarot", regions=("Dogtown",), category=LocationCategory.TAROT, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_23": LocationData(display_name="Collected 26 Tarot", regions=("Dogtown",), category=LocationCategory.TAROT, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),

    # --- Base Game Tarot Counter (Night City) ---
    "ap_tarot_1": LocationData(display_name="Collected 1 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_2": LocationData(display_name="Collected 2 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_3": LocationData(display_name="Collected 3 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_4": LocationData(display_name="Collected 4 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_5": LocationData(display_name="Collected 5 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_6": LocationData(display_name="Collected 6 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_7": LocationData(display_name="Collected 7 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_8": LocationData(display_name="Collected 8 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_9": LocationData(display_name="Collected 9 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_10": LocationData(display_name="Collected 10 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_11": LocationData(display_name="Collected 11 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_12": LocationData(display_name="Collected 12 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_13": LocationData(display_name="Collected 13 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_14": LocationData(display_name="Collected 14 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_15": LocationData(display_name="Collected 15 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_16": LocationData(display_name="Collected 16 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_17": LocationData(display_name="Collected 17 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_18": LocationData(display_name="Collected 18 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_19": LocationData(display_name="Collected 19 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_20": LocationData(display_name="Collected 20 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_21": LocationData(display_name="Collected 21 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_22": LocationData(display_name="Collected 22 Tarot", regions=("Watson",), category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    # =================================

    # =================================
    # Cyber Psycho Sighting Locations
    # ==================================
    "mq043_cyberpsychos": LocationData(display_name="Psycho Killer", regions=("Watson",),category=LocationCategory.CYBERPSYCHO),
    "ma_wat_nid_22": LocationData(display_name="Cyberpsycho Sighting: Six Feet Under", regions=("Watson",), category=LocationCategory.CYBERPSYCHO),
    "ma_wat_nid_15": LocationData(display_name="Cyberpsycho Sighting: Bloody Ritual", regions=("Watson",), category=LocationCategory.CYBERPSYCHO),
    "ma_wat_nid_03": LocationData(display_name="Cyberpsycho Sighting: Where the Bodies Hit the Floor", regions=("Watson",), category=LocationCategory.CYBERPSYCHO),
    "ma_wat_kab_02": LocationData(display_name="Cyberpsycho Sighting: Demons of War", regions=("Watson",), category=LocationCategory.CYBERPSYCHO),
    "ma_wat_kab_08": LocationData(display_name="Cyberpsycho Sighting: Lt. Mower", regions=("Watson",), category=LocationCategory.CYBERPSYCHO),
    "ma_wat_lch_06": LocationData(display_name="Cyberpsycho Sighting: Ticket to the Major Leagues", regions=("Watson",), category=LocationCategory.CYBERPSYCHO),
    "ma_bls_ina_se1_07": LocationData(display_name="Cyberpsycho Sighting: The Wasteland",regions=("Badlands",), category=LocationCategory.CYBERPSYCHO),
    "ma_bls_ina_se1_08": LocationData(display_name="Cyberpsycho Sighting: House on a Hill",regions=("Badlands",), category=LocationCategory.CYBERPSYCHO),
    "ma_bls_ina_se1_22": LocationData(display_name="Cyberpsycho Sighting: Second Chances",regions=("Badlands",), category=LocationCategory.CYBERPSYCHO),
    "ma_cct_dtn_03": LocationData(display_name="Cyberpsycho Sighting: On Deaf Ears",regions=("City Center",), category=LocationCategory.CYBERPSYCHO),
    "ma_cct_dtn_07": LocationData(display_name="Cyberpsycho Sighting: Phantom of Night City", regions=("City Center",), category=LocationCategory.CYBERPSYCHO),
    "ma_hey_spr_04": LocationData(display_name="Cyberpsycho Sighting: Seaside Cafe", regions=("Heywood",), category=LocationCategory.CYBERPSYCHO),
    "ma_hey_spr_06": LocationData(display_name="Cyberpsycho Sighting: Letter of the Law", regions=("Heywood",), category=LocationCategory.CYBERPSYCHO),
    "ma_pac_cvi_08": LocationData(display_name="Cyberpsycho Sighting: Smoke on the Water", regions=("Pacifica",), category=LocationCategory.CYBERPSYCHO),
    "ma_pac_cvi_15": LocationData(display_name="Cyberpsycho Sighting: Lex Talionis",regions=("Pacifica",), category=LocationCategory.CYBERPSYCHO),
    "ma_std_arr_06": LocationData(display_name="Cyberpsycho Sighting: Under the Bridge", regions=("Santo Domingo",), category=LocationCategory.CYBERPSYCHO),
    "ma_std_rcr_11": LocationData(display_name="Cyberpsycho Sighting: Discount Doc", regions=("Santo Domingo",), category=LocationCategory.CYBERPSYCHO),
    # =================================

    # =================================
    # Vendor Sanity
    # =================================

    # --- Ripperdocs (vendor_subtype="ripperdoc") ---
    # wbr_jpn_ripperdoc_01 (Fingers) omitted — scripted permanent vendor lockout
    "VendorCheck_Victor_1": LocationData(display_name="Victor's Shop 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_Victor_2": LocationData(display_name="Victor's Shop 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_Victor_3": LocationData(display_name="Victor's Shop 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_CctDtnRipdoc_1": LocationData(display_name="Downtown Ripperdoc 1", regions=("City Center",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_CctDtnRipdoc_2": LocationData(display_name="Downtown Ripperdoc 2", regions=("City Center",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_CctDtnRipdoc_3": LocationData(display_name="Downtown Ripperdoc 3", regions=("City Center",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),
    "VendorCheck_HeySprRipperdoc_1": LocationData(display_name="Wellsprings Ripperdoc 1", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_HeySprRipperdoc_2": LocationData(display_name="Wellsprings Ripperdoc 2", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_HeySprRipperdoc_3": LocationData(display_name="Wellsprings Ripperdoc 3", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),
    "VendorCheck_PacWwdRipperdoc_1": LocationData(display_name="West Wind Estate Ripperdoc 1", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_PacWwdRipperdoc_2": LocationData(display_name="West Wind Estate Ripperdoc 2", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_PacWwdRipperdoc_3": LocationData(display_name="West Wind Estate Ripperdoc 3", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),
    "VendorCheck_CzConRipdoc_1": LocationData(display_name="Dogtown Center Ripperdoc 1", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_CzConRipdoc_2": LocationData(display_name="Dogtown Center Ripperdoc 2", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_CzConRipdoc_3": LocationData(display_name="Dogtown Center Ripperdoc 3", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),
    "VendorCheck_CzMonumentAnderson_1": LocationData(display_name="Dogtown Monument Ripperdoc (Anderson) 1", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_CzMonumentAnderson_2": LocationData(display_name="Dogtown Monument Ripperdoc (Anderson) 2", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_CzMonumentAnderson_3": LocationData(display_name="Dogtown Monument Ripperdoc (Anderson) 3", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),
    "VendorCheck_CzMonumentFarida_1": LocationData(display_name="Dogtown Monument Ripperdoc (Farida) 1", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_CzMonumentFarida_2": LocationData(display_name="Dogtown Monument Ripperdoc (Farida) 2", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_CzMonumentFarida_3": LocationData(display_name="Dogtown Monument Ripperdoc (Farida) 3", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),
    "VendorCheck_StdArrRipperdoc_1": LocationData(display_name="Arroyo Ripperdoc 1", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_StdArrRipperdoc_2": LocationData(display_name="Arroyo Ripperdoc 2", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_StdArrRipperdoc_3": LocationData(display_name="Arroyo Ripperdoc 3", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),
    "VendorCheck_StdRcrRipperdoc_1": LocationData(display_name="Rancho Coronado Ripperdoc 1", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_StdRcrRipperdoc_2": LocationData(display_name="Rancho Coronado Ripperdoc 2", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_StdRcrRipperdoc_3": LocationData(display_name="Rancho Coronado Ripperdoc 3", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),
    "VendorCheck_WatKabRipperdoc01_1": LocationData(display_name="Kabuki Ripperdoc (Bucks' Clinic) 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WatKabRipperdoc01_2": LocationData(display_name="Kabuki Ripperdoc (Bucks' Clinic) 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WatKabRipperdoc01_3": LocationData(display_name="Kabuki Ripperdoc (Bucks' Clinic) 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WatKabRipperdoc02_1": LocationData(display_name="Kabuki Ripperdoc (Dr. Chrome) 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WatKabRipperdoc02_2": LocationData(display_name="Kabuki Ripperdoc (Dr. Chrome) 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WatKabRipperdoc02_3": LocationData(display_name="Kabuki Ripperdoc (Dr. Chrome) 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WatKabRipperdoc03_1": LocationData(display_name="Kabuki Ripperdoc (Instant Implants) 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WatKabRipperdoc03_2": LocationData(display_name="Kabuki Ripperdoc (Instant Implants) 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WatKabRipperdoc03_3": LocationData(display_name="Kabuki Ripperdoc (Instant Implants) 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_CassiusRyder_1": LocationData(display_name="Cassius Ryder's Clinic 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_CassiusRyder_2": LocationData(display_name="Cassius Ryder's Clinic 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_CassiusRyder_3": LocationData(display_name="Cassius Ryder's Clinic 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WbrHilRipdoc_1": LocationData(display_name="Charter Hill Ripperdoc (Kraviz) 1", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WbrHilRipdoc_2": LocationData(display_name="Charter Hill Ripperdoc (Kraviz) 2", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WbrHilRipdoc_3": LocationData(display_name="Charter Hill Ripperdoc (Kraviz) 3", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),
    "VendorCheck_WbrJpnRipperdoc01_1": LocationData(display_name="Japantown Ripperdoc (Clinic 01) 1", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WbrJpnRipperdoc01_2": LocationData(display_name="Japantown Ripperdoc (Clinic 01) 2", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WbrJpnRipperdoc01_3": LocationData(display_name="Japantown Ripperdoc (Clinic 01) 3", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),
    "VendorCheck_WbrJpnRipperdoc02_1": LocationData(display_name="Japantown Ripperdoc (Clinic 02) 1", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WbrJpnRipperdoc02_2": LocationData(display_name="Japantown Ripperdoc (Clinic 02) 2", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_WbrJpnRipperdoc02_3": LocationData(display_name="Japantown Ripperdoc (Clinic 02) 3", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),
    "VendorCheck_BlsInaSe1Ripperdoc01_1": LocationData(display_name="Jackson Plains Ripperdoc (Stall 1) 1", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_BlsInaSe1Ripperdoc01_2": LocationData(display_name="Jackson Plains Ripperdoc (Stall 1) 2", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_BlsInaSe1Ripperdoc01_3": LocationData(display_name="Jackson Plains Ripperdoc (Stall 1) 3", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),
    "VendorCheck_BlsInaSe1Ripperdoc02_1": LocationData(display_name="Jackson Plains Ripperdoc (Stall 2) 1", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_BlsInaSe1Ripperdoc02_2": LocationData(display_name="Jackson Plains Ripperdoc (Stall 2) 2", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="ripperdoc"),
    "VendorCheck_BlsInaSe1Ripperdoc02_3": LocationData(display_name="Jackson Plains Ripperdoc (Stall 2) 3", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="ripperdoc"),

    # --- Weapon Vendors (vendor_subtype="gunsmith") ---
    "VendorCheck_2ndAmendment_1": LocationData(display_name="2nd Amendment Shop 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_2ndAmendment_2": LocationData(display_name="2nd Amendment Shop 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_2ndAmendment_3": LocationData(display_name="2nd Amendment Shop 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_CctDtnGunsmith_1": LocationData(display_name="Downtown Weapon Vendor 1", regions=("City Center",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_CctDtnGunsmith_2": LocationData(display_name="Downtown Weapon Vendor 2", regions=("City Center",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_CctDtnGunsmith_3": LocationData(display_name="Downtown Weapon Vendor 3", regions=("City Center",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="gunsmith"),
    "VendorCheck_HeyGleGunsmith_1": LocationData(display_name="The Glen Weapon Vendor 1", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_HeyGleGunsmith_2": LocationData(display_name="The Glen Weapon Vendor 2", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_HeyGleGunsmith_3": LocationData(display_name="The Glen Weapon Vendor 3", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="gunsmith"),
    "VendorCheck_HeyReyGunsmith_1": LocationData(display_name="Vista del Rey Weapon Vendor 1", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_HeyReyGunsmith_2": LocationData(display_name="Vista del Rey Weapon Vendor 2", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_HeyReyGunsmith_3": LocationData(display_name="Vista del Rey Weapon Vendor 3", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="gunsmith"),
    "VendorCheck_HeySprGunsmith_1": LocationData(display_name="Wellsprings Weapon Vendor 1", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_HeySprGunsmith_2": LocationData(display_name="Wellsprings Weapon Vendor 2", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_HeySprGunsmith_3": LocationData(display_name="Wellsprings Weapon Vendor 3", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="gunsmith"),
    "VendorCheck_PacWwdGunsmith_1": LocationData(display_name="West Wind Estate Weapon Vendor 1", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_PacWwdGunsmith_2": LocationData(display_name="West Wind Estate Weapon Vendor 2", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_PacWwdGunsmith_3": LocationData(display_name="West Wind Estate Weapon Vendor 3", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="gunsmith"),
    "VendorCheck_StdArrGunsmith_1": LocationData(display_name="Arroyo Weapon Vendor 1", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_StdArrGunsmith_2": LocationData(display_name="Arroyo Weapon Vendor 2", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_StdArrGunsmith_3": LocationData(display_name="Arroyo Weapon Vendor 3", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="gunsmith"),
    "VendorCheck_StdRcrGunsmith_1": LocationData(display_name="Rancho Coronado Weapon Vendor 1", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_StdRcrGunsmith_2": LocationData(display_name="Rancho Coronado Weapon Vendor 2", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_StdRcrGunsmith_3": LocationData(display_name="Rancho Coronado Weapon Vendor 3", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="gunsmith"),
    "VendorCheck_WatNidGunsmith_1": LocationData(display_name="Northside Weapon Vendor 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_WatNidGunsmith_2": LocationData(display_name="Northside Weapon Vendor 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_WatNidGunsmith_3": LocationData(display_name="Northside Weapon Vendor 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_WbrJpnGunsmith_1": LocationData(display_name="Japantown Weapon Vendor 1", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_WbrJpnGunsmith_2": LocationData(display_name="Japantown Weapon Vendor 2", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_WbrJpnGunsmith_3": LocationData(display_name="Japantown Weapon Vendor 3", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="gunsmith"),
    "VendorCheck_BlsInaSe1Gunsmith01a_1": LocationData(display_name="Jackson Plains Weapon Vendor (Marty) 1", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_BlsInaSe1Gunsmith01a_2": LocationData(display_name="Jackson Plains Weapon Vendor (Marty) 2", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_BlsInaSe1Gunsmith01a_3": LocationData(display_name="Jackson Plains Weapon Vendor (Marty) 3", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="gunsmith"),
    "VendorCheck_BlsInaSe1Gunsmith02_1": LocationData(display_name="Jackson Plains Weapon Vendor (Stall 2) 1", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_BlsInaSe1Gunsmith02_2": LocationData(display_name="Jackson Plains Weapon Vendor (Stall 2) 2", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_BlsInaSe1Gunsmith02_3": LocationData(display_name="Jackson Plains Weapon Vendor (Stall 2) 3", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="gunsmith"),
    "VendorCheck_BlsInaSe5Gunsmith_1": LocationData(display_name="Rocky Ridge Weapon Vendor 1", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_BlsInaSe5Gunsmith_2": LocationData(display_name="Rocky Ridge Weapon Vendor 2", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_BlsInaSe5Gunsmith_3": LocationData(display_name="Rocky Ridge Weapon Vendor 3", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="gunsmith"),
    "VendorCheck_CzConGunsmith_1": LocationData(display_name="Dogtown Weapon Vendor 1", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_CzConGunsmith_2": LocationData(display_name="Dogtown Weapon Vendor 2", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="gunsmith"),
    "VendorCheck_CzConGunsmith_3": LocationData(display_name="Dogtown Weapon Vendor 3", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.PRIORITY, vendor_subtype="gunsmith"),

    # --- Clothing Vendors (vendor_subtype="clothing") ---
    "VendorCheck_CctCpzClothing_1": LocationData(display_name="Corpo Plaza Clothing Vendor 1", regions=("City Center",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_CctCpzClothing_2": LocationData(display_name="Corpo Plaza Clothing Vendor 2", regions=("City Center",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_CctCpzClothing_3": LocationData(display_name="Corpo Plaza Clothing Vendor 3", regions=("City Center",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="clothing"),
    "VendorCheck_CctDtnClothing_1": LocationData(display_name="Downtown Clothing Vendor 1", regions=("City Center",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_CctDtnClothing_2": LocationData(display_name="Downtown Clothing Vendor 2", regions=("City Center",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_CctDtnClothing_3": LocationData(display_name="Downtown Clothing Vendor 3", regions=("City Center",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="clothing"),
    "VendorCheck_HeySprClothing_1": LocationData(display_name="Wellsprings Clothing Vendor 1", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_HeySprClothing_2": LocationData(display_name="Wellsprings Clothing Vendor 2", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_HeySprClothing_3": LocationData(display_name="Wellsprings Clothing Vendor 3", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="clothing"),
    "VendorCheck_PacCviClothing_1": LocationData(display_name="Coastview Clothing Vendor 1", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_PacCviClothing_2": LocationData(display_name="Coastview Clothing Vendor 2", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_PacCviClothing_3": LocationData(display_name="Coastview Clothing Vendor 3", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="clothing"),
    "VendorCheck_PacWwdClothing_1": LocationData(display_name="West Wind Estate Clothing Vendor 1", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_PacWwdClothing_2": LocationData(display_name="West Wind Estate Clothing Vendor 2", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_PacWwdClothing_3": LocationData(display_name="West Wind Estate Clothing Vendor 3", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="clothing"),
    "VendorCheck_StdRcrClothing_1": LocationData(display_name="Rancho Coronado Clothing Vendor 1", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_StdRcrClothing_2": LocationData(display_name="Rancho Coronado Clothing Vendor 2", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_StdRcrClothing_3": LocationData(display_name="Rancho Coronado Clothing Vendor 3", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="clothing"),
    "VendorCheck_WatKabClothing_1": LocationData(display_name="Kabuki Clothing Vendor 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WatKabClothing_2": LocationData(display_name="Kabuki Clothing Vendor 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WatKabClothing_3": LocationData(display_name="Kabuki Clothing Vendor 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WatLchClothing_1": LocationData(display_name="Little China Clothing Vendor 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WatLchClothing_2": LocationData(display_name="Little China Clothing Vendor 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WatLchClothing_3": LocationData(display_name="Little China Clothing Vendor 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WatNidClothing_1": LocationData(display_name="Northside Clothing Vendor 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WatNidClothing_2": LocationData(display_name="Northside Clothing Vendor 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WatNidClothing_3": LocationData(display_name="Northside Clothing Vendor 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WbrHilClothing_1": LocationData(display_name="Charter Hill Clothing Vendor 1", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WbrHilClothing_2": LocationData(display_name="Charter Hill Clothing Vendor 2", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WbrHilClothing_3": LocationData(display_name="Charter Hill Clothing Vendor 3", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="clothing"),
    "VendorCheck_WbrJpnClothing01_1": LocationData(display_name="Japantown Clothing Vendor 1", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WbrJpnClothing01_2": LocationData(display_name="Japantown Clothing Vendor 2", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WbrJpnClothing01_3": LocationData(display_name="Japantown Clothing Vendor 3", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="clothing"),
    "VendorCheck_WbrJpnClothing02_1": LocationData(display_name="Japantown Clothing Vendor (2) 1", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WbrJpnClothing02_2": LocationData(display_name="Japantown Clothing Vendor (2) 2", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_WbrJpnClothing02_3": LocationData(display_name="Japantown Clothing Vendor (2) 3", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="clothing"),
    "VendorCheck_BlsInaSe1Clothing_1": LocationData(display_name="Jackson Plains Clothing Vendor 1", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_BlsInaSe1Clothing_2": LocationData(display_name="Jackson Plains Clothing Vendor 2", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_BlsInaSe1Clothing_3": LocationData(display_name="Jackson Plains Clothing Vendor 3", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="clothing"),
    "VendorCheck_CzConClothing_1": LocationData(display_name="Dogtown Clothing Vendor 1", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_CzConClothing_2": LocationData(display_name="Dogtown Clothing Vendor 2", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="clothing"),
    "VendorCheck_CzConClothing_3": LocationData(display_name="Dogtown Clothing Vendor 3", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.PRIORITY, vendor_subtype="clothing"),

    # --- Melee Vendors (vendor_subtype="melee") ---
    "VendorCheck_PacCviMelee_1": LocationData(display_name="Coastview Melee Vendor 1", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_PacCviMelee_2": LocationData(display_name="Coastview Melee Vendor 2", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_PacCviMelee_3": LocationData(display_name="Coastview Melee Vendor 3", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="melee"),
    "VendorCheck_PacWwdMelee_1": LocationData(display_name="West Wind Estate Melee Vendor 1", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_PacWwdMelee_2": LocationData(display_name="West Wind Estate Melee Vendor 2", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_PacWwdMelee_3": LocationData(display_name="West Wind Estate Melee Vendor 3", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="melee"),
    "VendorCheck_StdArrMelee_1": LocationData(display_name="Arroyo Melee Vendor 1", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_StdArrMelee_2": LocationData(display_name="Arroyo Melee Vendor 2", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_StdArrMelee_3": LocationData(display_name="Arroyo Melee Vendor 3", regions=("Santo Domingo",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="melee"),
    "VendorCheck_WatLchMelee01_1": LocationData(display_name="Little China Melee Vendor 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_WatLchMelee01_2": LocationData(display_name="Little China Melee Vendor 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_WatLchMelee01_3": LocationData(display_name="Little China Melee Vendor 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_WatLchMelee02_1": LocationData(display_name="Little China Melee Vendor (2) 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_WatLchMelee02_2": LocationData(display_name="Little China Melee Vendor (2) 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_WatLchMelee02_3": LocationData(display_name="Little China Melee Vendor (2) 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_WbrJpnMelee_1": LocationData(display_name="Japantown Melee Vendor 1", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_WbrJpnMelee_2": LocationData(display_name="Japantown Melee Vendor 2", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_WbrJpnMelee_3": LocationData(display_name="Japantown Melee Vendor 3", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="melee"),
    "VendorCheck_BlsInaSe5Melee_1": LocationData(display_name="Rocky Ridge Melee Vendor 1", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="melee"),
    "VendorCheck_BlsInaSe5Melee_2": LocationData(display_name="Rocky Ridge Melee Vendor 2", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.DEFAULT, vendor_subtype="melee"),
    "VendorCheck_BlsInaSe5Melee_3": LocationData(display_name="Rocky Ridge Melee Vendor 3", regions=("Badlands",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="melee"),

    # --- Netrunners (vendor_subtype="netrunner") ---
    "VendorCheck_HeyReyNetrunner_1": LocationData(display_name="Vista del Rey Netrunner 1", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_HeyReyNetrunner_2": LocationData(display_name="Vista del Rey Netrunner 2", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_HeyReyNetrunner_3": LocationData(display_name="Vista del Rey Netrunner 3", regions=("Heywood",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="netrunner"),
    "VendorCheck_PacCviNetrunner_1": LocationData(display_name="Coastview Netrunner (tech store) 1", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_PacCviNetrunner_2": LocationData(display_name="Coastview Netrunner (tech store) 2", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_PacCviNetrunner_3": LocationData(display_name="Coastview Netrunner (tech store) 3", regions=("Pacifica",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="netrunner"),
    "VendorCheck_WatLchNetrunner_1": LocationData(display_name="Little China Netrunner 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_WatLchNetrunner_2": LocationData(display_name="Little China Netrunner 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_WatLchNetrunner_3": LocationData(display_name="Little China Netrunner 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_WatKabNetrunner_1": LocationData(display_name="Kabuki Netrunner (Yoko Tsuru) 1", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_WatKabNetrunner_2": LocationData(display_name="Kabuki Netrunner (Yoko Tsuru) 2", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_WatKabNetrunner_3": LocationData(display_name="Kabuki Netrunner (Yoko Tsuru) 3", regions=("Watson",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_WbrJpnNetrunner01_1": LocationData(display_name="Japantown Netrunner 1", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_WbrJpnNetrunner01_2": LocationData(display_name="Japantown Netrunner 2", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_WbrJpnNetrunner01_3": LocationData(display_name="Japantown Netrunner 3", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="netrunner"),
    "VendorCheck_WbrJpnNetrunner02_1": LocationData(display_name="Japantown Netrunner (2) 1", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_WbrJpnNetrunner02_2": LocationData(display_name="Japantown Netrunner (2) 2", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_WbrJpnNetrunner02_3": LocationData(display_name="Japantown Netrunner (2) 3", regions=("Westbrook",), category=LocationCategory.VENDOR, progress_type=LocationProgressType.PRIORITY, vendor_subtype="netrunner"),
    "VendorCheck_CzConNetrunner_1": LocationData(display_name="Dogtown Netrunner 1", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_CzConNetrunner_2": LocationData(display_name="Dogtown Netrunner 2", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.EXCLUDED, vendor_subtype="netrunner"),
    "VendorCheck_CzConNetrunner_3": LocationData(display_name="Dogtown Netrunner 3", regions=("Dogtown",), category=LocationCategory.VENDOR, dlc_only=True, progress_type=LocationProgressType.PRIORITY, vendor_subtype="netrunner"),
}


# ===== AUTO-ASSIGN LOCATION CODES =====
# Assigns sequential codes (0, 1, 2, ...) to every location in the table.
# Must run BEFORE the derived mappings below that depend on data.code.

def _assign_location_codes(table: Dict[str, LocationData]) -> None:
    """
    Auto-assign sequential integer codes to all locations in the table.

    Each location receives its zero-based insertion index as its code.
    The full Archipelago ID is BASE_ID + code.

    This replaces the old scheme of manually hardcoding code values, which
    was error-prone (duplicate codes, gaps, collisions).

    Args:
        table: The location_table dict to mutate in-place.
    """
    for index, (name, data) in enumerate(table.items()):
        data.code = index


_assign_location_codes(location_table)


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

# Map all epilogue quest IDs to the single "Ending Reached" location
# Player only needs to complete ONE ending to get this check
location_internal_id_to_display_name["q201_heir"] = "Ending Reached"
location_internal_id_to_display_name["q202_nomads"] = "Ending Reached"
location_internal_id_to_display_name["q203_legend"] = "Ending Reached"
location_internal_id_to_display_name["q204_reborn"] = "Ending Reached"
location_internal_id_to_display_name["q307_tomorrow"] = "Ending Reached"  # Phantom Liberty DLC epilogue






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
    - Region (Watson, City Center, Heywood, Pacifica, Santo Domingo, Badlands, etc.)
    - Category (from LocationData.category field)

    Returns:
        Dictionary mapping group names to lists of location internal IDs
    """
    groups: Dict[str, List[str]] = {}

    # Group by region. Multi-region locations appear under every district they
    # touch so YAML references like ``priority_locations: [Watson]`` pick up
    # cross-district quests as well.
    regions: Dict[str, List[str]] = {}
    for loc_name, loc_data in location_table.items():
        if loc_data.code is None:
            continue  # Skip event locations

        for region_name in loc_data.regions:
            regions.setdefault(region_name, []).append(loc_name)

    # Add all region groups
    groups.update(regions)

    # Group by category
    main_quests = []
    side_quests = []
    gigs = []
    cyberpsychos = []
    ncpd_hustles = []
    minor_quests = []
    endings = []
    epilogues = []
    dlc_main = []
    dlc_side = []
    vendor = []
    misc = []

    for loc_name, loc_data in location_table.items():
        if loc_data.code is None:
            continue  # Skip event locations

        # Group by category
        if loc_data.category == LocationCategory.MAIN_QUEST:
            main_quests.append(loc_name)
        elif loc_data.category == LocationCategory.SIDE_QUEST:
            side_quests.append(loc_name)
        elif loc_data.category == LocationCategory.GIG:
            gigs.append(loc_name)
        elif loc_data.category == LocationCategory.CYBERPSYCHO:
            cyberpsychos.append(loc_name)
        elif loc_data.category == LocationCategory.NCPD_HUSTLE:
            ncpd_hustles.append(loc_name)
        elif loc_data.category == LocationCategory.MINOR_QUEST:
            minor_quests.append(loc_name)
        elif loc_data.category == LocationCategory.ENDING:
            endings.append(loc_name)
        elif loc_data.category == LocationCategory.EPILOGUE:
            epilogues.append(loc_name)
        elif loc_data.category == LocationCategory.DLC_MAIN:
            dlc_main.append(loc_name)
        elif loc_data.category == LocationCategory.DLC_SIDE:
            dlc_side.append(loc_name)
        elif loc_data.category == LocationCategory.VENDOR:
            vendor.append(loc_name)
        elif loc_data.category == LocationCategory.MISC:
            misc.append(loc_name)

    # Add category groups only if they have locations
    if main_quests:
        groups["Main Quests"] = main_quests
    if side_quests:
        groups["Side Quests"] = side_quests
    if gigs:
        groups["Gigs"] = gigs
    if cyberpsychos:
        groups["Cyberpsycho Sightings"] = cyberpsychos
    if ncpd_hustles:
        groups["NCPD Scanner Hustles"] = ncpd_hustles
    if minor_quests:
        groups["Minor Quests"] = minor_quests
    if endings:
        groups["Endings"] = endings
    if epilogues:
        groups["Epilogues"] = epilogues
    if dlc_main:
        groups["Phantom Liberty Main Quests"] = dlc_main
    if dlc_side:
        groups["Phantom Liberty Side Content"] = dlc_side
    if vendor:
        groups["Vendor Sanity"] = vendor
    if misc:
        groups["Miscellaneous"] = misc

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
    Get all internal location IDs that touch a specific region.

    Returns every location whose ``regions`` tuple contains ``region_name``,
    so multi-district quests show up under each district they involve.

    Args:
        region_name: The name of the region to filter by

    Returns:
        List of internal location IDs in that region
    """
    return [
        name
        for name, data in location_table.items()
        if region_name in data.regions
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

    A location is considered Phantom Liberty content if Dogtown is one of its
    declared regions, or if it is explicitly marked ``dlc_only``.

    Args:
        location_name: The location name to check

    Returns:
        True if the location belongs to the Phantom Liberty DLC, False otherwise
    """
    location_data = location_table.get(location_name)
    if location_data is None:
        return False
    return location_data.dlc_only or "Dogtown" in location_data.regions
