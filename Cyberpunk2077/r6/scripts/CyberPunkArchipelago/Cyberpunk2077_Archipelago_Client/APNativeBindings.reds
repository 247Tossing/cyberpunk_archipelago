module Archipelago

// RED4ext native bindings exposed by CyberpunkAP.dll
public static native func AP_Initialize(server: String, gameName: String, slotName: String, password: String) -> Bool
public static native func AP_Connect() -> Bool
public static native func AP_Disconnect() -> Void
public static native func AP_IsConnected() -> Bool
public static native func AP_GetConnectionStatus() -> Int32
public static native func AP_GetLastConnectionError() -> String
public static native func AP_SendLocationCheck(locationId: Int64) -> Bool
public static native func AP_SendDeathLink(cause: String) -> Bool
public static native func AP_Say(text: String) -> Bool
public static native func AP_StoryComplete() -> Bool
public static native func AP_IsDeathLinkPending() -> Bool
public static native func AP_ClearDeathLink() -> Void
public static native func AP_PollItemQueue() -> Int64
public static native func AP_GetPolledItemNotifySender() -> String
public static native func AP_GetPolledItemNotifyDisplayName() -> String
public static native func AP_GetPolledItemNetworkIndex() -> Int32
public static native func AP_GetPolledItemShouldNotify() -> Bool
public static native func AP_GetRestrictByMajorDistrict() -> Bool
public static native func AP_GetRestrictBySubDistrict() -> Bool
public static native func AP_GetDistrictTokenGatedMajorMask() -> Int32
public static native func AP_GetWeaponRestrictionType() -> Int32
public static native func AP_GetWeaponRestrictPistol() -> Bool
public static native func AP_GetWeaponRestrictMelee() -> Bool
public static native func AP_GetWeaponRestrictRifle() -> Bool
public static native func AP_GetWeaponRestrictSniper() -> Bool
public static native func AP_GetWeaponRestrictLmg() -> Bool
public static native func AP_GetWeaponRestrictShotgun() -> Bool
public static native func AP_GetWeaponRestrictSmg() -> Bool
public static native func AP_GetVendorSanityEnabled() -> Bool
public static native func AP_GetVendorSanityStockLine() -> String
public static native func AP_GetDeathLinkEnabled() -> Bool

// Thin wrappers around the generated APArchipelagoIdMappings class.
// The actual id <-> string tables live in APArchipelagoIdMappings.reds, which is
// emitted by worlds/cyberpunk2077/tools/generate_redscript_ap_mappings.py as
// part of the .apworld build pipeline (tools/build_cyberpunk2077_apworld.py).
// Do not hand-edit those tables here.
public class APNativeMappings {
    public static func ResolveLocationAddress(locationId: String) -> Int64 {
        return APArchipelagoIdMappings.ResolveLocationAddress(locationId);
    }

    public static func ResolveItemId(itemId: Int64) -> String {
        return APArchipelagoIdMappings.ResolveItemId(itemId);
    }
}

