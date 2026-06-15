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
public static native func AP_StoryComplete() -> Bool
public static native func AP_IsDeathLinkPending() -> Bool
public static native func AP_ClearDeathLink() -> Void
public static native func AP_PollItemQueue() -> Int64
public static native func AP_GetRestrictByMajorDistrict() -> Bool
public static native func AP_GetRestrictBySubDistrict() -> Bool
public static native func AP_GetDistrictTokenGatedMajorMask() -> Int32

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

