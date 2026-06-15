#pragma once

#include <cstdint>
#include <mutex>
#include <queue>
#include <string>

#include "Archipelago.h"

namespace CyberpunkArchipelago
{
class APBridge
{
public:
    static APBridge& Get();

    bool Initialize(const std::string& serverAddress,
                    const std::string& gameName,
                    const std::string& slotName,
                    const std::string& password);
    bool Connect();
    void Shutdown();

    bool IsReady() const;
    bool IsConnected() const;
    int32_t GetConnectionStatus() const;
    std::string GetLastConnectionError() const;

    bool SendLocationCheck(int64_t locationId);
    bool SendDeathLink(const std::string& cause);
    bool StoryComplete();

    bool PollReceivedItemId(int64_t& outItemId);
    bool IsDeathLinkPending() const;
    void ClearDeathLink();

    bool GetRestrictByMajorDistrict() const;
    bool GetRestrictBySubDistrict() const;
    int32_t GetDistrictTokenGatedMajorMask() const;

private:
    APBridge() = default;
    APBridge(const APBridge&) = delete;
    APBridge& operator=(const APBridge&) = delete;

    static void OnItemClear();
    static void OnItemReceived(int64_t itemId, bool notify);
    static void OnLocationChecked(int64_t locationId);
    static void OnDeathLinkReceived();
    static void OnSlotDataRestrictByMajorDistrict(int value);
    static void OnSlotDataRestrictBySubDistrict(int value);
    static void OnSlotDataDistrictTokenGatedMajorMask(int value);

    bool IsReadyLocked() const; // caller must hold m_mutex

    void PushItem(int64_t itemId);
    void MarkDeathLinkPending();
    void SetRestrictByMajorDistrict(bool value);
    void SetRestrictBySubDistrict(bool value);
    void SetDistrictTokenGatedMajorMask(int32_t value);

    mutable std::mutex m_mutex;
    bool m_initialized{false};
    bool m_started{false};
    bool m_deathLinkPending{false};
    bool m_restrictByMajorDistrict{false};
    bool m_restrictBySubDistrict{false};
    int32_t m_districtTokenGatedMajorMask{0};
    std::queue<int64_t> m_receivedItemIds;
};
} // namespace CyberpunkArchipelago
