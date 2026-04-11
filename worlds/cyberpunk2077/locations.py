"""
Cyberpunk 2077 Location Definitions

This file defines all locations (checks) where items can be found in the game.

Locations represent specific spots in the game where the player can collect
randomized items. They have unique IDs for network communication and are
organized by region for easier management.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
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

    Attributes:
        display_name: Human-readable location name (e.g., "Prologue - StreetKid Intro")
        region: Which region/area this location belongs to (e.g., "Watson")
        code: Unique numeric ID for network communication.
              Auto-assigned sequentially at module load by _assign_location_codes().
              Set to None for "event" locations that auto-complete.
        category: Location category for grouping and filtering (default: "misc")
                 Used to group locations by type (main quests, gigs, etc.)
        dlc_only: Whether this location requires Phantom Liberty DLC (default: False)
                 Locations marked dlc_only=True are excluded when DLC is disabled
    """
    display_name: str
    region: str  # Which region this location is in
    code: Optional[int] = None  # Auto-assigned at module load; None for event locations
    category: str = "misc"  # Location category (use LocationCategory constants)
    dlc_only: bool = False  # True for Phantom Liberty DLC locations
    progress_type: LocationProgressType = LocationProgressType.DEFAULT  # Controls fill priority (DEFAULT, PRIORITY, EXCLUDED)


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


# ===== LOCATION TABLE =====
# This dictionary maps internal location IDs to their definitions
# Keys are internal game IDs (what the game client sends)
# Values contain display names, codes, and regions

# Location codes are AUTO-ASSIGNED sequentially (0, 1, 2, ...) at module load
# by _assign_location_codes() below the table. The full Archipelago ID for each
# location is BASE_ID + code (e.g., 2077000 + 0 = 2077000).
#
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
    "Lifepath Chosen": LocationData(display_name="Lifepath Chosen", region="Watson", category=LocationCategory.MAIN_QUEST),
    "Ending Reached" : LocationData(display_name="Ending Reached", region="Watson", category=LocationCategory.MAIN_QUEST),
    # Tutorial might get re-added if requested
    #"q000_tutorial": LocationData(display_name="Prologue - Practice Makes Perfect", region="Watson", category=LocationCategory.MAIN_QUEST),
    "q001_intro": LocationData(display_name="Prologue - The Rescue", region="Watson", category=LocationCategory.MAIN_QUEST),
    "q001_01_victor": LocationData(display_name="Prologue - The Ripperdoc", region="Watson", category=LocationCategory.MAIN_QUEST),
    "q001_02_dex": LocationData(display_name="Prologue - The Ride", region="Watson", category=LocationCategory.MAIN_QUEST),
    "q003_maelstrom": LocationData(display_name="Prologue - The Pickup", region="Watson", category=LocationCategory.MAIN_QUEST),
    "q004_braindance": LocationData(display_name="Prologue - The Information", region="Watson", category=LocationCategory.MAIN_QUEST),
    "q005_heist": LocationData(display_name="Prologue - The Heist", region="Watson", category=LocationCategory.MAIN_QUEST),
    "q101_01_firestorm": LocationData(display_name="Prologue - Love Like Fire", region="Watson", category=LocationCategory.MAIN_QUEST),

    # =================================
    # Post-Heist Main Story
    # =================================
    "q101_resurrection": LocationData(display_name="Main - Playing for Time", region="Watson", category=LocationCategory.MAIN_QUEST),
    "q103_warhead": LocationData(display_name="Main - Ghost Town", region="Badlands", category=LocationCategory.MAIN_QUEST),
    "q104_01_sabotage": LocationData(display_name="Main - Lightning Breaks", region="Badlands", category=LocationCategory.MAIN_QUEST),
    "q104_02_av_chase": LocationData(display_name="Main - Life During Wartime", region="Badlands", category=LocationCategory.MAIN_QUEST),
    "q105_dollhouse": LocationData(display_name="Main - Automatic Love", region="Westbrook", category=LocationCategory.MAIN_QUEST),
    "q105_02_jigjig": LocationData(display_name="Main - The Space in Between", region="Westbrook", category=LocationCategory.MAIN_QUEST),
    "q105_03_braindance_studio": LocationData(display_name="Main - Disasterpiece", region="Santo Domingo", category=LocationCategory.MAIN_QUEST),
    "q105_04_judys": LocationData(display_name="Main - Double Life", region="Watson", category=LocationCategory.MAIN_QUEST),
    "q110_01_voodooboys": LocationData(display_name="Main - M'ap Tann Pèlen", region="Pacifica", category=LocationCategory.MAIN_QUEST),
    "q110_voodoo": LocationData(display_name="Main - I Walk the Line", region="Pacifica", category=LocationCategory.MAIN_QUEST),
    "q110_03_cyberspace": LocationData(display_name="Main - Transmission", region="Pacifica", category=LocationCategory.MAIN_QUEST),
    "q108_johnny": LocationData(display_name="Main - Never Fade Away", region="Pacifica", category=LocationCategory.MAIN_QUEST),
    "q112_01_old_friend": LocationData(display_name="Main - Down on the Street", region="City Center", category=LocationCategory.MAIN_QUEST),
    "q112_02_industrial_park": LocationData(display_name="Main - Gimme Danger", region="Santo Domingo", category=LocationCategory.MAIN_QUEST),
    "q112_03_dashi_parade": LocationData(display_name="Main - Play It Safe", region="Westbrook", category=LocationCategory.MAIN_QUEST),
    "q112_04_hideout": LocationData(display_name="Main - Search and Destroy", region="Heywood", category=LocationCategory.MAIN_QUEST),
    "02_sickness": LocationData(display_name="Point of No Return - Nocturne Op55N1", region="Heywood", category=LocationCategory.MAIN_QUEST),

    # =====================================
    # Endings
    # =====================================
    #"01_climbing_the_ladder": LocationData(display_name="Endgame - Become A Legend", region="Watson", category=LocationCategory.MAIN_QUEST),
    #"09_solo": LocationData(display_name="Endgame - (Don't Fear) The Reaper", region="City Center", category=LocationCategory.MAIN_QUEST),
    #"q113_rescuing_hanako": LocationData(display_name="Ending - Last Caress", region="North Oak", category=LocationCategory.ENDING),
    #"q113_corpo": LocationData(display_name="Ending - Total Immortal", region="City Center", category=LocationCategory.ENDING),
    #"q114_01_nomad_initiation": LocationData(display_name="Ending - We Gotta Live Together", region="Badlands", category=LocationCategory.ENDING),
    #"q114_02_maglev_line_assault": LocationData(display_name="Ending - Forward to Death", region="Badlands", category=LocationCategory.ENDING),
    #"q114_03_attack_on_arasaka_tower": LocationData(display_name="Ending - Belly of the Beast", region="City Center", category=LocationCategory.ENDING),
    #"q115_afterlife": LocationData(display_name="Ending - For Whom the Bell Tolls", region="Watson", category=LocationCategory.ENDING),
    #"q115_rogues_last_flight": LocationData(display_name="Ending - Knockin' on Heaven's Door", region="City Center", category=LocationCategory.ENDING),
    #"q116_cyberspace": LocationData(display_name="Ending - Changes", region="Watson", category=LocationCategory.ENDING),

    # =====================================
    # Phantom Liberty Checks
    # (Only applicable w/DLC)
    # =====================================
    "q300_phantom_liberty": LocationData(display_name="Phantom Liberty - Phantom Liberty", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q301_crash": LocationData(display_name="Phantom Liberty - Dog Eat Dog", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q301_finding_myers": LocationData(display_name="Phantom Liberty - Hole in the Sky", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q301_q302_rescue_myers": LocationData(display_name="Phantom Liberty - Spider and the Fly", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q302_reed": LocationData(display_name="Phantom Liberty - Lucretia My Reflection", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q303_baron": LocationData(display_name="Phantom Liberty - The Damned", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q303_hands": LocationData(display_name="Phantom Liberty - Get It Together", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q303_songbird": LocationData(display_name="Phantom Liberty - You Know My Name", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q304_stadium": LocationData(display_name="Phantom Liberty - Birds with Broken Wings", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q304_netrunners": LocationData(display_name="Phantom Liberty - I've Seen That Face Before", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q304_deal": LocationData(display_name="Phantom Liberty - Firestarter", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q305_prison_convoy": LocationData(display_name="Phantom Liberty - Black Steel In The Hour of Chaos", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q305_bunker": LocationData(display_name="Phantom Liberty - Somewhat Damaged", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q305_border_crossing": LocationData(display_name="Phantom Liberty - Leave in Silence", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q306_devils_bargain": LocationData(display_name="Phantom Liberty - The Killing Moon", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q307_before_tomorrow": LocationData(display_name="Phantom Liberty - Who Wants to Live Forever", region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),

    # =================================
    # Epilogues
    # =================================
    # NOTE: Individual epilogue locations removed - all epilogue quest IDs map to "Ending Reached"
    # This prevents items from being placed on multiple ending screens
    # See location_internal_id_to_display_name mappings below for quest ID assignments

    # =================================
    # Side Quests
    # =================================
    "07_nc_underground": LocationData(display_name="The Beast In Me", region="Various", category=LocationCategory.SIDE_QUEST),
    "sq004_riders_on_the_storm": LocationData(display_name="Riders on the Storm", region="Badlands", category=LocationCategory.ENDING_SIDE_QUEST),
    "sq006_dream_on": LocationData(display_name="Dream On", region="City Center", category=LocationCategory.SIDE_QUEST),
    "sq011_concert": LocationData(display_name="A Like Supreme", region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq011_johnny": LocationData(display_name="Second Conflict", region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq011_kerry": LocationData(display_name="Holdin' On", region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq012_lost_girl": LocationData(display_name="I Fought the Law", region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq017_01_riot_club": LocationData(display_name="I Don't Wanna Hear It", region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq017_02_lounge": LocationData(display_name="Off the Leash", region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq017_kerry": LocationData(display_name="Rebel! Rebel!", region="Badlands", category=LocationCategory.SIDE_QUEST),
    "sq018_jackie": LocationData(display_name="Heroes", region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq021_sick_dreams": LocationData(display_name="The Hunt", region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq023_bd_passion": LocationData(display_name="There Is A Light That Never Goes Out", region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq023_hit_order": LocationData(display_name="Sinnerman", region="Santo Domingo", category=LocationCategory.SIDE_QUEST),
    "sq023_real_passion": LocationData(display_name="They Won't Go When I Go", region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq024_badlands_race": LocationData(display_name="The Beast in Me: Badlands", region="Badlands", category=LocationCategory.SIDE_QUEST),
    "sq024_city_race": LocationData(display_name="The Beast in Me: City Center", region="City Center", category=LocationCategory.SIDE_QUEST),
    "sq024_santo_domingo_race": LocationData(display_name="The Beast in Me: Santo Domingo", region="Santo Domingo", category=LocationCategory.SIDE_QUEST),
    "sq024_the_big_race": LocationData(display_name="The Beast in Me: The Big Race", region="Santo Domingo", category=LocationCategory.SIDE_QUEST),
    "sq025_0_pickup": LocationData(display_name="Human Nature", region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq025_compensation": LocationData(display_name="Tune Up", region="City Center", category=LocationCategory.SIDE_QUEST),
    "sq025_delamain": LocationData(display_name="Epistrophy", region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq025b_delamain_insurgence": LocationData(display_name="Don't Lose Your Mind", region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq025c01_angry": LocationData(display_name="Epistrophy: Wellsprings", region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq025c02_sad": LocationData(display_name="Epistrophy: North Oak", region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq025c03_mean": LocationData(display_name="Epistrophy: Coastview", region="Pacifica", category=LocationCategory.SIDE_QUEST),
    "sq025c04_manic": LocationData(display_name="Epistrophy: Rancho Coronado", region="Santo Domingo", category=LocationCategory.SIDE_QUEST),
    "sq025c05_scared": LocationData(display_name="Epistrophy: Northside", region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq025c06_mean": LocationData(display_name="Epistrophy: Badlands", region="Badlands", category=LocationCategory.SIDE_QUEST),
    "sq025c07_suicidal": LocationData(display_name="Epistrophy: The Glen", region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq026_01_suicide": LocationData(display_name="Both Sides, Now", region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq026_02_maiko": LocationData(display_name="Ex-Factor", region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq026_03_pizza": LocationData(display_name="Talkin' 'bout a Revolution", region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq026_04_hiromi": LocationData(display_name="Pisces", region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq027_01_basilisk_convoy": LocationData(display_name="With a Little Help from My Friends", region="Badlands", category=LocationCategory.ENDING_SIDE_QUEST),
    "sq027_02_raffen_shiv_attack": LocationData(display_name="Queen of the Highway", region="Badlands", category=LocationCategory.ENDING_SIDE_QUEST),
    "sq028_kerry_romance": LocationData(display_name="Boat Drinks", region="Pacifica", category=LocationCategory.SIDE_QUEST),
    "sq029_sobchak_romance": LocationData(display_name="Following the River", region="Santo Domingo", category=LocationCategory.SIDE_QUEST),
    "sq030_judy_romance": LocationData(display_name="Pyramid Song", region="Badlands", category=LocationCategory.SIDE_QUEST),
    "sq031_cinema": LocationData(display_name="Blistering Love", region="Westbrook", category=LocationCategory.ENDING_SIDE_QUEST),
    "sq031_rogue": LocationData(display_name="Chippin' In", region="Watson", category=LocationCategory.ENDING_SIDE_QUEST),
    "sq031_smack_my_bitch_up": LocationData(display_name="A Cool Metal Fire", region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq_q001_tbug": LocationData(display_name="The Gift", region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq_q001_wakako": LocationData(display_name="The Gig", region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq_q001_wilson": LocationData(display_name="The Gun", region="Watson", category=LocationCategory.SIDE_QUEST),
    # =================================
    # Gigs
    # =================================
    "sts_bls_ina_02": LocationData(display_name="Gig: Big Pete's Got Big Problems", region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_03": LocationData(display_name="Gig: Flying Drugs", region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_04": LocationData(display_name="Gig: Radar Love", region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_05": LocationData(display_name="Gig: Goodbye, Night City", region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_06": LocationData(display_name="Gig: No Fixers", region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_07": LocationData(display_name="Gig: Dancing on a Minefield", region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_08": LocationData(display_name="Gig: Trevor's Last Ride", region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_09": LocationData(display_name="Gig: MIA", region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_11": LocationData(display_name="Gig: Sparring Partner", region="Badlands", category=LocationCategory.GIG),
    "sts_cct_cpz_01": LocationData(display_name="Gig: Serial Suicide", region="City Center", category=LocationCategory.GIG),
    "sts_cct_dtn_02": LocationData(display_name="Gig: An Inconvenient Killer", region="City Center", category=LocationCategory.GIG),
    "sts_cct_dtn_03": LocationData(display_name="Gig: A Lack of Empathy", region="City Center", category=LocationCategory.GIG),
    "sts_cct_dtn_04": LocationData(display_name="Gig: Guinea Pigs", region="City Center", category=LocationCategory.GIG),
    "sts_cct_dtn_05": LocationData(display_name="Gig: The Frolics of Councilwoman Cole", region="City Center", category=LocationCategory.GIG),
    "sts_hey_gle_01": LocationData(display_name="Gig: Eye for an Eye", region="Heywood", category=LocationCategory.GIG),
    "sts_hey_gle_03": LocationData(display_name="Gig: Psychofan", region="Heywood", category=LocationCategory.GIG),
    "sts_hey_gle_04": LocationData(display_name="Gig: Fifth Column", region="Heywood", category=LocationCategory.GIG),
    "sts_hey_gle_05": LocationData(display_name="Gig: Going Up or Down?", region="Heywood", category=LocationCategory.GIG),
    "sts_hey_gle_06": LocationData(display_name="Gig: Life's Work", region="Heywood", category=LocationCategory.GIG),
    "sts_hey_rey_01": LocationData(display_name="Gig: Bring Me the Head of Gustavo Orta", region="Heywood", category=LocationCategory.GIG),
    "sts_hey_rey_02": LocationData(display_name="Gig: Sr. Ladrillo's Private Collection", region="Heywood", category=LocationCategory.GIG),
    "sts_hey_rey_06": LocationData(display_name="Gig: Jeopardy", region="Heywood", category=LocationCategory.GIG),
    "sts_hey_rey_08": LocationData(display_name="Gig: Old Friends", region="Heywood", category=LocationCategory.GIG),
    "sts_hey_rey_09": LocationData(display_name="Gig: Getting Warmer...", region="Heywood", category=LocationCategory.GIG),
    "sts_hey_spr_01": LocationData(display_name="Gig: On a Tight Leash", region="Heywood", category=LocationCategory.GIG),
    "sts_hey_spr_03": LocationData(display_name="Gig: The Lord Giveth and Taketh Away", region="Heywood", category=LocationCategory.GIG),
    "sts_hey_spr_06": LocationData(display_name="Gig: Hot Merchandise", region="Heywood", category=LocationCategory.GIG),
    "sts_pac_cvi_02": LocationData(display_name="Gig: Two Wrongs Makes Us Right", region="Pacifica", category=LocationCategory.GIG),
    "sts_pac_wwd_05": LocationData(display_name="Gig: For My Son", region="Pacifica", category=LocationCategory.GIG),
    "sts_std_arr_01": LocationData(display_name="Gig: Serious Side Effects", region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_arr_03": LocationData(display_name="Gig: Race to the Top", region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_arr_05": LocationData(display_name="Gig: Breaking News", region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_arr_06": LocationData(display_name="Gig: Nasty Hangover", region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_arr_10": LocationData(display_name="Gig: Severance Package", region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_arr_11": LocationData(display_name="Gig: Hacking the Hacker", region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_arr_12": LocationData(display_name="Gig: Desperate Measures", region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_rcr_01": LocationData(display_name="Gig: The Union Strikes Back", region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_rcr_02": LocationData(display_name="Gig: Cuckoo's Nest", region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_rcr_03": LocationData(display_name="Gig: Going-away Party", region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_rcr_04": LocationData(display_name="Gig: Error 404", region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_rcr_05": LocationData(display_name="Gig: Family Matters", region="Santo Domingo", category=LocationCategory.GIG),
    "sts_wat_kab_01": LocationData(display_name="Gig: Concrete Cage Trap", region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_02": LocationData(display_name="Gig: Hippocratic Oath", region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_03": LocationData(display_name="Gig: Backs Against the Wall", region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_04": LocationData(display_name="Gig: Fixer, Merc, Soldier, Spy", region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_05": LocationData(display_name="Gig: Last Login", region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_06": LocationData(display_name="Gig: Shark in the Water", region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_07": LocationData(display_name="Gig: Monster Hunt", region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_08": LocationData(display_name="Gig: Woman of La Mancha", region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_101": LocationData(display_name="Gig: Small Man, Big Evil", region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_102": LocationData(display_name="Gig: Welcome to America, Comrade", region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_107": LocationData(display_name="Gig: Troublesome Neighbors", region="Watson", category=LocationCategory.GIG),
    "sts_wat_lch_01": LocationData(display_name="Gig: Catch a Tyger's Toe", region="Watson", category=LocationCategory.GIG),
    "sts_wat_lch_03": LocationData(display_name="Gig: Bloodsport", region="Watson", category=LocationCategory.GIG),
    "sts_wat_lch_05": LocationData(display_name="Gig: Playing for Keeps", region="Watson", category=LocationCategory.GIG),
    "sts_wat_lch_06": LocationData(display_name="Gig: The Heisenberg Principle", region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_01": LocationData(display_name="Gig: Occupational Hazard", region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_02": LocationData(display_name="Gig: Many Ways to Skin a Cat", region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_03": LocationData(display_name="Gig: Flight of the Cheetah", region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_04": LocationData(display_name="Gig: Dirty Biz", region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_05": LocationData(display_name="Gig: Rite of Passage", region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_06": LocationData(display_name="Gig: Lousy Kleppers", region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_07": LocationData(display_name="Gig: Scrolls before Swine", region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_12": LocationData(display_name="Gig: Freedom of the Press", region="Watson", category=LocationCategory.GIG),
    "sts_wbr_hil_01": LocationData(display_name="Gig: Until Death Do Us Part", region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_hil_06": LocationData(display_name="Gig: Family Heirloom", region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_hil_07": LocationData(display_name="Gig: Tyger and Vulture", region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_jpn_01": LocationData(display_name="Gig: Olive Branch", region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_jpn_02": LocationData(display_name="Gig: We Have Your Wife", region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_jpn_03": LocationData(display_name="Gig: A Shrine Defiled", region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_jpn_05": LocationData(display_name="Gig: Wakako's Favorite", region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_jpn_12": LocationData(display_name="Gig: Greed Never Pays", region="Westbrook", category=LocationCategory.GIG),

    # ================================
    # Contracts
    # ================================
    "ma_bls_ina_se1_02": LocationData(display_name="Reported Crime: Comrade Red", region="Badlands", category=LocationCategory.NCPD_HUSTLE),
    "ma_bls_ina_se1_03": LocationData(display_name="Reported Crime: Blood in the Air", region="Badlands", category=LocationCategory.NCPD_HUSTLE),
    "ma_bls_ina_se1_06": LocationData(display_name="Reported Crime: Extremely Loud and Incredibly Close", region="Badlands", category=LocationCategory.NCPD_HUSTLE),
    "ma_bls_ina_se1_18": LocationData(display_name="Reported Crime: I Don't Like Sand", region="Badlands", category=LocationCategory.NCPD_HUSTLE),
    "ma_bls_ina_se5_33": LocationData(display_name="Reported Crime: Delivery From Above", region="Badlands", category=LocationCategory.NCPD_HUSTLE),
    "ma_cct_dtn_12": LocationData(display_name="Reported Crime: Turn Off the Tap", region="City Center", category=LocationCategory.NCPD_HUSTLE),
    "ma_hey_gle_02": LocationData(display_name="Suspected Organized Crime Activity: Chapel", region="Heywood", category=LocationCategory.NCPD_HUSTLE),
    "ma_hey_gle_07": LocationData(display_name="Reported Crime: Smoking Kills", region="Heywood", category=LocationCategory.NCPD_HUSTLE),
    "ma_hey_spr_11": LocationData(display_name="Suspected Organized Crime Activity: Living the Big Life", region="Heywood", category=LocationCategory.NCPD_HUSTLE),
    "ma_pac_cvi_10": LocationData(display_name="Reported Crime: Roadside Picnic", region="Pacifica", category=LocationCategory.NCPD_HUSTLE),
    "ma_pac_cvi_12": LocationData(display_name="Suspected Organized Crime Activity: Wipe the Gonk, Take the Implants", region="Pacifica", category=LocationCategory.NCPD_HUSTLE),
    "ma_pac_cvi_13": LocationData(display_name="Reported Crime: Honey, Where are You?", region="Pacifica", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_arr_07": LocationData(display_name="Reported Crime: Disloyal Employee", region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_arr_10": LocationData(display_name="Reported Crime: Ooh, Awkward", region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_arr_14": LocationData(display_name="Reported Crime: Supply Management", region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_rcr_10": LocationData(display_name="Reported Crime: Welcome to Night City", region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_rcr_12": LocationData(display_name="Reported Crime: A Stroke of Luck", region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_rcr_13": LocationData(display_name="Reported Crime: Justice Behind Bars", region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_kab_05": LocationData(display_name="Reported Crime: Protect and Serve", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_01": LocationData(display_name="Suspected Organized Crime Activity: Opposites Attract", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_03": LocationData(display_name="Reported Crime: Worldly Possessions", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_05": LocationData(display_name="Reported Crime: Paranoia", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_08": LocationData(display_name="Suspected Organized Crime Activity: Tygers by the Tail", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_15": LocationData(display_name="Reported Crime: Dangerous Currents", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_01": LocationData(display_name="Suspected Organized Crime Activity: Vice Control", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_02": LocationData(display_name="Suspected Organized Crime Activity: Just Say No", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_06": LocationData(display_name="Suspected Organized Crime Activity: No License, No Problem", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_10": LocationData(display_name="Reported Crime: Dredged Up", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_12": LocationData(display_name="Reported Crime: Needle in a Haystack", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_26": LocationData(display_name="Reported Crime: One Thing Led to Another", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_27": LocationData(display_name="Reported Crime: Don't Forget the Parking Brake!", region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_hil_05": LocationData(display_name="Reported Crime: You Play with Fire...", region="Westbrook", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_jpn_07": LocationData(display_name="Reported Crime: Lost and Found", region="Westbrook", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_jpn_09": LocationData(display_name="Reported Crime: Another Circle of Hell", region="Westbrook", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_nok_01": LocationData(display_name="Reported Crime: Crash Test", region="Westbrook", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_nok_03": LocationData(display_name="Reported Crime: Table Scraps", region="Westbrook", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_nok_05": LocationData(display_name="Suspected Organized Crime Activity: Privacy Policy Violation", region="Westbrook", category=LocationCategory.NCPD_HUSTLE),

    # ==================================
    # Vehicle Quests
    # ==================================
    "arch": LocationData(display_name="Nazaré 'Racer'", region="Night City", category=LocationCategory.MINOR_QUEST),
    "archer_quartz": LocationData(display_name="Quartz EC-L r275", region="Night City", category=LocationCategory.MINOR_QUEST),
    "brennan_apollo": LocationData(display_name="Apollo", region="Night City", category=LocationCategory.MINOR_QUEST),
    "chevalier_emperor": LocationData(display_name="Emperor 620 Ragnar", region="Night City", category=LocationCategory.MINOR_QUEST),
    "chevalier_thrax": LocationData(display_name="Thrax 388 Jefferson", region="Night City", category=LocationCategory.MINOR_QUEST),
    "herrera_outlaw": LocationData(display_name="Outlaw", region="Night City", category=LocationCategory.MINOR_QUEST),
    "mahir_supron": LocationData(display_name="Supron FS3", region="Night City", category=LocationCategory.MINOR_QUEST),
    "makigai_maimai": LocationData(display_name="MaiMai P126", region="Night City", category=LocationCategory.MINOR_QUEST),
    "mizutani_shion": LocationData(display_name="Shion MZ2", region="Night City", category=LocationCategory.MINOR_QUEST),
    "mizutani_shion_nomad": LocationData(display_name="Shion 'Coyote'", region="Badlands", category=LocationCategory.MINOR_QUEST),
    "quadra_turbo": LocationData(display_name="Turbo-R 740", region="Night City", category=LocationCategory.MINOR_QUEST),
    "quadra_type66": LocationData(display_name="Type-66 640 TS", region="Night City", category=LocationCategory.MINOR_QUEST),
    "quadra_type66_avenger": LocationData(display_name="Quadra Type-66 Avenger", region="Night City", category=LocationCategory.MINOR_QUEST),
    "quadra_type66_nomad": LocationData(display_name="Quadra Type-66 'Javelina'", region="Badlands", category=LocationCategory.MINOR_QUEST),
    "quadra_type66_nomad_ncu": LocationData(display_name="Quadra Type-66 'Cthulhu'", region="Night City", category=LocationCategory.MINOR_QUEST),
    "rayfield_aerondight": LocationData(display_name="Rayfield Aerondight 'Guinevere'", region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "rayfield_caliburn": LocationData(display_name="Rayfield Caliburn", region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "thorton_colby": LocationData(display_name="Colby C125", region="Night City", category=LocationCategory.MINOR_QUEST),
    "thorton_colby_nomad": LocationData(display_name="Thorton Colby 'Little Mule'", region="Badlands", category=LocationCategory.MINOR_QUEST),
    "thorton_colby_pickup": LocationData(display_name="Thorton Colby CX410 Butte", region="Night City", category=LocationCategory.MINOR_QUEST),
    "thorton_galena": LocationData(display_name="Galena G240", region="Night City", category=LocationCategory.MINOR_QUEST),
    "thorton_galena_nomad": LocationData(display_name="Thorton Galena 'Gecko'", region="Badlands", category=LocationCategory.MINOR_QUEST),
    "thorton_mackinaw": LocationData(display_name="Mackinaw MTL1", region="Night City", category=LocationCategory.MINOR_QUEST),
    "villefort_alvarado": LocationData(display_name="Alvarado V4F 570 Delegate", region="Night City", category=LocationCategory.MINOR_QUEST),
    "villefort_columbus": LocationData(display_name="Columbus V340-F Freight", region="Night City", category=LocationCategory.MINOR_QUEST),
    "villefort_cortes": LocationData(display_name="Cortes V5000 Valor", region="Night City", category=LocationCategory.MINOR_QUEST),
    "yaiba_kusanagi": LocationData(display_name="Kusanagi CT-3X", region="Night City", category=LocationCategory.MINOR_QUEST),

    # =================================
    # Minor Quests
    # =================================
    "q003_stout": LocationData(display_name="Venus in Furs", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq001_scorpion": LocationData(display_name="I'll Fly Away", region="Badlands", category=LocationCategory.MINOR_QUEST),
    "mq002_veterans": LocationData(display_name="Gun Music", region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq003_orbitals": LocationData(display_name="Space Oddity", region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq005_alley": LocationData(display_name="Only Pain", region="Heywood", category=LocationCategory.MINOR_QUEST),
    "mq006_rollercoaster": LocationData(display_name="Love Rollercoaster", region="Pacifica", category=LocationCategory.MINOR_QUEST),
    "mq007_smartgun": LocationData(display_name="Machine Gun", region="Heywood", category=LocationCategory.MINOR_QUEST),
    "mq008_party": LocationData(display_name="Stadium Love", region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq010_barry": LocationData(display_name="Happy Together", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq011_wilson": LocationData(display_name="Shoot To Thrill", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq012_stud": LocationData(display_name="Burning Desire", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq013_punks": LocationData(display_name="A Day In The Life", region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq014_02_second": LocationData(display_name="Stairway To Heaven", region="Heywood", category=LocationCategory.MINOR_QUEST),
    "mq014_03_third": LocationData(display_name="Poem Of The Atoms", region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq014_04_fourth": LocationData(display_name="Meetings Along The Edge", region="City Center", category=LocationCategory.MINOR_QUEST),
    "mq014_zen": LocationData(display_name="Imagine", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq015_wizardbook": LocationData(display_name="Spellbound", region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq016_bartmoss": LocationData(display_name="KOLD MIRAGE", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq017_streetkid": LocationData(display_name="Small Man, Big Mouth", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq018_writer": LocationData(display_name="Killing In The Name", region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq019_paparazzi": LocationData(display_name="Violence", region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq021_guide": LocationData(display_name="Fortunate Son", region="Badlands", category=LocationCategory.MINOR_QUEST),
    "mq022_ezekiel": LocationData(display_name="Ezekiel Saw the Wheel", region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq023_bootleg": LocationData(display_name="The Ballad of Buck Ravers", region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq024_sandra": LocationData(display_name="Full Disclosure", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq025_02_kabuki": LocationData(display_name="Beat on the Brat: Kabuki", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq025_03_arroyo": LocationData(display_name="Beat on the Brat: Arroyo", region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq025_05_glen": LocationData(display_name="Beat on the Brat: The Glen", region="Heywood", category=LocationCategory.MINOR_QUEST),
    "mq025_06_pacifica": LocationData(display_name="Beat on the Brat: Pacifica", region="Pacifica", category=LocationCategory.MINOR_QUEST),
    "mq025_07_fight_club": LocationData(display_name="Beat on the Brat: Rancho Coronado", region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq025_psycho_brawl": LocationData(display_name="Beat on the Brat", region="Pacifica", category=LocationCategory.MINOR_QUEST),
    "mq026_conspiracy": LocationData(display_name="The Prophet's Song", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq027_stunts": LocationData(display_name="Living on the Edge", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq028_stalker": LocationData(display_name="Every Breath You Take", region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq029_tourist": LocationData(display_name="The Highwayman", region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq030_melisa": LocationData(display_name="Bullets", region="City Center", category=LocationCategory.MINOR_QUEST),
    "mq032_sacrum": LocationData(display_name="Sacrum Profanum", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq033_tarot": LocationData(display_name="Fool on the Hill", region="Night City", category=LocationCategory.MINOR_QUEST),
    "mq035_ozob": LocationData(display_name="Send in the Clowns", region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq036_overload": LocationData(display_name="Sweet Dreams", region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq037_brendan": LocationData(display_name="Coin Operated Boy", region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq038_neweridentity": LocationData(display_name="Big in Japan", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq040_biosculpt": LocationData(display_name="Raymond Chandler Evening", region="Heywood", category=LocationCategory.MINOR_QUEST),
    "mq041_corpo": LocationData(display_name="War Pigs", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq042_nomad": LocationData(display_name="These Boots Are Made for Walkin'", region="Badlands", category=LocationCategory.MINOR_QUEST),
    "mq044_jakes_vehicle": LocationData(display_name="Sex On Wheels", region="Heywood", category=LocationCategory.MINOR_QUEST),
    "mq045_victor_debt": LocationData(display_name="Paid in Full", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq046_cave_vehicle": LocationData(display_name="Murk Man Returns Again Once More Forever", region="Badlands", category=LocationCategory.MINOR_QUEST),
    "mq047_ad_vehicle": LocationData(display_name="Dressed to Kill", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq048_cyberware": LocationData(display_name="Upgrade U", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq049_edgerunners": LocationData(display_name="Over the Edge", region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq050_ken_block_tribute": LocationData(display_name="I'm in Love with My Car", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq057_motorbreath": LocationData(display_name="Motorbreath", region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq058_semimaru_crystalcoat": LocationData(display_name="Where Eagles Dare", region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq059_freedom": LocationData(display_name="Freedom", region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq060_nitro": LocationData(display_name="Nitro (Youth Energy)", region="Watson", category=LocationCategory.MINOR_QUEST),
    "archer_bandit": LocationData(display_name="Quartz 'Bandit'", region="Badlands", category=LocationCategory.MINOR_QUEST),

    #=====================================
    # Phantom Liberty Exclusive
    #====================================
    # --- Phantom Liberty: Side Quests ---
    "wst_ep1_11_bill_meeting": LocationData(display_name="New Person, Same Old Mistakes", region="Dogtown", category=LocationCategory.DLC_SIDE, dlc_only=True),

    # --- Phantom Liberty: Gigs (Mr. Hands) ---
    "sts_ep1_01": LocationData(display_name="Gig: Dogtown Saints", region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_03": LocationData(display_name="Gig: The Man Who Killed Jason Foreman", region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_04": LocationData(display_name="Gig: Prototype in the Scraper", region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_06": LocationData(display_name="Gig: Heaviest of Hearts", region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_07": LocationData(display_name="Gig: Roads to Redemption", region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_08": LocationData(display_name="Gig: Spy in the Jungle", region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_10": LocationData(display_name="Gig: Waiting for Dodger", region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_12": LocationData(display_name="Gig: Treating Symptoms", region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_13": LocationData(display_name="Gig: Talent Academy", region="Dogtown", category=LocationCategory.GIG, dlc_only=True),

    # --- Phantom Liberty: Minor Quests ---
    "mq033_ep1": LocationData(display_name="Tomorrow Never Knows", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "mq300_safehouse": LocationData(display_name="Water Runs Dry", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "mq301_bomb": LocationData(display_name="Balls to the Wall", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "mq303_addict": LocationData(display_name="Dazed and Confused", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "mq305_combat_zone_report": LocationData(display_name="Shot by Both Sides", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "mq306_dumpster": LocationData(display_name="No Easy Way Out", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "q304_car_retrieval": LocationData(display_name="Moving Heat", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "q304_gear_pickup": LocationData(display_name="Dirty Second Hands", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "q304_splinter_stash": LocationData(display_name="Voodoo Treasure", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "sts_ep1_08_loot_pickup": LocationData(display_name="Money For Nothing", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "sts_ep1_08_steven_meeting_night_city": LocationData(display_name="The Show Must Go On", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "sts_ep1_12_pickup": LocationData(display_name="Corpo of the Month", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "wst_ep1_04": LocationData(display_name="Addicted To Chaos", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "wst_ep1_05": LocationData(display_name="Go Your Own Way", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "wst_ep1_09": LocationData(display_name="One Way or Another", region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),

    # =================================
    # Unique Item Checks
    # =================================

    # =================================
    # Tarot
    # =================================
    # --- Phantom Liberty Tarot Counter (Dogtown) ---
    "ap_tarot_26": LocationData(display_name="Collected 23 Tarot", region="Dogtown", category=LocationCategory.TAROT, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_25": LocationData(display_name="Collected 24 Tarot", region="Dogtown", category=LocationCategory.TAROT, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_24": LocationData(display_name="Collected 25 Tarot", region="Dogtown", category=LocationCategory.TAROT, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_23": LocationData(display_name="Collected 26 Tarot", region="Dogtown", category=LocationCategory.TAROT, dlc_only=True, progress_type=LocationProgressType.EXCLUDED),

    # --- Base Game Tarot Counter (Night City) ---
    "ap_tarot_1": LocationData(display_name="Collected 1 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_2": LocationData(display_name="Collected 2 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_3": LocationData(display_name="Collected 3 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_4": LocationData(display_name="Collected 4 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_5": LocationData(display_name="Collected 5 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_6": LocationData(display_name="Collected 6 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_7": LocationData(display_name="Collected 7 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_8": LocationData(display_name="Collected 8 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_9": LocationData(display_name="Collected 9 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_10": LocationData(display_name="Collected 10 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_11": LocationData(display_name="Collected 11 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_12": LocationData(display_name="Collected 12 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_13": LocationData(display_name="Collected 13 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_14": LocationData(display_name="Collected 14 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_15": LocationData(display_name="Collected 15 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_16": LocationData(display_name="Collected 16 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_17": LocationData(display_name="Collected 17 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_18": LocationData(display_name="Collected 18 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_19": LocationData(display_name="Collected 19 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_20": LocationData(display_name="Collected 20 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_21": LocationData(display_name="Collected 21 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    "ap_tarot_22": LocationData(display_name="Collected 22 Tarot", region="Watson", category=LocationCategory.TAROT, progress_type=LocationProgressType.EXCLUDED),
    # =================================

    # =================================
    # Cyber Psycho Sighting Locations
    # ==================================
    "mq043_cyberpsychos": LocationData(display_name="Psycho Killer", region="Watson",category=LocationCategory.CYBERPSYCHO),
    "ma_wat_nid_22": LocationData(display_name="Cyberpsycho Sighting: Six Feet Under", region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_wat_nid_15": LocationData(display_name="Cyberpsycho Sighting: Bloody Ritual", region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_wat_nid_03": LocationData(display_name="Cyberpsycho Sighting: Where the Bodies Hit the Floor", region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_wat_kab_02": LocationData(display_name="Cyberpsycho Sighting: Demons of War", region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_wat_kab_08": LocationData(display_name="Cyberpsycho Sighting: Lt. Mower", region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_wat_lch_06": LocationData(display_name="Cyberpsycho Sighting: Ticket to the Major Leagues", region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_bls_ina_se1_07": LocationData(display_name="Cyberpsycho Sighting: The Wasteland",region="Badlands", category=LocationCategory.CYBERPSYCHO),
    "ma_bls_ina_se1_08": LocationData(display_name="Cyberpsycho Sighting: House on a Hill",region="Badlands", category=LocationCategory.CYBERPSYCHO),
    "ma_bls_ina_se1_22": LocationData(display_name="Cyberpsycho Sighting: Second Chances",region="Badlands", category=LocationCategory.CYBERPSYCHO),
    "ma_cct_dtn_03": LocationData(display_name="Cyberpsycho Sighting: On Deaf Ears",region="City Center", category=LocationCategory.CYBERPSYCHO),
    "ma_cct_dtn_07": LocationData(display_name="Cyberpsycho Sighting: Phantom of Night City", region="City Center", category=LocationCategory.CYBERPSYCHO),
    "ma_hey_spr_04": LocationData(display_name="Cyberpsycho Sighting: Seaside Cafe", region="Heywood", category=LocationCategory.CYBERPSYCHO),
    "ma_hey_spr_06": LocationData(display_name="Cyberpsycho Sighting: Letter of the Law", region="Heywood", category=LocationCategory.CYBERPSYCHO),
    "ma_pac_cvi_08": LocationData(display_name="Cyberpsycho Sighting: Smoke on the Water", region="Pacifica", category=LocationCategory.CYBERPSYCHO),
    "ma_pac_cvi_15": LocationData(display_name="Cyberpsycho Sighting: Lex Talionis",region="Pacifica", category=LocationCategory.CYBERPSYCHO),
    "ma_std_arr_06": LocationData(display_name="Cyberpsycho Sighting: Under the Bridge", region="Santo Domingo", category=LocationCategory.CYBERPSYCHO),
    "ma_std_rcr_11": LocationData(display_name="Cyberpsycho Sighting: Discount Doc", region="Santo Domingo", category=LocationCategory.CYBERPSYCHO),
    # =================================

    # =================================
    # Event Locations
    # =================================
    # Event locations have code=None and represent milestones or quest completions
    # They auto-complete when accessible and are used for internal logic

    # ===== STORY PROGRESSION EVENT LOCATIONS =====
    # These mark major milestones in the story progression
    # Event items with matching names are automatically placed here by regions.py
    # NOTE: Dictionary keys MUST match the item names in items.py exactly!

    # NOTE: Prologue milestone event locations removed - these were orphaned and not
    # used by any rules. Quest completion tracked via location access directly.

    # NOTE: Branch completion event locations removed - Nocturne Op55N1 checks quest
    # locations directly instead of using event items to avoid circular dependencies

    # NOTE: Side quest event locations removed - include_all_endings option handles
    # side quest progression by checking quest locations directly instead of using events

    # NOTE: Phantom Liberty event locations removed - DLC progression tracked directly
    # via quest location access rules, not through event items

    # NOTE: Victory event location is created manually in regions.py, NOT here
    # Event locations created through location_table may get auto-assigned addresses
    # which prevents them from being properly filtered as events
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

    # Group by region
    regions: Dict[str, List[str]] = {}
    for loc_name, loc_data in location_table.items():
        if loc_data.code is None:
            continue  # Skip event locations

        # Add to region group
        if loc_data.region not in regions:
            regions[loc_data.region] = []
        regions[loc_data.region].append(loc_name)

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
    Get all internal location IDs in a specific region.

    Filters the location_table to find all locations belonging to
    a specific region.

    Args:
        region_name: The name of the region to filter by

    Returns:
        List of internal location IDs in that region
    """
    # List comprehension syntax:
    # [name for name, data in location_table.items() if data.region == region_name]
    #
    # This is equivalent to:
    # result = []
    # for name, data in location_table.items():
    #     if data.region == region_name:
    #         result.append(name)
    # return result

    return [
        name
        for name, data in location_table.items()
        if data.region == region_name
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

    Phantom Liberty locations are all in the Dogtown region.
    This helper function makes it easy to filter DLC content.

    Args:
        location_name: The location name to check

    Returns:
        True if the location is in Dogtown (Phantom Liberty DLC), False otherwise
    """
    location_data = location_table.get(location_name)
    if location_data is None:
        return False
    return location_data.region == "Dogtown"
