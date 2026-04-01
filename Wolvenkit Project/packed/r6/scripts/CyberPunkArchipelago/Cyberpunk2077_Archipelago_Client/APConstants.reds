module Archipelago

// Central constants file to eliminate magic strings throughout the codebase
public class APConstants { 

    // ===== VERSION INFORMATION =====
    public static func GetClientVersion() -> String {
        return "0.5"; 
    }

    public static func GetRequiredServerVersion() -> String {
        return "0.5";
    } 

    // ===== Weapon Types =====
    // The weapon types in Cyberpunk are pretty granular, so we simplify them a bit


    // ===== ITEM TYPE PREFIXES =====
    // Used for parsing item IDs from the Archipelago server
    public static func GetItemTypeQuestKey() -> String { return "qk"; }
    public static func GetItemTypeSkillPoint() -> String { return "sp"; }
    public static func GetItemTypeTrap() -> String { return "trp"; }
    public static func GetItemTypeEddies() -> String { return "ed"; }
    public static func GetItemTypeInventory() -> String { return "inv"; }
    public static func GetItemTypeProgressive() -> String { return "prog"; }
    public static func GetItemTypeDistrict() -> String { return "dat"; }

    // ===== DISTRICT ACCESS TOKEN IDS =====
    // These are the item IDs for district unlock tokens
    public static func GetWatsonAccessToken() -> String { return "ap_dat_watson"; }
    public static func GetWestbrookAccessToken() -> String { return "ap_dat_westbrookAccessToken"; }
    public static func GetCityCenterAccessToken() -> String { return "ap_dat_city_centerAccessToken"; }
    public static func GetHeywoodAccessToken() -> String { return "ap_dat_heywoodAccessToken"; }
    public static func GetSantoDomingoAccessToken() -> String { return "ap_dat_santoDomingoAccessToken"; }
    public static func GetPacificaAccessToken() -> String { return "ap_dat_pacificaAccessToken"; }
    public static func GetBadlandsAccessToken() -> String { return "ap_dat_badlandsAccessToken"; }
    public static func GetDogtownAccessToken() -> String { return "ap_dat_dogtownAccessToken"; }

    // ===== PROTOCOL MESSAGES =====
    // Network protocol command strings
    public static func GetProtocolHello() -> String { return "HELLO"; }
    public static func GetProtocolConnectReq() -> String { return "CONNECT_REQ"; }
    public static func GetProtocolSyncItems() -> String { return "SYNC_ITEMS"; }
    public static func GetProtocolSyncChecks() -> String { return "SYNC_CHECKS"; }
    public static func GetProtocolSyncConfig() -> String { return "SYNC_CONFIG"; }
    public static func GetProtocolSyncComplete() -> String { return "SYNC_COMPLETE"; }
    public static func GetProtocolOkReady() -> String { return "OK_READY"; }
    public static func GetProtocolDeathLink() -> String { return "DEATHLINK_SEND"; }
    public static func GetProtocolDeathLinkReceived() -> String { return "DEATHLINK_RECEIVED"; }
    public static func GetProtocolItemReceived() -> String { return "ITEM_RECEIVED"; }
    public static func GetProtocolCheck() -> String { return "CHECK"; }

    // Protocol response status
    public static func GetProtocolStatusOk() -> String { return "OK"; }
    public static func GetProtocolStatusFail() -> String { return "FAIL"; }

    // ===== SPECIAL ITEM IDS =====
    public static func GetMoneyItemId() -> String { return "Items.money"; }

    // ===== QUEST FACT NAMES =====
    // Important quest facts used for progression tracking
    public static func GetQuestQ000Done() -> String { return "q000_done"; }
    public static func GetQuestQ001Done() -> String { return "q001_done"; }
    public static func GetQuestQ101Done() -> String { return "ap_q101_resurrection"; }
    public static func GetQuestQ101_01_firestormDone() -> String { return "ap_q101_01_firestorm"; }
    public static func GetTarotCounterFact() -> String { return "mq033_grafitti_counter"; }
    public static func GetVPillsFact() -> String { return "q101_v_reached_pills"; }

    // ===== SERVICE NAMES =====
    // CNames for retrieving services from the game engine
    public static func GetAPGameSystemName() -> CName { return n"Archipelago.APGameSystem"; }
    public static func GetAPGameStateName() -> CName { return n"Archipelago.APGameState"; }
    public static func GetTCPClientName() -> CName { return n"Archipelago.TCPClient"; }

    // ===== CONFIGURATION OPTIONS =====
    // Config option keys sent from server
    public static func GetConfigDeathLink() -> String { return "death_link"; }
    public static func GetConfigSkillPointsAsItems() -> String { return "skill_points_as_items"; }
    public static func GetConfigValueTrue() -> String { return "true"; }
    public static func GetConfigValueFalse() -> String { return "false"; }

    // ===== ITEM ID PREFIX =====
    // All Archipelago items start with this prefix
    public static func GetItemPrefix() -> String { return "ap"; }

    // ===== TAROT PREFIX =====
    public static func GetTarotCheckPrefix() -> String { return "ap_tarot_"; }

    // ===== PHONE EXTENSION =====
    public static func GetArchipelagoContactHash() -> Int32 { return 20777702; }

    // ===== DEBUG LOGGING =====
    // Set quest fact "ap_enable_debug_logs" to 1 in CET console to enable verbose logging
    public static func GetDebugLogFact() -> CName { return n"ap_enable_debug_logs"; }
}
