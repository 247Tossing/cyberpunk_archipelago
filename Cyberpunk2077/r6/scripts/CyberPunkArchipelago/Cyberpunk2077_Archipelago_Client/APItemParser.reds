module Archipelago

// Centralized item ID parsing to eliminate scattered parsing logic
// All Archipelago items follow the format: ap_[type]_[data]
public class APItemParser {

    // ===== MAIN PARSING FUNCTIONS =====

    // Check if an item ID is valid Archipelago format
    public static func IsValidAPItem(itemId: String) -> Bool {
        if StrLen(itemId) == 0 {
            return false;
        }

        let parts: array<String> = StrSplit(itemId, "_");
        if ArraySize(parts) < 2 {
            return false;
        }

        // Must start with "ap" prefix
        return StrCmp(parts[0], APConstants.GetItemPrefix()) == 0;
    }

    // Get the item type (qk, inv, ed, etc.)
    public static func GetItemType(itemId: String) -> String {
        let parts: array<String> = StrSplit(itemId, "_");
        if ArraySize(parts) >= 2 {
            return parts[1];
        }
        return "";
    }

    // ===== TYPE-SPECIFIC PARSERS =====

    // Parse eddies amount from: ap_ed_amount_[value]
    public static func ParseEddiesAmount(itemId: String) -> Int32 {
        let parts: array<String> = StrSplit(itemId, "_");
        if ArraySize(parts) >= 4 {
            return StringToInt(parts[3]);
        }
        return 0;
    }

    // Parse inventory item ID from: ap_inv_[ItemID]
    // Handles items with underscores in their ID (e.g., Items.Weapon_Base_Lexington)
    public static func ParseInventoryItemId(itemId: String) -> String {
        let parts: array<String> = StrSplit(itemId, "_");

        if ArraySize(parts) <= 2 {
            return "";
        }

        // Reconstruct the item ID, preserving underscores
        let reconstructedId: String = "";
        let i: Int32 = 2;

        while i < ArraySize(parts) {
            if i == 2 {
                reconstructedId = parts[i];
            } else {
                reconstructedId = reconstructedId + "_" + parts[i];
            }
            i += 1;
        }

        return reconstructedId;
    }

    // Check if item is a quest key
    public static func IsQuestKey(itemId: String) -> Bool {
        return StrCmp(APItemParser.GetItemType(itemId), APConstants.GetItemTypeQuestKey()) == 0;
    }

    // Check if item is eddies
    public static func IsEddies(itemId: String) -> Bool {
        return StrCmp(APItemParser.GetItemType(itemId), APConstants.GetItemTypeEddies()) == 0;
    }

    // Check if item is inventory item
    public static func IsInventoryItem(itemId: String) -> Bool {
        return StrCmp(APItemParser.GetItemType(itemId), APConstants.GetItemTypeInventory()) == 0;
    }

    // Check if item is progressive
    public static func IsProgressiveItem(itemId: String) -> Bool {
        return StrCmp(APItemParser.GetItemType(itemId), APConstants.GetItemTypeProgressive()) == 0;
    }

    // Check if item is district access token
    public static func IsDistrictToken(itemId: String) -> Bool {
        return StrCmp(APItemParser.GetItemType(itemId), APConstants.GetItemTypeDistrict()) == 0;
    }

    // Check if item is a trap
    public static func IsTrap(itemId: String) -> Bool {
        return StrCmp(APItemParser.GetItemType(itemId), APConstants.GetItemTypeTrap()) == 0;
    }

    // Check if item is a skill point
    public static func IsSkillPoint(itemId: String) -> Bool {
        return StrCmp(APItemParser.GetItemType(itemId), APConstants.GetItemTypeSkillPoint()) == 0;
    }

    // ===== PROTOCOL MESSAGE PARSING =====

    // Parse protocol message into parts
    public static func ParseProtocolMessage(message: String) -> array<String> {
        return StrSplit(message, ":");
    }

    // Get command from protocol message
    public static func GetProtocolCommand(message: String) -> String {
        let parts: array<String> = APItemParser.ParseProtocolMessage(message);
        if ArraySize(parts) >= 1 {
            return parts[0];
        }
        return "";
    }

    // Get status from protocol message (typically second part)
    public static func GetProtocolStatus(message: String) -> String {
        let parts: array<String> = APItemParser.ParseProtocolMessage(message);
        if ArraySize(parts) >= 2 {
            return parts[1];
        }
        return "";
    }

    // Parse item list from SYNC_ITEMS response
    // Format: SYNC_ITEMS:ITEMS:item1,item2,item3
    public static func ParseItemList(itemsString: String) -> array<String> {
        if StrLen(itemsString) == 0 {
            let emptyArray: array<String>;
            return emptyArray;
        }
        return StrSplit(itemsString, ",");
    }

    // Parse config options from SYNC_CONFIG response
    // Format: SYNC_CONFIG:OK:option1:value1,option2:value2
    public static func ParseConfigOptions(configString: String) -> array<String> {
        if StrLen(configString) == 0 {
            let emptyArray: array<String>;
            return emptyArray;
        }
        return StrSplit(configString, ",");
    }

    // ===== VALIDATION HELPERS =====

    // Validate that a protocol message has expected number of parts
    public static func ValidateProtocolParts(message: String, expectedParts: Int32) -> Bool {
        let parts: array<String> = APItemParser.ParseProtocolMessage(message);
        return ArraySize(parts) >= expectedParts;
    }

    // Check if protocol status is OK
    public static func IsProtocolStatusOk(status: String) -> Bool {
        return StrCmp(status, APConstants.GetProtocolStatusOk()) == 0;
    }

    // Check if protocol status is FAIL
    public static func IsProtocolStatusFail(status: String) -> Bool {
        return StrCmp(status, APConstants.GetProtocolStatusFail()) == 0;
    }
}
