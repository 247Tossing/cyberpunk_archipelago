"""
Cyberpunk 2077 Location Definitions

This file defines all locations (checks) where items can be found in the game.

Locations represent specific spots in the game where the player can collect
randomized items. They have unique IDs for network communication and are
organized by region for easier management.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from BaseClasses import Location

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
        code: Unique numeric ID for network communication (e.g., 1000)
              Set to None for "event" locations that auto-complete
        region: Which region/area this location belongs to (e.g., "Watson")
        category: Location category for grouping and filtering (default: "misc")
                 Used to group locations by type (main quests, gigs, etc.)
        dlc_only: Whether this location requires Phantom Liberty DLC (default: False)
                 Locations marked dlc_only=True are excluded when DLC is disabled
    """
    display_name: str
    code: Optional[int]  # None for event locations
    region: str  # Which region this location is in
    category: str = "misc"  # Location category (use LocationCategory constants)
    dlc_only: bool = False  # True for Phantom Liberty DLC locations


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

# Location codes are OFFSETS that get added to base_id (2077000) when creating locations
# Codes stored here: 0-499 (offsets)
# Actual Archipelago IDs: 2077000-2077499 (base_id + offset)
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
    "Lifepath Chosen": LocationData(display_name="Lifepath Chosen", code=1000, region="Watson", category=LocationCategory.MAIN_QUEST),
    "Ending Reached" : LocationData(display_name="Ending Reached", code=1001, region="Watson", category=LocationCategory.MAIN_QUEST),
    # Tutorial might get re-added if requested
    #"q000_tutorial": LocationData(display_name="Prologue - Practice Makes Perfect", code=1003, region="Watson", category=LocationCategory.MAIN_QUEST),
    "q001_intro": LocationData(display_name="Prologue - The Rescue", code=1004, region="Watson", category=LocationCategory.MAIN_QUEST),
    "q001_01_victor": LocationData(display_name="Prologue - The Ripperdoc", code=1005, region="Watson", category=LocationCategory.MAIN_QUEST),
    "q001_02_dex": LocationData(display_name="Prologue - The Ride", code=1006, region="Watson", category=LocationCategory.MAIN_QUEST),
    "q003_maelstrom": LocationData(display_name="Prologue - The Pickup", code=1007, region="Watson", category=LocationCategory.MAIN_QUEST),
    "q004_braindance": LocationData(display_name="Prologue - The Information", code=1008, region="Watson", category=LocationCategory.MAIN_QUEST),
    "q005_heist": LocationData(display_name="Prologue - The Heist", code=1009, region="Watson", category=LocationCategory.MAIN_QUEST),

    # =================================
    # Post-Heist Main Story
    # =================================
    "q101_01_firestorm": LocationData(display_name="Act 1 - Love Like Fire", code=1010, region="Watson", category=LocationCategory.MAIN_QUEST),
    "q101_resurrection": LocationData(display_name="Act 1 - Playing for Time", code=1011, region="Watson", category=LocationCategory.MAIN_QUEST),
    "q103_warhead": LocationData(display_name="Main - Ghost Town", code=1012, region="Badlands", category=LocationCategory.MAIN_QUEST),
    "q104_01_sabotage": LocationData(display_name="Main - Lightning Breaks", code=1013, region="Badlands", category=LocationCategory.MAIN_QUEST),
    "q104_02_av_chase": LocationData(display_name="Main - Life During Wartime", code=1014, region="Badlands", category=LocationCategory.MAIN_QUEST),
    "q105_dollhouse": LocationData(display_name="Main - Automatic Love", code=1015, region="Westbrook", category=LocationCategory.MAIN_QUEST),
    "q105_02_jigjig": LocationData(display_name="Main - The Space in Between", code=1016, region="Westbrook", category=LocationCategory.MAIN_QUEST),
    "q105_03_braindance_studio": LocationData(display_name="Main - Disasterpiece", code=1017, region="Santo Domingo", category=LocationCategory.MAIN_QUEST),
    "q105_04_judys": LocationData(display_name="Main - Double Life", code=1018, region="Watson", category=LocationCategory.MAIN_QUEST),
    "q110_01_voodooboys": LocationData(display_name="Main - M'ap Tann Pèlen", code=1019, region="Pacifica", category=LocationCategory.MAIN_QUEST),
    "q110_voodoo": LocationData(display_name="Main - I Walk the Line", code=1020, region="Pacifica", category=LocationCategory.MAIN_QUEST),
    "q110_03_cyberspace": LocationData(display_name="Main - Transmission", code=1021, region="Pacifica", category=LocationCategory.MAIN_QUEST),
    "q108_johnny": LocationData(display_name="Main - Never Fade Away", code=1022, region="Pacifica", category=LocationCategory.MAIN_QUEST),
    "q112_01_old_friend": LocationData(display_name="Main - Down on the Street", code=1023, region="City Center", category=LocationCategory.MAIN_QUEST),
    "q112_02_industrial_park": LocationData(display_name="Main - Gimme Danger", code=1024, region="Santo Domingo", category=LocationCategory.MAIN_QUEST),
    "q112_03_dashi_parade": LocationData(display_name="Main - Play It Safe", code=1025, region="Westbrook", category=LocationCategory.MAIN_QUEST),
    "q112_04_hideout": LocationData(display_name="Main - Search and Destroy", code=1026, region="Heywood", category=LocationCategory.MAIN_QUEST),
    "02_sickness": LocationData(display_name="Endgame - Nocturne Op55N1", code=1027, region="Heywood", category=LocationCategory.MAIN_QUEST),
    "01_climbing_the_ladder": LocationData(display_name="Endgame - Become A Legend", code=1028, region="Watson", category=LocationCategory.MAIN_QUEST),
    "09_solo": LocationData(display_name="Endgame - (Don't Fear) The Reaper", code=1029, region="City Center", category=LocationCategory.MAIN_QUEST),

    # =====================================
    # Endings
    # =====================================
    "q113_rescuing_hanako": LocationData(display_name="Ending - Last Caress", code=1030, region="North Oak", category=LocationCategory.ENDING),
    "q113_corpo": LocationData(display_name="Ending - Total Immortal", code=1031, region="City Center", category=LocationCategory.ENDING),
    "q114_01_nomad_initiation": LocationData(display_name="Ending - We Gotta Live Together", code=1032, region="Badlands", category=LocationCategory.ENDING),
    "q114_02_maglev_line_assault": LocationData(display_name="Ending - Forward to Death", code=1033, region="Badlands", category=LocationCategory.ENDING),
    "q114_03_attack_on_arasaka_tower": LocationData(display_name="Ending - Belly of the Beast", code=1034, region="City Center", category=LocationCategory.ENDING),
    "q115_afterlife": LocationData(display_name="Ending - For Whom the Bell Tolls", code=1035, region="Watson", category=LocationCategory.ENDING),
    "q115_rogues_last_flight": LocationData(display_name="Ending - Knockin' on Heaven's Door", code=1036, region="City Center", category=LocationCategory.ENDING),
    "q116_cyberspace": LocationData(display_name="Ending - Changes", code=1037, region="Watson", category=LocationCategory.ENDING),

    # =====================================
    # Phantom Liberty Checks
    # (Only applicable w/DLC)
    # =====================================
    "q300_phantom_liberty": LocationData(display_name="Phantom Liberty - Phantom Liberty", code=1042, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q301_crash": LocationData(display_name="Phantom Liberty - Dog Eat Dog", code=1043, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q301_finding_myers": LocationData(display_name="Phantom Liberty - Hole in the Sky", code=1044, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q301_q302_rescue_myers": LocationData(display_name="Phantom Liberty - Spider and the Fly", code=1045, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q302_reed": LocationData(display_name="Phantom Liberty - Lucretia My Reflection", code=1046, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q303_baron": LocationData(display_name="Phantom Liberty - The Damned", code=1047, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q303_hands": LocationData(display_name="Phantom Liberty - Get It Together", code=1048, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q303_songbird": LocationData(display_name="Phantom Liberty - You Know My Name", code=1049, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q304_stadium": LocationData(display_name="Phantom Liberty - Birds with Broken Wings", code=1050, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q304_netrunners": LocationData(display_name="Phantom Liberty - I've Seen That Face Before", code=1051, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q304_deal": LocationData(display_name="Phantom Liberty - Firestarter", code=1052, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q305_prison_convoy": LocationData(display_name="Phantom Liberty - Black Steel In The Hour of Chaos", code=1053, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q305_bunker": LocationData(display_name="Phantom Liberty - Somewhat Damaged", code=1058, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q305_border_crossing": LocationData(display_name="Phantom Liberty - Leave in Silence", code=1054, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q306_devils_bargain": LocationData(display_name="Phantom Liberty - The Killing Moon", code=1055, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),
    "q307_before_tomorrow": LocationData(display_name="Phantom Liberty - Who Wants to Live Forever", code=1056, region="Dogtown", category=LocationCategory.DLC_MAIN, dlc_only=True),

    # =================================
    # Epilogues
    # =================================
    "q201_heir": LocationData(display_name="Epilogue - Where is My Mind?", code=1038, region="Watson", category=LocationCategory.EPILOGUE),
    "q202_nomads": LocationData(display_name="Epilogue - All Along the Watchtower", code=1039, region="Badlands", category=LocationCategory.EPILOGUE),
    "q203_legend": LocationData(display_name="Epilogue - Path of Glory", code=1040, region="Watson", category=LocationCategory.EPILOGUE),
    "q204_reborn": LocationData(display_name="Epilogue - New Dawn Fades", code=1041, region="Badlands", category=LocationCategory.EPILOGUE),
    "q307_tomorrow": LocationData(display_name="Phantom Liberty - Things Done Changed", code=1057, region="Dogtown", category=LocationCategory.EPILOGUE, dlc_only=True),

    # =================================
    # Side Quests
    # =================================
    "07_nc_underground": LocationData(display_name="The Beast In Me", code=1060, region="Various", category=LocationCategory.SIDE_QUEST),
    "sq004_riders_on_the_storm": LocationData(display_name="Riders on the Storm", code=1061, region="Badlands", category=LocationCategory.ENDING_SIDE_QUEST),
    "sq006_dream_on": LocationData(display_name="Dream On", code=1062, region="City Center", category=LocationCategory.SIDE_QUEST),
    "sq011_concert": LocationData(display_name="A Like Supreme", code=1063, region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq011_johnny": LocationData(display_name="Second Conflict", code=1064, region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq011_kerry": LocationData(display_name="Holdin' On", code=1065, region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq012_lost_girl": LocationData(display_name="I Fought the Law", code=1066, region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq017_01_riot_club": LocationData(display_name="I Don't Wanna Hear It", code=1067, region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq017_02_lounge": LocationData(display_name="Off the Leash", code=1068, region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq017_kerry": LocationData(display_name="Rebel! Rebel!", code=1069, region="Badlands", category=LocationCategory.SIDE_QUEST),
    "sq018_jackie": LocationData(display_name="Heroes", code=1070, region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq021_sick_dreams": LocationData(display_name="The Hunt", code=1071, region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq022_head_hunter": LocationData(display_name="NO_TITLE", code=1072, region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq023_bd_passion": LocationData(display_name="There Is A Light That Never Goes Out", code=1073,region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq023_hit_order": LocationData(display_name="Sinnerman", code=1074, region="Santo Domingo", category=LocationCategory.SIDE_QUEST),
    "sq023_real_passion": LocationData(display_name="They Won't Go When I Go", code=1075, region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq024_badlands_race": LocationData(display_name="The Beast in Me: Badlands", code=1076, region="Badlands", category=LocationCategory.SIDE_QUEST),
    "sq024_city_race": LocationData(display_name="The Beast in Me: City Center", code=1077, region="City Center", category=LocationCategory.SIDE_QUEST),
    "sq024_santo_domingo_race": LocationData(display_name="The Beast in Me: Santo Domingo", code=1078,region="Santo Domingo", category=LocationCategory.SIDE_QUEST),
    "sq024_the_big_race": LocationData(display_name="The Beast in Me: The Big Race", code=1079, region="Santo Domingo", category=LocationCategory.SIDE_QUEST),
    "sq025_0_pickup": LocationData(display_name="Human Nature", code=1080, region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq025_compensation": LocationData(display_name="Tune Up", code=1081, region="City Center", category=LocationCategory.SIDE_QUEST),
    "sq025_delamain": LocationData(display_name="Epistrophy", code=1082, region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq025b_delamain_insurgence": LocationData(display_name="Don't Lose Your Mind", code=1083, region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq025c01_angry": LocationData(display_name="Epistrophy: Wellsprings", code=1084, region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq025c02_sad": LocationData(display_name="Epistrophy: North Oak", code=1085, region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq025c03_mean": LocationData(display_name="Epistrophy: Coastview", code=1086, region="Pacifica", category=LocationCategory.SIDE_QUEST),
    "sq025c04_manic": LocationData(display_name="Epistrophy: Rancho Coronado", code=1087, region="Santo Domingo", category=LocationCategory.SIDE_QUEST),
    "sq025c05_scared": LocationData(display_name="Epistrophy: Northside", code=1088, region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq025c06_mean": LocationData(display_name="Epistrophy: Badlands", code=1089, region="Badlands", category=LocationCategory.SIDE_QUEST),
    "sq025c07_suicidal": LocationData(display_name="Epistrophy: The Glen", code=1090, region="Heywood", category=LocationCategory.SIDE_QUEST),
    "sq026_01_suicide": LocationData(display_name="Both Sides, Now", code=1091, region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq026_02_maiko": LocationData(display_name="Ex-Factor", code=1092, region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq026_03_pizza": LocationData(display_name="Talkin' 'bout a Revolution", code=1093, region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq026_04_hiromi": LocationData(display_name="Pisces", code=1094, region="Westbrook", category=LocationCategory.SIDE_QUEST),
    "sq027_01_basilisk_convoy": LocationData(display_name="With a Little Help from My Friends", code=1095,region="Badlands", category=LocationCategory.ENDING_SIDE_QUEST),
    "sq027_02_raffen_shiv_attack": LocationData(display_name="Queen of the Highway", code=1096, region="Badlands", category=LocationCategory.ENDING_SIDE_QUEST),
    "sq028_kerry_romance": LocationData(display_name="Boat Drinks", code=1097, region="Pacifica", category=LocationCategory.SIDE_QUEST),
    "sq029_sobchak_romance": LocationData(display_name="Following the River", code=1098, region="Santo Domingo", category=LocationCategory.SIDE_QUEST),
    "sq030_judy_romance": LocationData(display_name="Pyramid Song", code=1099, region="Badlands", category=LocationCategory.SIDE_QUEST),
    "sq031_cinema": LocationData(display_name="Blistering Love", code=1100, region="Westbrook", category=LocationCategory.ENDING_SIDE_QUEST),
    "sq031_rogue": LocationData(display_name="Chippin' In", code=1101, region="Watson", category=LocationCategory.ENDING_SIDE_QUEST),
    "sq031_smack_my_bitch_up": LocationData(display_name="A Cool Metal Fire", code=1102, region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq_q001_tbug": LocationData(display_name="The Gift", code=1103, region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq_q001_wakako": LocationData(display_name="The Gig", code=1104, region="Watson", category=LocationCategory.SIDE_QUEST),
    "sq_q001_wilson": LocationData(display_name="The Gun", code=1105, region="Watson", category=LocationCategory.SIDE_QUEST),
    # =================================
    # Gigs
    # =================================
    "badlands_reward": LocationData(display_name="Every Grain of Sand", code=1115, region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_02": LocationData(display_name="Gig: Big Pete's Got Big Problems", code=1116, region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_03": LocationData(display_name="Gig: Flying Drugs", code=1117, region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_04": LocationData(display_name="Gig: Radar Love", code=1118, region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_05": LocationData(display_name="Gig: Goodbye, Night City", code=1119, region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_06": LocationData(display_name="Gig: No Fixers", code=1120, region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_07": LocationData(display_name="Gig: Dancing on a Minefield", code=1121, region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_08": LocationData(display_name="Gig: Trevor's Last Ride", code=1122, region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_09": LocationData(display_name="Gig: MIA", code=1123, region="Badlands", category=LocationCategory.GIG),
    "sts_bls_ina_11": LocationData(display_name="Gig: Sparring Partner", code=1124, region="Badlands", category=LocationCategory.GIG),
    "city_center_reward": LocationData(display_name="Gas Gas Gas", code=1125, region="City Center", category=LocationCategory.GIG),
    "sts_cct_cpz_01": LocationData(display_name="Gig: Serial Suicide", code=1126, region="City Center", category=LocationCategory.GIG),
    "sts_cct_dtn_02": LocationData(display_name="Gig: An Inconvenient Killer", code=1127, region="City Center", category=LocationCategory.GIG),
    "sts_cct_dtn_03": LocationData(display_name="Gig: A Lack of Empathy", code=1128, region="City Center", category=LocationCategory.GIG),
    "sts_cct_dtn_04": LocationData(display_name="Gig: Guinea Pigs", code=1129, region="City Center", category=LocationCategory.GIG),
    "sts_cct_dtn_05": LocationData(display_name="Gig: The Frolics of Councilwoman Cole", code=1130,region="City Center", category=LocationCategory.GIG),
    "generic_sts_quest": LocationData(display_name="Undiscovered", code=1131, region="Night City", category=LocationCategory.GIG),
    "sts_hey_gle_01": LocationData(display_name="Gig: Eye for an Eye", code=1132, region="Heywood", category=LocationCategory.GIG),
    "sts_hey_gle_03": LocationData(display_name="Gig: Psychofan", code=1133, region="Heywood", category=LocationCategory.GIG),
    "sts_hey_gle_04": LocationData(display_name="Gig: Fifth Column", code=1134, region="Heywood", category=LocationCategory.GIG),
    "sts_hey_gle_05": LocationData(display_name="Gig: Going Up or Down?", code=1135, region="Heywood", category=LocationCategory.GIG),
    "sts_hey_gle_06": LocationData(display_name="Gig: Life's Work", code=1136, region="Heywood", category=LocationCategory.GIG),
    "heywood_reward": LocationData(display_name="God Bless This Mess", code=1137, region="Heywood", category=LocationCategory.GIG),
    "sts_hey_rey_01": LocationData(display_name="Gig: Bring Me the Head of Gustavo Orta", code=1138, region="Heywood", category=LocationCategory.GIG),
    "sts_hey_rey_02": LocationData(display_name="Gig: Sr. Ladrillo's Private Collection", code=1139, region="Heywood", category=LocationCategory.GIG),
    "sts_hey_rey_06": LocationData(display_name="Gig: Jeopardy", code=1140, region="Heywood", category=LocationCategory.GIG),
    "sts_hey_rey_08": LocationData(display_name="Gig: Old Friends", code=1141, region="Heywood", category=LocationCategory.GIG),
    "sts_hey_rey_09": LocationData(display_name="Gig: Getting Warmer...", code=1142, region="Heywood", category=LocationCategory.GIG),
    "sts_hey_spr_01": LocationData(display_name="Gig: On a Tight Leash", code=1143, region="Heywood", category=LocationCategory.GIG),
    "sts_hey_spr_03": LocationData(display_name="Gig: The Lord Giveth and Taketh Away", code=1144, region="Heywood", category=LocationCategory.GIG),
    "sts_hey_spr_06": LocationData(display_name="Gig: Hot Merchandise", code=1145, region="Heywood", category=LocationCategory.GIG),
    "sts_pac_cvi_02": LocationData(display_name="Gig: Two Wrongs Makes Us Right", code=1146, region="Pacifica", category=LocationCategory.GIG),
    "sts_pac_wwd_05": LocationData(display_name="Gig: For My Son", code=1147, region="Pacifica", category=LocationCategory.GIG),
    "sts_std_arr_01": LocationData(display_name="Gig: Serious Side Effects", code=1148, region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_arr_03": LocationData(display_name="Gig: Race to the Top", code=1149, region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_arr_05": LocationData(display_name="Gig: Breaking News", code=1150, region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_arr_06": LocationData(display_name="Gig: Nasty Hangover", code=1151, region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_arr_10": LocationData(display_name="Gig: Severance Package", code=1152, region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_arr_11": LocationData(display_name="Gig: Hacking the Hacker", code=1153, region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_arr_12": LocationData(display_name="Gig: Desperate Measures", code=1154, region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_rcr_01": LocationData(display_name="Gig: The Union Strikes Back", code=1155, region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_rcr_02": LocationData(display_name="Gig: Cuckoo's Nest", code=1156, region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_rcr_03": LocationData(display_name="Gig: Going-away Party", code=1157, region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_rcr_04": LocationData(display_name="Gig: Error 404", code=1158, region="Santo Domingo", category=LocationCategory.GIG),
    "sts_std_rcr_05": LocationData(display_name="Gig: Family Matters", code=1159, region="Santo Domingo", category=LocationCategory.GIG),
    "santo_domingo_reward": LocationData(display_name="Ride Captain Ride", code=1160, region="Santo Domingo", category=LocationCategory.GIG),
    "sts_wat_kab_01": LocationData(display_name="Gig: Concrete Cage Trap", code=1161, region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_02": LocationData(display_name="Gig: Hippocratic Oath", code=1162, region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_03": LocationData(display_name="Gig: Backs Against the Wall", code=1163, region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_04": LocationData(display_name="Gig: Fixer, Merc, Soldier, Spy", code=1164, region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_05": LocationData(display_name="Gig: Last Login", code=1165, region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_06": LocationData(display_name="Gig: Shark in the Water", code=1166, region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_07": LocationData(display_name="Gig: Monster Hunt", code=1167, region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_08": LocationData(display_name="Gig: Woman of La Mancha", code=1168, region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_101": LocationData(display_name="Gig: Small Man, Big Evil", code=1169, region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_102": LocationData(display_name="Gig: Welcome to America, Comrade", code=1170, region="Watson", category=LocationCategory.GIG),
    "sts_wat_kab_107": LocationData(display_name="Gig: Troublesome Neighbors", code=1171, region="Watson", category=LocationCategory.GIG),
    "sts_wat_lch_01": LocationData(display_name="Gig: Catch a Tyger's Toe", code=1172, region="Watson", category=LocationCategory.GIG),
    "sts_wat_lch_03": LocationData(display_name="Gig: Bloodsport", code=1173, region="Watson", category=LocationCategory.GIG),
    "sts_wat_lch_05": LocationData(display_name="Gig: Playing for Keeps", code=1174, region="Watson", category=LocationCategory.GIG),
    "sts_wat_lch_06": LocationData(display_name="Gig: The Heisenberg Principle", code=1175, region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_01": LocationData(display_name="Gig: Occupational Hazard", code=1176, region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_02": LocationData(display_name="Gig: Many Ways to Skin a Cat", code=1177, region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_03": LocationData(display_name="Gig: Flight of the Cheetah", code=1178, region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_04": LocationData(display_name="Gig: Dirty Biz", code=1179, region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_05": LocationData(display_name="Gig: Rite of Passage", code=1180, region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_06": LocationData(display_name="Gig: Lousy Kleppers", code=1181, region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_07": LocationData(display_name="Gig: Scrolls before Swine", code=1182, region="Watson", category=LocationCategory.GIG),
    "sts_wat_nid_12": LocationData(display_name="Gig: Freedom of the Press", code=1183, region="Watson", category=LocationCategory.GIG),
    "watson_reward": LocationData(display_name="Last Call", code=1184, region="Watson", category=LocationCategory.GIG),
    "sts_wbr_hil_01": LocationData(display_name="Gig: Until Death Do Us Part", code=1185, region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_hil_06": LocationData(display_name="Gig: Family Heirloom", code=1186, region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_hil_07": LocationData(display_name="Gig: Tyger and Vulture", code=1187, region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_jpn_01": LocationData(display_name="Gig: Olive Branch", code=1188, region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_jpn_02": LocationData(display_name="Gig: We Have Your Wife", code=1189, region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_jpn_03": LocationData(display_name="Gig: A Shrine Defiled", code=1190, region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_jpn_05": LocationData(display_name="Gig: Wakako's Favorite", code=1191, region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_jpn_09": LocationData(display_name="Gig: Hothead", code=1192, region="Westbrook", category=LocationCategory.GIG),
    "sts_wbr_jpn_12": LocationData(display_name="Gig: Greed Never Pays", code=1193, region="Westbrook", category=LocationCategory.GIG),
    "westbrook_reward": LocationData(display_name="Professional Widow", code=1194, region="Westbrook", category=LocationCategory.GIG),

    # ================================
    # Contracts
    # ================================
    "ma_bls_ina_se1_02": LocationData(display_name="Reported Crime: Comrade Red", code=1196, region="Badlands", category=LocationCategory.NCPD_HUSTLE),
    "ma_bls_ina_se1_03": LocationData(display_name="Reported Crime: Blood in the Air", code=1197, region="Badlands", category=LocationCategory.NCPD_HUSTLE),
    "ma_bls_ina_se1_06": LocationData(display_name="Reported Crime: Extremely Loud and Incredibly Close", code=1198, region="Badlands", category=LocationCategory.NCPD_HUSTLE),
    "ma_bls_ina_se1_18": LocationData(display_name="Reported Crime: I Don't Like Sand", code=1199, region="Badlands", category=LocationCategory.NCPD_HUSTLE),
    "ma_bls_ina_se1_22": LocationData(display_name="Cyberpsycho Sighting: Second Chances", code=1200, region="Badlands", category=LocationCategory.CYBERPSYCHO),
    "ma_bls_ina_se5_33": LocationData(display_name="Reported Crime: Delivery From Above", code=1201, region="Badlands", category=LocationCategory.NCPD_HUSTLE),
    "ma_cct_dtn_03": LocationData(display_name="Cyberpsycho Sighting: On Deaf Ears", code=1202, region="City Center", category=LocationCategory.CYBERPSYCHO),
    "ma_cct_dtn_12": LocationData(display_name="Reported Crime: Turn Off the Tap", code=1203, region="City Center", category=LocationCategory.NCPD_HUSTLE),
    "ma_hey_gle_02": LocationData(display_name="Suspected Organized Crime Activity: Chapel", code=1204, region="Heywood", category=LocationCategory.NCPD_HUSTLE),
    "ma_hey_gle_07": LocationData(display_name="Reported Crime: Smoking Kills", code=1205, region="Heywood", category=LocationCategory.NCPD_HUSTLE),
    "ma_hey_spr_11": LocationData(display_name="Suspected Organized Crime Activity: Living the Big Life", code=1206, region="Heywood", category=LocationCategory.NCPD_HUSTLE),
    "ma_pac_cvi_10": LocationData(display_name="Reported Crime: Roadside Picnic", code=1207, region="Pacifica", category=LocationCategory.NCPD_HUSTLE),
    "ma_pac_cvi_12": LocationData(display_name="Suspected Organized Crime Activity: Wipe the Gonk, Take the Implants", code=1208, region="Pacifica", category=LocationCategory.NCPD_HUSTLE),
    "ma_pac_cvi_13": LocationData(display_name="Reported Crime: Honey, Where are You?", code=1209, region="Pacifica", category=LocationCategory.NCPD_HUSTLE),
    "ma_pac_wwd_02": LocationData(display_name="LocKey39425", code=1210, region="Pacifica", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_arr_03": LocationData(display_name="NO_TITLE", code=1211, region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_arr_07": LocationData(display_name="Reported Crime: Disloyal Employee", code=1212, region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_arr_10": LocationData(display_name="Reported Crime: Ooh, Awkward", code=1213, region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_arr_14": LocationData(display_name="Reported Crime: Supply Management", code=1214, region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_rcr_08": LocationData(display_name="LocKey39438", code=1215, region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_rcr_10": LocationData(display_name="Reported Crime: Welcome to Night City", code=1216, region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_rcr_12": LocationData(display_name="Reported Crime: A Stroke of Luck", code=1217, region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_rcr_13": LocationData(display_name="Reported Crime: Justice Behind Bars", code=1218, region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_rcr_16": LocationData(display_name="NO_TITLE", code=1219, region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_std_rcr_18": LocationData(display_name="LocKey42920", code=1220, region="Santo Domingo", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_kab_05": LocationData(display_name="Reported Crime: Protect and Serve", code=1221, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_01": LocationData(display_name="Suspected Organized Crime Activity: Opposites Attract", code=1222, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_03": LocationData(display_name="Reported Crime: Worldly Possessions", code=1223, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_05": LocationData(display_name="Reported Crime: Paranoia", code=1224, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_08": LocationData(display_name="Suspected Organized Crime Activity: Tygers by the Tail", code=1225, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_lch_15": LocationData(display_name="Reported Crime: Dangerous Currents", code=1226, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_01": LocationData(display_name="Suspected Organized Crime Activity: Vice Control", code=1227, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_02": LocationData(display_name="Suspected Organized Crime Activity: Just Say No", code=1228, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_03": LocationData(display_name="Cyberpsycho Sighting: Where the Bodies Hit the Floor", code=1229, region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_wat_nid_06": LocationData(display_name="Suspected Organized Crime Activity: No License, No Problem", code=1230, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_10": LocationData(display_name="Reported Crime: Dredged Up", code=1231, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_12": LocationData(display_name="Reported Crime: Needle in a Haystack", code=1232, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_26": LocationData(display_name="Reported Crime: One Thing Led to Another", code=1233, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wat_nid_27": LocationData(display_name="Reported Crime: Don't Forget the Parking Brake!", code=1234, region="Watson", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_hil_05": LocationData(display_name="Reported Crime: You Play with Fire...", code=1235, region="Westbrook", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_jpn_07": LocationData(display_name="Reported Crime: Lost and Found", code=1236, region="Westbrook", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_jpn_09": LocationData(display_name="Reported Crime: Another Circle of Hell", code=1237, region="Westbrook", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_jpn_20": LocationData(display_name="!DUPLICATE", code=1238, region="Westbrook", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_nok_01": LocationData(display_name="Reported Crime: Crash Test", code=1239, region="Westbrook", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_nok_03": LocationData(display_name="Reported Crime: Table Scraps", code=1240, region="Westbrook", category=LocationCategory.NCPD_HUSTLE),
    "ma_wbr_nok_05": LocationData(display_name="Suspected Organized Crime Activity: Privacy Policy Violation", code=1241, region="Westbrook", category=LocationCategory.NCPD_HUSTLE),

    # ==================================
    # Vehicle Quests
    # ==================================
    "arch": LocationData(display_name="Nazaré 'Racer'", code=1244, region="Night City", category=LocationCategory.MINOR_QUEST),
    "archer_quartz": LocationData(display_name="Quartz EC-L r275", code=1245, region="Night City", category=LocationCategory.MINOR_QUEST),
    "brennan_apollo": LocationData(display_name="Apollo", code=1246, region="Night City", category=LocationCategory.MINOR_QUEST),
    "chevalier_emperor": LocationData(display_name="Emperor 620 Ragnar", code=1247, region="Night City", category=LocationCategory.MINOR_QUEST),
    "chevalier_thrax": LocationData(display_name="Thrax 388 Jefferson", code=1248, region="Night City", category=LocationCategory.MINOR_QUEST),
    "herrera_outlaw": LocationData(display_name="Outlaw", code=1249, region="Night City", category=LocationCategory.MINOR_QUEST),
    "mahir_supron": LocationData(display_name="Supron FS3", code=1250, region="Night City", category=LocationCategory.MINOR_QUEST),
    "makigai_maimai": LocationData(display_name="MaiMai P126", code=1251, region="Night City", category=LocationCategory.MINOR_QUEST),
    "mizutani_shion": LocationData(display_name="Shion MZ2", code=1252, region="Night City", category=LocationCategory.MINOR_QUEST),
    "mizutani_shion_nomad": LocationData(display_name="Shion 'Coyote'", code=1253, region="Badlands", category=LocationCategory.MINOR_QUEST),
    "quadra_turbo": LocationData(display_name="Turbo-R 740", code=1254, region="Night City", category=LocationCategory.MINOR_QUEST),
    "quadra_type66": LocationData(display_name="Type-66 640 TS", code=1255, region="Night City", category=LocationCategory.MINOR_QUEST),
    "quadra_type66_avenger": LocationData(display_name="Quadra Type-66 Avenger", code=1256, region="Night City", category=LocationCategory.MINOR_QUEST),
    "quadra_type66_nomad": LocationData(display_name="Quadra Type-66 'Javelina'", code=1257, region="Badlands", category=LocationCategory.MINOR_QUEST),
    "quadra_type66_nomad_ncu": LocationData(display_name="Quadra Type-66 'Cthulhu'", code=1258, region="Night City", category=LocationCategory.MINOR_QUEST),
    "rayfield_aerondight": LocationData(display_name="Rayfield Aerondight 'Guinevere'", code=1259, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "rayfield_caliburn": LocationData(display_name="Rayfield Caliburn", code=1260, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "thorton_colby": LocationData(display_name="Colby C125", code=1261, region="Night City", category=LocationCategory.MINOR_QUEST),
    "thorton_colby_nomad": LocationData(display_name="Thorton Colby 'Little Mule'", code=1262, region="Badlands", category=LocationCategory.MINOR_QUEST),
    "thorton_colby_pickup": LocationData(display_name="Thorton Colby CX410 Butte", code=1263, region="Night City", category=LocationCategory.MINOR_QUEST),
    "thorton_galena": LocationData(display_name="Galena G240", code=1264, region="Night City", category=LocationCategory.MINOR_QUEST),
    "thorton_galena_nomad": LocationData(display_name="Thorton Galena 'Gecko'", code=1265, region="Badlands", category=LocationCategory.MINOR_QUEST),
    "thorton_mackinaw": LocationData(display_name="Mackinaw MTL1", code=1266, region="Night City", category=LocationCategory.MINOR_QUEST),
    "villefort_alvarado": LocationData(display_name="Alvarado V4F 570 Delegate", code=1275, region="Night City", category=LocationCategory.MINOR_QUEST),
    "villefort_columbus": LocationData(display_name="Columbus V340-F Freight", code=1276, region="Night City", category=LocationCategory.MINOR_QUEST),
    "villefort_cortes": LocationData(display_name="Cortes V5000 Valor", code=1277, region="Night City", category=LocationCategory.MINOR_QUEST),
    "yaiba_kusanagi": LocationData(display_name="Kusanagi CT-3X", code=1278, region="Night City", category=LocationCategory.MINOR_QUEST),

    # =================================
    # Minor Quests
    # =================================
    "q003_stout": LocationData(display_name="Venus in Furs", code=1294, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq001_scorpion": LocationData(display_name="I'll Fly Away", code=1295, region="Badlands", category=LocationCategory.MINOR_QUEST),
    "mq002_veterans": LocationData(display_name="Gun Music", code=1296, region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq003_orbitals": LocationData(display_name="Space Oddity", code=1297, region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq005_alley": LocationData(display_name="Only Pain", code=1298, region="Heywood", category=LocationCategory.MINOR_QUEST),
    "mq006_rollercoaster": LocationData(display_name="Love Rollercoaster", code=1299, region="Pacifica", category=LocationCategory.MINOR_QUEST),
    "mq007_smartgun": LocationData(display_name="Machine Gun", code=1300, region="Heywood", category=LocationCategory.MINOR_QUEST),
    "mq008_party": LocationData(display_name="Stadium Love", code=1301, region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq009_loser": LocationData(display_name="NO_TITLE", code=1302, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq010_barry": LocationData(display_name="Happy Together", code=1303, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq011_wilson": LocationData(display_name="Shoot To Thrill", code=1304, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq012_stud": LocationData(display_name="Burning Desire", code=1305, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq013_punks": LocationData(display_name="A Day In The Life", code=1306, region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq014_02_second": LocationData(display_name="Stairway To Heaven", code=1307, region="Heywood", category=LocationCategory.MINOR_QUEST),
    "mq014_03_third": LocationData(display_name="Poem Of The Atoms", code=1308, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq014_04_fourth": LocationData(display_name="Meetings Along The Edge", code=1309, region="City Center", category=LocationCategory.MINOR_QUEST),
    "mq014_zen": LocationData(display_name="Imagine", code=1310, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq015_wizardbook": LocationData(display_name="Spellbound", code=1311, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq016_bartmoss": LocationData(display_name="KOLD MIRAGE", code=1312, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq017_streetkid": LocationData(display_name="Small Man, Big Mouth", code=1313, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq018_writer": LocationData(display_name="Killing In The Name", code=1314, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq019_paparazzi": LocationData(display_name="Violence", code=1315, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq021_guide": LocationData(display_name="Fortunate Son", code=1316, region="Badlands", category=LocationCategory.MINOR_QUEST),
    "mq022_ezekiel": LocationData(display_name="Ezekiel Saw the Wheel", code=1317, region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq023_bootleg": LocationData(display_name="The Ballad of Buck Ravers", code=1318, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq024_sandra": LocationData(display_name="Full Disclosure", code=1319, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq025_02_kabuki": LocationData(display_name="Beat on the Brat: Kabuki", code=1320, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq025_03_arroyo": LocationData(display_name="Beat on the Brat: Arroyo", code=1321, region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq025_05_glen": LocationData(display_name="Beat on the Brat: The Glen", code=1322, region="Heywood", category=LocationCategory.MINOR_QUEST),
    "mq025_06_pacifica": LocationData(display_name="Beat on the Brat: Pacifica", code=1323, region="Pacifica", category=LocationCategory.MINOR_QUEST),
    "mq025_07_fight_club": LocationData(display_name="Beat on the Brat: Rancho Coronado", code=1324, region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq025_psycho_brawl": LocationData(display_name="Beat on the Brat", code=1325, region="Pacifica", category=LocationCategory.MINOR_QUEST),
    "mq026_conspiracy": LocationData(display_name="The Prophet's Song", code=1326, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq027_stunts": LocationData(display_name="Living on the Edge", code=1327, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq028_stalker": LocationData(display_name="Every Breath You Take", code=1328, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq029_tourist": LocationData(display_name="The Highwayman", code=1329, region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq030_melisa": LocationData(display_name="Bullets", code=1320, region="City Center", category=LocationCategory.MINOR_QUEST),
    "mq032_sacrum": LocationData(display_name="Sacrum Profanum", code=1331, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq033_tarot": LocationData(display_name="Fool on the Hill", code=1332, region="Night City", category=LocationCategory.MINOR_QUEST),
    "mq035_ozob": LocationData(display_name="Send in the Clowns", code=1333, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq036_overload": LocationData(display_name="Sweet Dreams", code=1334, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq037_brendan": LocationData(display_name="Coin Operated Boy", code=1335, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq037_brendan_dumpster": LocationData(display_name="I Can See Clearly Now", code=1336, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq037_brendan_hooligan001": LocationData(display_name="Spray Paint", code=1337, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq038_neweridentity": LocationData(display_name="Big in Japan", code=1338, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq040_biosculpt": LocationData(display_name="Raymond Chandler Evening", code=1339, region="Heywood", category=LocationCategory.MINOR_QUEST),
    "mq041_corpo": LocationData(display_name="War Pigs", code=1340, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq042_nomad": LocationData(display_name="These Boots Are Made for Walkin'", code=1341, region="Badlands", category=LocationCategory.MINOR_QUEST),
    "mq043_cyberpsychos": LocationData(display_name="Psycho Killer", code=1342, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq044_jakes_vehicle": LocationData(display_name="Sex On Wheels", code=1343, region="Heywood", category=LocationCategory.MINOR_QUEST),
    "mq045_victor_debt": LocationData(display_name="Paid in Full", code=1344, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq046_cave_vehicle": LocationData(display_name="Murk Man Returns Again Once More Forever", code=1345, region="Badlands", category=LocationCategory.MINOR_QUEST),
    "mq047_ad_vehicle": LocationData(display_name="Dressed to Kill", code=1346, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq048_cyberware": LocationData(display_name="Upgrade U", code=1347, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq049_edgerunners": LocationData(display_name="Over the Edge", code=1348, region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq050_ken_block_tribute": LocationData(display_name="I'm in Love with My Car", code=1349, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq055_romance_apartment": LocationData(display_name="I Really Want to Stay at Your House", code=1350, region="Night City", category=LocationCategory.MINOR_QUEST),
    "mq056_race_replay": LocationData(display_name="The Distance", code=1351, region="Night City", category=LocationCategory.MINOR_QUEST),
    "mq057_motorbreath": LocationData(display_name="Motorbreath", code=1352, region="Santo Domingo", category=LocationCategory.MINOR_QUEST),
    "mq058_semimaru_crystalcoat": LocationData(display_name="Where Eagles Dare", code=1353, region="Westbrook", category=LocationCategory.MINOR_QUEST),
    "mq059_freedom": LocationData(display_name="Freedom", code=1354, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mq060_nitro": LocationData(display_name="Nitro (Youth Energy)", code=1355, region="Watson", category=LocationCategory.MINOR_QUEST),
    "mws_se5_07": LocationData(display_name="Shape of a Pony", code=1356, region="Badlands", category=LocationCategory.MINOR_QUEST),
    "mws_wat_08_trauma_drama": LocationData(display_name="Career Opportunities", code=1357, region="Watson", category=LocationCategory.MINOR_QUEST),
    "ue_metro_start": LocationData(display_name="Don't Sleep on the Subway", code=1358, region="Night City", category=LocationCategory.MINOR_QUEST),
    "sq_cyberpsychos_regina": LocationData(display_name="Cyberpsychosis", code=1359, region="Watson", category=LocationCategory.MINOR_QUEST),
    "archer_bandit": LocationData(display_name="Quartz 'Bandit'", code=1360, region="Badlands", category=LocationCategory.MINOR_QUEST),

    #=====================================
    # Phantom Liberty Exclusive
    #====================================
    # --- Phantom Liberty: Side Quests ---
    "wst_ep1_11_bill_meeting": LocationData(display_name="New Person, Same Old Mistakes", code=1059, region="Dogtown", category=LocationCategory.DLC_SIDE, dlc_only=True),

    # --- Phantom Liberty: Gigs (Mr. Hands) ---
    "combat_zone_reward": LocationData(display_name="Hi Ho Silver Lining", code=1105, region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_01": LocationData(display_name="Gig: Dogtown Saints", code=1106, region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_03": LocationData(display_name="Gig: The Man Who Killed Jason Foreman", code=1107, region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_04": LocationData(display_name="Gig: Prototype in the Scraper", code=1108, region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_06": LocationData(display_name="Gig: Heaviest of Hearts", code=1109, region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_07": LocationData(display_name="Gig: Roads to Redemption", code=1110, region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_08": LocationData(display_name="Gig: Spy in the Jungle", code=1111, region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_10": LocationData(display_name="Gig: Waiting for Dodger", code=1112, region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_12": LocationData(display_name="Gig: Treating Symptoms", code=1113, region="Dogtown", category=LocationCategory.GIG, dlc_only=True),
    "sts_ep1_13": LocationData(display_name="Gig: Talent Academy", code=1114, region="Dogtown", category=LocationCategory.GIG, dlc_only=True),

    # --- Phantom Liberty: Contracts & Vehicle Meta ---
    "sa_ep1_15": LocationData(display_name="sa_ep1_15", code=1195, region="Dogtown", category=LocationCategory.NCPD_HUSTLE, dlc_only=True),
    "courier_outro": LocationData(display_name="Courier outro", code=1243, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),

    # --- Phantom Liberty: Minor Quests ---
    "mq033_ep1": LocationData(display_name="Tomorrow Never Knows", code=1279, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "mq300_safehouse": LocationData(display_name="Water Runs Dry", code=1280, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "mq301_bomb": LocationData(display_name="Balls to the Wall", code=1281, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "mq303_addict": LocationData(display_name="Dazed and Confused", code=1282, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "mq305_combat_zone_report": LocationData(display_name="Shot by Both Sides", code=1283, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "mq306_dumpster": LocationData(display_name="No Easy Way Out", code=1284, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "q304_car_retrieval": LocationData(display_name="Moving Heat", code=1285, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "q304_gear_pickup": LocationData(display_name="Dirty Second Hands", code=1286, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "q304_splinter_stash": LocationData(display_name="Voodoo Treasure", code=1287, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "sts_ep1_08_loot_pickup": LocationData(display_name="Money For Nothing", code=1288, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "sts_ep1_08_steven_meeting_night_city": LocationData(display_name="The Show Must Go On", code=1289, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "sts_ep1_12_pickup": LocationData(display_name="Corpo of the Month", code=1290, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "wst_ep1_04": LocationData(display_name="Addicted To Chaos", code=1291, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "wst_ep1_05": LocationData(display_name="Go Your Own Way", code=1292, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),
    "wst_ep1_09": LocationData(display_name="One Way or Another", code=1293, region="Dogtown", category=LocationCategory.MINOR_QUEST, dlc_only=True),

    # =================================
    # Unique Item Checks
    # =================================

    # =================================
    # Tarot
    # =================================
    # --- Phantom Liberty Tarot Counter (Dogtown) ---
    "ap_tarot_26": LocationData(display_name="Collected 1 Phantom Liberty Tarot", code=1294, region="Dogtown", category=LocationCategory.TAROT, dlc_only=True),
    "ap_tarot_25": LocationData(display_name="Collected 2 Phantom Liberty Tarot", code=1295, region="Dogtown", category=LocationCategory.TAROT, dlc_only=True),
    "ap_tarot_24": LocationData(display_name="Collected 3 Phantom Liberty Tarot", code=1296, region="Dogtown", category=LocationCategory.TAROT, dlc_only=True),
    "ap_tarot_23": LocationData(display_name="Collected 4 Phantom Liberty Tarot", code=1297, region="Dogtown", category=LocationCategory.TAROT, dlc_only=True),

    # --- Base Game Tarot Counter (Night City) ---
    "ap_tarot_1": LocationData(display_name="Collected 1 Tarot", code=1361, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_2": LocationData(display_name="Collected 2 Tarot", code=1362, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_3": LocationData(display_name="Collected 3 Tarot", code=1363, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_4": LocationData(display_name="Collected 4 Tarot", code=1364, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_5": LocationData(display_name="Collected 5 Tarot", code=1365, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_6": LocationData(display_name="Collected 6 Tarot", code=1366, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_7": LocationData(display_name="Collected 7 Tarot", code=1367, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_8": LocationData(display_name="Collected 8 Tarot", code=1368, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_9": LocationData(display_name="Collected 9 Tarot", code=1369, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_10": LocationData(display_name="Collected 10 Tarot", code=1370, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_11": LocationData(display_name="Collected 11 Tarot", code=1371, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_12": LocationData(display_name="Collected 12 Tarot", code=1372, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_13": LocationData(display_name="Collected 13 Tarot", code=1373, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_14": LocationData(display_name="Collected 14 Tarot", code=1374, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_15": LocationData(display_name="Collected 15 Tarot", code=1375, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_16": LocationData(display_name="Collected 16 Tarot", code=1376, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_17": LocationData(display_name="Collected 17 Tarot", code=1377, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_18": LocationData(display_name="Collected 18 Tarot", code=1378, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_19": LocationData(display_name="Collected 19 Tarot", code=1379, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_20": LocationData(display_name="Collected 20 Tarot", code=1380, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_21": LocationData(display_name="Collected 21 Tarot", code=1381, region="Watson", category=LocationCategory.TAROT),
    "ap_tarot_22": LocationData(display_name="Collected 22 Tarot", code=1382, region="Watson", category=LocationCategory.TAROT),

    # =================================
    # Cyber Psycho Sighting Locations
    # ==================================
    "ma_wat_nid_22": LocationData(display_name="Cyberpsycho Sighting: Six Feet Under", code=3000, region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_wat_nid_15": LocationData(display_name="Cyberpsycho Sighting: Bloody Ritual", code=3001, region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_wat_nid_03": LocationData(display_name="Cyberpsycho Sighting: Where the Bodies Hit the Floor", code=3002, region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_wat_kab_02": LocationData(display_name="Cyberpsycho Sighting: Demons of War", code=3003, region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_wat_kab_08": LocationData(display_name="Cyberpsycho Sighting: Lt. Mower", code=3004, region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_wat_lch_06": LocationData(display_name="Cyberpsycho Sighting: Ticket to the Major Leagues", code=3005, region="Watson", category=LocationCategory.CYBERPSYCHO),
    "ma_bls_ina_se1_07": LocationData(display_name="Cyberpsycho Sighting: The Wasteland",code=3006, region="Badlands", category=LocationCategory.CYBERPSYCHO),
    "ma_bls_ina_se1_08": LocationData(display_name="Cyberpsycho Sighting: House on a Hill",code=3007, region="Badlands", category=LocationCategory.CYBERPSYCHO),
    "ma_bls_ina_se1_22": LocationData(display_name="Cyberpsycho Sighting: Second Chances",code=3008, region="Badlands", category=LocationCategory.CYBERPSYCHO),
    "ma_cct_dtn_03": LocationData(display_name="Cyberpsycho Sighting: On Deaf Ears",code=3009, region="City Center", category=LocationCategory.CYBERPSYCHO),
    "ma_cct_dtn_07": LocationData(display_name="Cyberpsycho Sighting: Phantom of Night City", code=3010, region="City Center", category=LocationCategory.CYBERPSYCHO),
    "ma_hey_spr_04": LocationData(display_name="Cyberpsycho Sighting: Seaside Cafe", code=3011, region="Heywood", category=LocationCategory.CYBERPSYCHO),
    "ma_hey_spr_06": LocationData(display_name="Cyberpsycho Sighting: Letter of the Law", code=3012, region="Heywood", category=LocationCategory.CYBERPSYCHO),
    "ma_pac_cvi_08": LocationData(display_name="Cyberpsycho Sighting: Smoke on the Water", code=3013, region="Pacifica", category=LocationCategory.CYBERPSYCHO),
    "ma_pac_cvi_15": LocationData(display_name="Cyberpsycho Sighting: Lex Talionis",code=3014, region="Pacifica", category=LocationCategory.CYBERPSYCHO),
    "ma_std_arr_06": LocationData(display_name="Cyberpsycho Sighting: Under the Bridge", code=3015, region="Santo Domingo", category=LocationCategory.CYBERPSYCHO),
    "ma_std_rcr_11": LocationData(display_name="Cyberpsycho Sighting: Discount Doc", code=3016, region="Santo Domingo", category=LocationCategory.CYBERPSYCHO),
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
