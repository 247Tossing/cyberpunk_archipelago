// APNativeClient.reds
// Native class stub declaration for the CyberpunkArchipelagoPlugin Red4EXT DLL.
//
// The actual implementation lives in:
//   red4ext/plugins/CyberpunkArchipelagoPlugin/CyberpunkArchipelagoPlugin.dll
//
// This file just tells the RedScript compiler what methods exist so the rest
// of the mod can call them.  Do not add method bodies here – they are defined
// in C++.

module Archipelago

/// Direct Archipelago client backed by APCpp (native C++ library).
/// Replaces the RedSocket ↔ Python bridge architecture.
/// One instance is held by TCPClient (a ScriptableService).
public native class APNativeClient extends IScriptable {

    // -----------------------------------------------------------------------
    // Connection management
    // -----------------------------------------------------------------------

    /// Open a connection to an Archipelago server.
    /// @param host     Hostname or IP, e.g. "archipelago.gg"
    /// @param port     Server port, e.g. 38281
    /// @param slotName Player slot name registered in the room
    /// @param password Room password, or "" for none
    public native func Connect(host: String, port: Int32, slotName: String, password: String) -> Void;

    /// Cleanly disconnect from the server.
    public native func Disconnect() -> Void;

    /// True once the client has authenticated with the AP server.
    public native func IsConnected() -> Bool;

    /// Human-readable status string suitable for displaying in the CET overlay.
    public native func GetConnectionStatus() -> String;

    // -----------------------------------------------------------------------
    // Outgoing game events
    // -----------------------------------------------------------------------

    /// Report a completed location check.
    /// @param locationCheckId  Internal ID string, e.g. "q001_intro"
    public native func SendCheck(locationCheckId: String) -> Void;

    /// Report a tarot card found (the bridge converts the index to the AP ID).
    public native func SendTarotCheck(tarotNumber: Int32) -> Void;

    /// Mark the story as complete (triggers the AP victory condition).
    public native func StoryComplete() -> Void;

    /// Send a DeathLink event to the server.
    public native func SendDeathLink(cause: String) -> Void;

    // -----------------------------------------------------------------------
    // Incoming item polling
    // Call HasPendingItems() → PollNextItem() / PollNextItemSender() /
    // PollNextItemDisplayName() → ClearPendingItem() in a loop.
    // -----------------------------------------------------------------------

    /// True if at least one item is waiting to be delivered to the player.
    public native func HasPendingItems() -> Bool;

    /// Internal game ID string of the head item (what APItemParser expects).
    /// Returns "" when the queue is empty.
    public native func PollNextItem() -> String;

    /// Display name of the sender of the head item, e.g. "PlayerTwo".
    public native func PollNextItemSender() -> String;

    /// Human-readable name of the head item, e.g. "Westbrook Access Token".
    public native func PollNextItemDisplayName() -> String;

    /// Remove the head item from the queue.
    public native func ClearPendingItem() -> Void;

    // -----------------------------------------------------------------------
    // DeathLink
    // -----------------------------------------------------------------------

    /// True if a DeathLink death has arrived from the server.
    public native func IsDeathLinkPending() -> Bool;

    /// Consume the pending death and acknowledge it to APCpp.
    public native func ClearDeathLink() -> Void;

    // -----------------------------------------------------------------------
    // Item-clear / full re-sync signal
    // -----------------------------------------------------------------------

    /// True when APCpp signals that all items must be wiped and re-applied
    /// (happens on initial connect and on reconnect).
    public native func IsClearRequested() -> Bool;

    /// Consume the clear-requested flag.
    public native func ConsumeClearRequest() -> Void;

    // -----------------------------------------------------------------------
    // Slot data – populated after authentication
    // -----------------------------------------------------------------------

    /// Read a boolean slot-data value sent by the world when the room was created.
    public native func GetSlotDataBool(key: String, defaultValue: Bool) -> Bool;

    /// Read an integer slot-data value.
    public native func GetSlotDataInt(key: String, defaultValue: Int32) -> Int32;
}
