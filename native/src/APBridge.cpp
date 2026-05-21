#include "APBridge.hpp"
#include "ItemMapping.hpp"
#include "LocationMapping.hpp"
#include "DisplayNameMapping.hpp"

// APCpp public API
#include "Archipelago.h"

#include <sstream>

namespace Archipelago {

// ---------------------------------------------------------------------------
// Destruction
// ---------------------------------------------------------------------------

APBridge::~APBridge() {
    if (m_connected.load()) {
        AP_Shutdown();
    }
}

// ---------------------------------------------------------------------------
// Connection management
// ---------------------------------------------------------------------------

void APBridge::Connect(Red::CString host, int32_t port,
                       Red::CString slotName, Red::CString password) {
    if (m_connected.load()) {
        Disconnect();
    }

    const std::string hostStr   = host.c_str();
    const std::string slotStr   = slotName.c_str();
    const std::string passStr   = password.c_str();
    const std::string gameName  = "Cyberpunk 2077";

    // Build the address string APCpp expects: "host:port"
    const std::string address = hostStr + ":" + std::to_string(port);

    AP_Init(address.c_str(), gameName.c_str(), slotStr.c_str(), passStr.c_str());

    // -----------------------------------------------------------------------
    // Required callbacks
    // -----------------------------------------------------------------------

    AP_SetItemClearCallback([this]() {
        OnItemClear();
    });

    AP_SetItemRecvCallback([this](int64_t apItemId, bool notify) {
        OnItemReceived(apItemId, notify);
    });

    // Location-checked callback: AP server confirming one of our checks.
    // We don't need to do anything here – the game already set the quest fact
    // before calling SendCheck, so the check is already recorded locally.
    AP_SetLocationCheckedCallback([](int64_t /*locationId*/) {});

    // -----------------------------------------------------------------------
    // Optional callbacks
    // -----------------------------------------------------------------------

    AP_SetDeathLinkRecvCallback([this](const std::string& source, const std::string& cause) {
        OnDeathLinkReceived(source, cause);
    });

    // Slot data – boolean options (death_link comes through as an int 0/1)
    AP_RegisterSlotDataIntCallback("death_link", [this](int v) {
        OnSlotDataInt("death_link", v);
    });
    AP_RegisterSlotDataIntCallback("skill_points_as_items", [this](int v) {
        OnSlotDataInt("skill_points_as_items", v);
    });
    AP_RegisterSlotDataIntCallback("restrict_by_major_district", [this](int v) {
        OnSlotDataInt("restrict_by_major_district", v);
    });
    AP_RegisterSlotDataIntCallback("weapon_restriction_type", [this](int v) {
        OnSlotDataInt("weapon_restriction_type", v);
    });
    AP_RegisterSlotDataIntCallback("weapon_restrict_pistol",  [this](int v) { OnSlotDataInt("weapon_restrict_pistol",  v); });
    AP_RegisterSlotDataIntCallback("weapon_restrict_smg",     [this](int v) { OnSlotDataInt("weapon_restrict_smg",     v); });
    AP_RegisterSlotDataIntCallback("weapon_restrict_shotgun", [this](int v) { OnSlotDataInt("weapon_restrict_shotgun", v); });
    AP_RegisterSlotDataIntCallback("weapon_restrict_sniper",  [this](int v) { OnSlotDataInt("weapon_restrict_sniper",  v); });
    AP_RegisterSlotDataIntCallback("weapon_restrict_lmg",     [this](int v) { OnSlotDataInt("weapon_restrict_lmg",     v); });
    AP_RegisterSlotDataIntCallback("weapon_restrict_rifle",   [this](int v) { OnSlotDataInt("weapon_restrict_rifle",   v); });
    AP_RegisterSlotDataIntCallback("weapon_restrict_melee",   [this](int v) { OnSlotDataInt("weapon_restrict_melee",   v); });
    AP_RegisterSlotDataIntCallback("include_phantom_liberty_dlc", [this](int v) { OnSlotDataInt("include_phantom_liberty_dlc", v); });

    // Enable human-readable message queueing so we can retrieve sender names.
    AP_EnableQueueItemRecvMsgs(true);
    AP_SetDeathLinkSupported(true);

    {
        std::lock_guard lk(m_mutex);
        m_statusMessage = "Connecting to " + address + " as " + slotStr + "...";
    }

    AP_Start();
    m_connected.store(true);
}

void APBridge::Disconnect() {
    if (m_connected.load()) {
        AP_Shutdown();
        m_connected.store(false);
        std::lock_guard lk(m_mutex);
        m_statusMessage = "Disconnected";
    }
}

bool APBridge::IsConnected() const {
    if (!m_connected.load()) return false;
    return AP_GetConnectionStatus() == AP_ConnectionStatus::Authenticated;
}

Red::CString APBridge::GetConnectionStatus() const {
    if (!m_connected.load()) {
        return Red::CString("Not connected");
    }
    switch (AP_GetConnectionStatus()) {
        case AP_ConnectionStatus::Disconnected:    return Red::CString("Disconnected");
        case AP_ConnectionStatus::Connected:       return Red::CString("Connected (authenticating...)");
        case AP_ConnectionStatus::Authenticated:   {
            std::lock_guard lk(m_mutex);
            return Red::CString(m_statusMessage.c_str());
        }
        case AP_ConnectionStatus::ConnectionRefused:
            return Red::CString("Connection refused – check credentials");
        default:
            return Red::CString("Unknown");
    }
}

// ---------------------------------------------------------------------------
// Outgoing game events
// ---------------------------------------------------------------------------

void APBridge::SendCheck(Red::CString locationCheckId) {
    const std::string checkStr = locationCheckId.c_str();
    int64_t apId = LookupLocationId(checkStr);
    if (apId < 0) {
        // Unknown check – silently ignore (may be a non-randomised quest)
        return;
    }
    AP_SendItem(apId);
}

void APBridge::SendTarotCheck(int32_t tarotNumber) {
    const std::string checkId = "ap_tarot_" + std::to_string(tarotNumber);
    int64_t apId = LookupLocationId(checkId);
    if (apId >= 0) {
        AP_SendItem(apId);
    }
}

void APBridge::StoryComplete() {
    AP_StoryComplete();
}

void APBridge::SendDeathLink(Red::CString cause) {
    AP_DeathLinkSend(cause.c_str());
}

// ---------------------------------------------------------------------------
// Polling
// ---------------------------------------------------------------------------

bool APBridge::HasPendingItems() const {
    std::lock_guard lk(m_mutex);
    return !m_itemQueue.empty();
}

Red::CString APBridge::PollNextItem() {
    std::lock_guard lk(m_mutex);
    if (m_itemQueue.empty()) return Red::CString("");
    return Red::CString(m_itemQueue.front().gameId.c_str());
}

Red::CString APBridge::PollNextItemSender() {
    std::lock_guard lk(m_mutex);
    if (m_itemQueue.empty()) return Red::CString("");
    return Red::CString(m_itemQueue.front().sender.c_str());
}

Red::CString APBridge::PollNextItemDisplayName() {
    std::lock_guard lk(m_mutex);
    if (m_itemQueue.empty()) return Red::CString("");
    return Red::CString(m_itemQueue.front().displayName.c_str());
}

void APBridge::ClearPendingItem() {
    std::lock_guard lk(m_mutex);
    if (!m_itemQueue.empty()) m_itemQueue.pop();
}

bool APBridge::IsDeathLinkPending() const {
    return m_deathLinkPending.load();
}

void APBridge::ClearDeathLink() {
    m_deathLinkPending.store(false);
    AP_DeathLinkClear();
}

bool APBridge::IsClearRequested() const {
    return m_clearRequested.load();
}

void APBridge::ConsumeClearRequest() {
    m_clearRequested.store(false);
}

// ---------------------------------------------------------------------------
// Slot data
// ---------------------------------------------------------------------------

bool APBridge::GetSlotDataBool(Red::CString key, bool defaultValue) const {
    std::lock_guard lk(m_mutex);
    auto it = m_slotDataInt.find(key.c_str());
    if (it != m_slotDataInt.end()) return it->second != 0;
    auto jt = m_slotDataBool.find(key.c_str());
    if (jt != m_slotDataBool.end()) return jt->second;
    return defaultValue;
}

int32_t APBridge::GetSlotDataInt(Red::CString key, int32_t defaultValue) const {
    std::lock_guard lk(m_mutex);
    auto it = m_slotDataInt.find(key.c_str());
    if (it != m_slotDataInt.end()) return static_cast<int32_t>(it->second);
    return defaultValue;
}

// ---------------------------------------------------------------------------
// Private callbacks (called from the APCpp network thread)
// ---------------------------------------------------------------------------

void APBridge::OnItemClear() {
    std::lock_guard lk(m_mutex);
    while (!m_itemQueue.empty()) m_itemQueue.pop();
    m_clearRequested.store(true);
}

void APBridge::OnItemReceived(int64_t apItemId, bool /*notify*/) {
    // Try to look up the internal game ID by AP item ID.
    std::string_view gameIdView = LookupItemGameId(apItemId);

    // Simultaneously drain the AP message queue to get display name + sender.
    std::string displayName;
    std::string sender;
    if (AP_IsMessagePending()) {
        AP_Message* msg = AP_GetLatestMessage();
        if (msg && msg->type == AP_MessageType::ItemRecv) {
            auto* itemMsg = static_cast<AP_ItemRecvMessage*>(msg);
            displayName = itemMsg->item;
            sender      = itemMsg->sendPlayer;

            // If we didn't find the game ID by integer ID, try the display name.
            if (gameIdView.empty()) {
                gameIdView = LookupItemByDisplayName(displayName);
            }
            AP_ClearLatestMessage();
        }
    }

    if (gameIdView.empty()) {
        // Unknown item – skip; not in our world's item table.
        return;
    }

    PendingItem pending;
    pending.gameId      = std::string(gameIdView);
    pending.displayName = displayName.empty() ? pending.gameId : displayName;
    pending.sender      = sender;

    std::lock_guard lk(m_mutex);
    m_itemQueue.push(std::move(pending));

    // Update status message once connected + receiving items.
    m_statusMessage = "Authenticated";
}

void APBridge::OnDeathLinkReceived(const std::string& /*source*/, const std::string& /*cause*/) {
    m_deathLinkPending.store(true);
}

void APBridge::OnSlotDataInt(const std::string& key, int value) {
    std::lock_guard lk(m_mutex);
    m_slotDataInt[key] = value;
    // Mirror bool-typed keys into m_slotDataBool for convenience.
    m_slotDataBool[key] = (value != 0);
}

// ---------------------------------------------------------------------------
// RedLib RTTI definition
// ---------------------------------------------------------------------------

RTTI_DEFINE_CLASS(APBridge, {
    RTTI_ALIAS("Archipelago.APNativeClient");

    // Connection
    RTTI_METHOD(Connect);
    RTTI_METHOD(Disconnect);
    RTTI_METHOD(IsConnected);
    RTTI_METHOD(GetConnectionStatus);

    // Outgoing
    RTTI_METHOD(SendCheck);
    RTTI_METHOD(SendTarotCheck);
    RTTI_METHOD(StoryComplete);
    RTTI_METHOD(SendDeathLink);

    // Polling
    RTTI_METHOD(HasPendingItems);
    RTTI_METHOD(PollNextItem);
    RTTI_METHOD(PollNextItemSender);
    RTTI_METHOD(PollNextItemDisplayName);
    RTTI_METHOD(ClearPendingItem);
    RTTI_METHOD(IsDeathLinkPending);
    RTTI_METHOD(ClearDeathLink);
    RTTI_METHOD(IsClearRequested);
    RTTI_METHOD(ConsumeClearRequest);

    // Slot data
    RTTI_METHOD(GetSlotDataBool);
    RTTI_METHOD(GetSlotDataInt);
});

} // namespace Archipelago
