#pragma once

// RED4ext / RedLib
#include <RED4ext/RED4ext.hpp>
#include <RedLib.hpp>

#include <atomic>
#include <mutex>
#include <queue>
#include <string>
#include <unordered_map>

namespace Archipelago {

// ---------------------------------------------------------------------------
// PendingItem – one item queued from the APCpp callback thread, waiting to be
// consumed by the game thread when RedScript calls PollNextItem().
// ---------------------------------------------------------------------------
struct PendingItem {
    std::string gameId;       // Internal game ID string, e.g. "ap_dat_westbrookAccessToken"
    std::string sender;       // Display name of the player who sent this item
    std::string displayName;  // Human-readable item name, e.g. "Westbrook Access Token"
};

// ---------------------------------------------------------------------------
// APBridge – native Red4ext class exposed to RedScript as APNativeClient.
//
// Ownership: Red4ext creates one instance per `new APNativeClient()` call in
// RedScript (it derives from IScriptable, not ScriptableService, so it is NOT
// a singleton). The TCPClient ScriptableService holds a ref to it.
//
// Threading model:
//   APCpp uses its own internal thread for network I/O and calls the callbacks
//   registered in Connect() from that thread.  All mutable state shared
//   between the network thread and the game thread is protected by m_mutex.
//   RedScript-visible methods MUST only be called from the game thread.
// ---------------------------------------------------------------------------
class APBridge : public Red::IScriptable {
public:
    APBridge() = default;
    ~APBridge() override;

    // -----------------------------------------------------------------------
    // Connection management (called from RedScript / CET)
    // -----------------------------------------------------------------------

    /// Connect directly to an Archipelago server.
    /// @param host       e.g. "archipelago.gg" or "192.168.1.5"
    /// @param port       AP server port, typically 38281
    /// @param slotName   Player slot name registered in the room
    /// @param password   Room password, or "" if none
    void Connect(Red::CString host, int32_t port,
                 Red::CString slotName, Red::CString password);

    void Disconnect();

    bool IsConnected() const;

    /// Human-readable connection status string (for CET UI display).
    Red::CString GetConnectionStatus() const;

    // -----------------------------------------------------------------------
    // Outgoing game events → Archipelago server
    // -----------------------------------------------------------------------

    /// Report a completed location check by its internal ID string
    /// (e.g. "q001_intro", "sts_wat_kab_01").  The bridge maps it to the
    /// numeric AP location ID and forwards via AP_SendItem.
    void SendCheck(Red::CString locationCheckId);

    /// Send a tarot card found event.  The game calls this with a 1-based
    /// tarot number; the bridge converts it to the location check string
    /// "tarot_N" used in the location table.
    void SendTarotCheck(int32_t tarotNumber);

    /// Notify the AP server that the player has completed their goal.
    void StoryComplete();

    /// Send a DeathLink event.
    void SendDeathLink(Red::CString cause);

    // -----------------------------------------------------------------------
    // Polling – must be called regularly from the game thread
    // (e.g. on player spawn or via a tick hook)
    // -----------------------------------------------------------------------

    bool HasPendingItems() const;

    /// Returns the internal game ID of the next queued item, or "" if empty.
    /// Call ClearPendingItem() after processing to advance the queue.
    Red::CString PollNextItem();

    /// Sender name for the item currently at the head of the queue.
    Red::CString PollNextItemSender();

    /// Display name for the item currently at the head of the queue.
    Red::CString PollNextItemDisplayName();

    /// Discard the head item and advance the queue.
    void ClearPendingItem();

    /// True if APCpp has received a DeathLink death while we were alive.
    bool IsDeathLinkPending() const;

    /// Consume the pending DeathLink flag (call after killing the player).
    void ClearDeathLink();

    /// True if APCpp received a "clear all items" signal (reconnect/resync).
    bool IsClearRequested() const;

    /// Consume the clear-requested flag.
    void ConsumeClearRequest();

    // -----------------------------------------------------------------------
    // Slot data – populated by APCpp slot data callbacks after authentication
    // -----------------------------------------------------------------------

    /// Returns the value for a boolean slot data key, or defaultValue if absent.
    bool GetSlotDataBool(Red::CString key, bool defaultValue) const;

    /// Returns the value for an integer slot data key, or defaultValue if absent.
    int32_t GetSlotDataInt(Red::CString key, int32_t defaultValue) const;

    RTTI_IMPL_TYPEINFO(APBridge);
    RTTI_IMPL_ALLOCATOR();

private:
    // Called from APCpp's network thread – must be thread-safe.
    void OnItemClear();
    void OnItemReceived(int64_t apItemId, bool notify);
    void OnDeathLinkReceived(const std::string& source, const std::string& cause);
    void OnSlotDataInt(const std::string& key, int value);

    mutable std::mutex m_mutex;

    std::queue<PendingItem>                    m_itemQueue;
    std::atomic<bool>                          m_clearRequested{false};
    std::atomic<bool>                          m_deathLinkPending{false};
    std::atomic<bool>                          m_connected{false};

    std::unordered_map<std::string, bool>      m_slotDataBool;
    std::unordered_map<std::string, int>       m_slotDataInt;

    std::string                                m_statusMessage{"Not connected"};
};

} // namespace Archipelago
